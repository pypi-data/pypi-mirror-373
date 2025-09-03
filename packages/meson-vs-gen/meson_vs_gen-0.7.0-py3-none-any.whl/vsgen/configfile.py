from __future__ import annotations

import os.path
from pathlib import Path
import re
from typing import Optional, Union

import yaml

from .api import Generator
from .introspector import Introspector, UnconfiguredProject
from .runsettings import RunSettingsFile
from .sln import SolutionFile
from .vcxproj import VcxProj


class ConfigFile:

    SPECIAL_TARGETS = {'all', 'test'}

    def __init__(self, path: Path):
        self.path = path
        self.data = {'projects': {'*': False}}

    def load(self) -> ConfigFile:
        with self.path.open('r', encoding='utf8') as cf:
            self.data.update(yaml.safe_load(cf) or {})
        return self

    def analyse(self, basepath: Path) -> dict:
        results = {}

        if not self.data.get('configs'):
            return {'error': 'no configs defined'}

        targets = set()
        for config_path in self.data['configs']:
            try:
                introspector = Introspector(basepath / config_path)
                targets.update(introspector.all_targets())
            except UnconfiguredProject as e:
                print(e)

        if not targets:
            return {'error': 'no targets found. Is project configured?'}

        if self.data['projects'].get('*'):
            results.update(self._analyse_targets(targets))

        return results

    def generate(self, basepath: Path, outputpath: Optional[Path] = None, update: bool = True):

        use_include_from_env = self.data.get('include_from_env', False)
        if use_include_from_env == 'auto':
            use_include_from_env = os.environ.get('INCLUDE', None) is not None

        if not outputpath:
            outputpath = Path(self.data.get('outputdir', '.'))

        gen = Generator(outputpath, basepath, self.data.get('projectdir', ''))
        gen.cpu_arch = self.data.get('archs', {})

        all_projects = {}
        solutions = {}
        for config_path, config_name in self.data.get('configs', {}).items():
            if not gen.set_config(config_path, config_name, use_include_from_env):
                continue

            projects = self._generate_projects(gen, update)
            for p in projects:
                all_projects[p.uuid] = p
            solutions = self._generate_solutions(gen, projects, update)
            update = True

        self._generate_runsettings(gen, solutions, all_projects.values())

    def _analyse_targets(self, targets: set[str]) -> dict:
        listed_targets = set()
        for project_name, target in self.data['projects'].items():
            if project_name == '*':
                continue
            if isinstance(target, bool):
                listed_targets.add(project_name)
            elif isinstance(target, str):
                listed_targets.add(target)
            else:
                target = target.get('target', project_name)
                if isinstance(target, bool):
                    target = project_name

                listed_targets.add(target)

        unlisted_targets = targets - listed_targets
        missing_targets = listed_targets - targets - self.SPECIAL_TARGETS

        result = {}
        if unlisted_targets:
            result['unlisted_targets'] = list(unlisted_targets)
        if missing_targets:
            result['unexisting_targets'] = list(missing_targets)
        return result

    def _analyse_solutions_with_unexisting_projects(self):
        pass

    def _analyse_solutions_without_build(self):
        pass

    def _generate_projects(self, gen: Generator, update: bool) -> list[VcxProj]:
        ci_targets = self.data.get('case_insensitive_targets', False)
        orf = self.data.get('only_relative_files', False)

        projects = []
        all_targets = set(gen.all_targets())

        default_config = {
            'target': True,
            'subdir': '',
        }
        all_config = self.data.get('projects', {}).get('*')
        if isinstance(all_config, dict):
            default_config.update(all_config)

        for name, config in self.data.get('projects', {}).items():
            if name == '*':
                continue

            if config is False:
                if name in all_targets:
                    all_targets.remove(name)
                elif ci_targets and name.lower() in all_targets:
                    all_targets.remove(name.lower())
                elif 'dep:' + name in all_targets:
                    all_targets.remove('dep:' + name)
                elif ci_targets and 'dep:' + name.lower() in all_targets:
                    all_targets.remove('dep:' + name.lower())
                continue

            if config is True:
                config = default_config
            elif isinstance(config, str):
                config = default_config | {'target': config}
            else:
                config = default_config | config

            target = config['target']
            if target is True:
                target = name

                if target not in all_targets:
                    if ci_targets and target.lower() in all_targets:
                        target = target.lower()
                    elif 'dep:' + target in all_targets:
                        target = 'dep:' + target
                    elif ci_targets and 'dep:' + target.lower() in all_targets:
                        target = 'dep:' + target.lower()

            elif target is False:
                continue

            if isinstance(target, list):
                for t in target.copy():
                    if t not in all_targets and t not in self.SPECIAL_TARGETS:
                        target.remove(t)
                if not target:
                    continue

                for t in target:
                    if t in all_targets:
                        all_targets.remove(t)

                target = " ".join(target)

            else:
                if target in all_targets:
                    all_targets.remove(target)
                elif target not in self.SPECIAL_TARGETS:
                    target = False  # dummy target

            project = gen.project(name, target, config['subdir'], update, orf).write()
            projects.append(project)

        if self.data.get('projects', {}).get('*'):
            for target in all_targets:
                if target.startswith('dep:'):
                    continue
                project = gen.project(target, target, default_config['subdir'], update).write()
                projects.append(project)

        return projects

    def _generate_solutions(self, gen: Generator, projects: list[VcxProj], update: bool) -> dict[str, SolutionFile]:
        solutions = {}
        for name, slnconfig in self.data.get('solutions', {}).items():
            sln = gen.solution(name, update)

            build_solution = slnconfig.get('build_solution', [])
            if isinstance(build_solution, str):
                build_solution = [build_solution]

            structure = parse_project_struture(slnconfig.get('projects', {}))
            for project in projects:
                subdir = structure.get(project.name, structure.get('*'))
                if subdir is not None:
                    sln.add_project(project, subdir, project.name in build_solution)

            sln.write()
            solutions[name] = sln
        return solutions

    def _generate_runsettings(self, gen: Generator, solutions: dict[str, SolutionFile], projects: list[VcxProj]):
        for name, slnconfig in self.data.get('solutions', {}).items():
            if runsettings := slnconfig.get('runsettings'):
                sln = solutions[name]
                rsfile = RunSettingsFile(sln.path.with_suffix('.gta.runsettings'))
                prdict = {project.uuid: project for project in projects}

                if runsettings is True:
                    runsettings = [{".*\\.exe": True}]

                all_keys = {"*", ".*"}
                for rsconfig in runsettings:
                    for test_regex, rsoptions in rsconfig.items():
                        if test_regex in all_keys:
                            if rsoptions is True:
                                rsoptions = {}
                            for key, value in rsoptions.items():
                                rsfile.add_solution_setting(key, value)
                    for k in all_keys:
                        rsconfig.pop(k, None)

                for project_id in sln.projects:
                    project = prdict[project_id]

                    for config_name, config in project.configs.items():
                        params = project.params[config_name]

                        if not params.output:
                            continue

                        output = os.path.relpath(
                            (project.path / config.builddir / params.output).resolve(), gen.outputdir
                        )

                        is_matching = False
                        for rsconfig in runsettings:
                            for test_regex, rsoptions in rsconfig.items():
                                if re.fullmatch(test_regex, output):
                                    is_matching = True
                                    break
                            if is_matching:
                                break
                        if not is_matching:
                            continue

                        if rsoptions is True:
                            rsoptions = {}

                        output = output.removeprefix('..')
                        while output.startswith('\\..'):
                            output = output.removeprefix('\\..')

                        regex = ".*" + output.replace('\\', '\\\\')

                        for key, value in rsoptions.items():
                            rsfile.add_project_setting(key, value, regex)

                        pathext = ';'.join(
                            str((project.path / config.builddir / p).resolve()) for p in params.search_paths
                        ) if params.search_paths else ''
                        if pathext:
                            rsfile.add_project_setting("PathExtension", pathext, regex)

                rsfile.write()


def parse_project_struture(structure: Union[dict, list], current='') -> dict[str, str]:
    result = {}

    if isinstance(structure, list):
        for item in structure:
            if isinstance(item, str):
                result[item] = current
            else:
                result.update(parse_project_struture(item, current))
    else:
        for subdir, item in structure.items():
            if item is False:
                result[subdir] = None
            elif item is True:
                result[subdir] = current
            elif isinstance(item, str):
                result[item] = f'{current}/{subdir}'
            else:
                result.update(parse_project_struture(item, f'{current}/{subdir}'))

    return result
