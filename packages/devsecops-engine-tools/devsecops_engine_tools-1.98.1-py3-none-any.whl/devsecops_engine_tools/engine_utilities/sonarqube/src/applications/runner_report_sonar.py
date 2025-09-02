from devsecops_engine_tools.engine_utilities.sonarqube.src.infrastructure.driven_adapters.sonarqube.sonarqube_report import(
    SonarAdapter
)
from devsecops_engine_tools.engine_utilities.sonarqube.src.infrastructure.entry_points.entry_point_report_sonar import (
    init_report_sonar
)
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()

def runner_report_sonar(
    vulnerability_management_gateway,
    secrets_manager_gateway,
    devops_platform_gateway,
    remote_config_source_gateway,
    metrics_manager_gateway,
    args
):
    try:
        sonar_gateway = SonarAdapter()

        init_report_sonar(
            vulnerability_management_gateway=vulnerability_management_gateway,
            secrets_manager_gateway=secrets_manager_gateway,
            devops_platform_gateway=devops_platform_gateway,
            remote_config_source_gateway=remote_config_source_gateway,
            sonar_gateway=sonar_gateway,
            metrics_manager_gateway=metrics_manager_gateway,
            args=args,
        )

    except Exception as e:
        logger.error("Error report_sonar: {0} ".format(str(e)))
        print(
            devops_platform_gateway.message(
                "error", "Error report_sonar: {0} ".format(str(e))
            )
        )
        print(devops_platform_gateway.result_pipeline("failed"))
