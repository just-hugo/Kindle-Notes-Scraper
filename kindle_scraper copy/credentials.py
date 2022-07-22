# Python imports
import os
from dotenv import load_dotenv
import re

load_dotenv()


class Integration:
    def key(self):
        key = os.getenv("INTEGRATION_KEY")
        return key


class Databases:
    def quotes_db_id(self):
        database_id = os.environ.get("QUOTES_DB_ID")
        return database_id

    def insights_database_id(self):
        database_id = os.environ.get("INSIGHTS_DB_ID")
        return database_id


class Pages:
    def source_page_id(self):
        page_id = os.environ.get("LINKED_SOURCE_PAGE_ID")
        return page_id

    def extract_page_id_from_url(self, url: str) -> str:
        page_id = re.split("\-", url)[-1]
        return page_id

    def set_source_page_id(self, page_id):
        os.environ["LINKED_SOURCE_PAGE_ID"] = page_id
        return