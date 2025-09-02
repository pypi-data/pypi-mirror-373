import logging
import random
import semver

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from flags import Flags

from cyst.api.environment.stores import ExploitStore
from cyst.api.logic.exploit import Exploit, ExploitLocality, ExploitCategory
from netaddr import IPNetwork
from typing import List, Tuple, Optional, Dict, Any, Union, Callable, Awaitable, Set

from cyst.api.logic.action import Action
from cyst.api.logic.access import Authorization, AuthenticationToken
from cyst.api.environment.environment import EnvironmentMessaging
from cyst.api.environment.message import Request, Response, MessageType, Message, Signal, StatusValue, ComponentState, \
    StatusOrigin
from cyst.api.environment.resources import EnvironmentResources
from cyst.api.network.session import Session
from cyst.api.host.service import ActiveService, ActiveServiceDescription, Service
from cyst.api.utils.duration import msecs, Duration
from cyst.api.utils.counter import Counter

# ----------------------------------------------------------------------------------------------------------------------
# The network iterator is used to provide a chunks of IP addresses for discovery. It starts with a base address and
# a network range (in terms of significant bits, CIDR) and then works as an iterator giving the next chunk if needed.
# Because the attacker does not always have to be in the lowest section of an address range, it supports going to
# higher addresses, lower addresses, and even alternating, thus providing IPs further away from the base.
# ----------------------------------------------------------------------------------------------------------------------
class NetworkIteratorDirection(Enum):
    FORWARD = auto()
    BACKWARD = auto()
    ALTERNATING = auto()


class NetworkIterator:
    def __init__(self, base_ip: str, network_cidr: int, direction: NetworkIteratorDirection):
        self._base_net = IPNetwork(f"{base_ip}/{str(network_cidr)}")
        self._left_net = self._base_net.previous()
        self._right_net = self._base_net
        self._direction = direction
        self._right = False if direction == NetworkIteratorDirection.BACKWARD else True

    def __iter__(self):
        return self

    def __next__(self) -> IPNetwork:
        if self._right:
            result = self._right_net
            self._right_net = self._right_net.next()
            if self._direction == NetworkIteratorDirection.ALTERNATING:
                self._right = False
        else:
            result = self._left_net
            self._left_net = self._left_net.previous()
            if self._direction == NetworkIteratorDirection.ALTERNATING:
                self._right = True
        return result

    def base_net(self) -> IPNetwork:
        return self._base_net

# ----------------------------------------------------------------------------------------------------------------------
# Every possible target, i.e., the one revealed through a discovery, keeps track of the actions that can be done,
# the actions that has been done, and the resources available.
# ----------------------------------------------------------------------------------------------------------------------

# ExploitableService ties together service, action and exploit. In the first challenge, there are no authentication
# tokens, so we do not need to worry about it
@dataclass
class ExploitableService:
    action: Action
    service: str
    exploit: Exploit | None
    parameters: Dict[str, str] = field(default_factory=dict)
    ready: bool = False
    used: bool = False

# TargetState is used for deciding what to do next
class TargetState(Flags):
    REMOTELY_ACCESSIBLE = ()
    LOCALLY_ACCESSIBLE = ()
    REMOTELY_EXPLOITABLE = ()
    LOCALLY_EXPLOITABLE = ()
    EXFILTRATION_AVAILABLE = ()
    FINISHED = ()


