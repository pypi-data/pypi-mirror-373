Tools for generating VisualStudio solution from meson introspection files.
The usecase is when you want to use the `ninja` backend,
but edit or debug the project using the VisualStudio IDE.

Requirements: you need a C or C++ meson project, with at least one
configured build directory. You need meson 1.2.0 or higher.



## Using the command line

A command line interface is provided through the `vsgen` command.


### Generating project

The `project` command allows to generate one .vcxproj file from a configured
meson project:

`vsgen project [--target TARGET] [--update] [--sourcedir SOURCEDIR] [--outputdir OUTPUTDIR] [--builddir [CONFIG:]BUILDDIR, ...] NAME`

The `NAME` is the name of the generated .vcxproj. It can also be a full path.
By default, it will look for a target with the same name as the project,
unless `--target` option is provided. Project sources should be in current dir,
or specified with `--sourcedir`. Build directory must be provided using `--builddir`
option. It can be a path relative to SOURCEDIR. The config is deduced automatically,
but the config name to use can be specified using `CONFIGNAME:` prefix to the build dir
(e.g. `--builddir debug:/path/to/debug/build`).

Files are generated in `--outputdir`, unless a full path is provided for `NAME`.
By default, the `OUTPUTDIR` will be the current directory.

If `--update` option is provided, existing .vcxproj will be updated instead of
being rewritten. This is useful to add a new build config to an existing project.

Example:

```
vsgen project -t mylib -o vs -b build/debug -b build/release MyProject
```

will generate `vs/MyProject.vcxproj`, with configs for debug and release,
for the `mylib` build target.


### Generating solution

The `solution` command allows to generate a .sln file that includes one or many projects.

`vsgen solution [--project [TARGET:]PROJECT, ...] [--projectdir PROJECTDIR] [--update] [--sourcedir SOURCEDIR] [--outputdir OUTPUTDIR] [--builddir [CONFIG:]BUILDDIR, ...] NAME`

The `NAME` is the name of the generated .sln file. It can also be a full path.

The `--project` option allows to specify the name or the path of a project to include.
It may be specified multiple times. If not specified, all projects from PROJECTDIR are
included. `TARGET` if the name of the build target to use, if different from `PROJECT`.
If not specified, projects for all build targets are generated.

If specified, `PROJECTDIR` will be a sudir of `OUTPUTDIR` containing the project files.

Other options are similar to those of the `project` command.


### Using configuration file

The `generate` command allows the generation of complex solutions, using a .yaml
configuration file.

`vsgen generate [--sourcedir SOURCEDIR] [--outputdir OUTPUTDIR] CONFIGFILE`

`CONFIGFILE` is the path to the .yaml config file. Other options are similar
to those of `project` command.


The config file contains the following keys:

- `outputdir`: (optional) Where to generate the solution files, if not specified
  on the command line. Default is to use current dir.
- `projectdir`: (optional) Name of a subdirectory where to write project files.
- `case_insensitive_targets`: (optional) If true, lower case targets match project names containing uppercase characters.
- `only_relative_files`: (optional) If true, do not add files outside target source dir
                         (i.e. where target meson.build file is located) into the project.
- `include_from_env`: (optional) If true, will use `INCLUDE` env var for system include path.
                                 If 'auto', will use `INCLUDE` if it is defined.
                                 If false (default), will no rewrite the include path.
                                 This is useful when using a different build tools version that the IDE.                         
- `configs`: map build directories to config names.
- `archs`: (optional) map cpu_family to arch name. If not specified,
  use the cpu_family as the arch name.
- `projects`: The projects to generate. See project specifications below
  for more details.
- `solutions`: The solutions to generate. See solution specifications below
  for more details.

#### Project specifications

For each project, the key is the name of the project to generate.
If the key is `*`, the settings apply to all unlisted projects,
and is used as default config.

If the value is a boolean, `true` means to generate the project with default settings,
and `false` means to not generate that project.

If the value is a map, the following keys are recognized:

- `target`: the build target name. `true` means to use the project name as the target name.
            If target name begins with `dep:`, this is the name of an internal dependency object,
            used for a header only project. This project will not compile, but will display files
            from that dependency.
  `all` is used for a target that generates all targets.
