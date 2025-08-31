"""CLI handler for glpkg"""

import argparse
from netrc import netrc
import os
import sys
import urllib
from gitlab import Packages, __version__


class CLIHandler:
    """Class to parse CLI arguments and run the requested command"""

    def __init__(self):
        """
        Creates a new instance of CLIHandler.

        Parses the arguments from command line and prepares everything
        to be ready to executed. Just use do_it to run it!
        """
        parser = argparse.ArgumentParser(
            description="Toolbox for GitLab generic packages"
        )
        parser.add_argument("-v", "--version", action="store_true")
        parser.set_defaults(action=self._print_version)
        subparsers = parser.add_subparsers()
        list_parser = subparsers.add_parser(
            name="list",
            description="Lists the available version of a package from the "
            "package registry.",
        )
        self._register_list_parser(list_parser)
        download_parser = subparsers.add_parser(
            name="download",
            description="Downloads all files from a specific package version "
            "to the current directory.",
        )
        self._register_download_parser(download_parser)
        upload_parser = subparsers.add_parser(
            name="upload", description="Uploads file to a specific package version."
        )
        self._register_upload_parser(upload_parser)
        self.args = parser.parse_args()

    def _print_version(self, _args: argparse.Namespace) -> int:
        """
        A handler for printing the version of the tool to the console.

        Parameters
        ----------
        _args : argparse.Namespace
            Unused.

        Return
        ------
        int
            Zero when printing to console succeeded.
        """
        print(__version__)
        return 0

    def do_it(self) -> int:
        """
        Executes the requested command.

        In case of error, prints to stderr.

        Return
        ------
        int
            Zero when everything went fine, non-zero otherwise.
        """
        ret = 1
        try:
            ret = self.args.action(self.args)
        except urllib.error.HTTPError as e:
            # GitLab API returns 404 when a resource is not found
            # but also when the user has no access to the resource
            print("Oops! Something did go wrong.", file=sys.stderr)
            print(e, file=sys.stderr)
            print(
                "Note that Error 404 may also indicate authentication issues with GitLab API.",
                file=sys.stderr,
            )
            print("Check your arguments and credentials.", file=sys.stderr)
        return ret

    def _register_common_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Registers common arguments to the parser:
            - host
            - ci
            - project
            - name
            - token
            - netrc

        Parameters
        ----------
        parser:
            The argparser where to register the common arguments.
        """
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "-H",
            "--host",
            default="gitlab.com",
            type=str,
            help="The host address of GitLab instance without scheme, "
            "for example gitlab.com. Note that only https scheme is supported.",
        )
        group.add_argument(
            "-c",
            "--ci",
            action="store_true",
            help="Use this in GitLab jobs. In this case CI_SERVER_HOST, CI_PROJECT_ID, "
            "and CI_JOB_TOKEN variables from the environment are used. --project and --token "
            "can be used to override project ID and the CI_JOB_TOKEN to a personal or project "
            "access token.",
        )
        parser.add_argument(
            "-p",
            "--project",
            type=str,
            help="The project ID or path. For example 123456 or namespace/project.",
        )
        parser.add_argument("-n", "--name", type=str, help="The package name.")
        group2 = parser.add_mutually_exclusive_group()
        group2.add_argument(
            "-t",
            "--token",
            type=str,
            help="Private or project access token that is used to authenticate with "
            "the package registry. Leave empty if the registry is public. The token "
            "must have 'read API' or 'API' scope.",
        )
        group2.add_argument(
            "--netrc",
            action="store_true",
            help="Set to use a token from .netrc file (~/.netrc) for the host. The "
            ".netrc username is ignored due to API restrictions. PRIVATE-TOKEN is used "
            "instead. Note that .netrc file access rights must be correct.",
        )

    def _register_download_parser(self, parser: argparse.ArgumentParser):
        """
        Registers the download command related arguments to the parser:
            - version
            - file
            - destination
            - action

        Additionally, registers the common args.

        Parameters
        ----------
        parser:
            The argparser where to register the download arguments.
        """
        self._register_common_arguments(parser)
        parser.add_argument("-v", "--version", type=str, help="The package version.")
        parser.add_argument(
            "-f",
            "--file",
            type=str,
            help="The file to download from the package. If not defined, all "
            "files are downloaded.",
        )
        parser.add_argument(
            "-d",
            "--destination",
            default="",
            type=str,
            help="The path where the file(s) are downloaded. If not defined, "
            "the current working directory is used.",
        )
        parser.set_defaults(action=self._download_handler)

    def _args(self, args) -> tuple[str, str, str, str, str]:
        """
        Returns the connection parameters according to the args

        Parameters
        ----------
        args:
            The args that are used to determined the connection parameters

        Returns
        -------
        host : str
            The GitLab host name
        project : str
            The Project ID or name to use
        name : str
            The package name
        token_user : str
            The token user according to the args. If ci is used, returns `JOB-TOKEN`, else
            `PRIVATE-TOKEN`.
        token : str
            The token according to the args. If token is set, returns it. If netrc is set,
            reads the token from the .netrc file. If ci is set, reads the environment
            variable CI_JOB_TOKEN. Otherwise returns None.
        """
        if args.ci:
            host = os.environ["CI_SERVER_HOST"]
            project = os.environ["CI_PROJECT_ID"]
            token = os.environ["CI_JOB_TOKEN"]
            token_user = "JOB-TOKEN"
            if args.project:
                project = args.project
            if args.token:
                token = args.token
                token_user = "PRIVATE-TOKEN"
        else:
            host = args.host
            project = args.project
            token = args.token
            token_user = "PRIVATE-TOKEN"
        if args.netrc:
            _, _, token = netrc().authenticators(host)
            token_user = "PRIVATE-TOKEN"
        name = args.name
        return host, project, name, token_user, token

    def _download_handler(self, args: argparse.Namespace) -> int:
        """
        Downloads package file(s) from GitLab package registry.

        Parameters
        ----------
        args : argparse.Namespace
            The parsed arguments

        Returns
        -------
        int
            Zero if everything goes well, non-zero otherwise
        """
        ret = 1
        host, project, name, token_user, token = self._args(args)
        version = args.version
        destination = args.destination
        gitlab = Packages(host, token_user, token)
        package_id = gitlab.get_package_id(project, name, version)
        if package_id:
            files = []
            if args.file:
                files.append(args.file)
            else:
                files = gitlab.list_files(project, package_id)
            for file in files:
                ret = gitlab.download_file(project, name, version, file, destination)
                if ret:
                    print("Failed to download file " + file)
                    break
        else:
            print("No package " + name + " version " + version + " found!")
        return ret

    def _register_list_parser(self, parser: argparse.ArgumentParser):
        """
        Registers the list command related arguments to the parser:
            - action

        Additionally, registers the common args.

        Parameters
        ----------
        parser:
            The argparser where to register the list arguments.
        """
        self._register_common_arguments(parser)
        parser.set_defaults(action=self._list_packages)

    def _list_packages(self, args: argparse.Namespace) -> int:
        """
        List package versions from GitLab package registry.

        Parameters
        ----------
        args : argparse.Namespace
            The parsed arguments

        Returns
        -------
        int
            Zero if everything goes well, non-zero otherwise
        """
        host, project, name, token_user, token = self._args(args)
        gitlab = Packages(host, token_user, token)
        packages = gitlab.list_packages(project, name)
        print("Name" + "\t\t" + "Version")
        for package in packages:
            print(package["name"] + "\t" + package["version"])

    def _register_upload_parser(self, parser: argparse.ArgumentParser):
        """
        Registers the upload command related arguments to the parser:
            - version
            - file
            - action

        Additionally, registers the common args.

        Parameters
        ----------
        parser:
            The argparser where to register the upload arguments.
        """
        self._register_common_arguments(parser)
        parser.add_argument("-v", "--version", type=str, help="The package version.")
        parser.add_argument(
            "-f",
            "--file",
            type=str,
            help="The file to be uploaded, for example my_file.txt. Note that "
            "only relative paths (to the source) are supported and the relative "
            "path is preserved when uploading the file. If left undefined, all files "
            "of the source directory are uploaded. For example --source=temp --file=myfile "
            "will upload myfile to the GitLab generic package root. However using --source=. "
            "(or omittinge source) --file=temp/myfile will upload the file to temp folder "
            "in the GitLab package.",
        )
        parser.add_argument(
            "-s",
            "--source",
            type=str,
            default="",
            help="The source directory of the uploaded file(s). Defaults to current"
            "working directory.",
        )
        parser.set_defaults(action=self._upload)

    def _upload(self, args: argparse.Namespace) -> int:
        """
        Uploads a file to a GitLab package registry

        Parameters
        ----------
        args : argparse.Namespace
            The arguments from command line

        Returns
        -------
        int
            Zero if everything went fine, non-zero otherwise.
        """
        ret = 0
        host, project, name, token_user, token = self._args(args)
        version = args.version
        file = args.file
        source = args.source
        if file:
            # Check if the uploaded file exists.
            if not os.path.isfile(os.path.join(source, file)):
                print("File " + file + " does not exist!")
                ret = 1
        if not ret:
            gitlab = Packages(host, token_user, token)
            ret = gitlab.upload_file(project, name, version, file, source)
        return ret