# Target mostly tracks the information about target machines
class Target:
    def __init__(self, ip: str, services: List[Tuple[str, semver.VersionInfo]], exploit_store: ExploitStore,
                 actions: Dict[str, Action]):
        self._id = Counter().get("heuristic-agent.counter")
        self._ip = ip
        self._remote_services = services
        self._local_services = []
        self._state = TargetState.REMOTELY_ACCESSIBLE
        self._session = None
        self._exploit_store = exploit_store
        self._actions = actions

        self._remotely_exploitable = []
        self._locally_exploitable = []

        # When target is initialized, it is given the remotely accessible services. We check for available exploits...
        for service in self._remote_services:
            self._evaluate_service(service)

        # If there are any remotely exploitable services, we check, if they can go without parameters and if so, we
        # set the state to REMOTELY_EXPLOITABLE, which means that it can be remotely exploited as-is.
        for exploitable_service in self._remotely_exploitable:
            if exploitable_service.ready:
                self._state |= TargetState.REMOTELY_EXPLOITABLE
                break

    @property
    def id(self) -> int:
        return self._id

    @property
    def state(self) -> TargetState:
        return self._state

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def session(self) -> Session | None:
        return self._session

    def set_session(self, value: Session, local_access: bool = True) -> None:
        # Local access session do have priority and are not overwritten.
        # Remote access sessions can get overwritten by local access ones.
        if local_access:
            self._session = value
            # Mark that the target supports local access
            self._state |= TargetState.LOCALLY_ACCESSIBLE
            # And disable all actions that would provide the local access again
            for es in self._remotely_exploitable:
                if es.action.id == "ac1:access_target" and not es.used:
                    es.used = True
        else:
            if not self._session:
                self._session = value

    @property
    def remote_services(self) -> List[Tuple[str, semver.VersionInfo]]:
        return self._remote_services

    @property
    def local_services(self) -> List[Tuple[str, semver.VersionInfo]]:
        return self._local_services

    def add_local_service(self, service: Tuple[str, semver.VersionInfo]):
        self._local_services.append(service)
        self._evaluate_service(service)

    @property
    def remotely_exploitable(self) -> List[ExploitableService]:
        return self._remotely_exploitable

    @property
    def locally_exploitable(self) -> List[ExploitableService]:
        return self._locally_exploitable

    def add_data_paths(self, service: str, paths: List):
        data_for_exfiltration = False
        # We cheat a bit and use only the first path
        path = paths[0]
        # First we check for exploitable services, if they are not missing a path parameter. If they do,
        # add it and mark it ready for attack
        for es in [*self._remotely_exploitable, *self._locally_exploitable]:
            if es.action.id == "ac1:exfiltrate_data" and es.service == service and not es.ready:
                es.parameters["path"] = path
                es.ready = True
                data_for_exfiltration = True

        # Then we add exploit-free exfiltration action to local exploitables, if it is not already there
        if service not in [es.service for es in self._locally_exploitable]:
            self._locally_exploitable.append(ExploitableService(self._actions["ac1:exfiltrate_data"], service, None,
                                                                {"path": path}, True, False))
            data_for_exfiltration = True

        if data_for_exfiltration:
            self._state |= TargetState.EXFILTRATION_AVAILABLE

    def _evaluate_service(self, service: Tuple[str, semver.VersionInfo]):
        exploits = self._exploit_store.get_exploit(service=service[0])
        if exploits:
            for exploit in exploits:
                for vulnerable_service in exploit.services.values():
                    if vulnerable_service.min_version <= service[1] <= vulnerable_service.max_version:
                        if exploit.category == ExploitCategory.CODE_EXECUTION:
                            action = self._actions["ac1:access_target"]
                        elif exploit.category == ExploitCategory.DATA_MANIPULATION:
                            action = self._actions["ac1:exfiltrate_data"]
                        else:
                            # We are not ready for another exploit category, so we just skip it
                            continue

                        # Action requiring parameters cannot be executed right away (at least that's what goes for
                        # the two that we have here
                        ready = not action.parameters

                        if exploit.locality == ExploitLocality.LOCAL:
                            self._locally_exploitable.append(
                                ExploitableService(action, service[0], exploit, ready=ready))
                        else:
                            self._remotely_exploitable.append(
                                ExploitableService(action, service[0], exploit, ready=ready))

# ----------------------------------------------------------------------------------------------------------------------
class AgentState(Enum):
    INIT = auto()
    DISCOVERING = auto()
    PROBING = auto()
    BREACHING = auto()
    EXFILTRATING = auto()
    EVADING = auto()


