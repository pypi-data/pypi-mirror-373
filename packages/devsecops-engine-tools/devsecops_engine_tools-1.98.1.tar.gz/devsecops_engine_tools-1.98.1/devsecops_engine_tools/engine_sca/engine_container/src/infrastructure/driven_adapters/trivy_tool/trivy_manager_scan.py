from devsecops_engine_tools.engine_sca.engine_container.src.domain.model.gateways.tool_gateway import (
    ToolGateway,
)
from devsecops_engine_tools.engine_utilities.sbom.deserealizator import (
    get_list_component,
)
from devsecops_engine_tools.engine_utilities.trivy_utils.infrastructure.driven_adapters.trivy_manager_scan_utils import (
    TrivyManagerScanUtils
)
import subprocess
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()


class TrivyScan(ToolGateway):

    def scan_image(self, prefix, image_name, result_file, base_image, is_compressed_file=False):
        command = [
            prefix,
            "--scanners",
            "vuln",
            "-f",
            "json",
            "-o",
            result_file,
        ]
        
        if is_compressed_file:
            command.extend(["--quiet", "image", "--input", image_name])
        else:
            command.extend(["--quiet", "image", image_name])
            
        try:
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            print(f"The image {image_name} was scanned")

            return result_file

        except Exception as e:
            logger.error(f"Error during image scan of {image_name}: {e}")

    def _generate_sbom(self, prefix, image_name, remoteconfig, is_compressed_file=False):
        result_sbom = f"{image_name.replace('/', '_')}_SBOM.json"
        command = [
            prefix,
            "image",
            "--format",
            remoteconfig["TRIVY"]["SBOM_FORMAT"],
            "--output",
            result_sbom
        ]
        if is_compressed_file:
            command.extend(["--quiet", "--input", image_name])
        else:
            command.extend(["--quiet", image_name])
        try:
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            print(f"SBOM generated and saved to: {result_sbom}")

            return get_list_component(result_sbom, remoteconfig["TRIVY"]["SBOM_FORMAT"])

        except Exception as e:
            logger.error(f"Error generating SBOM: {e}")

    def run_tool_container_sca(self, remoteconfig, secret_tool, token_engine_container, image_name, result_file, base_image, exclusions, generate_sbom, is_compressed_file=False):
        trivy_version = remoteconfig["TRIVY"]["TRIVY_VERSION"]        
        command_prefix = TrivyManagerScanUtils().identify_os_and_install(trivy_version)
        sbom_components = None
        
        if not command_prefix:
            return None

        image_scanned = (
            self.scan_image(command_prefix, image_name, result_file, base_image, is_compressed_file)
        )
        if generate_sbom:
            sbom_components = self._generate_sbom(command_prefix, image_name, remoteconfig, is_compressed_file)

        return image_scanned, sbom_components
