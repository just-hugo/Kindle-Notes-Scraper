## 🚧 This code is a work in progress.

<aside>

This tool scrapes a downloaded file of any Kindle book's highlights notebook, and stores the contents in a Notion database.

Notion’s databases are ideal for anyone engaged in research, or as an active reading tool.

[Click here for a practical example](https://www.notion.so/Notion-as-a-Research-Tool-f5241a5a209b4ce4a7a7489b8c63c876) of 3 related Notion databases to help organize research materials, which is set up to use this API integration to import highlights from Kindle books.

</aside>

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

# **Known bugs**

The Notion integration works to update and retrieve databases and pages. However, the code which scrapes the Kindle notebook has the following issues to be worked out.

- There is a bug which adds Kindle notes to both the Quotes and the Insights databases, when they should go only to the Insights database.

# Usage

Replace all the values in `.env` to suit your Notion setup. Once you've done that, make sure you download the highlights notebook from the Kindle book of your choosing.

Run `run_script.py` and follow the prompts, entering the path to the highlights file when asked. The script should handle the rest.
