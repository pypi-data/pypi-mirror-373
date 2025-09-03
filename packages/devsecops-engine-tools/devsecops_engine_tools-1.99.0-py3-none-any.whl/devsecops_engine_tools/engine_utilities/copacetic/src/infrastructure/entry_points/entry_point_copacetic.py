from devsecops_engine_tools.engine_utilities.copacetic.src.domain.usecases.copacetic import (
    Copacetic,
)
from devsecops_engine_tools.engine_core.src.domain.usecases.metrics_manager import (
    MetricsManager,
)
import re
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()


def init_copacetic(
    vulnerability_management_gateway,
    secrets_manager_gateway,
    devops_platform_gateway,
    remote_config_source_gateway,
    copacetic_gateway,
    metrics_manager_gateway,
    args,
):
    config_tool = remote_config_source_gateway.get_remote_config(
        args["remote_config_repo"], "/engine_core/ConfigTool.json", args["remote_config_branch"]
    )
    copacetic_config_tool = remote_config_source_gateway.get_remote_config(
        args["remote_config_repo"], "/engine_integrations/copacetic/ConfigTool.json", args["remote_config_branch"]
    )
    excluded_pipelines = remote_config_source_gateway.get_remote_config(
        args["remote_config_repo"], "/engine_integrations/copacetic/Exclusions.json", args["remote_config_branch"]
    )

    pipeline_name = devops_platform_gateway.get_variable("pipeline_name")
    branch = devops_platform_gateway.get_variable("branch_tag")

    is_valid_pipeline = pipeline_name not in excluded_pipelines and not any(
        [
            re.match(
                pattern,
                pipeline_name,
                re.IGNORECASE
            ) for pattern in
            [copacetic_config_tool["IGNORE_SEARCH_PATTERN"]] +
            list(excluded_pipelines.get("BY_PATTERN_SEARCH", {}).keys())
        ]
    )
    
    is_valid_branch = any(
        target_branch in str(branch).split("/")
        for target_branch in copacetic_config_tool["TARGET_BRANCHES"]
    )

    is_enabled = config_tool["COPACETIC"]["ENABLED"]

    if is_enabled and is_valid_pipeline and is_valid_branch:
        input_core = Copacetic(
            vulnerability_management_gateway,
            secrets_manager_gateway,
            devops_platform_gateway,
            remote_config_source_gateway,
            copacetic_gateway,
        ).process(args)

        if args["send_metrics"] == "true":
            MetricsManager(devops_platform_gateway, metrics_manager_gateway).process(
                config_tool, input_core, {"module": "copacetic"}, ""
            )
    else:
        if not is_enabled:
            message = "DevSecOps Engine Tool - {0} in maintenance...".format(
                "copacetic"
            )
        else:
            message = "Tool skipped by DevSecOps policy"

        print(
            devops_platform_gateway.message("warning", message),
        )
