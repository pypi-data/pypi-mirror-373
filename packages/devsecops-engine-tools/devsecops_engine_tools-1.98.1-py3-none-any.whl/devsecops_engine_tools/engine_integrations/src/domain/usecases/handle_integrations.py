from devsecops_engine_tools.engine_core.src.domain.model.gateway.vulnerability_management_gateway import (
    VulnerabilityManagementGateway
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.secrets_manager_gateway import (
    SecretsManagerGateway
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.devops_platform_gateway import (
    DevopsPlatformGateway
)
from devsecops_engine_tools.engine_core.src.domain.model.gateway.metrics_manager_gateway import (
    MetricsManagerGateway,
)
from devsecops_engine_tools.engine_utilities.sonarqube.src.applications.runner_report_sonar import (
    runner_report_sonar
)

class Integrations():
    def __init__(
        self,
        vulnerability_management_gateway: VulnerabilityManagementGateway,
        secrets_manager_gateway: SecretsManagerGateway,
        devops_platform_gateway: DevopsPlatformGateway,
        remote_config_source_gateway: DevopsPlatformGateway,
        metrics_manager_gateway: MetricsManagerGateway,
    ):
        self.vulnerability_management_gateway = vulnerability_management_gateway
        self.secrets_manager_gateway = secrets_manager_gateway
        self.devops_platform_gateway = devops_platform_gateway
        self.remote_config_source_gateway = remote_config_source_gateway
        self.metrics_manager_gateway = metrics_manager_gateway

    def process(self, args):
        integration = args.get("integration")
        if integration == "report_sonar":
            return runner_report_sonar(
                vulnerability_management_gateway=self.vulnerability_management_gateway,
                secrets_manager_gateway=self.secrets_manager_gateway,
                devops_platform_gateway=self.devops_platform_gateway,
                remote_config_source_gateway=self.remote_config_source_gateway,
                metrics_manager_gateway=self.metrics_manager_gateway,
                args=args,
            )
