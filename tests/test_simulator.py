import os
import shutil

import pytest
from click.testing import CliRunner

from iotedgedev.compat import PY35

pytestmark = pytest.mark.e2e

root_dir = os.getcwd()
tests_dir = os.path.join(root_dir, 'tests')
env_file = os.path.join(root_dir, '.env')
test_solution = 'test_solution'
test_solution_dir = os.path.join(tests_dir, test_solution)


@pytest.fixture(scope="module", autouse=True)
def create_solution(request):
    cli = __import__('iotedgedev.cli', fromlist=['main'])

    runner = CliRunner()
    os.chdir(tests_dir)
    result = runner.invoke(cli.main, ['solution', 'create', test_solution])
    print(result.output)

    assert 'AZURE IOT EDGE SOLUTION CREATED' in result.output

    shutil.copyfile(env_file, os.path.join(test_solution_dir, '.env'))
    os.chdir(test_solution_dir)

    def clean():
        os.chdir(root_dir)
        shutil.rmtree(test_solution_dir, ignore_errors=True)
        runner.invoke(cli.main, ['simulator', 'stop'])

    request.addfinalizer(clean)

    return


def test_setup():
    cli = __import__('iotedgedev.cli', fromlist=['main'])
    runner = CliRunner()

    result = runner.invoke(cli.main, ['simulator', 'setup'])
    print(result.output)

    assert 'Setup IoT Edge Simulator successfully.' in result.output


def test_start_single():
    cli = __import__('iotedgedev.cli', fromlist=['main'])
    runner = CliRunner()

    result = runner.invoke(cli.main, ['simulator', 'start', '-i', 'setup'])
    print(result.output)

    assert 'IoT Edge Simulator has been started in single module mode.' in result.output


def test_modulecred():
    cli = __import__('iotedgedev.cli', fromlist=['main'])
    runner = CliRunner()

    result = runner.invoke(cli.main, ['simulator', 'modulecred'])
    print(result.output)

    assert 'EdgeHubConnectionString=HostName=' in result.output
    assert 'EdgeModuleCACertificateFile=' in result.output


def test_stop(capfd):
    cli = __import__('iotedgedev.cli', fromlist=['main'])
    runner = CliRunner()

    result = runner.invoke(cli.main, ['simulator', 'stop'])
    print(result.output)
    out, err = capfd.readouterr()
    print(out)
    print(err)

    assert 'IoT Edge Simulator has been stopped successfully.' in out


def test_start_solution(capfd):
    cli = __import__('iotedgedev.cli', fromlist=['main'])
    runner = CliRunner()

    result = runner.invoke(cli.main, ['simulator', 'start', '-s', '-b'])
    print(result.output)
    out, err = capfd.readouterr()
    print(out)
    print(err)

    assert 'BUILD COMPLETE' in result.output
    assert 'IoT Edge Simulator has been started in solution mode.' in out


def test_monitor(capfd):
    cli = __import__('iotedgedev.cli', fromlist=['main'])
    runner = CliRunner()
    result = runner.invoke(cli.main, ['monitor', '--timeout', '5'])
    out, err = capfd.readouterr()
    print(out)
    print(err)
    print(result.output)

    if PY35:
        assert 'Starting event monitor' in out
    else:
        assert 'Monitoring events from device' in out
    assert 'timeCreated' in out
