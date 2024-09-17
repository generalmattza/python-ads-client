#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Matthew Davidson
# Created Date: 2023-01-23
# version ='1.0'
# ---------------------------------------------------------------------------
"""a_short_module_description"""
# ---------------------------------------------------------------------------

import asyncio
import sys
from typing import Union
from collections import deque
from pathlib import Path
import logging
import time

from ads_client import ADSConnection
from pyads import ADSError

logger = logging.getLogger(__name__)


def id_generator(prefix: str = "instance"):
    """Generator function to create unique IDs with a configurable prefix."""
    counter = 1
    while True:
        yield f"{prefix}-{counter}"
        counter += 1


class ADSClient:
    """ADSClient class to manage the connection to an ADS target device and read data from it."""

    client_id = id_generator(prefix="client")

    def __init__(
        self,
        buffer: Union[list, deque],
        name: str = None,
        ams_net_id=None,
        ip_address=None,
        ams_net_port=None,
        data_names=None,
        update_interval: int = 1,
        retry_attempts: int = 10,
    ):
        self.name = name or next(self.client_id)
        self._buffer = buffer
        self.target = ADSConnection(
            ams_net_id=ams_net_id, ip_address=ip_address, ams_net_port=ams_net_port
        )
        self.update_interval = update_interval
        self.data_names = data_names
        self.retry_attempts = retry_attempts

    async def do_work_periodically(self, *args, update_interval=None, **kwargs):
        update_interval = update_interval or self.update_interval
        while True:
            await self.do_work(args, kwargs)
            await asyncio.sleep(update_interval)

    async def do_work(self, *args, **kwargs):

        operation_successful = False
        retry_attempts = self.retry_attempts
        while not operation_successful and retry_attempts > 0:
            # Get data in form of dict to load to the buffer
            try:
                read_data = self.target.read_list_by_name(data_names=self.data_names)
                operation_successful = True
            except ADSError as e:
                retry_attempts -= 1
                logger.error(
                    f"Failed to read data from target. Retrying ... ({retry_attempts} remaining) {e}"
                )
                # await asyncio.sleep(1)
        else:
            if not operation_successful:
                logger.error(
                    f"Failed to read data from target after {self.retry_attempts} attempts. Exiting application."
                )
                sys.exit(1)

        # Add to input buffer
        if read_data:
            # Build metric
            processed_data = {}
            read_time = time.time()
            processed_data["time"] = read_time
            processed_data["measurement"] = self.name
            processed_data["tags"] = {"device": self.name}
            processed_data["fields"] = {"value": data["value"] for data in read_data}

            logger.info(f"Adding {len(processed_data)} metrics to queue")
            self._buffer.append(processed_data)
