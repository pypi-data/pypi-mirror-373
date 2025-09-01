from danoan.journal_manager.core import api, model, exceptions

from danoan.journal_manager.cli import utils
from danoan.journal_manager.cli.wrappers import (
    general_proc_call,
    mkdocs_wrapper,
    node_wrapper,
)

from danoan.journal_manager.cli.commands.journal_commands.register import (
    register as register_journal,
)

import multiprocessing
import argparse
from importlib_resources import files, as_file
from io import StringIO
from jinja2 import Environment, PackageLoader
import logging
from pathlib import Path
import shutil
import signal
from typing import List, Any, Optional, Dict, Tuple


logger = logging.getLogger("danoan.journal_manager")

# -------------------- Helper Functions --------------------


def __remove_directory_before_copy__(src_dir: Path, dest_dir: Path):
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    shutil.copytree(src_dir, dest_dir)


def __register_journals_by_location__(locations: List[Path]):
    """
    Register journals by location in the registry.

    Args:
        locations: A list of journal location folders.
    Raises:
        InvalidLocation if one or more locations are not valid or do
        not exist.
    """
    invalid_locations: List[Path] = []
    for journal_location in locations:
        if not journal_location.exists():
            invalid_locations.append(journal_location)

    if len(invalid_locations) != 0:
        raise exceptions.InvalidLocation(invalid_locations)

    for journal_location in locations:
        journal_title = Path(journal_location).expanduser().name
        register_journal(Path(journal_location), journal_title)


def __collect_journal_names_from_location__(
    list_of_locations: List[str],
) -> List[str]:
    """
    Return a list of journals names based on their journal location.

    Args:
        list_of_locations: A list with journal location folders.
    Returns:
        A list of journal names.
    Raises:
        InvalidLocation if one or more locations are not valid or do
        not exist.
    """
    journal_data_file = api.get_journal_data_file()
    journals = map(
        lambda location: api.find_journal_by_location(
            journal_data_file, location
        ),
        list_of_locations,
    )
    return list(map(lambda journal: journal.name if journal else "", journals))


def __validate_journal_names_in_registry__(
    names: List[str],
) -> Tuple[List[str], List[str]]:
    """
    Separate a list of journal names in registered and non registered.

    Args:
        names: List of journal names.
    Returns:
        Two lists of journal names. The first one contain journal names that
        were found in the registry and the second one contain journal names
        that were not found in the registry.
    """
    journal_data_file = api.get_journal_data_file()
    registered_names = list(
        filter(lambda x: api.find_journal_by_name(journal_data_file, x), names)
    )
    non_registered_names = list(
        filter(lambda x: x not in registered_names, names)
    )

    return registered_names, non_registered_names


def __validate_journal_locations_in_registry__(
    locations: List[str],
) -> Tuple[List[str], List[str]]:
    """
    Separate a list of journal locations in registered and non registered.

    Args:
        list_of_locations: A list with journal location folders.
    Returns:
        Two lists of journal names. The first one contain journal names that
        were found in the registry and the second one contain journal names
        that were not found in the registry.
    """
    journal_data_file = api.get_journal_data_file()
    registered_locations = list(
        filter(
            lambda x: api.find_journal_by_location(journal_data_file, x),
            locations,
        )
    )
    non_registered_locations = list(
        filter(lambda x: x not in registered_locations, locations)
    )

    return registered_locations, non_registered_locations


def __validate_journal_from_include_all_folder__(
    include_all_folder: Path,
) -> Tuple[List[str], List[str]]:
    """
    Separate a list of journal locations in registered and non registered.

    All folders located in include_all_folder are considered as a journal location.

    Args:
        include_all_folder: Location where all children folders are considered
                            as a journal location.
    Returns:
        Two lists of journal names. The first one contain journal names that
        were found in the registry and the second one contain journal names
        that were not found in the registry.
    Raises:
        IncludeLocation if the include_all_folder is not valid or does not
        exist.
    """
    if not include_all_folder.exists():
        raise exceptions.InvalidLocation(include_all_folder)

    return __validate_journal_locations_in_registry__(
        list(map(lambda x: x.as_posix(), include_all_folder.iterdir()))
    )


# -------------------- Build Utilities --------------------


