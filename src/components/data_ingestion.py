import os
import sys

from utils.exception import CustomException
from utils.logger import get_logger

from dataclasses import dataclass
from binance.client import Client

from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
import pandas as pd


@dataclass
class BinanceConfig:
    api_key: str
    api_secret: str


@dataclass
class FileConfig:
    base_path: str


@dataclass
class TaskConfig:
    name: str                    # Name of the task
    source: str                  # Source name (e.g., binance, file)
    params: Dict[str, Any]       # Parameters to fetch data


@dataclass
class DataIngestionConfig:
    binance: Optional[BinanceConfig] = None
    # file: Optional[FileConfig] = None
    tasks: List[TaskConfig] = None



class BaseDataSource(ABC):
    """
    Abstract base class for data sources.
    """
    @abstractmethod
    def fetch_data(self, **kwargs) -> pd.DataFrame:
        pass


class BinanceDataSource(BaseDataSource):
    def __init__(self, api_key: str, api_secret: str):
        from binance.client import Client
        self.client = Client(api_key=api_key, api_secret=api_secret)

    def fetch_data(self, symbols: list, interval: str, start_time: str, end_time: str = None) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical data for multiple symbols from Binance.

        Args:
            symbols (list): List of symbols to fetch data for.
            interval (str): Time interval (e.g., 1m, 1h, 1d).
            start_time (str): Start date for historical data.
            end_time (str): End date for historical data (optional).

        Returns:
            Dict[str, pd.DataFrame]: A dictionary of DataFrames, keyed by symbol.
        """
        data = {}
        for symbol in symbols:
            klines = self.client.get_historical_klines(symbol, interval, start_time, end_time)
            df = pd.DataFrame(
                klines,
                columns=[
                    "timestamp", "open", "high", "low", "close", "volume",
                    "close_time", "quote_asset_volume", "number_of_trades",
                    "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
                ]
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            data[symbol] = df
        return data

    

class DataIngestion:
    def __init__(self, config: DataIngestionConfig, data_sources: Dict[str, BaseDataSource], logger=None):
        self.config = config
        self.data_sources = data_sources
        self.logger = logger or get_logger("DataIngestion")

    def fetch_from_source(self, source_name: str, **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Fetch data from a specific data source for multiple symbols.

        Args:
            source_name (str): Name of the data source.
            kwargs: Parameters for fetching data.

        Returns:
            Dict[str, pd.DataFrame]: A dictionary of DataFrames, keyed by symbol.
        """
        if source_name not in self.data_sources:
            raise ValueError(f"Unknown data source: {source_name}")
        self.logger.info(f"Fetching data from {source_name} with parameters: {kwargs}")
        return self.data_sources[source_name].fetch_data(**kwargs)

    def run(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Run all tasks and fetch data for multiple symbols.

        Returns:
            Dict[str, Dict[str, pd.DataFrame]]: A dictionary of tasks, each containing a dictionary of DataFrames keyed by symbol.
        """
        all_data = {}
        for task in self.config.tasks.tasks:
            source_name = task.source
            params = task.params
            self.logger.info(f"Running task: {task.name}")
            try:
                task_data = self.fetch_from_source(source_name, **params)
                all_data[task.name] = task_data
                self.logger.info(f"Task {task.name} completed successfully.")
            except Exception as e:
                self.logger.error(f"Task {task.name} failed: {e}")
        return all_data
