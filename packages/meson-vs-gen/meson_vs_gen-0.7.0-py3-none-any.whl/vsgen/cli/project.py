from cleo.commands.command import Command
from cleo.helpers import argument, option

from ._pathconfig import PathConfig, pathconfig
from ..api import Generator


class ProjectCommand(Command):
    name = "project"
    description = "Generate one Visual Studio project (.vcxproj file)."
    arguments = [argument("name", description="project name or path of generated project")]
    options = [
        option("target", "t", description="build target to use (default is same as project name)", flag=False),
        option("update", "u", description="update existing project", flag=True),
    ] + PathConfig.options

    def handle(self) -> int:
        try:
            paths = pathconfig(self)
        except SystemExit as e:
            if e.code:
                return e.code

        self.info("Generating VisualStudio project...")
        gen = Generator(paths.output_path, paths.source_path, "")

        update = self.option("update")
        for build_path, config_name in paths.build_paths.items():
            gen.set_config(build_path, config_name)
            prj = gen.project(paths.name, self.option("target"), paths.project_dir, update)
            prj.write()
            update = True

        return 0