class BuildStep:
    """
    Base class for a build step in the process of building a journal.

    This class defined the interface and also the basic implementations
    of the methods that made the BuildStep interface.

    The design of the journal build process expects build steps to be
    called in a chain. For example:

        MyFirstBuildStep(some_parameters)
        .build()
        .next(MySecondBuildStep(another_parameters))

    The parameters passed to a build step persist in following steps.
    If a parameter of same name had been set before, it will be overwritten.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    def build(self, **kwargs):
        return self

    def next(self, build_step_class):
        return build_step_class(**self.__dict__).build()

    def __getitem__(self, key):
        return self.__dict__[key]


class FailedStep(BuildStep):
    """
    BuildStep to be returned whenever an error is detected.
    """

    def __init__(self, build_step: BuildStep, msg: str):
        self.build_step = build_step
        self.msg = msg

    def build(self, **kwargs):
        return self

    def next(self, build_step):
        return self


class BuildJournals(BuildStep):
    """
    Build html static pages from journals using mkdocs
    """

    def __init__(self, build_instructions: model.BuildInstructions, **kwargs):
        super().__init__(**kwargs)
        self.build_instructions = build_instructions

        if not self.build_instructions.build_location:
            raise RuntimeError(
                "Journal could not be built because a location was not specified."
            )

        self.journals_site_folder = Path(
            self.build_instructions.build_location
        ).joinpath("site")

    def build(self, **kwargs):
        try:
            data: Dict[str, Any] = {"journals": []}
            for journal_name in get_journals_names_to_build(
                self.build_instructions
            ):
                journal_data_file = api.get_journal_data_file()
                journal_data = api.find_journal_by_name(
                    journal_data_file, journal_name
                )

                if (
                    journal_data
                    and not journal_data.active
                    and not self.build_instructions.build_inactive
                ):
                    logger.info(
                        f"Skipping {journal_data.name} because it is marked as inactive."
                    )
                    continue

                if journal_data and journal_data.name == journal_name:
                    if (
                        journal_data.active
                        or self.build_instructions.build_inactive
                    ):
                        mkdocs_wrapper.build(
                            Path(journal_data.location_folder),
                            Path(
                                f"{self.journals_site_folder}/{journal_data.name}"
                            ),
                        )
                    data["journals"].append(journal_data)

            self.journal_data = data
            return self
        except exceptions.InvalidName as ex:
            ss = StringIO()
            ss.write(
                "The following journal names are not part of the registry:"
            )
            for journal_name in ex.names:
                ss.write(f"{journal_name}")
            ss.write("Build is aborted.")

            return FailedStep(self, ss.getvalue())
        except exceptions.InvalidLocation as ex:
            ss = StringIO()
            ss.write(
                "The following journal location folders were not found in the registry:"
            )
            for journal_location in ex:
                ss.write(f"{journal_location}")
            ss.write("Build is aborted.")

            return FailedStep(self, ss.getvalue())
        except exceptions.InvalidIncludeAllFolder as ex:
            ss = StringIO()
            ss.write(
                f"The path specified in the build instructions: {ex.path} does not exist. Build is aborted."
            )
            return FailedStep(self, ss.getvalue())
        except BaseException as ex:
            return FailedStep(self, str(ex))


class BuildIndexPage(BuildStep):
    """
    Build the index page with links to all rendered journals.
    """

    assets = files("danoan.journal_manager.assets.templates").joinpath(
        "material-index", "assets"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Not really necessay, but this make explicit the variables that are inherit
        # by other build steps and that are necessary to be defined at this point. It
        # is also useful as a sanity check during static type checking
        self.journals_site_folder = self.__dict__["journals_site_folder"]
        self.build_instructions: model.BuildInstructions = self.__dict__[
            "build_instructions"
        ]

    def build(self, **kwargs):
        if not self.build_instructions.build_index:
            return self

        env = Environment(
            loader=PackageLoader(
                "danoan.journal_manager.assets", package_path="templates"
            )
        )

        with as_file(BuildIndexPage.assets) as assets_path:
            __remove_directory_before_copy__(
                assets_path, self.journals_site_folder.joinpath("assets")
            )

        with open(self.journals_site_folder.joinpath("index.html"), "w") as f:
            template = env.get_template("material-index/index.tpl.html")
            f.write(template.render(self["journal_data"]))

        return self


class BuildHttpServer(BuildStep):
    """
    Sets up the http server that will serve the journals.

    The http server structure is composed of:
        1. An http server written in node.js + express
        2. A file monitor script using entr
        3. A file monitor action to rebuild journals that are updated

    The http server and the file monitor run independently. Whenever a
    markdown file is modified, the file monitor triggers the file monitor
    action scripts that rebuilds only the journal affected. The http server
    will automatically reflect the changes.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.build_instructions.build_location:
            raise exceptions.InvalidAttribute("No build location was given")

        self.http_server_folder = Path(
            self.build_instructions.build_location
        ).joinpath("http-server")

        # Not really necessay, but this make explicit the variables that are inherit
        # by other build steps and that are necessary to be defined at this point. It
        # is also useful as a sanity check during static type checking
        self.journals_site_folder = self.__dict__["journals_site_folder"]
        self.build_instructions: model.BuildInstructions = self.__dict__[
            "build_instructions"
        ]

    def build(self, **kwargs):
        try:
            if not self.build_instructions.with_http_server:
                return self

            env = Environment(
                loader=PackageLoader(
                    "danoan.journal_manager.assets", package_path="templates"
                )
            )

            http_server = files(
                "danoan.journal_manager.assets.templates"
            ).joinpath("http-server")
            shutil.copytree(
                http_server, self.http_server_folder, dirs_exist_ok=True
            )

            node_wrapper.install_dependencies(self.http_server_folder)

            file_monitor_action_template = env.get_template(
                "file-monitor/file-monitor-action.tpl.sh"
            )
            file_monitor_template = env.get_template(
                "file-monitor/file-monitor.tpl.sh"
            )

            if not self.build_instructions.build_location:
                raise RuntimeError("No build location was given.")

            file_monitor_folder = Path(
                self.build_instructions.build_location
            ).joinpath("file-monitor")
            file_monitor_folder.mkdir(exist_ok=True)

            self.file_monitor_script = file_monitor_folder.joinpath(
                "file-monitor.sh"
            )
            file_monitor_action_script = file_monitor_folder.joinpath(
                "file-monitor-action.sh"
            )

            folders_to_monitor = set()
            journal_data_file = api.get_journal_data_file()
            for journal_name in get_journals_names_to_build(
                self.build_instructions
            ):
                journal_data = api.find_journal_by_name(
                    journal_data_file, journal_name
                )
                if journal_data:
                    folders_to_monitor.add(journal_data.location_folder)

            data = {
                "journals_site_folder": self.journals_site_folder,
                "journals_files_folder": list(folders_to_monitor),
            }

            with open(self.file_monitor_script, "w") as f:
                f.write(file_monitor_template.render(data=data))
            self.file_monitor_script.chmod(0o777)

            with open(file_monitor_action_script, "w") as f:
                f.write(file_monitor_action_template.render(data=data))
            file_monitor_action_script.chmod(0o777)

            return self
        except BaseException as ex:
            return FailedStep(self, str(ex))


