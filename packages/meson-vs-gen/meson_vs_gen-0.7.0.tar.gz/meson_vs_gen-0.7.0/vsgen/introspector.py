from functools import lru_cache
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Optional, Iterable, List


def lmfind(d: list[dict[str, Any]], v: Any, key: str = 'name', default: Any = None) -> Any:
    for item in d:
        if item.get(key, ...) == v:
            return item
    return default


def lmget(d: list[dict[str, Any]], v: Any, key: str = 'name', value: str = 'value', default: Any = None) -> Any:
    item = lmfind(d, v, key, ...)
    if item is ...:
        return default
    return item[value]


def is_relative_to(path: str, root: Optional[str]) -> bool:
    return path.replace(os.altsep, os.sep).startswith(root)


class MesonVersionError(RuntimeError):
    pass


class UnconfiguredProject(RuntimeError):
    pass


class UnsuportedLanguageError(RuntimeError):
    pass


class Introspector:

    INFO_DIR = 'meson-info'
    INFO_FILE = 'meson-info.json'
    LANGUAGES = {'cpp', 'c'}
    HEADER_SUFFIXES = ('.h', '.hh', '.hpp', 'h++', '.H')

    def __init__(self, build_dir: Path):
        self.build_dir = build_dir
        self.intro_data = {}
        self._mesonenv_paths = None

        info_file = self.build_dir / self.INFO_DIR / self.INFO_FILE
        if not info_file.exists():
            raise UnconfiguredProject(f"{self.build_dir} does not contain a configured meson project")

        with info_file.open('r', encoding='utf8') as f:
            info_data = json.load(f)

        m = re.match(r'([0-9]+)\.([0-9]+)\.([0-9]+)', info_data['meson_version']['full'])
        meson_version = tuple(map(int, m.groups()))
        if meson_version < (1, 1, 99):
            raise MesonVersionError("vsgen requires at lest meson 1.2.0")

        for name, data in info_data['introspection']['information'].items():
            with (self.build_dir / self.INFO_DIR / data['file']).open('r', encoding='utf8') as f:
                self.intro_data[name] = json.load(f)

    def cpu_family(self) -> str:
        return self.intro_data["machines"]["host"]["cpu_family"]

    def is_debug(self) -> bool:
        return lmget(self.intro_data['buildoptions'], 'debug')

    def toolset(self) -> str:

        for lang in self.LANGUAGES:
            compiler = self.intro_data['compilers']['host'].get(lang)
            if compiler:
                compiler_version = compiler['version']
                version = compiler_version.split('.')
                if version[0] == '19':
                    return f'v14{version[1][0]}'
                else:
                    return f'v{int(version[0])-6}0'

        raise UnsuportedLanguageError(
            "vsgen is only compatible with projects using {} language".format(" and ".join(self.LANGUAGES))
        )

    def get_target_filename(self, target: str) -> Optional[str]:
        if target.startswith('dep:'):
            return None

        data = self._target_data(target)
        if not data:
            return None

        return data['filename'][0]

    def get_target_params(self, target: str) -> tuple[list[Path], list[str], list[str]]:
        includes = []
        macros = []
        options = []

        data = self._target_data(target)
        if not data:
            return [], [], []

        if target.startswith('dep:'):
            includes.extend(map(Path, data['include_directories']))
            for param in data['compile_args']:
                if param.startswith(('-I', '/I')):
                    includes.append(Path(param[2:]))
                elif param.startswith(('-D', '/D')):
                    macros.append(param[2:])
                else:
                    options.append(param)

        else:
            for sources in data["target_sources"]:
                lang = sources.get("language")
                if lang in self.LANGUAGES:
                    for param in sources['parameters']:
                        if param.startswith(('-I', '/I')):
                            includes.append(Path(param[2:]))
                        elif param.startswith(('-D', '/D')):
                            macros.append(param[2:])
                        else:
                            options.append(param)

        return includes, macros, options
    
    def _filter_sources(self, sources: Iterable[Path], rel_dir: str) -> Iterable[Path]:
        for src in sources:
            if str(src).startswith(rel_dir):
                yield src

    def get_target_sources(self, target: str, only_relative_files: bool = False) -> list[Path]:
        data = self._target_data(target)
        if not data:
            return []

        sources = []

        if 'defined_in' not in data:
            only_relative_files = False
        if only_relative_files:
            source_dir = os.path.dirname(data['defined_in']) + os.sep

        if target.startswith('dep:'):
            sources.extend(map(Path, data['sources']))

        else:
            for source_item in data["target_sources"]:
                if source_item.get("linker"):
                    continue

                source_files = map(Path, source_item['sources'])
                if only_relative_files:
                    source_files = self._filter_sources(source_files, source_dir)
                sources.extend(source_files)

                unity_sources = map(Path, source_item.get('unity_sources', []))
                if only_relative_files:
                    unity_sources = self._filter_sources(unity_sources, source_dir)
                else:
                    unity_sources = (us for us in unity_sources if not us.is_relative_to(self.build_dir))
                sources.extend(unity_sources)

        return sources

    def get_target_headers(self, target: str, only_relative_files: bool = False) -> list[Path]:
        data = self._target_data(target)
        if not data:
            return []

        if target.startswith('dep:') or not only_relative_files:
            headers = [Path(s) for s in data['extra_files'] if s.endswith(self.HEADER_SUFFIXES)]

        elif 'defined_in' in data:
            source_dir = os.path.dirname(data['defined_in']) + os.sep
            headers = [Path(s) for s in data['extra_files'] if s.endswith(self.HEADER_SUFFIXES) and is_relative_to(s, source_dir)]

        return headers

    def get_target_extra_files(self, target: str, sources_root: Path, only_relative_files: bool = False) -> list[Path]:
        data = self._target_data(target)
        if not data:
            return []
        
        source_dir = os.path.dirname(data['defined_in']) + os.sep if 'defined_in' in data else None

        extras = set()
        if target.startswith('dep:') or not only_relative_files:
            extras.update(Path(s) for s in data['extra_files'] if not s.endswith(self.HEADER_SUFFIXES))
        elif source_dir:
            extras.update(Path(s) for s in data['extra_files'] if not s.endswith(self.HEADER_SUFFIXES) and is_relative_to(s, source_dir))
        
        if source_dir:
            # meson.build files
            extras.update(Path(m) for m in self.intro_data['buildsystem_files'] if is_relative_to(m, source_dir))

        if not target.startswith('dep:'):
            if def_file := data.get('vs_module_defs'):
                def_file = (sources_root / def_file).resolve()
                extras.add(def_file)

        return list(sorted(extras))

    def mesonenv_paths(self) -> List[Path]:
        if self._mesonenv_paths is None:
            command = [
                'meson',
                'devenv',
                '-C', str(self.build_dir),
                '--dump',
                '--dump-format=sh'
            ]
            result = subprocess.run(command, capture_output=True, encoding='utf-8')
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    varname, value = line.split('=', maxsplit=1)
                    if varname.upper() == 'PATH':
                        value = value.strip('"').replace('$'+varname, f'$({varname})')
                        self._mesonenv_paths = [self.build_dir / p for p in value.split(os.pathsep)]

        return self._mesonenv_paths

    def get_target_extra_paths(self, target: str) -> tuple[list[Path], dict[str, str]]:
        if target.startswith('dep:'):
            return [], {}

        data = self._target_data(target)
        if not data:
            return [], {}

        target_id = data["id"]
        if data["type"] != "executable":
            return [], {}

        test_data = lmfind(self.intro_data["tests"], [target_id], key="depends")
        if test_data:
            extra_paths = list(map(Path, test_data.get("extra_paths", [])))
            extra_envs = test_data.get("env", {})
            return extra_paths, extra_envs
        
        return self.mesonenv_paths(), {}

    def get_build_files(self) -> list[Path]:
        return list(map(Path, self.intro_data['buildsystem_files']))

    @lru_cache(maxsize=None)
    def _target_data(self, target: str) -> Optional[dict]:
        if target.startswith('dep:'):
            return lmfind(self.intro_data['dependencies'], [target[4:]], key='meson_variables', default=None)

        target_data = lmfind(self.intro_data["targets"], target)

        if target_data and target_data['type'] == "alias":

            depends = target_data.get("depends")
            if depends and len(depends) > 0:
                target_data = lmfind(self.intro_data["targets"], depends[0], key="id")

        return target_data

    def all_targets(self) -> list[str]:
        targets = {}

        for target_data in self.intro_data['targets']:
            if target_data['type'] == 'alias':
                prefix = target_data['id'].removesuffix('@run')
                for tname, tid in reversed(targets.items()):
                    if tid.startswith(prefix):
                        del targets[tname]
                        break

            targets[target_data['name']] = target_data['id']

        for dep_data in self.intro_data['dependencies']:
            if dep_data['type'] == 'internal' and dep_data['meson_variables']:
                target_name = 'dep:' + dep_data['meson_variables'][0]
                targets[target_name] = dep_data['name']

        return list(targets)
