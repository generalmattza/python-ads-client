from src.ads_client import ADSClient


def test_ads_client(pyads_testserver):
    """Test the ADS client class."""
    client = ADSClient(adsAddress="127.0.0.1.1.1", adsPort=48898)
    client.openConnection()
    assert client.adsTarget.is_open
    data = client.readVariables(["var1", "var2"])
    print(data)
