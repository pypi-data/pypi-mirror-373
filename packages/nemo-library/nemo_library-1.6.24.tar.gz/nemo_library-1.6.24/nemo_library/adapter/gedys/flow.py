from prefect import flow, task, get_run_logger
from nemo_library.adapter.gedys.extract import GedysExtract
from nemo_library.adapter.gedys.load import GedysLoad
from nemo_library.adapter.gedys.transform import GedysTransform


@flow(name="Gedys ETL Flow", log_prints=True)
def gedys_flow(
    bextract: bool = True,
    btransform: bool = True,
    bload: bool = True,
    # transform sub-steps:
    tsentiment: bool = True,
    tflatten: bool = True,
    tjoin: bool = True,
    # load sub-steps:
    lload_entities: bool = True,
    lload_joined: bool = True,
):
    logger = get_run_logger()
    logger.info("Starting Gedys ETL Flow")

    if bextract:
        logger.info("Extracting objects from Gedys")
        extract()

    if btransform:
        logger.info("Transforming Gedys objects")
        transform(tsentiment=tsentiment, tflatten=tflatten, tjoin=tjoin)

    if bload:
        logger.info("Loading Gedys objects")
        load(lload_entities=lload_entities, lload_joined=lload_joined)

    logger.info("Gedys ETL Flow finished")


@task(name="Extract All Objects from Gedys")
def extract():
    logger = get_run_logger()
    logger.info("Extracting all Gedys objects")

    extractor = GedysExtract()
    extractor.extract()


@task(name="Transform Objects")
def transform(
    tsentiment: bool = True,
    tflatten: bool = True,
    tjoin: bool = True,
):
    logger = get_run_logger()
    logger.info("Transforming Gedys objects")

    transformer = GedysTransform()
    if tsentiment:
        transformer.sentiment_analysis()
    if tflatten:
        transformer.flatten()
    if tjoin:
        transformer.join()


@task(name="Load Objects into Nemo")
def load(lload_entities: bool = True, lload_joined: bool = True):
    logger = get_run_logger()
    logger.info("Loading Gedys objects into Nemo")

    loader = GedysLoad()
    loader.load(lload_entities=lload_entities, lload_joined=lload_joined)
