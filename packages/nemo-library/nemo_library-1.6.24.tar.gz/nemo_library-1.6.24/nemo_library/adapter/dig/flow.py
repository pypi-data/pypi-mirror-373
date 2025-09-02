from prefect import flow, task, get_run_logger

from nemo_library.adapter.dig.extract import DigExtract


@flow(name="DIG ETL Flow", log_prints=True)
def dig_flow():
    logger = get_run_logger()
    logger.info("Starting DIG ETL Flow")

    logger.info("Extracting objects from DIG")
    extract()

    logger.info("Transforming DIG objects")
    transform()

    logger.info("Loading DIG objects")
    load()

    logger.info("DIG ETL Flow finished")


@task(name="Extract All Objects from DIG")
def extract():
    logger = get_run_logger()
    logger.info("Extracting all DIG objects")
    extractor = DigExtract()
    extractor.extract()


@task(name="Transform Objects")
def transform():
    logger = get_run_logger()
    logger.info("Transforming DIG objects")


@task(name="Load Objects into Nemo")
def load():
    logger = get_run_logger()
    logger.info("Loading DIG objects into Nemo")

