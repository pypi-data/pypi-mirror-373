from pathlib import Path
from typing import Optional

from cleo.commands.command import Command
from cleo.helpers import option


class PathConfig:

    options = [
        option("sourcedir", "s", description="path to source dir (default is current dir)", flag=False),
        option("outputdir", "o", description="where to write projects and solutions", flag=False),
        option(
            "builddir",
            "b",
            description="paths to build dir ([configname:]path/to/builddir) (relative to sourcedir)",
            flag=False,
            multiple=True,
        ),
    ]

    def __init__(self, name: str, sourcedir: Optional[str], builddir: Optional[list[str]], outputdir: Optional[str]):
        self.source_path = Path(sourcedir or ".").resolve()

        namepath = Path(name)
        self.name = namepath.stem

        self.build_paths = {}
        builddirs = builddir or []

        for b in builddirs:
            if ':' in b[2:]:  # do not split if b is "C:\..."
                config_name, build_path = b.split(":", maxsplit=1)

            else:
                config_name = None
                build_path = b

            build_path = self.source_path / build_path
            self.build_paths[build_path] = config_name

        if outputdir:
            self.output_path = Path(outputdir).resolve().absolute()
            self.project_dir = (self.output_path / namepath.parent).resolve()
            if self.project_dir.is_relative_to(self.output_path):
                self.project_dir = self.project_dir.relative_to(self.output_path)
            if self.project_dir == Path("."):
                self.project_dir = False

        else:
            self.output_path = namepath.parent.resolve().absolute()
            self.project_dir = False


def pathconfig(cmd: Command) -> PathConfig:
    pc = PathConfig(cmd.argument("name"), cmd.option("sourcedir"), cmd.option("builddir"), cmd.option("outputdir"))

    if not pc.source_path.is_dir():
        cmd.line_error("sourcedir must be a directory", "error")
        raise SystemExit(1)

    if not pc.build_paths:
        cmd.line_error("You must provide at least one builddir", "error")
        raise SystemExit(2)

    if pc.project_dir and pc.project_dir.is_absolute():
        cmd.line_error("name should be relative to output path", "error")
        raise SystemExit(1)

    return pc
