from dataclasses import dataclass
import requests
import subprocess
import platform

from devsecops_engine_tools.engine_core.src.domain.model.gateway.sbom_manager import (
    SbomManagerGateway,
)
from devsecops_engine_tools.engine_utilities.sbom.deserealizator import (
    get_list_component,
)
from devsecops_engine_tools.engine_core.src.domain.model.component import (
    Component,
)

from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()


@dataclass
class CdxGen(SbomManagerGateway):

    def get_components(self, artifact, config, service_name) -> "list[Component]":
        try:
            cdxgen_version = config["CDXGEN"]["CDXGEN_VERSION"]
            slim = "-slim" if config["CDXGEN"]["SLIM_BINARY"] else ""
            os_platform = platform.system()
            base_url = (
                f"https://github.com/CycloneDX/cdxgen/releases/download/v{cdxgen_version}/"
            )

            command_prefix = "cdxgen"
            if os_platform == "Linux":
                file = f"cdxgen-linux-amd64{slim}"
                command_prefix = self._install_tool_unix(
                    file, base_url + file, command_prefix
                )
            elif os_platform == "Darwin":
                file = f"cdxgen-darwin-amd64{slim}"
                command_prefix = self._install_tool_unix(
                    file, base_url + file, command_prefix
                )
            elif os_platform == "Windows":
                file = f"cdxgen-windows-amd64{slim}.exe"
                command_prefix = self._install_tool_windows(
                    file, base_url + file, "cdxgen.exe"
                )
            else:
                logger.warning(f"{os_platform} is not supported.")
                return None

            result_sbom = self._run_cdxgen(command_prefix, artifact, service_name)
            return get_list_component(result_sbom, config["CDXGEN"]["OUTPUT_FORMAT"])
        except Exception as e:
            logger.error(f"Error generating SBOM: {e}")
            return None

    def _run_cdxgen(self, command_prefix, artifact, service_name):
        result_file = f"{service_name}_SBOM.json"
        command = [
            command_prefix,
            artifact,
            "-o",
            result_file,
        ]

        try:
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            print(f"SBOM generated and saved to: {result_file}")
            return result_file
        except Exception as e:
            logger.error(f"Error running cdxgen: {e}")

    def _install_tool_unix(self, file, url, command_prefix):
        installed = subprocess.run(
            ["which", command_prefix],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if installed.returncode == 1:
            try:
                self._download_tool(file, url)
                subprocess.run(
                    ["chmod", "+x", f"./{file}"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                return f"./{file}"
            except Exception as e:
                logger.error(f"Error installing cdxgen: {e}")
        else:
            return installed.stdout.decode("utf-8").strip()

    def _install_tool_windows(self, file, url, command_prefix):
        try:
            installed = subprocess.run(
                [command_prefix, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return installed.stdout.decode("utf-8").strip()
        except:
            try:
                self._download_tool(file, url)
                return f"{file}"
            except Exception as e:
                logger.error(f"Error installing cdxgen: {e}")

    def _download_tool(self, file, url):
        try:
            response = requests.get(url, allow_redirects=True)
            with open(file, "wb") as compress_file:
                compress_file.write(response.content)
        except Exception as e:
            logger.error(f"Error downloading cdxgen: {e}")
