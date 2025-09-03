"""
GoogleTestAdapter is now part of VisualStudio, and identified as TAfGT:
https://github.com/microsoft/TestAdapterForGoogleTest
It is installed from VisualStudio Installer.
However, it may be outdated and lack features from original project.

Original GoogleTestAdapter is still maintained, and identifier as GTA:
https://github.com/csoltenborn/GoogleTestAdapter
It is installed from VisualStudio Marketplace.
However, it is not installable (yet) on VS2022:
(https://github.com/csoltenborn/GoogleTestAdapter/issues/333)

"""


from pathlib import Path
from typing import Union

import lxml.etree as ET


class RunSettingsFile:

    KNOWN_SETTINGS = {
        "AdditionalTestExecutionParam",
        "BatchForTestSetup",
        "BatchForTestTeardown",
        "BreakOnFailure",
        "CatchExceptions",
        "DebugMode",
        "TimestampMode",
        "SeverityMode",
        "SummaryMode",
        "PrefixOutputWithGta",
        "MaxNrOfThreads",
        "NrOfTestRepetitions",
        "ParallelTestExecution",
        "PrintTestOutput",
        "RunDisabledTests",
        "ShuffleTests",
        "ShuffleTestsSeed",
        "TestDiscoveryRegex",
        "AdditionalPdbs",
        "TestDiscoveryTimeoutInSeconds",
        "WorkingDir",
        "PathExtension",
        "EnvironmentVariables",
        "TraitsRegexesAfter",
        "TraitsRegexesBefore",
        "TestNameSeparator",
        "ParseSymbolInformation",
        "UseNewTestExecutionFramework",
        "KillProcessesOnCancel",
        "ExitCodeTestCase",
        "MissingTestsReportMode",
    }
    TRAITS_REGEX_SEPARATOR = "//||//"

    def __init__(self, path: Path):
        self.path = path

        self.solution_settings = {}
        self.project_settings = {}

    def add_solution_setting(self, name: str, value: Union[str, bool, list[str]]):
        if name not in self.KNOWN_SETTINGS:
            raise ValueError(f'Invalid setting {name}')
        self.solution_settings[name] = value

    def add_project_setting(self, name: str, value: Union[str, bool, list[str]], regex: str):
        if name not in self.KNOWN_SETTINGS:
            raise ValueError(f'Invalid setting {name}')
        s = self.project_settings.setdefault(regex, {})
        s[name] = value

    def _write_setting(self, parent: ET.Element, items: dict[str, Union[str, bool, list[str]]]):
        for key, value in items.items():
            if isinstance(value, bool):
                value = str(value).lower()

            elif isinstance(value, list):
                value = self.TRAITS_REGEX_SEPARATOR.join(value)

            ET.SubElement(parent, key).text = value

    def write(self):
        root = ET.Element("RunSettings")
        gta = ET.SubElement(root, "GoogleTestAdapterSettings")

        if self.solution_settings:
            sol = ET.SubElement(gta, "SolutionSettings")
            solset = ET.SubElement(sol, "Settings")
            self._write_setting(solset, self.solution_settings)

        if self.project_settings:
            prj = ET.SubElement(gta, "ProjectSettings")
            for regex, settings in self.project_settings.items():
                prjset = ET.SubElement(prj, "Settings", ProjectRegex=regex)
                self._write_setting(prjset, settings)

        self.path.write_bytes(ET.tostring(root, encoding='UTF-8', xml_declaration=True, pretty_print=True))
