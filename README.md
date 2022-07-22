<aside>
📚 Notion’s databases are ideal for anyone engaged in research, or as an active reading tool.

</aside>

This is an example of 3 related Notion databases to help organize research materials, including an API integration to import highlights from Kindle books.

---

---

# Databases

---

[Source Material](https://www.notion.so/6dfb0b2b77f74d2da929161d1942d360)

[Quotes](https://www.notion.so/af3e2a2c4e244906bd3f31e5c7d4d7ba)

[Insights](https://www.notion.so/c63413c217eb41959085e8ee9756bafa)

# API Integration

---

Notion offers API access to manipulate pages and databases programmatically. Their [documentation](https://developers.notion.com/docs) is fantastic, with ample guides, Postman examples, and API specs to cover all your CRUD operations.

For this Research Tool, I wanted to be able to imported highlights and notes from Kindle books I was reading.

Luckily, Amazon allows you to download up to 10% of highlighted content (as well as your notes) from Kindle books as an HTML file. **Limitation:** you must use their desktop app to export this file.

This integration solves my problem by:

1. Scraping a Kindle highlights HTML file to find each highlight and note
2. Uploading each highlight as a new page in the Quotes database
   1. correctly linked to the Kindle book’s entry in the Source Material database
3. Uploading each note as a new page in the Insights database
   1. correctly linked to the relevant Quote in the Quotes database

## Kindle Integration Code

<aside>
🚧 This code is a work in progress.

</aside>

The Notion integration works to update and retrieve databases and pages. However, the code which scrapes the Kindle notebook has the following issues to be worked out.

**Known bugs**

- There is a bug which adds Kindle notes to both the Quotes and the Insights databases, when they should go only to the Insights database.

### Project directory structure

```bash
/project_root
	notion_interface.py
	kindle_scraper.py
	credentials.py
	run_script.py
	example.html
	.env
	readme.md
```

### Project files

[research_api_integration.zip](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/cffce3e4-9141-498c-b4c3-4f11170a7e54/research_api_integration.zip)

- `notion_interface.py`
  ```python
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
  ```
- `kindle_scraper.py`
  ```python
  # Python imports
  from bs4 import BeautifulSoup
  import re

  class Scraper:

      def make_soup(self, filepath: str) -> BeautifulSoup:
          # Make soup
          with open(filepath, 'r') as file:
              soup = BeautifulSoup(file, 'html.parser')

          return soup

      def build_highlight_spreadsheet(self, heading_selector: list, body_selector: list) -> list:
          highlights_spreadsheet = self.parse_kindle_notebook(heading_selector, body_selector)["highlights"][0]
          return highlights_spreadsheet

      def build_notes_spreadsheet(self, heading_selector: list, body_selector: list) -> dict:
          notes_spreadsheet = self.parse_kindle_notebook(heading_selector, body_selector)["notes"][0]
          return notes_spreadsheet

      def parse_kindle_notebook(self, heading_selector: list, body_selector: list) -> dict:
          highlights_spreadsheet = []
          notes_spreadsheet = []
          all_spreadsheets = {"highlights": [], "notes": []}

          index = 0

          for item in heading_selector:
              row_in_highlights_spreadsheet = []
              row_in_notes_spreadsheet = []

              raw_notebook_section = item.text
              raw_notebook_entry = body_selector[index].text

              # Find and clean Notes and their linked highlights
              if raw_notebook_entry.__contains__("Note -"):
                  # highlight above the note
                  linked_highlight = body_selector[index].text
                  linked_highlight_clean = re.split("\n", linked_highlight)[0]

                  # the note text
                  note_text = body_selector[index + 1].text
                  note_text_clean = re.split("\n", note_text)[0]

                  # Add each item to the notes_spreadsheet row
                  row_in_notes_spreadsheet.append(note_text_clean)
                  row_in_notes_spreadsheet.append(linked_highlight_clean)

                  # Add the notes_spreadsheet row to the notes_spreadsheet
                  notes_spreadsheet.append(row_in_notes_spreadsheet)

              # Find and clean highlights and their location data
              # Find chapter
              raw_chapter = re.search("\-.*>", item.text)

              if raw_chapter is None:
                  chapter = "Prologue"
              else:
                  extract_chapter_name = re.split("\s>", re.split("\-\s", raw_chapter[0])[1])
                  chapter = extract_chapter_name[0]

              # Find page number
              page_number = int(re.split("\s", re.search("Page \d*", raw_notebook_section)[0])[1])

              # Find highlighted text
              highlight_text = re.split("\n", raw_notebook_entry)[0]

              # Build the spreadsheet

              # Add each item to the highlights_spreadsheet row
              row_in_highlights_spreadsheet.append(highlight_text)
              row_in_highlights_spreadsheet.append(chapter)
              row_in_highlights_spreadsheet.append(page_number)

              # Add the highlights_spreadsheet row to the highlights_spreadsheet
              highlights_spreadsheet.append(row_in_highlights_spreadsheet)

              # increment the body list
              index = index + 1

          # Add both spreadsheets to the dictionary
          all_spreadsheets["highlights"].append(highlights_spreadsheet)
          all_spreadsheets["notes"].append(notes_spreadsheet)

          return all_spreadsheets
  ```
- `credentials.py`
  ```python
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
  ```
- `run_script.py`
  ```python
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
  ```
- `example.html`
  ```html
  <?xml version="1.0" encoding="UTF-8"?>
  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "XHTML1-s.dtd" >
  <html xmlns="http://www.w3.org/TR/1999/REC-html-in-xml" xml:lang="en" lang="en">

  <head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></meta>
  <style>
  .bodyContainer {
      font-family: Arial, Helvetica, sans-serif;
      text-align: center;
      padding-left: 32px;
      padding-right: 32px;
  }

  .notebookFor {
      font-size: 18px;
      font-weight: 700;
      text-align: center;
      color: rgb(119, 119, 119);
      margin: 24px 0px 0px;
      padding: 0px;
  }

  .bookTitle {
      font-size: 32px;
      font-weight: 700;
      text-align: center;
      color: #333333;
      margin-top: 22px;
      padding: 0px;
  }

  .authors {
      font-size: 13px;
      font-weight: 700;
      text-align: center;
      color: rgb(119, 119, 119);
      margin-top: 22px;
      margin-bottom: 24px;
      padding: 0px;
  }

  .sectionHeading {
      font-size: 24px;
      font-weight: 700;
      text-align: left;
      color: #333333;
      margin-top: 24px;
      padding: 0px;
  }

  .noteHeading {
      font-size: 18px;
      font-weight: 700;
      text-align: left;
      color: #333333;
      margin-top: 20px;
      padding: 0px;
  }

  .noteText {
      font-size: 18px;
      font-weight: 500;
      text-align: left;
      color: #333333;
      margin: 2px 0px 0px;
      padding: 0px;
  }

  .highlight_blue {
      color: rgb(178, 205, 251);
  }

  .highlight_orange {
      color: #ffd7ae;
  }

  .highlight_pink {
      color: rgb(255, 191, 206);
  }

  .highlight_yellow {
      color: rgb(247, 206, 0);
  }

  .notebookGraphic {
      margin-top: 10px;
      text-align: left;
  }

  .notebookGraphic img {
      -o-box-shadow:      0px 0px 5px #888;
      -icab-box-shadow:   0px 0px 5px #888;
      -khtml-box-shadow:  0px 0px 5px #888;
      -moz-box-shadow:    0px 0px 5px #888;
      -webkit-box-shadow: 0px 0px 5px #888;
      box-shadow:         0px 0px 5px #888;
      max-width: 100%;
      height: auto;
  }

  hr {
      border: 0px none;
      height: 1px;
      background: none repeat scroll 0% 0% rgb(221, 221, 221);
  }
  </style>
  </head>
  <body>
  <div class='bodyContainer'>
  <h1><div class='notebookFor'>Notes and highlights for</div><div class='bookTitle'>Conflicted
  </div><div class='authors'>
  Leslie, Ian
  </div></h1><hr/>

  <h2 class='sectionHeading'>Prologue: The Interview</h2><h3 class='noteHeading'>Highlight (<span class='highlight_yellow'>yellow</span>) - Page 3 &middot; Location 71</div><div class='noteText'>Principles like ‘ assume good faith ’ , ‘ get to know your opponent’s argument as well as your own ’ , ‘ don’t argue with straw men ’ .</h3>
  <h3 class='noteHeading'>Highlight (<span class='highlight_yellow'>yellow</span>) - Page 3 &middot; Location 75</div><div class='noteText'>I came to think of productive disagreement not as a philosophy so much as a discipline , and a skill .</h3>
  <h3 class='noteHeading'>Highlight (<span class='highlight_yellow'>yellow</span>) - Page 6 &middot; Location 110</div><div class='noteText'>disagreeing productively is hard .</h3>
  <h2 class='sectionHeading'>Part One: Why We Need New Ways to Argue</h2><h3 class='noteHeading'>Highlight (<span class='highlight_yellow'>yellow</span>) - 1. Beyond Fight or Flight &gt; Page 9 &middot; Location 123</div><div class='noteText'>The internet is connecting people , but it doesn’t always create fellow - feeling . At its worst , it can resemble a machine for the production of discord and division .</h3>
  <h3 class='noteHeading'>Highlight (<span class='highlight_yellow'>yellow</span>) - 1. Beyond Fight or Flight &gt; Page 13 &middot; Location 180</div><div class='noteText'>Now , we frequently encounter others with values and customs different to our own . At the same time , we are more temperamentally egalitarian than ever .</h3>
  <h3 class='noteHeading'>Highlight (<span class='highlight_blue'>blue</span>) - 1. Beyond Fight or Flight &gt; Page 13 &middot; Location 183</div><div class='noteText'>People outsourced those decisions to the culture . With the rise of gender equality , the modern household requires more explicit communication and negotiation .</h3>
  <h3 class='noteHeading'>Note - 1. Beyond Fight or Flight &gt; Page 13 &middot; Location 184</div><div class='noteText'>This is the key insight I think. Humans have to do more cognitive lifting in every aspect of their lives, and our growing discontent across the board may have to do with that. The key to a stable, productive, happy workplace is to have clear, structured communication that removes the load from employees.</h3>
  <h3 class='noteHeading'>Highlight (<span class='highlight_yellow'>yellow</span>) - 1. Beyond Fight or Flight &gt; Page 13 &middot; Location 185</div><div class='noteText'>You can believe , as I do , that this change is overwhelmingly a good thing , and still recognise that it increases the potential for thorny disagreements .</h3>
  <h3 class='noteHeading'>Highlight (<span class='highlight_yellow'>yellow</span>) - 9. Get Curious &gt; Page 170 &middot; Location 2287</div><div class='noteText'>rather than trying to sound convincing , try to be interesting and interested .</h3>
  <h3 class='noteHeading'>Highlight (<span class='highlight_yellow'>yellow</span>) - 10. Make Wrong Strong &gt; Page 172 &middot; Location 2297</div><div class='noteText'>‘ There is no wrong note , it has to do with how you resolve it . ’ Thelonious Monk</h3>
  <h3 class='noteHeading'>Highlight (<span class='highlight_blue'>blue</span>) - 10. Make Wrong Strong &gt; Page 174 &middot; Location 2323</div><div class='noteText'>negotiators were wary of the whole notion of errors . They regarded stray messages as an inevitable side - effect of thinking on their feet . Trying to avoid them would only ensure the conversation was superficial and impersonal</h3>
  <h3 class='noteHeading'>Note - 10. Make Wrong Strong &gt; Page 174 &middot; Location 2324</div><div class='noteText'>The ever elusive authenticity.</h3>
  <h3 class='noteHeading'>Highlight (<span class='highlight_yellow'>yellow</span>) - 10. Make Wrong Strong &gt; Page 174 &middot; Location 2326</div><div class='noteText'>The negotiators felt that ‘ error ’ was too unambiguously negative a term to describe an event that can have positive consequences , if handled skilfully .</h3>
  <h3 class='noteHeading'>Highlight (<span class='highlight_yellow'>yellow</span>) - 11. Disrupt the Script &gt; Page 187 &middot; Location 2507</div><div class='noteText'>Meanwhile , the constructive conversations are not necessarily serene or well mannered – they can involve verbal attacks and bad faith , and the participants can report feeling hurt and annoyed – but , at certain points , the participants are able to escape or subvert the dynamic</h3>
  <h3 class='noteHeading'>Highlight (<span class='highlight_blue'>blue</span>) - 11. Disrupt the Script &gt; Page 188 &middot; Location 2518</div><div class='noteText'></h3>
  <h3 class='noteHeading'>Note - 11. Disrupt the Script &gt; Page 188 &middot; Location 2518</div><div class='noteText'>This visual is so fascinating.</h3>
  <h3 class='noteHeading'>Highlight (<span class='highlight_blue'>blue</span>) - 11. Disrupt the Script &gt; Page 190 &middot; Location 2543</div><div class='noteText'>Humphrys had stumbled across a truth about human arguments : they tend towards statelessness</h3>
  <h3 class='noteHeading'>Note - 11. Disrupt the Script &gt; Page 190 &middot; Location 2544</div><div class='noteText'>Also see: Monty Python humor.</h3>
  <h3 class='noteHeading'>Highlight (<span class='highlight_yellow'>yellow</span>) - 13. Only Get Mad on Purpose &gt; Page 216 &middot; Location 2910</div><div class='noteText'>Skilful communicators , says Alan Sillars , refuse to submit to the logic of reciprocity without considering , first , if that’s the wise thing to do . They deliberately slow the conversation down and consider their options . They’re not just thinking about what they want to do , but how what they do affects the other , and about the best way to reach their goal for the conversation</h3>
  <h3 class='noteHeading'>Highlight (<span class='highlight_yellow'>yellow</span>) - 14. Golden Rule: Be Real &gt; Page 225 &middot; Location 3021</div><div class='noteText'>There is a golden thread running through all the conversations I had with people in the course of researching and writing this book , and it’s this : you can’t handle disagreement and conflict successfully if you don’t make a truthful human connection . If you have one , then all rules are moot .</h3>
  <h2 class='sectionHeading'>Part Three: Staying in the Room</h2><h3 class='noteHeading'>Highlight (<span class='highlight_yellow'>yellow</span>) - 15. The Infinite Game &gt; Page 231 &middot; Location 3065</div><div class='noteText'>Productive disagreement is not the same as good manners , but some minimal form of civility is required to keep our disagreements going</h3>
  <h3 class='noteHeading'>Highlight (<span class='highlight_yellow'>yellow</span>) - 17. Toolkit of Productive Argument &gt; Page 257 &middot; Location 3406</div><div class='noteText'>Don’t just correct – create</h3>
  </div>
  </body>
  </html>
  ```
- `.env`
  ```python
  INTEGRATION_KEY = ""
  INSIGHTS_DB_ID = ""
  QUOTES_DB_ID = ""
  LINKED_SOURCE_PAGE_ID = ""
  ```
- `readme.md`
  ***
  # Setup Instructions
  ## Python Setup
  Download and unzip the project files. Create a [virtual environment](https://docs.python.org/3/library/venv.html).
  This integration makes use of 3 external Python libraries: [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), [Python-Dotenv](https://pypi.org/project/python-dotenv/), and [Requests](https://docs.python-requests.org/en/latest/). To install them run `pip install requests python-dotenv beautifulsoup4` in the project directory.
  ## Notion Integration Setup
  Follow the Notion API [documentation](https://developers.notion.com/docs#getting-started) to create an integration with the databases you’ve created.
  In `.env`, insert the integration key you received at the end of the integration creation step as the value for `INTEGRATION_KEY`.
  ## Notion Database Setup
  In Notion, create a Source Material database, a Quotes database, and an Insights database, each with the schema and relationships as modeled in the example above.
  Once created, you’ll need to retrieve each database’s ID. To do so, follow [these instructions](https://developers.notion.com/docs/getting-started#step-2-share-a-database-with-your-integration) from the Notion API documentation.
  In `.env`, replace the empty string for `QUOTE_DB_ID` and `INSIGHTS_DB_ID` with the Notion ID for the Quotes Database and the Insights Database respectively.
  Back in Notion, add an entry to your Source Material Database for the Kindle book. In the example database above, the example page name is Conflicted.
  Get the link for the Kindle book entry by clicking on the “Share” button and then clicking on the “Copy link” icon in the bottom right corner of the popup. The link will look something like `https://www.notion.so/cheyannehewitt/Conflicted-How-Productive-Disagreements-Lead-to-Better-Outcomes-0bdde4977c414ba786003f0133beb254`
  Save this link, because you will be asked for it when you run the code.
  ## Kindle File Download
  From the Kindle desktop app:
  - click on the Show Notebook button
  - Press the Export button
  - export all highlights and notes as a single HTML file
  Save it to your project directory.
  ## Running the Code
  From the project directory, run `python run_script.py`
  You will be prompted for the filepath of the HTML file; in this case, since `example.html` is in the project directory, just use the filename, including extension. If you saved it elsewhere, like to your Downloads folder, then use the complete filepath to the file.
