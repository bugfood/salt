import pytest
import sys

import salt.utils.platform

pytestmark = [
    pytest.mark.slow_test,
    pytest.mark.skip_on_windows(reason="salt-ssh not available on Windows"),
]


@pytest.fixture(scope="module")
def salt_ssh_cli(salt_master, salt_ssh_roster_file, sshd_config_dir):
    """
    The ``salt-ssh`` CLI as a fixture against the running master
    """
    assert salt_master.is_running()
    print(salt_master, file=sys.stderr)
    cf = salt_master.config_file
    with open(cf) as fh:
        print(fh.read(), file=sys.stderr)

    return salt_master.salt_ssh_cli(
        timeout=180,
        roster_file=salt_ssh_roster_file,
        target_host="localhost",
        client_key=str(sshd_config_dir / "client_key"),
        base_script_args=["--ignore-host-keys"],
    )


def test_grains_id(salt_ssh_cli):
    """
    Test salt-ssh grains id work for localhost.
    """
    ret = salt_ssh_cli.run("grains.get", "id")
    assert ret.returncode == 0
    assert ret.data == "localhost"


def test_grains_items(salt_ssh_cli):
    """
    test grains.items with salt-ssh
    """
    ret = salt_ssh_cli.run("grains.items")
    assert ret.returncode == 0
    assert ret.data
    assert isinstance(ret.data, dict)
    if salt.utils.platform.is_darwin():
        grain = "Darwin"
    elif salt.utils.platform.is_aix():
        grain = "AIX"
    elif salt.utils.platform.is_freebsd():
        grain = "FreeBSD"
    else:
        grain = "Linux"
    assert ret.data["kernel"] == grain
