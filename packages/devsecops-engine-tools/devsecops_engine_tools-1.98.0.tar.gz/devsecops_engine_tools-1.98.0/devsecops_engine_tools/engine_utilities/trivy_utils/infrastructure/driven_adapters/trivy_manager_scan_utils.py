import subprocess
import platform
import requests
import tarfile
import zipfile
from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()

class TrivyManagerScanUtils():
    def identify_os_and_install(self, trivy_version):
        os_platform = platform.system()
        arch_platform = platform.architecture()[0]
        base_url = f"https://github.com/aquasecurity/trivy/releases/download/v{trivy_version}/"

        command_prefix = "trivy"
        if os_platform == "Linux":
            file=f"trivy_{trivy_version}_Linux-{arch_platform}.tar.gz"
            command_prefix = self._install_tool(file, base_url+file, "trivy")
        elif os_platform == "Darwin":
            file=f"trivy_{trivy_version}_macOS-{arch_platform}.tar.gz"
            command_prefix = self._install_tool(file, base_url+file, "trivy")
        elif os_platform == "Windows":
            file=f"trivy_{trivy_version}_windows-{arch_platform}.zip"
            command_prefix = self._install_tool_windows(file, base_url+file, "trivy.exe")
        else:
            logger.warning(f"{os_platform} is not supported.")
            return None

        return command_prefix

    def _install_tool(self, file, url, command_prefix):
        installed = subprocess.run(
            ["which", command_prefix],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if installed.returncode == 1:
            try:
                self._download_tool(file, url)
                with tarfile.open(file, 'r:gz') as tar_file:
                    tar_file.extract(member=tar_file.getmember("trivy"))
                    return "./trivy"
            except Exception as e:
                logger.error(f"Error installing trivy: {e}")
        else:
            return installed.stdout.decode().strip()
        
    def _install_tool_windows(self, file, url, command_prefix):
        try:
            subprocess.run(
                [command_prefix, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return command_prefix
        except:
            try:
                self._download_tool(file, url)
                with zipfile.ZipFile(file, 'r') as zip_file:
                    zip_file.extract(member="trivy.exe")
                    return "./trivy.exe"
            except Exception as e:
                logger.error(f"Error installing trivy: {e}")
    
    def _download_tool(self, file, url):
        try:
            response = requests.get(url, allow_redirects=True)
            with open(file, "wb") as compress_file:
                compress_file.write(response.content)
        except Exception as e:
            logger.error(f"Error downloading trivy: {e}")
