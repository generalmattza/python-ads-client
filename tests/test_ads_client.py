import asyncio

from collections import deque
from config_loader import load_configs

from ads_client.ads_client import ADSClient


ADS_TARGETS_CONFIG = load_configs("config/ads_targets.yaml")


async def test_ads_clients():
    buffer = deque(maxlen=1_000)

    ads_clients = [
        ADSClient(buffer=buffer, name=name, **target)
        for name, target in ADS_TARGETS_CONFIG.items()
    ]

    await asyncio.gather(*[client.do_work_periodically() for client in ads_clients])


if __name__ == "__main__":
    asyncio.run(test_ads_clients())
