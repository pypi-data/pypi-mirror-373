from pathlib import Path
from unittest.mock import patch

import pytest
import typer
from typer.testing import CliRunner

from planar.cli import app, find_default_app_path, get_module_str_from_path


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def mock_uvicorn_run():
    with patch("planar.cli.uvicorn.run") as mock_run:
        yield mock_run


@pytest.fixture
def mock_path_exists():
    with patch("pathlib.Path.exists", return_value=True) as mock_exists:
        yield mock_exists


@pytest.fixture
def mock_path_is_file():
    with patch("pathlib.Path.is_file", return_value=True) as mock_is_file:
        yield mock_is_file


class TestDevCommand:
    def test_dev_command_defaults(
        self, cli_runner, mock_uvicorn_run, mock_path_is_file
    ):
        """Test that 'planar dev' sets correct defaults and invokes uvicorn.run."""
        env = {}
        with patch("os.environ", env):
            result = cli_runner.invoke(app, ["dev"])

        assert result.exit_code == 0
        mock_uvicorn_run.assert_called_once()

        # Verify uvicorn.run arguments
        call_args = mock_uvicorn_run.call_args
        assert call_args[0][0] == "app:app"
        assert call_args.kwargs["reload"] is True
        assert call_args.kwargs["host"] == "127.0.0.1"
        assert call_args.kwargs["port"] == 8000
        assert call_args.kwargs["timeout_graceful_shutdown"] == 4

        # Verify environment variable
        assert env["PLANAR_ENV"] == "dev"


class TestProdCommand:
    def test_prod_command_defaults(
        self, cli_runner, mock_uvicorn_run, mock_path_is_file
    ):
        """Test that 'planar prod' sets correct defaults and invokes uvicorn.run."""
        env = {}
        with patch("os.environ", env):
            result = cli_runner.invoke(app, ["prod"])

        assert result.exit_code == 0
        mock_uvicorn_run.assert_called_once()

        # Verify uvicorn.run arguments
        call_args = mock_uvicorn_run.call_args
        assert call_args[0][0] == "app:app"
        assert call_args.kwargs["reload"] is False
        assert call_args.kwargs["host"] == "0.0.0.0"
        assert call_args.kwargs["port"] == 8000
        assert call_args.kwargs["timeout_graceful_shutdown"] == 4

        # Verify environment variable
        assert env["PLANAR_ENV"] == "prod"


class TestArgumentParsing:
    @pytest.mark.parametrize("command", ["dev", "prod"])
    def test_custom_port(
        self, cli_runner, mock_uvicorn_run, mock_path_is_file, command
    ):
        """Test custom port settings for both dev and prod commands."""
        port = "9999"
        with patch("os.environ", {}):
            result = cli_runner.invoke(app, [command, "--port", port])

        assert result.exit_code == 0
        mock_uvicorn_run.assert_called_once()

        # Verify config arguments
        call_args = mock_uvicorn_run.call_args
        assert call_args.kwargs["port"] == int(port)

    @pytest.mark.parametrize("command", ["dev", "prod"])
    def test_custom_host(
        self, cli_runner, mock_uvicorn_run, mock_path_is_file, command
    ):
        """Test custom host settings."""
        host = "0.0.0.0"
        with patch("os.environ", {}):
            result = cli_runner.invoke(app, [command, "--host", host])

        assert result.exit_code == 0
        mock_uvicorn_run.assert_called_once()

        # Verify config arguments
        call_args = mock_uvicorn_run.call_args
        assert call_args.kwargs["host"] == host

    @pytest.mark.parametrize("command", ["dev", "prod"])
    def test_custom_app_name(
        self, cli_runner, mock_uvicorn_run, mock_path_is_file, command
    ):
        """Test custom app instance name."""
        with (
            patch("os.environ", {}),
            patch("planar.cli.get_module_str_from_path", return_value="app"),
        ):
            result = cli_runner.invoke(app, [command, "--app", "server"])

        assert result.exit_code == 0
        mock_uvicorn_run.assert_called_once()

        # Verify config arguments
        call_args = mock_uvicorn_run.call_args
        assert call_args[0][0] == "app:server"

    @pytest.mark.parametrize("command", ["dev", "prod"])
    def test_custom_path(
        self, cli_runner, mock_uvicorn_run, mock_path_is_file, command
    ):
        """Test custom application path."""
        path = "custom/app.py"
        with (
            patch("os.environ", {}),
            patch("planar.cli.get_module_str_from_path", return_value="custom.app"),
        ):
            result = cli_runner.invoke(app, [command, path])

        assert result.exit_code == 0
        mock_uvicorn_run.assert_called_once()

        # Verify config arguments
        call_args = mock_uvicorn_run.call_args
        assert call_args[0][0] == "custom.app:app"

    @pytest.mark.parametrize("command", ["dev", "prod"])
    def test_invalid_path(self, cli_runner, mock_uvicorn_run, command):
        """Test handling of invalid path."""
        with patch("pathlib.Path.is_file", return_value=False):
            result = cli_runner.invoke(app, [command, "nonexistent/app.py"])

        assert result.exit_code == 1
        assert "not found" in result.output
        mock_uvicorn_run.assert_not_called()


