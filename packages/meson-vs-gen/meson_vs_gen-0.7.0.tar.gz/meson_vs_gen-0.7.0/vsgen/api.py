from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from .configuration import Configuration, BuildParams
from .introspector import Introspector
from .vcxproj import VcxProj
from .sln import SolutionFile


if TYPE_CHECKING:
    from os import PathLike

    PathOrStr = Union[PathLike, str]


class Generator:
    def __init__(self, vspath: PathOrStr, basedir: PathOrStr = ".", projectdir: PathOrStr = "projects") -> None:
        self.basedir: Path = Path(basedir).absolute()
        self.outputdir: Path = self.basedir / vspath
        self.projectdir: Path = self.outputdir / projectdir

        # cpu_family to arch conversion
        # you may override or update this dict
        self.cpu_arch: dict[str, str] = {
            'x86_64': 'x64',
            'x86': 'Win32',
        }

        self._intro: Optional[Introspector] = None
        self._config: Optional[Configuration] = None

    def set_config(self, builddir: PathOrStr, name: Optional[str] = None, use_include_from_env: bool = False) -> bool:
        try:
            self._intro = Introspector(self.basedir / builddir)
        except RuntimeError:
            return False

        cpu_family = self._intro.cpu_family()
        arch = self.cpu_arch.get(cpu_family, cpu_family)

        self._config = Configuration(
            name or self._intro.build_dir.name,
            arch,
            self._intro.is_debug(),
            self._intro.toolset(),
            self._intro.build_dir,
            use_include_from_env,
        )
        return True

    @property
    def introspector(self) -> Introspector:
        if self._intro is None:
            raise RuntimeError("Generator not configured. Call `set_config()` first.")
        return self._intro

    @property
    def builddir(self) -> Path:
        return self.introspector.build_dir

    @property
    def config(self) -> Configuration:
        if self._config is None:
            raise RuntimeError("Generator not configured. Call `set_config()` first.")
        return self._config

    def all_targets(self) -> list[str]:
        return self.introspector.all_targets()

    def project(
        self,
        name: str,
        target: Union[str, bool, None] = True,
        subdir: Union[PathOrStr, bool] = False,
        update: bool = True,
        only_relative_files: bool = False
    ) -> VcxProj:
        project_path = self.projectdir
        if subdir is True:
            project_path /= name
        elif subdir:
            project_path /= subdir

        vcxproj = VcxProj(name, project_path)
        if update:
            vcxproj.load(required=False)
        else:
            vcxproj.remove_user_file()

        vcxproj.add_config(self.config)

        if target:
            if target is True:
                target = name

            output = self.introspector.get_target_filename(target)
            extra_paths, envs = self.introspector.get_target_extra_paths(target)

        if not target:
            build_params = BuildParams()
        elif target.startswith('dep:'):
            build_params = BuildParams(
                None,
                *self.introspector.get_target_params(target)
            )
        elif output:
            output = Path(output).relative_to(self.builddir)

            build_params = BuildParams(
                str(output),
                *self.introspector.get_target_params(target),
                extra_paths,
                envs,
            )
        else:
            build_params = BuildParams(output=target)

        vcxproj.add_build_params(str(self.config), build_params)

        if target:
            if output or target.startswith('dep:'):
                vcxproj.add_sources(self.introspector.get_target_sources(target, only_relative_files))
                vcxproj.add_headers(self.introspector.get_target_headers(target, only_relative_files))
                vcxproj.add_extra_files(self.introspector.get_target_extra_files(target, self.basedir, only_relative_files))
            elif target == 'all':
                vcxproj.add_extra_files(self.introspector.get_build_files())

        return vcxproj

    def solution(self, name: str, update: bool = True) -> SolutionFile:
        sln = SolutionFile(self.outputdir / name)

        if update:
            sln.load_configs()

        return sln
