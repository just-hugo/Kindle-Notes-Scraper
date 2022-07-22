# Python imports
import requests
from requests import Response


class RequestBuilder:
    def request_header(self, integration_key: str) -> dict:
        headers = {
            "Authorization": integration_key,
            "Notion-Version": "2022-02-22",
            "Content-Type": "application/json"
        }
        return headers

    def quotes_page_request_body(self, database_id: str, quote_title: str, linked_id: str, chapter_name: str,
                                 page_number: int) -> dict:
        body = {
            "parent": {
                "database_id": database_id
            },
            "properties": {
                "Quote": {
                    "title": [
                        {
                            "text": {
                                "content": quote_title
                            }
                        }
                    ]
                },
                "Source Material": {
                    "relation": [
                        {
                            "id": linked_id
                        }
                    ]
                },
                "Chapter": {
                    "type": "rich_text",
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": chapter_name
                            }
                        }
                    ]
                },
                "Page": {
                    "type": "number",
                    "number": page_number
                }
            }
        }
        return body

    def insights_page_request_body(self, database_id: str, insight_title: str, linked_id: str) -> dict:
        body = {
            "parent": {
                "database_id": database_id
            },
            "properties": {
                "Insight": {
                    "title": [
                        {
                            "text": {
                                "content": insight_title
                            }
                        }
                    ]
                },
                "Source Material": {
                    "relation": [
                        {
                            "id": linked_id
                        }
                    ]
                }
            }
        }
        return body

    def page_name_search_request_body(self, page_name: str) -> dict:
        body = {"query": page_name}
        return body


class RequestSender:
    def __init__(self):
        # Base urls
        self.pages_api_base_url = "https://api.notion.com/v1/pages/"
        self.search_all_base_url = "https://api.notion.com/v1/search"

    def post_request(self, url: str, header: dict, body: dict) -> Response:
        response = requests.request("POST", url, headers=header, json=body)
        return response

    def get_page_id_from_search(self, header: dict, body: dict) -> str:
        # Create request url
        search_url = self.search_all_base_url

        # Create request header
        header = header

        # body
        body = body

        response = self.post_request(search_url, header, body)

        if len(response.json()["results"]) > 0:
            page_id = response.json()["results"][0]["id"]
            return page_id
        else:
            return "No results matching page name query."