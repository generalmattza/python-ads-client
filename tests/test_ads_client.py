import asyncio

from collections import deque
import itertools
from config_loader import load_configs

from ads_client.ads_client import ADSClient


ADS_TARGETS_CONFIG = load_configs("config/ads_targets.yaml")

# sine wave geenrator
import math
import random

# generate sinusoidal wave values when next is called
# infinite generator
# returns integer values between -100 and 100


def sine_wave(amplitude=100, frequency=1, phase=0, offset=0, return_type=float):
    while True:
        for i in range(0, 360):
            yield return_type(
                amplitude * math.sin(math.radians(frequency * i + phase)) + offset
            )


def bool_wave(threshold=0.5, frequency=1):
    sine_wave_base = sine_wave(
        amplitude=1, frequency=frequency, phase=0, offset=0, return_type=float
    )
    while True:
        yield next(sine_wave_base) > threshold


class ADSClientWriter(ADSClient):
    """ADSClient class to manage the connection to an ADS target device and write data to it."""

    sine_wave_1 = sine_wave(return_type=int)
    sine_wave_2 = sine_wave(return_type=int, phase=90, frequency=2)
    sine_wave_3 = sine_wave(return_type=int, phase=180, frequency=3)
    sine_wave_4 = sine_wave(return_type=int, phase=270, frequency=4)
    bool_wave_1 = bool_wave()
    bool_wave_2 = bool_wave(frequency=3)
    generators = {
        "MAIN.nVar1": sine_wave_1,
        "MAIN.nVar2": sine_wave_2,
        "MAIN.nVar3": sine_wave_3,
        "MAIN.nVar4": sine_wave_4,
        "MAIN.bool1": bool_wave_1,
        "MAIN.bool2": bool_wave_2,
    }

    async def do_work(self, *args, **kwargs):
        data = {
            data_name: next(self.generators[data_name]) for data_name in self.data_names
        }
        try:
            self.target.write_list_by_name(data)
        except Exception as e:
            pass


async def test_ads_clients_read():
    buffer = deque(maxlen=1_000)

    ads_clients = [
        ADSClient(buffer=buffer, name=name, **target, retain_connection=False)
        for name, target in ADS_TARGETS_CONFIG.items()
    ]

    await asyncio.gather(
        *[client.do_work_periodically(update_interval=0.5) for client in ads_clients]
    )


async def test_ads_clients_write():
    buffer = deque(maxlen=1_000)

    ads_clients = [
        ADSClientWriter(buffer=buffer, name=name, **target, retain_connection=True)
        for name, target in ADS_TARGETS_CONFIG.items()
    ]

    await asyncio.gather(*[client.do_work_periodically() for client in ads_clients])


if __name__ == "__main__":
    # asyncio.run(test_ads_clients_read())
    asyncio.run(test_ads_clients_write())
