from nemo_library.adapter.utils.sentiment_analyzer import SentimentAnalyzer
from prefect import get_run_logger
from nemo_library.adapter.gedys.gedys_object_type import GedysObjectType
from nemo_library.adapter.utils.file_handler import ETLFileHandler
from nemo_library.adapter.utils.recursive_json_flattener import RecursiveJsonFlattener
from nemo_library.adapter.utils.structures import ETLAdapter, ETLStep
from nemo_library.core import NemoLibrary


class GedysTransform:
    """
    Class to handle transformation of data for the Gedys adapter.
    """

    def __init__(self):

        nl = NemoLibrary()
        self.config = nl.config
        self.logger = get_run_logger()

        super().__init__()

    def sentiment_analysis(self) -> None:
        filehandler = ETLFileHandler()
        sentiment_analyzer = SentimentAnalyzer()
        for entity in GedysObjectType:
            data = filehandler.readJSON(
                adapter=ETLAdapter.GEDYS,
                step=ETLStep.EXTRACT,
                entity=entity,
                ignore_nonexistent=True,  # Ignore if file does not exist
            )

            if not data:
                self.logger.warning(
                    f"No data found for entity {entity.label}. Skipping sentiment analysis."
                )
                continue

            if entity.sentiment_analysis:
                self.logger.info(
                    f"Performing sentiment analysis for entity {entity.label}"
                )
                data = sentiment_analyzer.analyze_sentiment(
                    data=data,
                    sentiment_analysis_fields=entity.sentiment_analysis_fields,
                )

            filehandler.writeJSON(
                adapter=ETLAdapter.GEDYS,
                step=ETLStep.TRANSFORM,
                data=data,
                entity=entity,
                filename=f"01_{entity.filename}_sentiment",
                label=f"{entity.label} with sentiment",
            )

    def flatten(self) -> None:
        filehandler = ETLFileHandler()
        flattener = RecursiveJsonFlattener()
        for entity in GedysObjectType:
            data = filehandler.readJSON(
                adapter=ETLAdapter.GEDYS,
                step=ETLStep.TRANSFORM,
                entity=entity,
                ignore_nonexistent=True,  # Ignore if file does not exist
                filename=f"01_{entity.filename}_sentiment",
            )

            if not data:
                self.logger.warning(
                    f"No data found for entity {entity.label}. Skipping flattening."
                )
                continue

            self.logger.info(f"Flattening data for entity {entity.label}")
            flattened_data = flattener.flatten(data)

            filehandler.writeJSON(
                adapter=ETLAdapter.GEDYS,
                step=ETLStep.TRANSFORM,
                data=flattened_data,
                entity=entity,
                filename=f"02_{entity.filename}_flattened",
            )

    def join(self) -> None:
        filehandler = ETLFileHandler()

        # Load base data from GEDYS
        company_data = filehandler.readJSON(
            adapter=ETLAdapter.GEDYS,
            step=ETLStep.EXTRACT,
            entity=GedysObjectType.COMPANY,
        )
        if not company_data:
            raise ValueError("No company data found for joining with opportunities.")

        contact_data = filehandler.readJSON(
            adapter=ETLAdapter.GEDYS,
            step=ETLStep.EXTRACT,
            entity=GedysObjectType.CONTACT,
        )
        if not contact_data:
            raise ValueError("No contact data found for joining with opportunities.")

        opportunities_data = filehandler.readJSON(
            adapter=ETLAdapter.GEDYS,
            step=ETLStep.EXTRACT,
            entity=GedysObjectType.OPPORTUNITY,
        )
        if not opportunities_data:
            raise ValueError("No opportunities data found for joining with companies.")

        # Map company OIDs for fast lookup
        company_oids = {company["Oid"]: company for company in company_data}

        # Initialize result containers
        for company in company_data:
            company["opportunities"] = []
            company["contacts"] = []

        # Assign contacts to their related companies
        for contact in contact_data:
            related_ids = set()

            for key in [
                "RelatedMainParents",
                "RelatedParents",
            ]:
                if key in contact:
                    related_ids.update(entry["Oid"] for entry in contact[key])

            for rel_id in related_ids:
                if rel_id in company_oids:
                    company_oids[rel_id]["contacts"].append(contact)

        # Assign directly related opportunities to companies
        for opp in opportunities_data:
            related_ids = set()

            for key in [
                "RelatedMainParents",
                "RelatedParents",
            ]:
                if key in opp:
                    related_ids.update(entry["Oid"] for entry in opp[key])

            for rel_id in related_ids:
                if rel_id in company_oids:
                    company_oids[rel_id]["opportunities"].append(opp)

        # Map opportunities to contacts
        contact_opportunity_map = {}  # contact OID → list of related opportunities

        for opp in opportunities_data:
            related_contacts = set()

            for key in [
                "RelatedMainParents",
                "RelatedParents",
            ]:
                if key in opp:
                    related_contacts.update(entry["Oid"] for entry in opp[key])

            for contact_oid in related_contacts:
                contact_opportunity_map.setdefault(contact_oid, []).append(opp)

        # Assign opportunities from contacts to their companies
        for company in company_data:
            for contact in company["contacts"]:
                contact_oid = contact["Oid"]
                if contact_oid in contact_opportunity_map:
                    company["opportunities"].extend(
                        contact_opportunity_map[contact_oid]
                    )

        # Identify opportunities that are not linked to any company or contact
        known_company_ids = set(company_oids.keys())
        known_contact_ids = {contact["Oid"] for contact in contact_data}

        unlinked_opportunities = []

        for opp in opportunities_data:
            related_ids = set()

            for key in [
                "RelatedMainParents",
                "RelatedParents",
            ]:
                if key in opp:
                    related_ids.update(entry["Oid"] for entry in opp[key])

            # Check if none of the related IDs match known companies or contacts
            if not any(
                oid in known_company_ids or oid in known_contact_ids
                for oid in related_ids
            ):
                unlinked_opportunities.append(opp)

        # output for analysis
        if unlinked_opportunities:
            self.logger.warning(
                f"{len(unlinked_opportunities)} opportunities are not linked to known companies or contacts."
            )
            self.logger.info("Unlinked Opportunities:")
            for opp in unlinked_opportunities:
                self.logger.info(
                    f"- Opportunity OID: {opp.get('Oid')}, Subject: {opp.get('Subject')}"
                )
                for key in [
                    "RelatedMainParents",
                    "RelatedParents",
                ]:
                    if key in opp:
                        self.logger.info(
                            f"  {key}: {[entry['Oid'] for entry in opp[key]]}"
                        )

        # flatten the data
        flattener = RecursiveJsonFlattener()
        company_flat = flattener.flatten(company_data)

        # save the transformed data finally
        filehandler.writeJSON(
            adapter=ETLAdapter.GEDYS,
            step=ETLStep.TRANSFORM,
            data=company_flat,
            entity=None,
            filename=f"03_{GedysObjectType.COMPANY.filename}_joined",
            label=f"{GedysObjectType.COMPANY.label} joined",
        )