class TestAppPathResolution:
    @pytest.mark.parametrize("command", ["dev", "prod"])
    def test_explicit_path(
        self, cli_runner, mock_uvicorn_run, mock_path_is_file, command
    ):
        """Test command --path sets PLANAR_ENTRY_POINT and generates correct import string."""
        env = {}
        with (
            patch("os.environ", env),
            patch("planar.cli.get_module_str_from_path", return_value="path.to.app"),
        ):
            result = cli_runner.invoke(app, [command, "path/to/app.py"])

        assert result.exit_code == 0
        assert env["PLANAR_ENTRY_POINT"] == "path/to/app.py"
        mock_uvicorn_run.assert_called_once()

        # Verify config arguments
        call_args = mock_uvicorn_run.call_args
        assert call_args[0][0] == "path.to.app:app"

    @pytest.mark.parametrize(
        "path,error_text",
        [
            ("non_existent/app.py", "not found or is not a file"),
            ("directory/", "not found or is not a file"),
        ],
    )
    def test_invalid_paths(self, cli_runner, path, error_text):
        """Test invalid paths exit with error."""
        with patch("pathlib.Path.is_file", return_value=False):
            result = cli_runner.invoke(app, ["dev", path])

        assert result.exit_code == 1
        assert error_text in result.output


class TestDefaultPathDiscovery:
    @pytest.mark.parametrize(
        "file_exists,expected_path",
        [
            (lambda p: p.name == "app.py", Path("app.py")),
            (lambda p: p.name == "main.py", Path("main.py")),
        ],
    )
    def test_default_files(
        self, cli_runner, mock_uvicorn_run, file_exists, expected_path
    ):
        """Test default file discovery works for app.py and main.py."""
        env = {}
        expected_name = expected_path.stem
        with (
            patch("os.environ", env),
            patch("pathlib.Path.is_file", file_exists),
            patch("planar.cli.get_module_str_from_path", return_value=expected_name),
        ):
            result = cli_runner.invoke(app, ["dev"])

        assert result.exit_code == 0
        assert env["PLANAR_ENTRY_POINT"] == str(expected_path)
        mock_uvicorn_run.assert_called_once()

    def test_no_default_files(self, cli_runner):
        """Test with neither app.py nor main.py existing: Verify exit code 1 and error message."""
        with patch("pathlib.Path.is_file", return_value=False):
            result = cli_runner.invoke(app, ["dev"])

        assert result.exit_code == 1
        assert "Could not find app.py or main.py" in result.output


class TestModuleStringConversion:
    @pytest.mark.parametrize(
        "path,expected",
        [
            (Path("app.py"), "app"),
            (Path("src/api/main.py"), "src.api.main"),
        ],
    )
    def test_valid_paths(self, path, expected):
        """Test module string conversion for valid paths."""
        abs_path = Path.cwd() / path
        with (
            patch("pathlib.Path.resolve", return_value=abs_path),
            patch("pathlib.Path.relative_to", return_value=path),
        ):
            result = get_module_str_from_path(path)

        assert result == expected

    def test_outside_cwd(self):
        """Test conversion for a path outside CWD results in exit code 1 and error."""
        path = Path("/tmp/app.py")
        with (
            patch("pathlib.Path.resolve", return_value=Path("/tmp/app.py")),
            patch("pathlib.Path.relative_to", side_effect=ValueError("Not relative")),
        ):
            with pytest.raises(typer.Exit) as exc_info:
                get_module_str_from_path(path)

        assert exc_info.value.exit_code == 1


