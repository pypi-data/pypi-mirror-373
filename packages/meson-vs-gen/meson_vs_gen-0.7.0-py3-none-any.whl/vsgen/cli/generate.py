from pathlib import Path

from cleo.commands.command import Command
from cleo.helpers import argument, option

from ..configfile import ConfigFile
from ..introspector import MesonVersionError


class GenerateCommand(Command):
    name = "generate"
    description = "Generate solutions and projects from config file."
    arguments = [argument("configfile", description="yaml config file")]
    options = [
        option("sourcedir", "s", description="path to source dir (default is current dir)", flag=False),
        option("outputdir", "o", description="where to write projects and solutions", flag=False),
        option("update", "u", description="update existing solution and projects", flag=True),
    ]

    def handle(self) -> int:
        configfile = Path(self.argument("configfile"))
        if not configfile.is_file():
            self.line_error(f"{configfile} does not exist", "error")
            return 1

        source_path = Path(self.option("sourcedir") or ".").resolve()
        if not source_path.is_dir():
            self.line_error("sourcedir must be a directory", "error")
            return 1

        output_path = self.option("outputdir")
        if output_path:
            output_path = Path(output_path)

        self.info("Generating VisualStudio solution...")
        cf = ConfigFile(configfile).load()
        try:
            cf.analyse(source_path)
        except MesonVersionError as e:
            self.error(str(e))
            return 1
        cf.generate(source_path, output_path, update=self.option("update"))
        return 0
