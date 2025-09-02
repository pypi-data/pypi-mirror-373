import logging
from time import sleep

from bs4 import BeautifulSoup
from nemo_library.model.migman import MigMan

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import json
import sys
import time

from nemo_library.utils.utils import log_error

# constants
SNOW_URL = "https://proalpha.service-now.com/csm?id=kb_article_view&sysparm_article=KB0010909&sys_kb_id=fa635efb8397d2145f6ac420feaad35e&spa=1"
"""URL OF Service Now Overview Page for MigMan"""
POSTFIX_MAPPING = {1: "", 2: "ADD1", 3: "ADD2"}
"""mapping of table number with postfix that we use"""
IGNORE_LINKS = ["KB0011475", "KB0016496"]
"""links from migman overview table that should be ignored"""
TITLE_PROJECT_MAPPING = {
    "Revenue Groups/Purchasing Groups": "Revenue Groups-Purchasing Groups",
    "Field/Coloumn Securities": "Field-Coloumn Securities",
    "Packaging Instructions (Header Data Part/Customer)": "Packaging Instructions (Header Data Part-Customer)",
    "Role (Group Assignments)": "Role (Group Assignments)",
    "European Article Numbers": "Global Trade Item Numbers",
    "Error Types AND Causes": "Error Types And Causes"
}


