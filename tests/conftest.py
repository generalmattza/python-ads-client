import pyads.testserver
import pytest
import time
import pyads

from ads_client import ADSTarget

PYADS_TESTSERVER_ADS_ADDRESS = "127.0.0.1.1.1"
PYADS_TESTSERVER_ADS_PORT = 48898
PYADS_TESTSERVER_VARIABLE_NAMES = [f"var{n}" for n in range(12)]
PYADS_TESTSERVER_TIMEOUT_MS = 1000


@pytest.fixture
def testserver_target():
    """Fixture to create an instance of the ADS client class."""
    target = ADSTarget(
        adsAddress=PYADS_TESTSERVER_ADS_ADDRESS, adsPort=PYADS_TESTSERVER_ADS_PORT
    )
    target.set_timeout(PYADS_TESTSERVER_TIMEOUT_MS)
    return target


@pytest.fixture(scope="session")
def testserver_advanced():

    try:
        pyads.add_route("127.0.0.1.1.1", "127.0.0.1")
    except (pyads.ADSError, RuntimeError):
        pass

    handler = pyads.testserver.AdvancedHandler()

    for var_name in PYADS_TESTSERVER_VARIABLE_NAMES:
        handler.add_variable(
            pyads.testserver.PLCVariable(
                var_name,
                bytes(8),
                ads_type=pyads.constants.ADST_REAL64,
                symbol_type="LREAL",
            )
        )

    pyads_testserver = pyads.testserver.AdsTestServer(handler)
    # Wait a bit to ensure the server has time to start
    time.sleep(0.5)

    # Yield control to the tests, then cleanup after tests
    with pyads_testserver:
        yield pyads_testserver
