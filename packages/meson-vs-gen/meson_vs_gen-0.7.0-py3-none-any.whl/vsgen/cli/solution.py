from pathlib import Path

from cleo.commands.command import Command
from cleo.helpers import argument, option

from ._pathconfig import PathConfig, pathconfig
from ..api import Generator


class SolutionCommand(Command):
    name = "solution"
    description = "Generate one Visual Studio solution (.sln file)."
    arguments = [
        argument("name", description="solution name or path of generated solution"),
        argument(
            "project", description="projects to include ([target:][path/to/]project)", multiple=True, optional=True
        ),
    ]
    options = [
        option("projectdir", "p", description="where to put projects (relative to outputdir)", flag=False),
        option("update", "u", description="update existing solution and projects", flag=True),
    ] + PathConfig.options

    def handle(self) -> int:
        try:
            paths = pathconfig(self)
        except SystemExit as e:
            if e.code:
                return e.code

        projectdir = self.option("projectdir")
        if projectdir:
            projectdir = Path(projectdir)
            if projectdir.is_absolute():
                self.line_error("projectdir must be a relative path", "error")
                return 2
        else:
            projectdir = ""

        projects = self.argument("project")
        if projects:
            for p in projects:
                if ":" in p:
                    target, p = p.rsplit(p, maxsplit=1)
                else:
                    target = None
                pp = Path(p)
                if pp.name == p:
                    subdir = True
                else:
                    subdir = pp.parent
                projects.append((pp.stem, subdir, target))
        else:
            projects = None

        self.info("Generating VisualStudio solution...")
        gen = Generator(paths.output_path, paths.source_path, projectdir)

        update = self.option("update")
        for build_path, config_name in paths.build_paths.items():
            gen.set_config(build_path, config_name)
            sln = gen.solution(paths.name, update)

            if projects:
                for name, subdir, target in projects:
                    prj = gen.project(name, target, subdir, update)
                    prj.write()
                    sln.add_project(prj)
            else:
                for target in gen.all_targets():
                    prj = gen.project(target, subdir=False, update=update)
                    prj.write()
                    sln.add_project(prj)

            all_prj = gen.project("ALL", "all", False, update)
            all_prj.write()
            sln.add_project(all_prj, build_solution_target=True)

            sln.write()
            update = True

        return 0