class SNOWScraper:
    def __init__(self, database: list[MigMan]):
        self.database = database
        self.driver = None
        self.missing_projects = []

    def scrape(self) -> None:
        # Scrape the snow data from the URL
        try:
            self._init_selenium()
            self._login()
            self._scrape_overview()
            if self.missing_projects:
                logging.warning(
                    f"the following projects where found on SNOW overview, but could not be identified in migman database. Please check typing."
                )
                logging.warning(json.dumps(self.missing_projects, indent=2))
        finally:
            if self.driver:
                self.driver.quit()

    def _init_selenium(self) -> None:
        # Initialize the selenium driver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def _login(self) -> None:
        # Login to the snow page
        try:
            # Open the ServiceNow login page
            self.driver.get(SNOW_URL)

            # Wait for the user to manually log in (if SSO is interactive)
            print("Please log in via the browser window...")
            for remaining in range(60, 0, -1):
                sys.stdout.write("\r")
                sys.stdout.write(f"{remaining} seconds remaining.")
                sys.stdout.flush()
                time.sleep(1)
            sys.stdout.write("\rLogin time expired. Continuing...\n")

        except Exception as e:
            log_error(f"Error: {e}")

    def _wait_for_page_load(self, driver, timeout=10):
        """Waits for the page to load by checking for a specific element."""
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            logging.info("Page loaded successfully.")
        except Exception as e:
            logging.error(f"Page load timed out: {e}")
            raise

    def _scrape_overview(self) -> None:

        self.driver.get(SNOW_URL)
        self.driver.refresh()
        self._wait_for_page_load(self.driver)
        sleep(5)  # Wait for the page to fully load

        # Parse the dynamically loaded content with Beautiful Soup
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Locate the specific table by its content or attributes
        tables = soup.find_all("table")  # Finds all tables
        logging.info(f"Found {len(tables)} tables on the page.")

        for table in tables:

            unique_links = set()

            rows = table.find_all("tr")
            rows = rows[1:]
            for row in rows:
                cells = row.find_all("td")

                # ignore all "ready2run" packages
                if cells[0].get_text() == "R2R":
                    logging.info(f"Ignoring R2R package: {cells[1].text}")
                    continue

                # get link text and href from column 1
                link = cells[1].find("a", href=True)
                if link:
                    link_text = link.text.strip() or "No Text"
                    link_href = link["href"]
                    unique_links.add((link_text, link_href))

            # Convert the set to a list and return it
            link_list = list(unique_links)
            logging.info(f"Collected {len(link_list)} unique hyperlinks.")

            # Scrape the details for each link
            for link in link_list:

                # ignore links
                if any(ignore in link[1] for ignore in IGNORE_LINKS):
                    logging.info(f"Ignoring link: {link[0]}: {link[1]}")
                    continue

                # scrape detail page
                self._scrape_details(link[1])

    def _scrape_details(self, link: str) -> None:
        logging.info(f"Scraping details for link: {link}")
        self.driver.get(link)
        self._wait_for_page_load(self.driver)

        try:
            # Scroll down to trigger lazy loading
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "tbody"))
            )
            logging.info("Found <tbody> element after scrolling.")
        except Exception as e:
            log_error(f"<tbody> element not found: {e}")
            return

        # Parse the dynamically loaded content
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        title = soup.find("title")
        if title:
            logging.info(f"Title: {title.text.strip()}")
            if not ".." in title.text.strip():
                logging.info(f"Title does not contain '..'")
                log_error(f"Title {title }does not contain '..'")
            project = title.text.strip().split("..", 1)[1].strip()

            if project in TITLE_PROJECT_MAPPING:
                project = TITLE_PROJECT_MAPPING[project]

            if not project:
                logging.info(f"No project found for title: {title}. Skipping...")
                return

            if len([x for x in self.database if x.project == project]) == 0:
                logging.info(
                    f"No MigMan project found for project: {project}. Skipping..."
                )
                self.missing_projects.append(project)
                return

            logging.info(f"Project: {project}")
        else:
            log_error("No title found in the parsed HTML.")

        tbody = soup.find("tbody")
        if not tbody:
            log_error("No <tbody> element found in the parsed HTML.")

        tables = soup.find_all("table")  # Finds all tables
        logging.info(f"Found {len(tables)} tables on the page.")
        if len(tables) > 3:
            log_error(f"Found more than 3 tables on the page: {len(tables)}")

        for idx, table in enumerate(tables, start=1):

            # postfix mapping
            postfix = POSTFIX_MAPPING[idx]

            # Extract rows and cells
            rows = table.find_all("tr")
            rows = rows[1:]
            logging.info(f"Found {len(rows)} rows in the <table> with number {idx}.")

            for row in rows:
                cells = row.find_all("td")

                if len(cells) != 10:
                    logging.info(f"Row does not contain 10 cells: {cells}")
                    continue

                def get_cell_text(cell):
                    return cell.text.strip() if cell else None

                def get_cell_link(cell):
                    return cell.find("a")["href"] if cell.find("a") else None

                # example of extract from page
                # ['Spalte', 'Spaltenname', 'Anmerkung / Link Application Guide', 'Speicherort', 'Datentyp', 'Format', 'Update', 'Pflicht', 'Ref', 'Relevanz']
                row_Spalte = (
                    int(get_cell_text(cells[0]))
                    if get_cell_text(cells[0]).isdigit()
                    else get_cell_text(cells[0])
                )
                row_Spaltenname = get_cell_text(cells[1])
                row_AppGuide_text = get_cell_text(cells[2])
                row_AppGuide_link = get_cell_link(cells[2])
                row_Speicherort = get_cell_text(cells[3])
                row_Datentyp = get_cell_text(cells[4]).lower()
                row_Format = get_cell_text(cells[5])
                row_Update = get_cell_text(cells[6])
                row_Pflicht = get_cell_text(cells[7])
                row_Ref = get_cell_text(cells[8])
                row_Relevanz = get_cell_text(cells[9])

                # Find the corresponding MigMan object in the database
                migman = [
                    x
                    for x in self.database
                    if x.project == project
                    and x.postfix == postfix
                    and x.index == row_Spalte
                ]
                if not migman:
                    logging.warning(
                        f"No MigMan object found for project '{project}' and column '{row_Spalte}' ({row_Speicherort})."
                    )
                    continue
                migman = migman[0]

                # check consistency of data
                migman.snow_remark = []
                if migman.desc_section_data_type != row_Datentyp:
                    migman.snow_remark.append(
                        f"Data type mismatch: {migman.desc_section_data_type} != {row_Datentyp}"
                    )
                if migman.desc_section_location_in_proalpha != row_Speicherort:
                    migman.snow_remark.append(
                        f"Location mismatch: {migman.desc_section_location_in_proalpha} != {row_Speicherort}"
                    )
                if migman.desc_section_format != row_Format:
                    migman.snow_remark.append(
                        f"Format mismatch: {migman.desc_section_format} != {row_Format}"
                    )

                # Update the MigMan object
                migman.snow_appguide_text = row_AppGuide_text
                migman.snow_appguide_link = row_AppGuide_link
                migman.snow_update = row_Update == "ja"
                migman.snow_mandatory = row_Pflicht == "ja"
                migman.snow_ref = row_Ref == "ja"
                migman.snow_relevance = row_Relevanz
