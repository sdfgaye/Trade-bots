import os
from dotenv import load_dotenv
import hydra
from omegaconf import DictConfig
from src.components.data_ingestion import DataIngestion, DataIngestionConfig, BinanceDataSource
from utils.logger import get_logger

# Load environment variables from .env file
load_dotenv()

@hydra.main(version_base="1.2", config_path="../config", config_name="config")
def main(cfg: DictConfig):
    # Convert Hydra configuration to DataIngestionConfig dataclass
    config = DataIngestionConfig(
        binance=cfg.data_sources.binance,
        # rest_api=None,
        # file=cfg.data_sources.file,
        tasks=cfg.tasks
    )

    # Initialize logger
    logger = get_logger("DataIngestion", cfg)

    # Initialize data sources with keys from environment variables
    data_sources = {
        "binance": BinanceDataSource(
            api_key=os.getenv("BINANCE_API_KEY"),  # Load from .env
            api_secret=os.getenv("BINANCE_API_SECRET")  # Load from .env
        ),
        # "file": FileDataSource(config.file.base_path)
    }

    # Initialize DataIngestion
    ingestion = DataIngestion(config, data_sources, logger)

    # Run tasks
    data = ingestion.run()

    # Print a summary
    for task_name, task_data in data.items():
        print(f"Task: {task_name}")
        for symbol, df in task_data.items():
            print(f"  {symbol}: {len(df)} rows fetched")

if __name__ == "__main__":
    main()
