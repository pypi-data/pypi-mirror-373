import asyncio

from cyst.api.logic.access import AccessLevel
from cyst.api.logic.exploit import ExploitCategory, ExploitLocality
from netaddr import IPNetwork
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedAsDataclass, Session, relationship
from typing import Tuple, Callable, Union, List, Coroutine, Optional

from cyst.api.environment.configuration import EnvironmentConfiguration
from cyst.api.environment.infrastructure import EnvironmentInfrastructure
from cyst.api.environment.message import Request, Response, Status, StatusOrigin, StatusValue, StatusDetail
from cyst.api.environment.messaging import EnvironmentMessaging
from cyst.api.environment.policy import EnvironmentPolicy
from cyst.api.environment.platform_specification import PlatformSpecification, PlatformType
from cyst.api.environment.resources import EnvironmentResources
from cyst.api.logic.action import ActionDescription, ActionParameterType, ActionParameter, Action, ActionType
from cyst.api.logic.behavioral_model import BehavioralModel, BehavioralModelDescription
from cyst.api.logic.composite_action import CompositeActionManager
from cyst.api.network.node import Node
from cyst.api.utils.duration import Duration, msecs


class AC1Model(BehavioralModel):
    def __init__(self, configuration: EnvironmentConfiguration, resources: EnvironmentResources,
                 policy: EnvironmentPolicy, messaging: EnvironmentMessaging, infrastructure: EnvironmentInfrastructure,
                 composite_action_manager: CompositeActionManager) -> None:

        self._configuration = configuration
        self._action_store = resources.action_store
        self._exploit_store = resources.exploit_store
        self._policy = policy
        self._messaging = messaging
        self._infrastructure = infrastructure
        self._cam = composite_action_manager

        self._action_store.add(ActionDescription(
            id="ac1:inspect",
            type=ActionType.DIRECT,
            platform=[PlatformSpecification(PlatformType.SIMULATED_TIME, "CYST"),
                      PlatformSpecification(PlatformType.REAL_TIME, "CYST")],
            description="Inspecting a machine, where you have an access to.",
            parameters=[])
        )

        self._action_store.add(ActionDescription(
            id="ac1:scan_host",
            type=ActionType.DIRECT,
            platform=[PlatformSpecification(PlatformType.SIMULATED_TIME, "CYST"),
                      PlatformSpecification(PlatformType.REAL_TIME, "CYST")],
            description="Scanning of one specific host",
            parameters=[])
        )

        self._action_store.add(ActionDescription(
            id="ac1:scan_network",
            type=ActionType.COMPOSITE,
            platform=[PlatformSpecification(PlatformType.SIMULATED_TIME, "CYST"),
                      PlatformSpecification(PlatformType.REAL_TIME, "CYST")],
            description="Scanning of a subnet",
            parameters=[ActionParameter(type=ActionParameterType.NONE, name="net",
                                        domain=configuration.action.create_action_parameter_domain_any())])
        )

        self._action_store.add(ActionDescription(
            id="ac1:access_target",
            type=ActionType.DIRECT,
            platform=[PlatformSpecification(PlatformType.SIMULATED_TIME, "CYST"),
                      PlatformSpecification(PlatformType.REAL_TIME, "CYST")],
            description="Use either exploit or a valid authentication/authorization to open a session to a target service",
            parameters=[])
        )

        self._action_store.add(ActionDescription(
            id="ac1:exfiltrate_data",
            type=ActionType.DIRECT,
            platform=[PlatformSpecification(PlatformType.SIMULATED_TIME, "CYST"),
                      PlatformSpecification(PlatformType.REAL_TIME, "CYST")],
            description="Exfiltrate an interesting data from a target.",
            parameters=[ActionParameter(type=ActionParameterType.NONE, name="path",
                                        domain=configuration.action.create_action_parameter_domain_any())]
        ))

    async def action_flow(self, message: Request) -> Tuple[Duration, Response]:
        if not message.action:
            raise ValueError("Action not provided")

        action_name = "_".join(message.action.fragments)
        fn: Callable[[Request], Coroutine[None, None, Tuple[Duration, Response]]] = getattr(self, "process_" + action_name, self.process_default_flow)
        duration, response = await fn(message)

        return duration, response

    async def action_effect(self, message: Request, node: Node) -> Tuple[Duration, Response]:
        if not message.action:
            raise ValueError("Action not provided")

        action_name = "_".join(message.action.fragments)
        fn: Callable[[Request, Node], Coroutine[None, None, Tuple[Duration, Response]]] = getattr(self, "process_" + action_name, self.process_default_effect)
        duration, response = await fn(message, node)

        return duration, response

    def action_components(self, message: Union[Request, Response]) -> List[Action]:
        return []

    async def process_default_effect(self, message: Request, node: Node) -> Tuple[Duration, Response]:
        error = f"A direct action with unknown semantics specified: {message.action.id}."
        return msecs(0), self._messaging.create_response(message, status=Status(StatusOrigin.SYSTEM, StatusValue.ERROR),
                                                         content=error, session=message.session)

    async def process_default_flow(self, message: Request) -> Tuple[Duration, Response]:
        error = f"A composite action with unknown semantics specified: {message.action.id}."
        return msecs(0), self._messaging.create_response(message, status=Status(StatusOrigin.SYSTEM, StatusValue.ERROR),
                                                         content=error, session=message.session)

    async def process_inspect(self, message: Request, node: Node) -> Tuple[Duration, Response]:

        if message.dst_ip != "127.0.0.1" and message.src_ip != message.dst_ip and \
                (message.session and message.session.end[0] != message.dst_ip):

            error = f"The agent does not have an access to the following IP address {message.dst_ip}."
            return msecs(20), self._messaging.create_response(message,
                                                              status=Status(StatusOrigin.SERVICE, StatusValue.FAILURE),
                                                              content=error, session=message.session)

        result = None
        status = None

        if not message.dst_service:
            services = []
            for service in node.services.values():
                if service.passive_service:
                    services.append((service.name, str(service.passive_service.version)))

            result = {
                "ips": [str(x) for x in node.ips],
                "services": services
            }
            status = Status(StatusOrigin.SERVICE, StatusValue.SUCCESS)
        else:
            if not message.dst_service in node.services:
                result = f"The service '{message.dst_service}' does not exist on the target machine."
                status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.SERVICE_NOT_EXISTING)
            else:
                service = node.services[message.dst_service].passive_service
                result = {
                    "name": message.dst_service,
                    "version": service.version,
                    "data": [x.path for x in self._configuration.service.private_data(service)]
                }
                status = Status(StatusOrigin.SERVICE, StatusValue.SUCCESS)

        return msecs(20), self._messaging.create_response(message, status=status, content=result,
                                                          session=message.session, auth=message.auth)

    async def process_scan_host(self, message: Request, node: Node) -> Tuple[Duration, Response]:
        host_ip = message.dst_ip
        services = []
        for service in node.services.values():
            if service.passive_service and not service.passive_service.local:
                services.append((service.name, str(service.passive_service.version)))

        result = {
            "ip": host_ip,
            "services": services
        }

        return msecs(40), self._messaging.create_response(message,
                                                          status=Status(StatusOrigin.SERVICE, StatusValue.SUCCESS),
                                                          session=message.session, auth=message.auth, content=result)

    async def process_scan_network(self, message: Request) -> Tuple[Duration, Response]:
        if "net" not in message.action.parameters or not message.action.parameters["net"].value:
            return msecs(0), self._messaging.create_response(message,
                                                             status=Status(StatusOrigin.SERVICE, StatusValue.FAILURE,
                                                                           StatusDetail.ACTION_PARAMETER_NOT_PROVIDED),
                                                             session=message.session, auth=message.auth)

        net = IPNetwork(message.action.parameters["net"].value)
        if not net:
            return msecs(0), self._messaging.create_response(message,
                                                             status=Status(StatusOrigin.SERVICE, StatusValue.FAILURE,
                                                                           StatusDetail.ACTION_PARAMETER_NOT_APPLICABLE),
                                                             session=message.session, auth=message.auth)

        tasks = []

        if net.prefixlen < 31:
            ips = [net.cidr.ip]
            ips.extend(list(net.iter_hosts()))
            ips.append(net.broadcast)
        else:
            ips = [net.iter_hosts()]

        for ip in ips:
            action = self._action_store.get("ac1:scan_host")
            request = self._messaging.create_request(ip, "", action, original_request=message)
            tasks.append(self._cam.call_action(request, 0))

        results: List[Response] = await asyncio.gather(*tasks)
        successes = []
        failures = []
        errors = []
        for r in results:
            if r.status.value == StatusValue.SUCCESS:
                successes.append(r.content)
            elif r.status.value == StatusValue.FAILURE:
                failures.append(r.src_ip)
            elif r.status.value == StatusValue.ERROR:
                errors.append(r.src_ip)

        content = {
            "success": successes,
            "failure": failures,
            "error": errors
        }

        response = self._messaging.create_response(message,
                                                   status=Status(StatusOrigin.NETWORK, StatusValue.SUCCESS),
                                                   content=content, session=message.session, auth=message.auth)

        return msecs(0), response

    async def process_access_target(self, message: Request, node: Node) -> Tuple[Duration, Response]:

        content = ""
        status = None
        session = None

        # A target service is provided
        if not message.dst_service:
            content = "The action requires a specific service as a target."
            status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.SERVICE_NOT_PROVIDED)

        # The service exists at the target
        if not content and message.dst_service not in node.services:
            content = f"Service '{message.dst_service}' is not running at the target."
            status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.SERVICE_NOT_EXISTING)

        # The service can be accessed
        if not content:
            target_service = node.services[message.dst_service].passive_service
            if target_service.local and message.src_ip not in node.ips:
                if not message.session or message.session.end[0] not in node.ips:
                    content = f"Service '{message.dst_service}' can only be accessed locally."
                    status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.SESSION_NOT_PROVIDED)

        # Either exploit or auth was provided
        if not content:
            if not message.action.exploit and not message.auth:
                content = f"The action requires either an exploit or a correct authorization"
                status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.EXPLOIT_NOT_PROVIDED | StatusDetail.AUTHORIZATION_NOT_PROVIDED | StatusDetail.AUTHENTICATION_NOT_PROVIDED)

        # Exploit is being used
        if not content and message.action.exploit:
            # It is the correct category
            if message.action.exploit.category != ExploitCategory.CODE_EXECUTION:
                content = "Provided exploit cannot be used to open a session."
                status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.EXPLOIT_CATEGORY_NOT_APPLICABLE)
            # It is the correct locality
            elif message.action.exploit.locality == ExploitLocality.LOCAL:
                if message.src_ip not in node.ips or (message.session and message.session.end[0] not in node.ips):
                    content = "Attempting to use a local exploit remotely."
                    status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.EXPLOIT_LOCALITY_NOT_APPLICABLE)
            # It can be used on the target service
            elif not self._exploit_store.evaluate_exploit(message.action.exploit, message, node):
                content = "The provided exploit cannot be used"
                status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.EXPLOIT_NOT_APPLICABLE)

            content = "Session successfully opened"
            status = Status(StatusOrigin.SERVICE, StatusValue.SUCCESS)
            session = self._messaging.open_session(message)

        # Auth is being used (Authentication shoudl be handled before entering the behavioral model)
        if not content and message.auth:
            result, reason = self._policy.decide(node, message.dst_service, AccessLevel.LIMITED, message.auth)
            if not result:
                content = f"Could not use the authorization to open a session. Reason: {reason}"
                status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.AUTHORIZATION_NOT_APPLICABLE)
            else:
                content = "Session successfully opened"
                status = Status(StatusOrigin.SERVICE, StatusValue.SUCCESS)
                session = self._messaging.open_session(message)

        response = self._messaging.create_response(message, status, content, session if session else message.session, message.auth)
        return msecs(20), response

    async def process_exfiltrate_data(self, message: Request, node: Node) -> Tuple[Duration, Response]:

        content = ""
        status = None

        # A target service is provided
        if not message.dst_service:
            content = "The action requires a specific service as a target."
            status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.SERVICE_NOT_PROVIDED)

        # The service exists at the target
        if not content and message.dst_service not in node.services:
            content = f"Service '{message.dst_service}' is not running at the target."
            status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.SERVICE_NOT_EXISTING)

        # The path is provided
        if not content and "path" not in message.action.parameters:
            content = "Required parameter 'path' not provided."
            status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.ACTION_PARAMETER_NOT_PROVIDED)

        if not content:
            service = node.services[message.dst_service].passive_service
            service_data = {x.path: x for x in self._configuration.service.private_data(service)}
            data_path = message.action.parameters["path"].value

            # local extraction
            if message.src_ip in node.ips or (message.session and message.session.end[0] in node.ips):
                if data_path not in service_data:
                    content = f"Data with required path '{data_path}' not within the service."
                    status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.ACTION_PARAMETER_NOT_APPLICABLE)
                else:
                    content = {"path": data_path, "content": service_data[data_path].description}
                    status = Status(StatusOrigin.SERVICE, StatusValue.SUCCESS)
            # remote extraction
            else:
                if not message.action.exploit:
                    content = "An exploit is required for remote data exfiltration."
                    status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.EXPLOIT_NOT_PROVIDED)

                if not content and message.action.exploit.category != ExploitCategory.DATA_MANIPULATION:
                    content = "The exploit does not have a suitable DATA_MANIPULATION category."
                    status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.EXPLOIT_CATEGORY_NOT_APPLICABLE)

                if not content and message.action.exploit.locality != ExploitLocality.REMOTE:
                    content = "Attempting to use a local exploit remotely."
                    status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.EXPLOIT_LOCALITY_NOT_APPLICABLE)

                if not content and not self._exploit_store.evaluate_exploit(message.action.exploit, message, node):
                    content = "The provided exploit cannot be used"
                    status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.EXPLOIT_NOT_APPLICABLE)

                if data_path not in service_data:
                    content = f"Data with required path '{data_path}' not within the service."
                    status = Status(StatusOrigin.SERVICE, StatusValue.FAILURE, StatusDetail.ACTION_PARAMETER_NOT_APPLICABLE)
                else:
                    content = {"path": data_path, "content": service_data[data_path].description}
                    status = Status(StatusOrigin.SERVICE, StatusValue.SUCCESS)

        response = self._messaging.create_response(message, status, content, message.session, message.auth)
        return msecs(20), response


def create_ac1_model(configuration: EnvironmentConfiguration, resources: EnvironmentResources,
                      policy: EnvironmentPolicy, messaging: EnvironmentMessaging,
                      infrastructure: EnvironmentInfrastructure,
                      composite_action_manager: CompositeActionManager) -> BehavioralModel:
    model = AC1Model(configuration, resources, policy, messaging, infrastructure, composite_action_manager)
    return model


behavioral_model_description = BehavioralModelDescription(
    namespace="ac1",
    description="Behavioral model for the first AICA challenge.",
    creation_fn=create_ac1_model,
    platform=[PlatformSpecification(PlatformType.SIMULATED_TIME, "CYST"), PlatformSpecification(PlatformType.REAL_TIME, "CYST")]
)
