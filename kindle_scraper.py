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