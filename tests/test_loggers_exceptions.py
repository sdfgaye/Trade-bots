import hydra
from omegaconf import DictConfig
from utils.exception import CustomException
from utils.logger import get_logger
import sys

@hydra.main(version_base="1.2", config_path="config", config_name="config")
def main(cfg: DictConfig):
    logger = get_logger(__name__, cfg)  # Initialize logger
    logger.info("Starting the test script...")
    try:
        logger.info("Performing a risky operation...")
        result = 10 / 0  # Simulate an error
    except Exception as e:
        raise CustomException(str(e), sys, cfg)

if __name__ == "__main__":
    try:
        main()
    except CustomException as ce:
        print(ce)  # Print clean error message
