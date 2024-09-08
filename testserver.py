import pyads.testserver
from src.ads_client import ADSTarget
import pyads
import time


def start_testserver():
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
    pyads_testserver = pyads.testserver.AdsTestServer(handler)
    with pyads_testserver:
        while True:
            time.sleep(1)


if __name__ == "__main__":
    start_testserver()
