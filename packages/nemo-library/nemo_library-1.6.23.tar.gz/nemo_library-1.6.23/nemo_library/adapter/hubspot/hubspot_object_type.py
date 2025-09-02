from nemo_library.adapter.utils.structures import ETLBaseObjectType


class HubSpotObjectType(ETLBaseObjectType):
    DEALS = ("Deals", "0001")
    PIPELINES = ("Pipelines", "0002")
    DEAL_OWNERS = ("Deal Owners", "0003")
    DEAL_COMPANIES = ("Deal Companies", "0004")
    COMPANY_DETAILS = ("Company Details", "0005")
    DEALS_FORECAST_HEADER = ("Deals Forecast Header", "0006")
    DEALS_FORECAST_DEALS = ("Deals Forecast Deals", "0007")