class TestConfigFileHandling:
    def test_config_handling(self, cli_runner, mock_uvicorn_run, mock_path_is_file):
        """Test config file handling."""
        env = {}
        with patch("os.environ", env):
            with patch("pathlib.Path.exists", return_value=True):
                result = cli_runner.invoke(
                    app, ["dev", "--config", "valid/config.yaml"]
                )

        assert result.exit_code == 0
        assert env["PLANAR_CONFIG"] == "valid/config.yaml"
        mock_uvicorn_run.assert_called_once()

        # Test invalid config
        with patch("pathlib.Path.exists", return_value=False):
            result = cli_runner.invoke(app, ["dev", "--config", "invalid/config.yaml"])

        assert result.exit_code == 1
        assert "Config file invalid/config.yaml not found" in result.output


class TestUvicornInteraction:
    def test_successful_run(self, cli_runner, mock_uvicorn_run, mock_path_is_file):
        """Test successful uvicorn.run with correct parameters."""
        with (
            patch("os.environ", {}),
            patch("planar.cli.get_module_str_from_path", return_value="src.main"),
        ):
            result = cli_runner.invoke(app, ["dev", "src/main.py"])

        assert result.exit_code == 0
        mock_uvicorn_run.assert_called_once()

        # Verify config arguments
        call_args = mock_uvicorn_run.call_args
        assert call_args[0][0] == "src.main:app"
        assert call_args.kwargs["host"] == "127.0.0.1"
        assert call_args.kwargs["port"] == 8000
        assert call_args.kwargs["reload"] is True


class TestScaffoldCommand:
    def test_scaffold_creates_project_structure(self, cli_runner, tmp_path):
        """Test that scaffold command creates the correct directory structure and files."""
        project_name = "test_project"

        result = cli_runner.invoke(
            app, ["scaffold", "--name", project_name, "--directory", str(tmp_path)]
        )

        assert result.exit_code == 0
        assert "created successfully" in result.output

        # Check project directory exists
        project_dir = tmp_path / project_name
        assert project_dir.exists()
        assert project_dir.is_dir()

        # Check directory structure
        assert (project_dir / "app").exists()
        assert (project_dir / "app" / "db").exists()
        assert (project_dir / "app" / "flows").exists()

        # Check expected files exist
        expected_files = [
            "app/__init__.py",
            "app/db/entities.py",
            "app/flows/process_invoice.py",
            "main.py",
            "pyproject.toml",
            "planar.dev.yaml",
            "planar.prod.yaml",
        ]

        for file_path in expected_files:
            assert (project_dir / file_path).exists(), f"File {file_path} should exist"
            assert (project_dir / file_path).is_file(), f"{file_path} should be a file"

    def test_scaffold_fails_if_directory_exists(self, cli_runner, tmp_path):
        """Test that scaffold command fails if target directory already exists."""
        project_name = "existing_project"
        existing_dir = tmp_path / project_name
        existing_dir.mkdir()

        result = cli_runner.invoke(
            app, ["scaffold", "--name", project_name, "--directory", str(tmp_path)]
        )

        assert result.exit_code == 1
        assert "already exists" in result.output

    def test_scaffold_with_default_directory(self, cli_runner, tmp_path, monkeypatch):
        """Test scaffold command with default directory (current directory)."""
        project_name = "test_project"

        # Change to tmp_path to test default directory behavior
        monkeypatch.chdir(tmp_path)

        result = cli_runner.invoke(app, ["scaffold", "--name", project_name])

        assert result.exit_code == 0

        # Check project directory exists in current directory
        project_dir = tmp_path / project_name
        assert project_dir.exists()
        assert (project_dir / "main.py").exists()


class TestUtilityFunctions:
    @pytest.mark.parametrize(
        "file_exists,expected",
        [
            (lambda p: p.name == "app.py", Path("app.py")),
            (lambda p: p.name == "main.py", Path("main.py")),
        ],
    )
    def test_find_default_app_path(self, file_exists, expected):
        """Test find_default_app_path function."""
        with patch("pathlib.Path.is_file", file_exists):
            path = find_default_app_path()
        assert path == expected

    def test_find_default_app_path_no_files(self):
        """Test find_default_app_path raises typer.Exit when no default files exist."""
        with patch("pathlib.Path.is_file", return_value=False):
            with pytest.raises(typer.Exit) as exc_info:
                find_default_app_path()
        assert exc_info.value.exit_code == 1
