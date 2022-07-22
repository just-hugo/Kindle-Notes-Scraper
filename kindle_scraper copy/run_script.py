# App imports
from notion_interface import RequestSender, RequestBuilder
from credentials import Databases, Integration, Pages
from kindle_scraper import Scraper


send = RequestSender()
build = RequestBuilder()
scraper = Scraper()
databases = Databases()
integration = Integration()
pages = Pages()

# Set page_id of the book entry in Source Material Database that all highlights and notes should be linked to
source_page = input("Please enter the URL  of the Notion page you want to add highlights and notes to. ")
page_id = pages.extract_page_id_from_url(source_page)
pages.set_source_page_id(page_id)

# Parse the HTML file into a BS4 object
filepath = input("Enter the file path of your Kindle highlights and notes HTML file. ")
soup = scraper.make_soup(rf"{filepath}")

# BS4 Selectors
highlight_heading = soup.body.find_all("h3", class_="noteHeading")
highlight_body = soup.body.find_all("div", class_="noteText")

# Make spreadsheets from the BS4 object
highlights_spreadsheet = scraper.build_highlight_spreadsheet(highlight_heading, highlight_body)
notes_spreadsheet = scraper.build_notes_spreadsheet(highlight_heading, highlight_body)

# Request data
pages_url = send.pages_api_base_url
header = build.request_header(integration.key())

# Upload highlights to quotes database
for each_row in highlights_spreadsheet:

    body = build.quotes_page_request_body(databases.quotes_db_id(), each_row[0], pages.source_page_id(), each_row[1], each_row[2])

    response = send.post_request(pages_url, header, body)

# Upload notes to insights database
for each_row in notes_spreadsheet:

    note = each_row[0]
    linked_highlight = each_row[1]

    # Query the quotes database for matches to linked_highlights
    body = build.page_name_search_request_body(linked_highlight)
    linked_highlight_id = send.get_page_id_from_search(header, body)

    body = build.insights_page_request_body(databases.insights_database_id(), note, linked_highlight_id)

    response = send.post_request(pages_url, header, body)