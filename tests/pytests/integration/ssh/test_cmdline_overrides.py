import pytest
import sys

pytestmark = [
    pytest.mark.slow_test,
    pytest.mark.skip_on_windows(reason="salt-ssh not available on Windows"),
]


# originally copied from tests/tests/pytests/integration/conftest.py
@pytest.fixture(scope="module")
def salt_ssh_cli(salt_master, salt_ssh_roster_file, sshd_config_dir):
    """
    The ``salt-ssh`` CLI as a fixture against the running master
    """
    assert salt_master.is_running()
    print(salt_master, file=sys.stderr)
    cf = salt_master.config_file
    with open(cf) as fh:
        print("---start config file---")
        print(fh.read(), file=sys.stderr)
        print("---end config file---")

    print("pki_dir:", salt_master.config.get("pki_dir", "None"))

    return salt_master.salt_ssh_cli(
        timeout=180,
        roster_file=salt_ssh_roster_file,
        target_host="localhost",
        client_key=str(sshd_config_dir / "client_key"),
        # setting the pki dir here has no effect
        base_script_args=["--ignore-host-keys", "--pki-dir", "/tmp/pki-base"],
    )
    print("pki_dir:", salt_master.config.get("pki_dir", "None"))


# don't know how to handle the scope specification
@pytest.fixture(scope="session")
def salt_master_extra_config_overrides():
    # can't do this--other code chokes if the option exists and is set to None.
    # return {"pki_dir": None}

    # set a temporary value for now and see if we can override it
    # So far, this value is respected and the attempted command-line overrides
    # do nothing.
    return {"pki_dir": "/tmp/pki-default"}


def test_experiment(salt_ssh_cli):
    ret = salt_ssh_cli.run(
        # setting the pki dir here has no effect
        "--pki-dir",
        "/tmp/pki-experiment",
        "grains.items",
    )
    assert ret.returncode == 0
