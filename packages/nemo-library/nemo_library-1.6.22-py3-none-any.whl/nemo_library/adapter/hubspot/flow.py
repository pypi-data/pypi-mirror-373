from prefect import flow, task, get_run_logger

from nemo_library.adapter.hubspot.extract import HubSpotExtract
from nemo_library.adapter.hubspot.load import HubSpotLoad
from nemo_library.adapter.hubspot.transform import HubSpotTransform


@flow(name="HubSpot ETL Flow", log_prints=True)
def hubspot_flow(
    bextract: bool = True,
    btransform: bool = True,
    bload: bool = True,
    filter_deal_pipelines: list[str] = ["default"],
):
    logger = get_run_logger()
    logger.info("Starting HubSpot ETL Flow")

    if bextract:
        logger.info("Extracting objects from HubSpot")
        extract(filter_deal_pipelines=filter_deal_pipelines)

    if btransform:
        logger.info("Transforming HubSpot objects")
        transform()

    if bload:
        logger.info("Loading HubSpot objects")
        load()

    logger.info("HubSpot ETL Flow finished")


@task(name="Extract All Objects from HubSpot")
def extract(filter_deal_pipelines: list[str]):
    logger = get_run_logger()
    logger.info("Extracting all HubSpot objects")

    extractor = HubSpotExtract()
    extractor.extract_pipelines()
    extractor.extract_deals(filter_deal_pipelines=filter_deal_pipelines)
    extractor.extract_deal_owners()
    extractor.extract_deal_companies()
    extractor.extract_companies()


@task(name="Transform Objects")
def transform():
    logger = get_run_logger()
    logger.info("Transforming HubSpot objects")

    transformer = HubSpotTransform()
    transformer.transform_deals()


@task(name="Load Objects")
def load():
    logger = get_run_logger()
    logger.info("Loading HubSpot objects")

    loader = HubSpotLoad()
    loader.load_forecast_call()
