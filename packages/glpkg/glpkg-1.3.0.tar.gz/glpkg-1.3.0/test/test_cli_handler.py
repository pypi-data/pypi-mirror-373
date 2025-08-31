from unittest.mock import patch

import urllib

from gitlab import __version__
from gitlab.cli_handler import CLIHandler
import sys

from utils import mock_empty_response, mock_one_response


class TestCliHandler:

    def test_version(self, capsys):
        args = ["glpkg", "-v"]
        with patch.object(sys, "argv", args):
            handler = CLIHandler()
            handler.do_it()
            out, err = capsys.readouterr()
            assert out == __version__ + "\n"
            assert err == ""

    def test_list_empty(self, mock_empty_response, capsys):
        args = ["glpkg", "list", "--project", "18105942", "--name", "AABCComponent"]
        with patch.object(sys, "argv", args):
            with patch.object(
                urllib.request, "urlopen", return_value=mock_empty_response
            ):
                handler = CLIHandler()
                handler.do_it()
                out, err = capsys.readouterr()
                assert out == "Name\t\tVersion\n"
                assert err == ""

    def test_list_one(self, mock_one_response, capsys):
        args = ["glpkg", "list", "--project", "18105942", "--name", "ABCComponent"]
        with patch.object(sys, "argv", args):
            with patch.object(
                urllib.request, "urlopen", return_value=mock_one_response
            ):
                handler = CLIHandler()
                handler.do_it()
                out, err = capsys.readouterr()
                assert out == "Name\t\tVersion\nABCComponent\t0.0.1\n"
                assert err == ""