class MyAgent(ActiveService):
    def __init__(self, msg: EnvironmentMessaging, res: EnvironmentResources, id: str, args: Optional[Dict[str, Any]]):
        self._msg = msg
        self._res = res
        self._id = id
        self._args = args
        self._log = logging.getLogger("service.heuristic_agent")

        self._actions = {x.id: x for x in self._res.action_store.get_prefixed("ac1")}

        self._state = AgentState.INIT
        self._last_state = AgentState.INIT

        self._origin_ips = []
        self._target_networks: Dict[str, List[NetworkIterator]] = {}

        self._targets: Dict[int, Target] = {}
        self._targets_discovered: Set[str] = set()
        self._last_target: Target | None = None
        self._probe_counter = 0

        self._discovered: List[int] = []
        self._breaching: List[int] = []
        self._probing: List[int] = []
        self._exfiltrating: List[int] = []
        self._finished: List[int] = []

        self._sessions: Dict[str, Session] = {}

        self._last_request: Optional[Request] = None
        self._evading_delay = 10
        self._evade_probe_id = -1

        self._goal_reached = False

        # If we are given target network, we do not do the look-around step and instead take a mid-IP as a starting
        # point and then look there
        if "target_network" in self._args:
            net = IPNetwork(self._args["target_network"])
            base_ip = str(net.network + (net.last - net.first) // 2)
            iterator = NetworkIterator(base_ip, 29, NetworkIteratorDirection.ALTERNATING)
            self._target_networks[""] = [iterator]

    async def run(self):
        self._log.info(f"Running the agent with id '{self._id}'")

        # If we already have a target, we proceed
        if self._target_networks:
            self._send_next_action()
        # Otherwise, we use the information about the agent as a starting point
        else:
            self._log.info("Sending a self-inspecting requests")
            req = self._msg.create_request("127.0.0.1", "", action=self._actions["ac1:inspect"])
            self._msg.send_message(req)

    # Review agent's state according to target queues
    def _update_agent_state(self):
        if self._state == AgentState.EVADING:
            self._state = AgentState.EVADING
        elif self._exfiltrating:
            self._state = AgentState.EXFILTRATING
        elif self._probing:
            self._state = AgentState.PROBING
        elif self._breaching:
            self._state = AgentState.BREACHING
        else:
            self._state = AgentState.DISCOVERING

        if self._last_state != self._state:
            self._log.info(f"Changing agent's state from {self._last_state.name} to {self._state.name}")
            self._last_state = self._state

    def _send_next_action(self):
        # Before choosing the next action, update agent's state according to target states
        self._update_agent_state()

        request = None

        if self._state == AgentState.EVADING:
            # When the agent is evading defensive actions (currently only by a delay), we do progressively longer
            # delays in message sending to find out, when we can attack again.
            # For that, we attack a first target IP
            action = self._actions["ac1:scan_host"]
            target = next(self._target_networks[""][0].base_net().iter_hosts())
            probe = self._msg.create_request(target, "", action)
            self._evade_probe_id = probe.id
            self._msg.send_message(probe, self._evading_delay)
            # We send the message with a delay and do not store it in a request_queue
            return

        # If there is anything in the request queue, we resend it as fast as we can
        if self._last_request:
            # we make a copy of the request to prevent id repetition
            request = self._msg.create_request(dst_ip=self._last_request.dst_ip,
                                               dst_service=self._last_request.dst_service,
                                               action=self._last_request.action,
                                               session=self._last_request.session,
                                               auth=self._last_request.auth)

            self._log.info(f"Resending a request with original ID {self._last_request.id}")

            self._msg.send_message(request)
            return

        # When the agent is in discovering mode, it tries to scan around itself in small chunks
        if self._state == AgentState.DISCOVERING:
            # We select a session ID that we want to use (the preference is to use an existing session)
            session_id = random.choice(list(self._sessions.keys())) if self._sessions else ""
            # And we select a random network associated with the session
            target_net: IPNetwork = next(random.choice(self._target_networks[session_id]))
            # We set it as an action parameter
            action = self._actions["ac1:scan_network"]
            action.parameters["net"].value = target_net

            self._log.info(f"Scanning network '{str(target_net)}' for potential targets. Session: '{"None" if not session_id else session_id}'.")

            # Then we just craft and send the scanning message
            request = self._msg.create_request(target_net.ip, "", action, session=self._sessions.get(session_id, None))

        # In breaching mode, an agents chooses a breachable target and attempts to attack
        if self._state == AgentState.BREACHING:
            # Choose a random viable target
            breach_id = random.choice(range(len(self._breaching)))
            target = self._targets[self._breaching[breach_id]]

            # Choose a random exploitable service
            exploitable_services = [service for service in target.remotely_exploitable if service.ready and not service.used]
            exploitable_service: ExploitableService = random.choice(exploitable_services)

            # Set exploit and action parameters
            exploitable_service.action.set_exploit(exploitable_service.exploit)
            for name, value in exploitable_service.parameters.items():
                exploitable_service.action.parameters[name].value = value

            self._log.info(f"Attempting to breach the target with IP {target.ip}, using the {exploitable_service.action.id} action.")

            # Create and send the breach request
            request = self._msg.create_request(target.ip, exploitable_service.service, exploitable_service.action, session=target.session)

            # Do not repeat already done actions
            exploitable_service.used = True

            # If there was only one exploitable service, we remove the target from breaching queue. It the breach
            # is successful, this will happen anyway
            if len(exploitable_services) == 1:
                del self._breaching[breach_id]
                self._discovered.append(target.id)

            # We keep track of the last target, so that it is easier to link responses
            self._last_target = target

        if self._state == AgentState.PROBING:
            # Choose a random target viable for probing
            probe_id = random.choice(range(len(self._probing)))
            target = self._targets[self._probing[probe_id]]

            self._log.info(f"Starting an inspection of locally accessed target with IP {target.ip}")

            # Run the inspect action, we do not know about local services yet, so we use it to get a list of them
            request = self._msg.create_request(target.ip, "", self._actions["ac1:inspect"], target.session)

            self._last_target = target
            # We keep the target in the probing queue, because there will be more probing actions after this one on
            # the same target

        if self._state == AgentState.EXFILTRATING:
            # Choose a random target available for exfiltrating
            exfiltrate_id = random.choice(range(len(self._exfiltrating)))
            target = self._targets[self._exfiltrating[exfiltrate_id]]

            # Select a random exfiltrating action
            exploitable_services = [service for service in [*target.remotely_exploitable, *target.locally_exploitable]
                                    if service.ready and not service.used and service.action.id == "ac1:exfiltrate_data"]
            exploitable_service = random.choice(exploitable_services)

            # Create and send the request
            # The 'path' parameter we know that we already set.
            # We are using session regardless of the remote/local exploit distinction. Remote exploits work locally.
            action = self._actions["ac1:exfiltrate_data"]
            action.parameters["path"].value = exploitable_service.parameters["path"]

            self._log.info(f"Attempting to exfiltrate data from the target with IP {target.ip}. I am using a "
                           f"{"remote exploit" if exploitable_service.exploit else "local access"} "
                           f"to get data at '{exploitable_service.parameters["path"]}'.")

            request = self._msg.create_request(target.ip, exploitable_service.service, action, target.session)

            exploitable_service.used = True
            # If there are no more ways to exfiltrate data on this target, we move it to finished pile.
            if len(exploitable_services) == 1:
                del self._exfiltrating[exfiltrate_id]
                self._finished.append(target.id)

        if request:
            self._last_request = request
            self._msg.send_message(request)

    def _process_response_access_target(self, response: Response) -> Tuple[bool, Duration]:
        # If we do not successfully access the target, we ignore it
        if response.status.value == StatusValue.SUCCESS:
            # If the target access was successful, we get a session to it, so we store it ...
            self._last_target.set_session(response.session)
            # ... add it among the agent's sessions ...
            self._sessions[response.session.id] = response.session
            # ... create a target network with the session end as a base_ip for further discovery ...
            self._target_networks[response.session.id] = [NetworkIterator(str(response.session.end[0]), 29, NetworkIteratorDirection.ALTERNATING)]
            # ... and add the target to the probing queue and remove it from the breaching queue.
            if self._last_target.id in self._breaching:
                self._breaching.remove(self._last_target.id)
            self._probing.append(self._last_target.id)

            self._log.info(f"Successfully got session to the target with IP {str(response.src_ip)} with ID '{response.session.id}'.")

        self._send_next_action()

        return True, msecs(20)

    def _process_response_inspect(self, response: Response) -> Tuple[bool, Duration]:
        # Our first inspection, looking around ourselves
        if str(response.src_ip) == "127.0.0.1":
            if response.status.value != StatusValue.SUCCESS:
                self._log.error("Cannot get information about the closest environment, shutting down")
                return False, msecs(20)

            self._origin_ips = response.content["ips"]
            self._state = AgentState.DISCOVERING
            self._log.info(f"Local IPs: {self._origin_ips}")

            self._target_networks[""] = []
            for ip in self._origin_ips:
                self._target_networks[""].append(NetworkIterator(ip, 29, NetworkIteratorDirection.ALTERNATING))

            self._send_next_action()
        else:
            if response.status.value != StatusValue.SUCCESS:
                if response.src_service:
                    self._log.warn(f"Could not get detailed information about service '{response.src_service}' on target with ip '{response.src_ip}'")
                    # We could not get info about a service, but the rest may provide some clues. Just lower the
                    # counter and move on.
                    self._probe_counter -= 1
                else:
                    self._log.warn(f"Could not get detailed information about target with ip '{response.src_ip}'")
                    # At this point, we are not able to move on with the attack, so we remove the target from the
                    # probing queue
                    self._probe_counter = 0
            else:
                # If we were inspecting the whole machine and not concrete services, we update the local services list
                # and inspect all the available services afterward. If we were in a setting with multiple networks,
                # we would also take note of the IPs and eventually add them to our discovery pool.
                if not response.src_service:
                    # Whenever we do the inspect without target, we set the prob counter to zero
                    self._probe_counter = 0
                    for service in response.content["services"]:
                        # We do not know from the response of the inspect action, whether a service is remote or local,
                        # so we need to check it against what we have.
                        if service not in self._last_target.remote_services:
                            # And add it among the local services if it is new (this will check for exploits)
                            self._last_target.add_local_service(service)

                        self._log.info(f"Inspecting service '{service[0]}' at the target with IP {self._last_target.ip}.")

                        # We send inspect request to each service
                        request = self._msg.create_request(self._last_target.ip, service[0],
                                                           self._actions["ac1:inspect"], self._last_target.session)
                        self._msg.send_message(request)
                        # we increase the probe counter to keep track of when we should finish with probing
                        self._probe_counter += 1

                # In case of a specific service, we currently care only about the data part of the answer,
                # and we abuse the knowledge that only one interesting piece of data will be present now
                else:
                    paths = response.content.get("data", None)
                    # If there are data, we update the exploitables in the target
                    if paths:
                        self._log.info(f"Found data that can be exfiltrated from service '{response.src_service}' at the target with IP {response.src_ip}.")
                        self._last_target.add_data_paths(response.src_service, paths)
                    # Decrease the probe counter
                    self._probe_counter -= 1

            if self._probe_counter == 0:
                self._probing.remove(self._last_target.id)
                # If there is something to exfiltrate, do it. Otherwise, mark the target as finished
                if TargetState.EXFILTRATION_AVAILABLE in self._last_target.state:
                    self._exfiltrating.append(self._last_target.id)
                else:
                    self._finished.append(self._last_target.id)
                self._send_next_action()

        return True, msecs(20)

    def _process_response_scan_network(self, response: Response) -> Tuple[bool, Duration]:
        if response.status.value == StatusValue.SUCCESS:
            # Store the successfully discovered IPs for further breaching
            if response.content["success"]:
                for target in response.content["success"]:
                    # Skip self-scanning and re-probing
                    target_ip = str(target["ip"])
                    if not target_ip in self._origin_ips and not target_ip in self._targets_discovered:
                        self._targets_discovered.add(target_ip)
                        t = Target(target["ip"], target["services"], self._res.exploit_store, self._actions)
                        # Target only works with its session
                        if response.session:
                            t.set_session(response.session, False)
                        self._targets[t.id] = t
                        if TargetState.REMOTELY_EXPLOITABLE in t.state:
                            self._breaching.append(t.id)
                        else:
                            self._discovered.append(t.id)


        self._send_next_action()
        return True, msecs(20)

    def _process_response_exfiltrate_data(self, response: Response) -> Tuple[bool, Duration]:
        # If we are successful with exfiltration, we signal to the challenge that we are done
        if response.status.value == StatusValue.SUCCESS:
            self._log.info(f"Successfully exfiltrated the data!")
            self._goal_reached = True
            sig = self._msg.create_signal(signal_origin=self._id,
                                          state=ComponentState.FINISHED | ComponentState.GOAL_REACHED,
                                          effect_origin=self._id,
                                          effect_message=response.id)
            self._msg.send_message(sig)
            # We do not send another message
        # Otherwise, we move on...
        else:
            self._send_next_action()
        return True, msecs(20)

    def _process_response(self, response: Response) -> Tuple[bool, Duration]:
        # In case of network scan, any error represents a detection (currently)
        # In case of other actions, network.error is the telltale sign
        if (response.action.id == "ac1:scan_network" and response.content["error"]) or \
           (response.status.origin == StatusOrigin.NETWORK and response.status.value == StatusValue.ERROR):

            # If the agent is already in the evading state, we check if this is a response to our probe. If not,
            # we just keep the original request in the queue and otherwise do nothing.
            # If we, however, get a network.error response to our probe, we need to extend the evading delay
            if response.id == self._evade_probe_id:
                self._evading_delay += 10

            self._state = AgentState.EVADING
            self._send_next_action()
            return True, msecs(20)

        # If we are in the evading state, and we get a good response, we change our state to something else, and send
        # a next action. If a good response is not related to a probe, it means that there was some very delayed
        # response, and we process it normally.
        elif self._state == AgentState.EVADING:
            if response.id == self._evade_probe_id:
                self._state = AgentState.DISCOVERING
                self._send_next_action()
                return True, msecs(20)

        # If we got a normal response, we do not need to keep the last request
        self._last_request = None

        process_fn = getattr(self, '_process_response_' + response.action.id[4:], None)
        if not process_fn:
            return False, msecs(0)
        else:
            return process_fn(response)

    def _process_request(self, request: Request):
        self._log.info(f"Received a request with ID: {request.id} and action: {request.action.id}. Ignoring it...")
        return True, msecs(20)

    def _process_signal(self, signal: Signal):
        # If we receive a signal, it is a hint that everything is going down.
        # We ignore it in case the environment is shutting down, because we already reached the goal
        if not self._goal_reached:
            own_signal = self._msg.create_signal(signal_origin=self._id,
                                                 state=ComponentState.TERMINATED | ComponentState.GOAL_UNREACHABLE,
                                                 effect_origin=signal.effect_origin,
                                                 effect_message=signal.id)
            self._msg.send_message(own_signal)
        return True, msecs(20)

    async def process_message(self, message: Message) -> Tuple[bool, Duration]:
        if isinstance(message, Response):
            return self._process_response(message)
        elif isinstance(message, Request):
            return self._process_request(message)
        elif isinstance(message, Signal):
            return self._process_signal(message)
        else:
            return False, msecs(0)
        

def create_agent(msg: EnvironmentMessaging, res: EnvironmentResources, id: str, args: Optional[Dict[str, Any]]) -> ActiveService:
    actor = MyAgent(msg, res, id, args)
    return actor


service_description = ActiveServiceDescription(
    "aica-challenge-1-heuristic-agent",
    "A reference heuristic agent for the AICA challenge.",
    create_agent
)