import os
import sys

from utils.exception import CustomException
from utils.logger import logging

from dataclasses import dataclass
from binance.client import Client


@dataclass
class DataIngestionConfig:
    pass