# -------------------- API --------------------


def get_journals_names_to_build(
    build_instructions: model.BuildInstructions,
) -> List[str]:
    """
    Read the build instructions and collect the journal names to build.

    There are four ways to build journals:
        1. Giving a list of journal names;
        2. Giving a list of journal locations;
        3. Giving a directory that contains journal folders and build all of them;
        4. Saying nothing and then all registered journals are built.

    This function reads the build instructions and extracts the journals names
    accordingly with the chosen method.

    Args:
        build_instructions: A BuildInstructions object.
    Returns:
        A list of journal names to build.
    Raises:
        InvalidName if invalid journal names are given.
        InvalidLocation if invalid journal locations are given.
        InvalidIncludeAllFolder if invalid include_all_folder location
        is given.
    """
    journal_data_file = api.get_journal_data_file()

    journals_names_to_build = []
    if build_instructions.journals_names_to_build is not None:
        (
            registered_names,
            non_registered_names,
        ) = __validate_journal_names_in_registry__(
            build_instructions.journals_names_to_build
        )

        if len(non_registered_names) != 0:
            raise exceptions.InvalidName(non_registered_names)

        journals_names_to_build = registered_names
    elif build_instructions.journals_locations_to_build is not None:
        (
            registered_locations,
            non_registered_locations,
        ) = __validate_journal_locations_in_registry__(
            build_instructions.journals_locations_to_build
        )
        __register_journals_by_location__(
            [Path(p) for p in non_registered_locations]
        )

        journals_names_to_build = __collect_journal_names_from_location__(
            registered_locations + non_registered_locations
        )

    elif build_instructions.include_all_folder is not None:
        (
            registered_locations,
            non_registered_locations,
        ) = __validate_journal_from_include_all_folder__(
            Path(build_instructions.include_all_folder)
        )
        __register_journals_by_location__(
            [Path(p) for p in non_registered_locations]
        )

        journals_names_to_build = __collect_journal_names_from_location__(
            registered_locations + non_registered_locations
        )
    else:
        # Build all registered journals
        journals_names_to_build.extend(
            map(lambda x: x.name, journal_data_file.list_of_journal_data)
        )
    return journals_names_to_build


def build(build_instructions: model.BuildInstructions):
    """
    Build html static pages from journals.
    """
    if not build_instructions.build_location:
        raise RuntimeError("No build location was given.")

    build_location = Path(build_instructions.build_location)
    build_location.mkdir(exist_ok=True)

    return (
        BuildJournals(build_instructions=build_instructions)
        .build()
        .next(BuildIndexPage)
        .next(BuildHttpServer)
    )


# -------------------- CLI --------------------


