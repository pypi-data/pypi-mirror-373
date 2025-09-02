from kelvin.sdk.lib.utils.logger_utils import logger

try:
    import mlflow

    _ = mlflow  # To avoid unused import warning
except ImportError:
    logger.error(
        "MLFlow is not installed. To use kelvin-sdk mlflow features install `pip install 'kelvin-sdk[mlflow]'`"
    )
    exit(1)
