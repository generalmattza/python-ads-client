import subprocess
import pyads.testserver
import pytest
import time
import pyads


@pytest.fixture(scope="session")
def pyads_testserver():
    handler = pyads.testserver.AdvancedHandler()
    handler.add_variable(
        pyads.testserver.PLCVariable(
            "var1", bytes(8), ads_type=pyads.constants.ADST_REAL64, symbol_type="LREAL"
        )
    )
    handler.add_variable(
        pyads.testserver.PLCVariable(
            "var2", bytes(8), ads_type=pyads.constants.ADST_REAL64, symbol_type="LREAL"
        )
    )
    handler.add_variable(
        pyads.testserver.PLCVariable(
            "var3", bytes(8), ads_type=pyads.constants.ADST_REAL64, symbol_type="LREAL"
        )
    )

    pyads_testserver = pyads.testserver.AdsTestServer(handler)

    # Wait a bit to ensure the server has time to start
    time.sleep(1)
    try:
        pyads.add_route("127.0.0.1.1.1", "127.0.0.1")
    except (pyads.ADSError, RuntimeError):
        pass
    # Yield control to the tests, then cleanup after tests
    yield pyads_testserver
