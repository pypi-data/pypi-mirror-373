from prefect import flow, task, get_run_logger

from nemo_library.adapter.zentis.extract import ZentisExtract
from nemo_library.adapter.zentis.load import ZentisLoad
from nemo_library.adapter.zentis.transform import ZentisTransform


@flow(name="Zentis ETL Flow", log_prints=True)
def zentis_flow(
    bextract: bool = True,
    btransform: bool = True,
    bload: bool = True,
):
    logger = get_run_logger()
    logger.info("Starting Zentis ETL Flow")

    if bextract:
        logger.info("Extracting objects from Zentis")
        extract()

    if btransform:
        logger.info("Transforming Zentis objects")
        transform()

    if bload:
        logger.info("Loading Zentis objects")
        load()

    logger.info("Zentis ETL Flow finished")


@task(name="Extract All Objects from Zentis")
def extract():
    logger = get_run_logger()
    logger.info("Extracting all Zentis objects")

    extractor = ZentisExtract()
    extractor.extract()


@task(name="Transform Objects")
def transform():
    logger = get_run_logger()
    logger.info("Transforming Zentis objects")

    transformer = ZentisTransform()
    transformer.transform()
    transformer.join()


@task(name="Load Objects into Nemo")
def load():
    logger = get_run_logger()
    logger.info("Loading Zentis objects into Nemo")

    loader = ZentisLoad()
    loader.load()
