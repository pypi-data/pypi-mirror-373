import pkg_resources

from cleo.application import Application

from .generate import GenerateCommand
from .project import ProjectCommand
from .solution import SolutionCommand

version = pkg_resources.get_distribution('meson-vs-gen').version
application = Application("vsgen", version)
application.add(GenerateCommand())
application.add(ProjectCommand())
application.add(SolutionCommand())


def main() -> int:
    return application.run()
