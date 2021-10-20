# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import logging
import os
from zipfile import ZipFile

from build_workflow.build_artifact_check import BuildArtifactCheck
from system.properties_file import PropertiesFile


class BuildArtifactOpenSearchCheckMaven(BuildArtifactCheck):
    def check(self, path):
        ext = os.path.splitext(path)[1]
        if ext not in [
            ".asc",
            ".jar",
            ".md5",
            ".module",
            ".pom",
            ".sha1",
            ".sha256",
            ".sha512",
            ".war",
            ".xml",
            ".zip",
        ]:
            raise BuildArtifactCheck.BuildArtifactInvalidError(path, f"{ext} is not a valid extension for a maven file")
        if os.path.splitext(path)[1] == ".jar":
            with ZipFile(path, "r") as zip:
                data = zip.read("META-INF/MANIFEST.MF").decode("UTF-8")
                properties = PropertiesFile(data)
                try:
                    properties.check_value_in(
                        "Implementation-Version",
                        [
                            self.target.component_version,
                            self.target.opensearch_version,
                            None,
                        ],
                    )
                except PropertiesFile.CheckError as e:
                    raise BuildArtifactCheck.BuildArtifactInvalidError(path, str(e))
                logging.info(f'Checked {path} ({properties.get_value("Implementation-Version", "N/A")})')
