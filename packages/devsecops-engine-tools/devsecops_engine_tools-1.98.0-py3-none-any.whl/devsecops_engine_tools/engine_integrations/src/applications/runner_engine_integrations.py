from devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.azure.azure_devops import (
    AzureDevops
)
from devsecops_engine_tools.engine_integrations.src.infrastructure.entry_points.entry_point_integrations import (
    init_engine_integrations
)
from devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.aws.secrets_manager import (
    SecretsManager
)
from devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.azure.azure_devops import (
    AzureDevops
)
from devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.github.github_actions import (
    GithubActions,
)
from devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.runtime_local.runtime_local import (
    RuntimeLocal,
)
from devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.defect_dojo.defect_dojo import (
    DefectDojoPlatform
)
from devsecops_engine_tools.engine_core.src.infrastructure.driven_adapters.aws.s3_manager import (
    S3Manager,
)
import sys
import argparse
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()

def get_inputs_from_cli(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--integration",
        choices=["report_sonar"],
        type=str,
        required=True,
        help="Name of the integration to run",
    )
    parser.add_argument(
        "-rcf",
        "--remote_config_repo",
        type=str,
        required=True,
        help="Name of Config Repo",
    )
    parser.add_argument(
        "-rcb",
        "--remote_config_branch",
        type=str,
        required=False,
        default="",
        help="Name of the branch of Config Repo",
    )
    parser.add_argument(
        "-pd",
        "--platform_devops",
        choices=["azure", "github", "local"],
        type=str,
        required=True,
        help="Platform where is executed",
    )
    parser.add_argument(
        "-rcs",
        "--remote_config_source",
        choices=["azure", "github", "local"],
        type=str,
        required=False,
        help="Source of the remote config repo",
    )
    parser.add_argument(
        "--use_secrets_manager",
        choices=["true", "false"],
        type=str,
        required=True,
        help="Use Secrets Manager to get the tokens",
    )
    parser.add_argument(
        "--send_metrics",
        choices=["true", "false"],
        type=str,
        required=False,
        help="Enable or Disable the send metrics to the driven adapter metrics",
    )
    # report_sonar flags
    parser.add_argument(
        "--sonar_url",
        required=False,
        help="Url to access sonar API",
    )
    parser.add_argument(
        "--sonar_instance",
        required=False,
        help="Name of the sonar instance to recognize tool config",
    )
    parser.add_argument(
        "--token_cmdb", 
        required=False, 
        help="Token to connect to the CMDB"
    )
    parser.add_argument(
        "--token_vulnerability_management",
        required=False,
        help="Token to connect to the Vulnerability Management",
    )
    parser.add_argument(
        "--token_sonar",
        required=False,
        help="Token to access sonar server",
    )

    args = parser.parse_args()
    return {
        "integration": args.integration,
        "remote_config_repo": args.remote_config_repo,
        "remote_config_branch": args.remote_config_branch,
        "platform_devops": args.platform_devops,
        "remote_config_source": args.remote_config_source,
        "use_secrets_manager": args.use_secrets_manager,
        "send_metrics": args.send_metrics,
        "sonar_url": args.sonar_url,
        "sonar_instance": args.sonar_instance,
        "token_cmdb": args.token_cmdb,
        "token_vulnerability_management": args.token_vulnerability_management,
        "token_sonar": args.token_sonar,
    }

def runner_engine_integrations():
    try:
        args = get_inputs_from_cli(sys.argv[1:])
        if not args["remote_config_source"]: 
            args["remote_config_source"] = args["platform_devops"]

        vulnerability_management_gateway = DefectDojoPlatform()
        secrets_manager_gateway = SecretsManager()
        devops_platform_gateway = {
            "azure": AzureDevops(),
            "github": GithubActions(),
            "local": RuntimeLocal(),
        }.get(args["platform_devops"])
        remote_config_source_gateway = {
            "azure": AzureDevops(),
            "github": GithubActions(),
            "local": RuntimeLocal(),
        }.get(args["remote_config_source"])
        metrics_manager_gateway = S3Manager()
        
        init_engine_integrations(
            vulnerability_management_gateway=vulnerability_management_gateway,
            secrets_manager_gateway=secrets_manager_gateway,
            devops_platform_gateway=devops_platform_gateway,
            remote_config_source_gateway=remote_config_source_gateway,
            metrics_manager_gateway=metrics_manager_gateway,
            args=args,
        )

    except Exception as e:
        logger.error("Error engine_integrations: {0} ".format(str(e)))
        print(
            devops_platform_gateway.message(
                "error", "Error engine_integrations: {0} ".format(str(e))
            )
        )
        print(devops_platform_gateway.result_pipeline("failed"))


if __name__ == "__main__":
    runner_engine_integrations()