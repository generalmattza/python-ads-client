import subprocess
import pytest
import time
import pyads


@pytest.fixture(scope="session")
def pyads_testserver():
    # Start the pyads test server as a subprocess
    server_process = subprocess.Popen(
        ["python", "-m", "pyads.testserver", "--handler", "basic"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait a bit to ensure the server has time to start
    time.sleep(2)
    try:
        pyads.add_route("127.0.0.1.1.1", "127.0.0.1")
    except (pyads.ADSError, RuntimeError):
        pass

    # Yield control to the tests, then cleanup after tests
    yield server_process

    # Terminate the server process after the tests
    server_process.terminate()
    server_process.wait()
