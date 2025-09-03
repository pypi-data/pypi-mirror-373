from devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.driven_adapters.copacetic.copacetic_adapter import(
    CopaceticAdapter
)
from devsecops_engine_tools.engine_utilities.copacetic.src.infrastructure.entry_points.entry_point_copacetic import (
    init_copacetic
)
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()

def runner_copacetic(
    vulnerability_management_gateway,
    secrets_manager_gateway,
    devops_platform_gateway,
    remote_config_source_gateway,
    metrics_manager_gateway,
    args
):
    try:
        copacetic_gateway = CopaceticAdapter()

        init_copacetic(
            vulnerability_management_gateway=vulnerability_management_gateway,
            secrets_manager_gateway=secrets_manager_gateway,
            devops_platform_gateway=devops_platform_gateway,
            remote_config_source_gateway=remote_config_source_gateway,
            copacetic_gateway=copacetic_gateway,
            metrics_manager_gateway=metrics_manager_gateway,
            args=args,
        )

    except Exception as e:
        logger.error("Error copacetic: {0} ".format(str(e)))
        print(
            devops_platform_gateway.message(
                "error", "Error copacetic: {0} ".format(str(e))
            )
        )
        print(devops_platform_gateway.result_pipeline("failed"))
