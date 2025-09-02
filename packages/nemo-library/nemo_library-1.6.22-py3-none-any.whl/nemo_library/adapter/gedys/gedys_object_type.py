from nemo_library.adapter.utils.structures import ETLBaseObjectType


class GedysObjectType(ETLBaseObjectType):
    APPOINTMENT = (
        "Appointment",
        "5c6b0dd8-d322-4e22-9228-dc8b8b4f40e9",
        ["HTMLDescription"],
    )

    BUSINESS_RELATIONS = ("Business relations", "4c1604f5-6406-465e-a067-cb009c83b765")
    CALCULATION = ("Calculation", "4c0da124-0030-4b20-b4d0-25c2e6b24e8f")
    CALCULATION_POSITION = (
        "Calculation position",
        "758f0282-3a72-4184-9ab5-bec337b0a643",
    )
    COMPANY = ("Company", "fe7eb8ae-71be-4220-8da5-dc04078e6b3c")
    COMPANY_PROFILE = ("Company profile", "253a8224-e7b5-4ef7-8dec-b50b8763ad19")
    CONTACT = ("Contact", "44fcb6fb-9230-48cf-a406-8f1f8c4d0b8c")
    CONTRACT = ("Contract", "68f19801-3220-4429-8c9c-cc0550f4aebb")
    CONTRACT_TO_ADDITIONAL_ADDRESS_RELATION = (
        "Contract to additional address relation",
        "831e8588-a10d-4f3e-947a-5abc6b51f929",
    )
    COSTS = ("Costs", "3a68d347-1c07-4a5c-9878-666a324f5795")
    # DIRECTORY_ROLE = ("Directory role", "287c1d19-61e4-4686-8818-d7166bee2374")
    EMAIL = ("E-Mail", "d4fb7372-1fdb-4022-be2f-2a35289f50a3", ["Body"])
    EMAIL_SYNC_LOG = ("E-mail sync log", "f6db090f-5c0d-46d8-9fd4-20de41c4459d")
    EMAIL_TEMPLATE = ("E-mail template", "521f702a-7cb7-4ca7-a2c0-960f1c3a2bb0")
    # EVALANCHE_STATISTICS = ("Evalanche statistics", "37c59cc8-b540-474f-b1ce-fef5cf1ccdf2")
    EVENT = ("Event", "5f967e0a-76ed-45fc-b081-8edba0a57c63")
    EVENT_PARTICIPATION = (
        "Event participation",
        "c4b49a47-f129-4abb-a1fc-69e031b5687f",
    )
    EVENT_SERVICE = ("Event service", "dde1e571-289a-47c6-bae6-52b515bfb8e0")
    EVENT_SERVICE_TO_PARTICIPATION_RELATION = (
        "Event service to participation relation",
        "9f5e1d3e-1323-4a6d-a522-5167dff4a87b",
    )
    EVENT_SESSION = ("Event session", "3bfb83e7-9a77-4a1d-9ce6-4f9ff2d58ec7")
    EVENT_SESSION_TO_PARTICIPATION_RELATION = (
        "Event session to participation relation",
        "5142be61-b600-438d-8c23-86508eb0ffc5",
    )
    EVENT_TO_ADDITIONAL_ADDRESS_RELATION = (
        "Event to additional address relation",
        "604e35ad-f28e-4315-8ec6-12aed3818ace",
    )
    FOLDER = ("Folder", "e50a3c2c-2966-4e23-b1d3-221091662c86")
    FOLLOW_UP = ("Follow-up", "055c7b1c-0c95-40ce-9e97-072afbcb3afa")
    LETTER = ("Letter", "a6cc7c12-f461-4706-a102-bb2f637e78ca")
    LETTER_TEMPLATE = ("Letter template", "6fe9f0f3-a527-4cb1-8249-14d8571a503b")
    MARKETING_CAMPAIGN = ("Marketing campaign", "02dc3b17-ae42-4f0f-9a5f-48ee39abf15e")
    MARKETING_CAMPAIGN_ACTIVITY = (
        "Marketing campaign activity",
        "4d1baca8-b5bb-4364-89e6-b866cb964181",
    )
    MARKETING_CAMPAIGN_ADDRESS = (
        "Marketing campaign address",
        "b12b812e-5b70-4749-910b-ed50b062630a",
    )
    MASS_EMAIL = ("Mass e-mail", "da4041cc-e4fb-4edc-8e4f-9864777160fa")
    MASS_EMAIL_CONTROL = ("Mass e-mail control", "2b2afbb2-25cd-4ad6-a577-c30a7c8d3140")
    MASS_LETTER = ("Mass letter", "45a49d16-e981-4fd0-a783-c8827170164d")
    MASS_LETTER_CONTROL = (
        "Mass letter control",
        "f65a1841-dcbc-4669-b1d5-7b030371afeb",
    )
    MINUTES_OF_MEETING = (
        "Minutes of Meeting",
        "6c7efc33-7e1a-484b-b063-1d7581b28e08",
        ["Body"],
    )
    MISCELLANEOUS = ("Miscellaneous", "ccc307a5-a400-4b2b-9f6b-73727b8b242a", ["Body"])
    NOTIFICATION = ("Notification", "765def66-a6cf-4a85-a434-b83988f6f908", ["Body"])
    OFFER = ("Offer", "6e90a625-c7de-4451-b525-92c4dd646c16")
    OPPORTUNITY = ("Opportunity", "a087729c-d7e8-4c11-8470-b331ea6cf0b1")
    OPPORTUNITY_TO_COMPETITOR_RELATION = (
        "Opportunity to competitor relation",
        "ef3bb514-9479-4b3c-a194-23f6cad244f3",
    )
    # OPPORTUNITY_TO_PARTICIPANTS_RELATION = ("Opportunity to participants relation", "848310d0-f855-4606-a858-2111ddf99ea0")
    OPPORTUNITY_TO_SALES_TEAM_RELATION = (
        "Opportunity to sales team relation",
        "5856f46b-df43-405c-bc60-fbccddba1e95",
    )
    # PERMISSION = ("Permission", "2f758d8c-862e-4b15-b0c6-0ebb1120732e")
    PHONE_CALL = ("Phone call", "975da1fa-7357-4336-80b0-68f23e04e748", ["Body"])
    PROALPHA_OFFER = ("Proalpha offer", "80018a48-5688-41a6-bdb1-fc005da30c0b")
    PROALPHA_QUOTE = ("Proalpha Quote", "7d61175e-7dd5-4a38-994b-1c13ca8baf15")
    PROJECT = ("Project", "2d6cb945-4227-4dae-bc5b-3bf42aaa4b6c")
    PROJECT_TO_PARTICIPANTS_RELATION = (
        "Project to participants relation",
        "239dc608-a4f4-4b84-992a-a174598aeb4f",
    )
    QUOTE = ("Quote", "f9e70444-b262-4df6-93ea-b9986aa0fc36")
    # ROLE = ("Role", "98a37e68-b310-49ac-bc82-9d21bdf059d3")
    SPREAD_SHEET_TEMPLATE = (
        "Spread sheet template",
        "76acce7a-4afb-46da-b69a-2c2f101c5c2d",
    )
    TICKET = ("Ticket", "81255801-deb4-40a5-853b-0c1aa795772a")
    USERPROFILE = ("User profile", "4b00f31c-e05d-42ef-9172-64608316c4c3")
    WEB_SERVICE_CALL_LOG = (
        "Web service call log",
        "7884299b-c3f3-4414-834c-57e88882c923",
    )
    WORK_PACKAGE = ("Work package", "2f528c7e-e7a4-4fb5-9a5c-25d1d65d0873")

    # part data tables
    # ATTENDEES_OF_APPOINTMENTS = ("Attendees of appointments", "70a398ec-39fd-4eb5-a242-7e911f5f90fd")
    # EMAIL_ADDRESSES_OF_ADDRESSES = ("E-mail addresses of addresses", "59456265-3f3b-498b-bd5e-6687dc68556a")
    # EMAIL_ADDRESSES_OF_EMAILS = ("E-mail addresses of e-mails", "2a681287-f499-4434-a536-829c8e6ed86b")
    # EVALUATION_QUESTIONS = ("Evaluation questions", "5eeabd3b-cce6-471f-9e55-69e6fef9b370")
    # REVENUE_STREAM = ("Revenue stream", "0ef76293-93dc-402c-8d7a-fb9a7bfbf074")
    # SCORING_HISTORY = ("Scoring history", "00346be9-aafb-4983-ba33-5572aec55d75")
    # STATE_OF_MARKETING_CAMPAIGN_ADDRESSES = ("State of marketing campaign addresses", "eaa89a44-60ce-4f29-a18d-1151750adf5a")
    # TRACKING_HISTORY = ("Tracking history", "d97784b6-b1d7-4bbf-94cb-8b0d2b04acf8")
