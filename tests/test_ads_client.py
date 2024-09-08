import pyads.testserver
from src.ads_client import ADSClient
import pyads
import logging


def test_ads_client(pyads_testserver):
    """Test the ADS client class."""

    with pyads_testserver:
        client = ADSClient(adsAddress="127.0.0.1.1.1", adsPort=48898)
        logging.info(client.connection)
        variables = (("var1", 1), ("var2", 2), ("var3", 3))
        client.writeVariables(variables)
        logging.info(client.connection)
        varNames = ["var1", "var2", "var3"]
        data = client.readVariables(["var1", "var2", "var3"])
        logging.info(client.connection)
        assert client.connection.open_events == 3
        assert client.connection.close_events == 3