- `subdir`: if specified, put the generated project into that subdir of the project dir.

#### Solution specifications

For each solution, the key is the name of the solution to generate.

Value is a map with the following keys:

- `projects`: A list of projects to include into the solution.
  If the value is a string, this project is included (must be listed into
  the `projects` section). If the value is a map, it map a directory name
  with a list of projects. This allow to put projects into logical directories
  in the solution. The structure is recursive. If the value is `*`, it means
  to include all projects not referenced elsewhere in the solution. If the value
  is a map with a boolean value, the key is a project name, and it is included if
  the value is `true`, and explicitly skipped if the value is `false`.
- `build_solution`: The value is the project (or a list of projects) invoked when
  building the solution.
- `runsettings`: (optional) If `true`, generates runsettings for all executables.
  Otherwise, map a wildcard with runsettings options. This allow special configurations
  for running tests with Google Test Adapter.

## Using the API

### The Generator object

`vsgen` package can also be used as an API, from a python script:
`from vsgen.api import Generator`.

The generator object takes 3 arguments:
- `vspath`: The path where to generate the solution and project files
  (absolute, or relative to `basedir`)
- `basedir`: (optional) The base path for other paths. Default is current dir.
- `projectdir`: (optional) The subdir where to generate projects (relative to `vapath`)

You can also modify or override the `cpu_arch` dictionary,
mapping cpu_family to arch name for the solution and projects.

The next step is to call `set_config`. The method takes the following arguments:
- `builddir`: meson build dir, absolute, or relative to `self.basedir`.
- `name`: (optional) config name to use (default is builddir name).
- `use_include_from_env`: (optional) If `True`, will use the `INCLUDE` env var
                          as system include path.

The `project` method is used to create a `VcxProj` object. Arguments are:
- `name`: The project name.
- `target`: (optional) The build target name. Default is project name.
- `subdir`: (optional) Subdir (relative to projectdir) where to write the project.
  If `True`, the subdir is the project name. If `False`, no subdir is used.
- `update`: (optional) If `True`, update existing project instead of overwriting it.
  Default is `True`.
- `only_relative_files`: (optional) If `True`, will not reference source files that
                         are not relative to the project root.

The method returns a `VcxProj` object.

The `solution` method is used to create a `SolutionFile` object.
Arguments are:
- `name`: The solution name.
- `update`: Whether to update existing files instead of overwriting them.

### The ConfigFile object

This is a high-level interface to deal with complex solutions
managed by a configuration file. See [Using configuration file] above
for more details about the configuration file syntax.

```
from vsgen.configfile import ConfigFile
from pathlib import Path

cf = ConfigFile('path/to/config.yaml').load()  # load config file

basepath = Path('project/basepath')
outputpath = Path('project/outputpath')

cf.analyse(basepath)  # analyse project introspection data
cf.generate(basepath, outputpath, update=True)  # generate project and solution files

```


### The SolutionFile object

You usually create the `SolutionFile` object using the `Generator`.

Next step is to add projects to the solution:

```
sln.add_project(project, subdir, build_solution_target=False)
```

- `project` is a `VcxProj` object
- `subdir` is an optional string if you want the project into a logical
  subdirectory in the solution.
- `build_solution_target`: if `True`, this project is build when
  generating the whold solution. This is usually used for the `all` target only.

Finally, you can write the solution file:

```
sln.write()
```


### The VcxProj object

To write the .vcxproj file: `prj.write()`/


### The RunSettingsFile object

[https://learn.microsoft.com/en-us/visualstudio/test/configure-unit-tests-by-using-a-dot-runsettings-file?view=vs-2022]

This allow to configure and write a runsettings file.

```
from vsgen.runsettings import RunSettingsFile
from pathlib import Path

rsfile = RunSettingsFile(Path('path/to/runsettings/file'))
rsfile.add_solution_setting(name, value)  # add a setting for whole solution
rsfile.add_project_setting(name, value, regex)  # add a setting for projects
                                                # matched by regex

rsfile.write()

```

