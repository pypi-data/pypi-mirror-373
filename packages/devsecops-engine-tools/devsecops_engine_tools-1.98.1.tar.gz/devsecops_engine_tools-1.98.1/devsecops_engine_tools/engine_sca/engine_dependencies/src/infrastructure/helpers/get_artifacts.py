import os
import re
import tarfile
import subprocess
import shutil

from devsecops_engine_tools.engine_utilities.utils.logger_info import MyLogger
from devsecops_engine_tools.engine_utilities import settings

logger = MyLogger.__call__(**settings.SETTING_LOGGER).get_logger()


class GetArtifacts:

    def excluded_files(self, remote_config, pipeline_name, exclusions, tool):
        pattern = remote_config[tool]["REGEX_EXPRESSION_EXTENSIONS"]
        if (pipeline_name in exclusions) and (
            exclusions[pipeline_name].get(tool, None)
        ):
            for ex in exclusions[pipeline_name][tool]:
                if ex.get("SKIP_FILES", 0):
                    exclusion = ex.get("SKIP_FILES")
                    if exclusion.get("files", 0):
                        excluded_file_types = exclusion["files"]
                        pattern2 = pattern
                        for ext in excluded_file_types:
                            pattern2 = (
                                pattern2.replace("|" + ext, "")
                                .replace(ext + "|", "")
                                .replace(ext, "")
                            )
                        pattern = pattern2

        return pattern

    def filter_ignored_files(self, files_list, ignore_files):
        if not ignore_files:
            return files_list
            
        filtered_files = []
        for file_path in files_list:
            should_ignore = False
            file_name = os.path.basename(file_path)
            
            for ignore_pattern in ignore_files:
                if (re.search(ignore_pattern, file_name, re.IGNORECASE) or re.search(ignore_pattern, file_path, re.IGNORECASE)):
                    should_ignore = True
                    break
                    
            if not should_ignore:
                filtered_files.append(file_path)
                
        return filtered_files

    def find_packages(self, pattern, packages, working_dir):
        packages_list = []
        files_list = []
        extension_pattern = re.compile(pattern, re.IGNORECASE)
        for root, dirs, files in os.walk(working_dir):
            components = root.split(os.path.sep)
            flag = 0
            for package in packages:
                if not (package in components):
                    flag = 1
                    if package in dirs:
                        packages_list.append(os.path.join(root, package))
            if flag:
                for file in files:
                    if extension_pattern.search(file):
                        files_list.append(os.path.join(root, file))
        return packages_list, files_list

    def compress_and_mv(self, tar_path, package):
        try:
            with tarfile.open(tar_path, "w") as tar:
                tar.add(
                    package,
                    arcname=os.path.basename(package),
                    filter=lambda x: None if "/.bin/" in x.name else x,
                )

        except subprocess.CalledProcessError as e:
            logger.error(f"Error during {package} compression: {e}")

    def move_files(self, dir_to_scan_path, finded_files):
        for file in finded_files:
            target = os.path.join(dir_to_scan_path, os.path.basename(file))
            shutil.copy2(file, target)
            logger.debug(f"File to scan: {file}")

    def find_artifacts(self, to_scan, pattern, packages, ignore_files=None):
        dir_to_scan_path = os.path.join(to_scan, "dependencies_to_scan")
        if os.path.exists(dir_to_scan_path):
            shutil.rmtree(dir_to_scan_path)
        os.makedirs(dir_to_scan_path)

        packages_list, files_list = self.find_packages(pattern, packages, to_scan)

        if ignore_files:
            filtered_files_list = self.filter_ignored_files(files_list, ignore_files)
        else:
            filtered_files_list = files_list

        for package in packages_list:
            tar_path = os.path.join(
                dir_to_scan_path,
                "pkg"
                + str(packages_list.index(package) + 1)
                + "_"
                + os.path.basename(package)
                + ".tar",
            )
            self.compress_and_mv(tar_path, package)

        if len(filtered_files_list):
            self.move_files(dir_to_scan_path, filtered_files_list)

        files = os.listdir(dir_to_scan_path)
        files = [
            file
            for file in files
            if os.path.isfile(os.path.join(dir_to_scan_path, file))
        ]
        file_to_scan = None
        if files:
            file_to_scan = os.path.join(dir_to_scan_path, "file_to_scan.tar")
            self.compress_and_mv(file_to_scan, dir_to_scan_path)
            files_string = ", ".join(files)
            print(f"Files to scan: {files_string}")

            if ignore_files and len(filtered_files_list) < len(files_list):
                ignored_files = set([os.path.basename(f) for f in files_list if f not in filtered_files_list])
                files_ignore_string = ", ".join(ignored_files)
                print(f"Files ignored: {files_ignore_string}")
        else:
            logger.warning("No artifacts found")

        return file_to_scan
