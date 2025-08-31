import html as std_html
import re

import bs4
from bs4 import BeautifulSoup
from loguru import logger

# Configure Loguru Logger (optional)
# logger.remove()  # Remove default logger to prevent duplicate logs
# logger.add(
#     "text_extractor.log",
#     rotation="10 MB",
#     level="ERROR",
#     format="{time} {level} {message}",
# )


class TextExtractor:
    """
    A class that traverses an HTML parse tree to extract text content, handling various HTML elements.
    """

    BLOCK_ELEMENTS = {
        "ADDRESS",
        "ARTICLE",
        "ASIDE",
        "BLOCKQUOTE",
        "BODY",
        "BR",
        "BUTTON",
        "CANVAS",
        "CAPTION",
        "COL",
        "COLGROUP",
        "DD",
        "DIV",
        "DL",
        "DT",
        "EMBED",
        "FIELDSET",
        "FIGCAPTION",
        "FIGURE",
        "FOOTER",
        "FORM",
        "H1",
        "H2",
        "H3",
        "H4",
        "H5",
        "H6",
        "HEADER",
        "HGROUP",
        "HR",
        "LI",
        "MAP",
        "NOSCRIPT",
        "OBJECT",
        "OL",
        "OUTPUT",
        "P",
        "PRE",
        "PROGRESS",
        "SECTION",
        "TABLE",
        "TBODY",
        "TEXTAREA",
        "TFOOT",
        "TH",
        "THEAD",
        "TR",
        "UL",
        "VIDEO",
    }
    INLINE_SPACING_ELEMENTS = {
        "ADDRESS",
        "CITE",
        "DETAILS",
        "DATALIST",
        "IFRAME",
        "IMG",
        "INPUT",
        "LABEL",
        "LEGEND",
        "OPTGROUP",
        "Q",
        "SELECT",
        "SUMMARY",
        "TBODY",
        "TD",
        "TIME",
        "SPAN",
        "A",
    }
    HEADING_TAGS = {"H1", "H2", "H3", "H4", "H5", "H6"}
    UNWANTED_ELEMENTS = {"SCRIPT", "STYLE", "HEAD", "META", "NOSCRIPT"}

    def __init__(self):
        self.text_extract = []  # List to accumulate text segments
        self.extracted_text = None  # Will be set to final extracted text or None
        self.in_pre = False  # Indicates if we're inside a <pre> tag

    def handle_node(self, node):  # noqa: C901
        """
        Recursively handle each node in the HTML tree.
        """
        if isinstance(node, BeautifulSoup):
            # Root of the soup
            for child in node.contents:
                self.handle_node(child)
        elif isinstance(node, bs4.element.Tag):
            name = self.get_node_tag_name(node)
            if name in self.UNWANTED_ELEMENTS:
                return  # Skip this node and its children
            self.handle_tag_open(name)

            # Process children
            for child in node.contents:
                self.handle_node(child)

            self.handle_tag_close(name)
        elif isinstance(node, bs4.element.NavigableString):
            if not isinstance(node, bs4.element.Comment):
                self.handle_text_node(node)

    def get_node_tag_name(self, node):
        """
        Safely get the uppercased tag name of an element node.
        """
        try:
            name = node.name
            return name.upper() if name else None
        except Exception as e:
            logger.error(f"Error processing node tag: {e}")
            return None

    def handle_tag_open(self, name):
        """
        Handle the opening of an HTML tag.
        """
        if name == "PRE":
            self.in_pre = True

        if name in self.BLOCK_ELEMENTS:
            self.append_paragraph_separator()
        elif name in self.INLINE_SPACING_ELEMENTS:
            self.append_space()

    def handle_tag_close(self, name):
        """
        Handle the closing of an HTML tag.
        """
        if name == "PRE":
            self.in_pre = False

        if name in self.BLOCK_ELEMENTS:
            self.append_paragraph_separator()
        elif name in self.INLINE_SPACING_ELEMENTS:
            self.append_space()

        if name in self.HEADING_TAGS:
            self.append_paragraph_separator()

    def handle_text_node(self, text_node):
        """
        Handle the text content of an HTML node.
        """
        try:
            txt = self.decode_char_ent(str(text_node))
            if self.in_pre:
                t = txt  # Preserve whitespace in <pre> tags
            else:
                t = " ".join(txt.split())

            if not t.strip():
                return  # Skip empty strings

            self.text_extract.append(t + " ")  # Append a space after the text
        except Exception as e:
            logger.error(f"Error handling text node: {e}")

    def append_paragraph_separator(self):
        """
        Append a paragraph separator (newline) to the text extract.
        """
        if self.text_extract and not self.text_extract[-1].endswith("\n"):
            self.text_extract.append("\n")
        else:
            self.text_extract.append("\n")

    def append_space(self):
        """
        Append a space to the text extract if appropriate.
        """
        if self.text_extract:
            if not self.text_extract[-1].endswith((" ", "\n")):
                self.text_extract.append(" ")
        else:
            self.text_extract.append(" ")

    def decode_char_ent(self, text):
        """
        Decode HTML character entities.
        """
        return std_html.unescape(text)

    def get_extracted_text(self):
        """
        After processing, get the final extracted text.
        """
        if self.text_extract:
            # Join the text segments and perform final cleanup
            final_text = "".join(self.text_extract)
            # Remove text enclosed in curly braces {}
            final_text = re.sub(r"\{.*?\}", "", final_text, flags=re.DOTALL)
            # Replace multiple newlines with a single newline
            final_text = re.sub(r"\n+", "\n", final_text)
            # Replace multiple spaces with a single space
            final_text = re.sub(r"[ ]{2,}", " ", final_text)
            self.extracted_text = final_text.strip()
        else:
            self.extracted_text = None  # No text extracted
