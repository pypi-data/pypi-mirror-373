from unittest.mock import MagicMock, patch

import pytest

from libdc3.services.bril.client import Brilcalc, BrilcalcError


@pytest.fixture
def fake_html_success():
    return """
    <html>
    <body>
    <table>
      <tr><th>run:fill</th><th>delivered(/ub)</th><th>recorded(/ub)</th></tr>
      <tr><td>123:456</td><td>1.0</td><td>0.9</td></tr>
    </table>
    <table>
      <tr><th>nfill</th><th>nrun</th><th>nls</th><th>ncms</th><th>totdelivered(/ub)</th><th>totrecorded(/ub)</th></tr>
      <tr><td>1</td><td>1</td><td>1</td><td>1</td><td>1.0</td><td>0.9</td></tr>
    </table>
    </body>
    </html>
    """


@pytest.fixture
def brilcalc_local():
    with patch("os.path.isdir", return_value=True):
        yield Brilcalc(keytab_usr=None, keytab_pwd=None)


@pytest.fixture
def brilcalc_remote():
    with patch("os.path.isdir", return_value=False):
        with patch.object(Brilcalc, "connect_ssh", return_value=MagicMock()):
            yield Brilcalc(keytab_usr="user", keytab_pwd="pwd")


def test_execute_locally_success(brilcalc_local):
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = [
            MagicMock(returncode=0),  # pip install
            MagicMock(returncode=0, stdout=b"html", stderr=b""),  # brilcalc
        ]
        rc, stdout, _ = brilcalc_local.execute_locally(["brilcalc", "lumi"])
        assert rc == 0
        assert stdout == "html"


def test_execute_locally_failure(brilcalc_local):
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = [
            MagicMock(returncode=0),  # pip install
            MagicMock(returncode=1, stdout=b"", stderr=b"fail"),  # brilcalc
        ]
        rc, _, stderr = brilcalc_local.execute_locally(["brilcalc", "lumi"])
        assert rc == 1
        assert stderr == "fail"


def test_execute_ssh_success(brilcalc_remote):
    mock_ssh = brilcalc_remote.ssh_client
    mock_stdout = MagicMock()
    mock_stdout.read.return_value = b"html"
    mock_stdout.channel.recv_exit_status.return_value = 0
    mock_stderr = MagicMock()
    mock_stderr.read.return_value = b""
    mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)
    rc, stdout, stderr = brilcalc_remote.execute_ssh(["brilcalc", "lumi"])
    assert rc == 0
    assert stdout == "html"


def test_execute_ssh_no_client(brilcalc_remote):
    brilcalc_remote.keytab_usr = None
    brilcalc_remote.keytab_pwd = None
    brilcalc_remote.ssh_client = None
    with pytest.raises(ValueError):
        brilcalc_remote.execute_ssh(["brilcalc", "lumi"])


def test_lumi_local_success(brilcalc_local, fake_html_success):
    with patch.object(brilcalc_local, "execute_locally", return_value=(0, fake_html_success, "")):
        result = brilcalc_local.lumi()
        assert "detailed" in result
        assert "summary" in result
        assert result["detailed"][0]["run"] == 123
        assert result["summary"]["nfill"] == 1


def test_lumi_local_failure(brilcalc_local):
    with patch.object(brilcalc_local, "execute_locally", return_value=(1, "", "error")):
        with pytest.raises(BrilcalcError):
            brilcalc_local.lumi()


def test_parse_lumi_html_byls():
    html = """
    <html>
    <body>
    <table>
      <tr><th>run:fill</th><th>ls</th><th>delivered(/ub)</th><th>recorded(/ub)</th><th>E(GeV)</th><th>avgpu</th></tr>
      <tr><td>123:456</td><td>1:2</td><td>1.0</td><td>0.9</td><td>6500</td><td>20.5</td></tr>
    </table>
    <table>
      <tr><th>nfill</th><th>nrun</th><th>nls</th><th>ncms</th><th>totdelivered(/ub)</th><th>totrecorded(/ub)</th></tr>
      <tr><td>1</td><td>1</td><td>1</td><td>1</td><td>1.0</td><td>0.9</td></tr>
    </table>
    </body>
    </html>
    """
    # We can access the method using Python's name-mangling pattern
    # This works because Python internally renames __parse_lumi_html to _Brilcalc__parse_lumi_html for encapsulation.
    result = Brilcalc._Brilcalc__parse_lumi_html(html, byls=True)
    assert result["detailed"][0]["ls_number"] == 1
    assert result["detailed"][0]["_ls_number"] == 2
    assert result["detailed"][0]["E(GeV)"] == 6500
    assert pytest.approx(result["detailed"][0]["avgpu"]) == 20.5


def test_swan_vars(brilcalc_local):
    with patch.dict("os.environ", {brilcalc_local.SWAN_KEY_IN_ENV: "/swan/opt/example/lib"}):
        with patch("libdc3.services.bril.client.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            brilcalc_local.execute_locally(["some", "bril", "command"])

            # Grab the env passed to subprocess.run
            called_env = mock_run.call_args[1]

            assert called_env["env"]["PYTHONHOME"] == brilcalc_local.BRILCONDA
            assert called_env["env"]["PYTHONPATH"] == brilcalc_local.BRILCONDA_PY27