def __start_http_server__(http_server_folder: Path, file_monitor_script: Path):
    """
    Start a local http server.

    This function is offered as as a helper for test purposes. It expects
    that the structure of the http_server_folder is exactly the same created
    by the BuildHttpServer build step.
    """
    t1 = multiprocessing.Process(
        target=node_wrapper.start_server,
        args=[http_server_folder.joinpath("init.js")],
    )
    t2 = multiprocessing.Process(
        target=general_proc_call.start, args=[file_monitor_script]
    )

    try:
        t1.start()
    except Exception as ex:
        print(ex)
        print(
            "HTTP server could not be started. Make sure you have `nodejs` installed."
        )

    try:
        t2.start()
    except Exception as ex:
        print(ex)
        print(
            "File monitor could not be started. Make sure you have `entr` installed."
        )

    def terminate_processes(sig, frame):
        print("Terminating http server")
        t1.terminate()
        print("Terminating file-monitor")
        t2.terminate()

    signal.signal(signal.SIGINT, terminate_processes)
    signal.signal(signal.SIGTERM, terminate_processes)

    while t1.is_alive() and t2.is_alive():
        t1.join(0.1)
        t2.join(0.1)


def __merge_build_instructions__(
    build_location: Path,
    build_instructions_path: Optional[Path] = None,
    **kwargs,
):
    """
    Helper function to merge build instructions.

    The cli parser offer several options to build journals. This helper function
    merge all these parameters in a unique object.
    """
    build_instructions = None
    if build_instructions_path is None:
        build_instructions = model.BuildInstructions(build_location)
    else:
        build_instructions = model.BuildInstructions.read(
            build_instructions_path
        )

    if build_instructions and not build_instructions.build_location:
        build_instructions.build_location = str(build_location)

    for keyword, value in kwargs.items():
        if value is not None:
            build_instructions.__dict__[keyword] = value

    return build_instructions


def __build__(
    build_location: Path,
    build_inactive: bool = False,
    build_instructions_path: Optional[Path] = None,
    build_index: Optional[bool] = None,
    journals_names_to_build: Optional[List[str]] = None,
    journals_locations_to_build: Optional[List[str]] = None,
    with_http_server: Optional[bool] = None,
    ignore_safety_questions: bool = False,
    **kwargs,
):
    utils.ensure_configuration_file_exists()
    build_location = Path(build_location).absolute()

    if build_location.exists():
        if not ignore_safety_questions:
            ok_continue = input(
                f"The directory {build_location} exists already. If you continue the operation the files there will be overwritten. Are you sure you want to continue?\n"
            )

            if ok_continue.lower() not in ["y", "yes"]:
                exit(1)

    build_instructions = __merge_build_instructions__(
        build_location.expanduser(),
        build_instructions_path,
        build_inactive=build_inactive,
        build_index=build_index,
        journals_names_to_build=journals_names_to_build,
        journals_locations_to_build=journals_locations_to_build,
        with_http_server=with_http_server,
    )

    build_result = build(build_instructions)

    if not isinstance(build_result, FailedStep):
        if with_http_server:
            __start_http_server__(
                build_result.http_server_folder,
                build_result.file_monitor_script,
            )
    else:
        print(f"Build was not successful with error: {build_result.msg}.")
    pass


def get_parser(subparser_action=None):
    command_name = "build"
    command_description = build.__doc__ if build.__doc__ else ""
    command_help = command_description.split(".")[0]

    parser = None
    if subparser_action:
        parser = subparser_action.add_parser(
            command_name,
            description=command_description,
            help=command_help,
            aliases=["b"],
        )
    else:
        parser = argparse.ArgumentParser(
            command_name,
            description=command_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

    parser.add_argument(
        "--build-inactive",
        help="If passed, inactive journals will also be built.",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--build-instructions",
        dest="build_instructions_path",
        type=Path,
        help="Configuration file with build instructions.",
    )
    parser.add_argument(
        "--build-location",
        help="Directory where build artifacts will be stored. If not specified, current working directory is used",
        type=Path,
        default=Path.cwd(),
    )
    parser.add_argument(
        "--do-not-build-index",
        dest="build_index",
        help="The index page with the table of content won't be rebuilt",
        action="store_false",
        default=True,
    )
    parser.add_argument(
        "--ignore-safety-questions",
        action="store_true",
        help="If specified, the program will overwrite the contents of BUILD_LOCATION without previous warning.",
    )
    parser.add_argument(
        "--journal-name",
        "--jn",
        dest="journals_names_to_build",
        action="append",
        help="Name of the journal to build",
    )
    parser.add_argument(
        "--journal-location",
        "--jl",
        dest="journals_locations_to_build",
        action="append",
        help="Location of the journal to build",
    )
    parser.add_argument(
        "--with-http-server",
        action="store_true",
        help="A http-server will be started and the journals files monitored.",
    )
    parser.set_defaults(func=__build__)

    return parser
