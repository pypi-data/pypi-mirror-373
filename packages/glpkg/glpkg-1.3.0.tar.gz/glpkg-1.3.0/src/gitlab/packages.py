"""GitLab generic packages module"""

from glob import glob
from http.client import HTTPMessage
from json import loads
import logging
import os
from urllib import request, parse

logger = logging.getLogger(__name__)


class Packages:
    """Class to interact with GitLab packages REST API"""

    def __init__(self, host: str, token_type: str, token: str):
        """
        Creates a new instance of Packages class.

        Parameters
        ----------
        host : str
            The GitLab instance hostname, without schema.
            The host will be used for the package API interaction.
            For example gitlab.com.
        token_type : str
            The token type or "user" to authenticate with GitLab REST API.
            For personal, project, and group tokens this is `PRIVATE-TOKEN`.
            For `CI_JOB_TOKEN` this is `JOB-TOKEN`.
            Can be left empty when authentication is not used.
        token : str
            The token (secret) to authenticate with GitLab REST API.
            This can be a personal token, project token, or`CI_JOB_TOKEN`.
            Leave empty when authentication is not used.
        """
        self.host = host
        self.token_type = token_type
        self.token = token

    def api_url(self) -> str:
        """
        Returns the GitLab REST API URL by using the host variable.

        Returns
        -------
        str
            The GitLab REST API URL, for example `https://gitlab.com/api/v4/`.
        """
        return f"https://{self.host}/api/v4/"

    def project_api_url(self, project: str) -> str:
        """
        Returns the project REST API URL of the project

        Parameters
        ----------
        project : str
            The project ID or the path of the project, including namespace.
            Examples: `123` or `namespace/project`.

        Returns
        -------
        str
            The project REST API URL, for example `https://gitlab.com/api/v4/projects/123/`
            or `https://gitlab.com/api/v4/projects/namespace%2Fproject/`
        """
        return f"{self.api_url()}projects/{parse.quote_plus(project)}/"

    def get_headers(self) -> dict:
        """
        Creates headers for a GitLab REST API call.

        The headers contain token for authentication according to the
        instance variables.

        Returns
        -------
        dict
            Headers for a REST API request, that contain the authentication token.
        """
        headers = {}
        if self.token_type and self.token:
            headers = {self.token_type: self.token}
        return headers

    def _request(self, url: str) -> tuple[int, bytes, HTTPMessage]:
        """
        Makes a HTTP request to the given URL, and returns
        the response status, body, and headers.


        Parameters
        ----------
        url : str
            The URL of the HTTP request to make.

        Returns
        -------
        int
            The HTTP response code, such as 200
        bytes
            The HTTP response body read as bytes
        HTTPMessage
            The HTTP response headers
        """
        logger.debug("Requesting %s", url)
        req = request.Request(url, headers=self.get_headers())
        with request.urlopen(req) as response:
            return response.status, response.read(), response.headers

    def _get_next_page(self, headers: HTTPMessage) -> int:
        """
        Returns the next page from headers for pagination.

        Uses the field x-next-page from the headers.

        Parameters
        ----------
        headers : HTTPMessage
            The header from which to get the next page number for
            pagination

        Returns
        -------
        int
            The next page number. If headers were empty or they
            did not include suitable item, returns 0. In such
            case, do not attempt to fetch a next page.
        """
        ret = 0
        if headers:
            next_page = headers.get("x-next-page")
            if next_page:
                ret = int(next_page)
                logger.debug("Response incomplete, next page is %s", next_page)
            else:
                logger.debug("Response complete")
        return ret

    def _build_query(self, arg: str, page: int) -> str:
        """
        Builds a query for a GitLab REST API request

        Parameters
        ----------
        arg : str
            The args of the query that is endpoint specific
        page : int
            Page number for the pagination of the request.
            Set to 0 to omit the pagination.

        Returns
        -------
        str
            A query string for a REST API request. Append this to
            the request URL. Example `?arg=this&page=3`.
        """
        query = ""
        if arg or page:
            if page:
                page = "page=" + str(page)
            query = f"?{'&'.join(filter(None, (arg, page)))}"
        return query

    def gl_project_api(self, project: str, apath: str, arg: str = None) -> list:
        """
        Returns data from the project REST API for the path. In case
        of multiple pages, all data will be returned.

        Parameters
        ----------
        project : str
            The project ID or the path of the project, including namespace.
            Examples: `123` or `namespace/project`.
        apath : str
            The path of the project API endpoint that is called. For example packages
        arg : str, optional
            Additional arguments for the query of the URL, for example to filter
            results: package_name=mypackage

        Returns
        -------
        list
            Data from GitLab REST API endpoint with the arguments.
        """
        data = []
        more = True
        page = None
        while more:
            more = False
            query = self._build_query(arg, page)
            url = self.project_api_url(project) + apath + query
            status, res_data, headers = self._request(url)
            logger.debug("Response status: %d", status)
            res_data = loads(res_data)
            logger.debug("Response data: %s", res_data)
            data = data + res_data
            page = self._get_next_page(headers)
            if page:
                more = True
        return data

    def list_packages(self, project: str, package_name: str) -> list:
        """
        Lists the available versions of the package

        Parameters
        ----------
        project : str
            The project ID or the path of the project, including namespace.
            Examples: `123` or `namespace/project`.
        package_name : str
            The name of the package that is listed.

        Returns
        -------
        list
            List of {package: name, version: version} that are available.
        """
        packages = []
        logger.debug("Listing packages with name %s", package_name)
        data = self.gl_project_api(
            project, "packages", "package_name=" + parse.quote_plus(package_name)
        )
        for package in data:
            name = parse.unquote(package["name"])
            version = parse.unquote(package["version"])
            # GitLab API returns packages that have some match to the filter;
            # let's filter out non-exact matches
            if package_name != name:
                continue
            packages.append({"name": name, "version": version})
        return packages

    def list_files(self, project: str, package_id: int) -> list:
        """
        Lists all files of a specific package ID from GitLab REST API

        Parameters
        ----------
        project : str
            The project ID or the path of the project, including namespace.
            Examples: `123` or `namespace/project`.
        package_id : int
            The package ID that is listed

        Return
        ------
        list
            List of file (names) that are in the package.
        """
        files = []
        logger.debug("Listing package %d files", package_id)
        apath = "packages/" + parse.quote_plus(str(package_id)) + "/package_files"
        data = self.gl_project_api(project, apath)
        for package in data:
            # Only append the filename once to the list of files
            # as there's no way to download them separately through
            # the API
            filename = parse.unquote(package["file_name"])
            if filename not in files:
                files.append(filename)
        return files

    def get_package_id(
        self, project: str, package_name: str, package_version: str
    ) -> int:
        """
        Gets the package ID of a specific package version.

        Parameters
        ----------
        project : str
            The project ID or the path of the project, including namespace.
            Examples: `123` or `namespace/project`.
        package_name : str
            The name of the package.
        package_version : str
            The version of the package

        Return
        ------
        int
            The ID of the package. Zero if no ID was found.
        """
        package_id = 0
        logger.debug("Fetching package %s (%s) ID", package_name, package_version)
        apath = "packages"
        arg = (
            "package_name="
            + parse.quote_plus(package_name)
            + "&package_version="
            + parse.quote_plus(package_version)
        )
        data = self.gl_project_api(project, apath, arg)
        if len(data) == 1:
            package = data.pop()
            package_id = package["id"]
        return package_id

    def download_file(
        self,
        project: str,
        package_name: str,
        package_version: str,
        filename: str,
        destination: str = "",
    ) -> int:
        """
        Downloads a file from a GitLab generic package

        Parameters
        ----------
        project : str
            The project ID or the path of the project, including namespace.
            Examples: `123` or `namespace/project`.
        package_name : str
            The name of the generic package.
        package_version : str
            The version of the generic package
        filename : str
            The file that is downloaded
        destination : str, optional
            The destination folder of the downloaded file. If not set,
            current working directory is used.

        Return
        ------
        int
            Zero if everything went fine, non-zero coke otherwise.
        """
        ret = 1
        logger.debug("Downloading file %s", filename)
        url = (
            self.project_api_url(project)
            + "packages/generic/"
            + parse.quote_plus(package_name)
            + "/"
            + parse.quote_plus(package_version)
            + "/"
            + parse.quote(filename)
        )
        status, data, _ = self._request(url)
        if status == 200:
            fpath = os.path.join(destination, filename)
            parent = os.path.dirname(fpath)
            if parent:
                # Create missing directories if needed
                # In case path has no parent, current
                # workind directory is used
                os.makedirs(os.path.dirname(fpath), exist_ok=True)
            with open(fpath, "wb") as file:
                file.write(data)
                ret = 0
        return ret

    def upload_file(
        self,
        project: str,
        package_name: str,
        package_version: str,
        pfile: str,
        source: str,
    ) -> int:
        """
        Uploads file(s) to a GitLab generic package.

        Parameters
        ----------
        project : str
            The project ID or the path of the project, including namespace.
            Examples: `123` or `namespace/project`.
        package_name : str
            The name of the generic package.
        package_version : str
            The version of the generic package
        file : str
            The relative path of the file that is uploaded. If left empty,
            all files from the source folder, and it's subfolders, are uploaded.
        source : str
            The source folder that is used as root when uploading. If empty,
            current working directory is used.

        Return
        ------
        int
            Zero if everything went fine, non-zero coke otherwise.
        """
        files = []
        ret = 1
        if pfile:
            files.append(pfile)
        else:
            filelist = glob(os.path.join(source, "**"), recursive=True)
            for item in filelist:
                # Only add files, not folders
                if os.path.isfile(os.path.join(item)):
                    # Remove the source folder from the path of the files
                    files.append(os.path.relpath(item, source))
        for ufile in files:
            ret = self._upload_file(
                project, package_name, package_version, ufile, source
            )
            if ret:
                break
        return ret

    def _upload_file(
        self,
        project: str,
        package_name: str,
        package_version: str,
        pfile: str,
        source: str,
    ) -> int:
        """
        Uploads a file to a GitLab generic package.

        Parameters
        ----------
        project : str
            The project ID or the path of the project, including namespace.
            Examples: `123` or `namespace/project`.
        package_name : str
            The name of the generic package.
        package_version : str
            The version of the generic package
        file : str
            The relative path of the file that is uploaded.
        source : str
            The source folder that is used as root when uploading.

        Return
        ------
        int
            Zero if everything went fine, non-zero coke otherwise.
        """
        ret = 1
        fpath = os.path.join(source, pfile)
        logger.debug("Uploading file %s from %s", pfile, source)
        with open(fpath, "rb") as data:
            url = (
                self.project_api_url(project)
                + "packages/generic/"
                + parse.quote_plus(package_name)
                + "/"
                + parse.quote_plus(package_version)
                + "/"
                + parse.quote(pfile)
            )
            req = request.Request(
                url, method="PUT", data=data, headers=self.get_headers()
            )
            with request.urlopen(req) as res:
                if res.status == 201:  # 201 is created
                    ret = 0
        return ret
