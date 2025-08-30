from __future__ import annotations

import re
from typing import Final


class HtmlFormatter:
    """
    A class for formatting text in HTML with tag classes supported by the client.
    """
    TIMESTAMP_TEXT__CSS_CLASS_NAME: Final[str] = "timestamp-text"
    HEADER_1_TEXT__CSS_CLASS_NAME: Final[str] = "header1-text"
    HEADER_2_TEXT__CSS_CLASS_NAME: Final[str] = "header2-text"
    HEADER_3_TEXT__CSS_CLASS_NAME: Final[str] = "header3-text"
    BODY_TEXT__CSS_CLASS_NAME: Final[str] = "body-text"
    CAPTION_TEXT__CSS_CLASS_NAME: Final[str] = "caption-text"

    @staticmethod
    def timestamp(text: str) -> str:
        """
        Given a text string, return that same text string HTML formatted using the timestamp CSS class.

        :param text: The text to format.
        :return: The HTML formatted text.
        """
        return f'<span class="{HtmlFormatter.TIMESTAMP_TEXT__CSS_CLASS_NAME}">{text}</span>'

    @staticmethod
    def header_1(text: str) -> str:
        """
        Given a text string, return that same text string HTML formatted using the header 1 CSS class.

        :param text: The text to format.
        :return: The HTML formatted text.
        """
        return f'<span class="{HtmlFormatter.HEADER_1_TEXT__CSS_CLASS_NAME}">{text}</span>'

    @staticmethod
    def header_2(text: str) -> str:
        """
        Given a text string, return that same text string HTML formatted using the header 2 CSS class.

        :param text: The text to format.
        :return: The HTML formatted text.
        """
        return f'<span class="{HtmlFormatter.HEADER_2_TEXT__CSS_CLASS_NAME}">{text}</span>'

    @staticmethod
    def header_3(text: str) -> str:
        """
        Given a text string, return that same text string HTML formatted using the header 3 CSS class.

        :param text: The text to format.
        :return: The HTML formatted text.
        """
        return f'<span class="{HtmlFormatter.HEADER_3_TEXT__CSS_CLASS_NAME}">{text}</span>'

    @staticmethod
    def body(text: str) -> str:
        """
        Given a text string, return that same text string HTML formatted using the body text CSS class.

        :param text: The text to format.
        :return: The HTML formatted text.
        """
        return f'<span class="{HtmlFormatter.BODY_TEXT__CSS_CLASS_NAME}">{text}</span>'

    @staticmethod
    def caption(text: str) -> str:
        """
        Given a text string, return that same text string HTML formatted using the caption text CSS class.

        :param text: The text to format.
        :return: The HTML formatted text.
        """
        return f'<span class="{HtmlFormatter.CAPTION_TEXT__CSS_CLASS_NAME}">{text}</span>'

    @staticmethod
    def replace_newlines(text: str) -> str:
        """
        Given a text string, return that same text string HTML formatted with newlines replaced by HTML line breaks.

        :param text: The text to format.
        :return: The HTML formatted text.
        """
        return re.sub("\r?\n", "<br>", text)

    @staticmethod
    def scrub_html(text: str) -> str:
        """
        Given a string that contains HTML, return that same string with all HTML removed.

        :param text: The HTML string to scrub.
        :return: The scrubbed text.
        """
        if not text:
            return ""

        from bs4 import BeautifulSoup
        return BeautifulSoup(text, "html.parser").get_text()

    @staticmethod
    def scrub_markdown(text: str) -> str:
        """
        Given a string that contains markdown, return that same string with all markdown removed.

        :param text: The markdown string to scrub.
        :return: The scrubbed text.
        """
        if not text:
            return ""

        # --- Remove Headers ---
        # Level 1-6 headers (# to ######)
        text = re.sub(r"^#{1,6}\s*(.*)$", r"\1", text, flags=re.MULTILINE).strip()

        # --- Remove Emphasis ---
        # Bold (**text** or __text__)
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"__(.*?)__", r"\1", text)

        # Italic (*text* or _text_)
        text = re.sub(r"\*(.*?)\*", r"\1", text)
        text = re.sub(r"_(.*?)_", r"\1", text)

        # --- Remove Strikethrough ---
        # Strikethrough (~~text~~)
        text = re.sub(r"~~(.*?)~~", r"\1", text)

        # --- Remove Links ---
        # Links ([text](url))
        text = re.sub(r"\[(.*?)]\((.*?)\)", r"\1", text)

        # --- Remove Images ---
        # Images (![alt text](url))
        text = re.sub(r"!\\[(.*?)\\]\\((.*?)\\)", "", text)  # remove the entire image tag

        # --- Remove Code ---
        # Inline code (`code`)
        text = re.sub(r"`(.*?)`", r"\1", text)

        # Code blocks (```code```)
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)  # multiline code blocks

        # --- Remove Lists ---
        # Unordered lists (* item, - item, + item)
        text = re.sub(r"(?m)^[*\-+]\s+", "", text)

        # Ordered lists (1. item)
        text = re.sub(r"(?m)^\d+\.\s+", "", text)

        # --- Remove Blockquotes ---
        # Blockquotes (> text)
        text = re.sub(r"(?m)^>\s+", "", text)

        # --- Remove Horizontal Rules ---
        # Horizontal rules (---, ***, ___)
        text = re.sub(r"(?m)^[-_*]{3,}\s*$", "", text)  # Remove horizontal rules

        # --- Remove HTML tags (basic)---
        #  This is a very simple HTML tag removal, it does not handle nested tags or attributes properly.
        text = re.sub(r"<[^>]*>", "", text)

        # --- Remove escaped characters ---
        text = re.sub(r"\\([!\"#$%&'()*+,./:;<=>?@\\[]^_`{|}~-])", r"\1", text)

        return text

    @staticmethod
    def convert_markdown_to_html(text: str) -> str:
        """
        Given a markdown string, convert it to HTML and return the HTML string.

        :param text: The markdown string to convert.
        :return: The HTML string.
        """
        if not text:
            return ""

        # Replace newlines with break tags and tabs with em spaces.
        text = text.replace("\r\n", "<br>").replace("\n", "<br>").replace("\t", "&emsp;")

        # Format code blocks to maintain indentation.
        text = HtmlFormatter.format_code_blocks(text, "<br>")

        # Convert any other markdown to HTML.
        text = HtmlFormatter._convert_markdown_by_line(text)

        return text

    @staticmethod
    def format_code_blocks(text: str, newline: str = "\n") -> str:
        """
        Locate each markdown code block in the given text and format it with HTML code and preformatting tags
        to maintain indentation and add language-specific syntax highlighting.

        :param text: The text to format.
        :param newline: The newline character to expect in the input text.
        :return: The formatted text.
        """
        # Extract all the code blocks from the text
        code_blocks = HtmlFormatter.extract_code_blocks(text, newline)
        if not code_blocks:
            return text

        # Iterate through the code blocks, adding them to the text with the <pre><code> </code></pre>
        # so that indentation is preserved.
        current_index = 0
        formatted = []
        for code_block in code_blocks:
            formatted.append(text[current_index:code_block.start_index])
            formatted.append(code_block.to_html())
            current_index = code_block.end_index
        # Append the rest of the text after the last code block.
        formatted.append(text[current_index:])
        return "".join(formatted)

    @staticmethod
    def sanitize_code_blocks(text: str, newline: str = "\n") -> str:
        """
        Given the input text, remove all code blocks while leaving all other text unchanged.
        For use in any location where we don't want to display code (because it's scary).

        :param text: The text to sanitize.
        :param newline: The newline character to expect in the input text.
        :return: The sanitized text.
        """
        code_blocks = HtmlFormatter.extract_code_blocks(text, newline)

        if not code_blocks:
            return text

        current_index = 0
        formatted_text = []

        for block in code_blocks:
            formatted_text.append(text[current_index: block.start_index])
            current_index = block.end_index

        formatted_text.append(text[current_index:])

        return "".join(formatted_text)

    @staticmethod
    def extract_code_blocks(text: str, newline: str = "\n") -> list[CodeBlock]:
        """
        Extract all code blocks from the given response.

        :param text: The text to extract the code blocks from.
        :param newline: The newline character to expect in the input text.
        :return: A list of code blocks.
        """
        code: list[CodeBlock] = []
        current_index = 0
        while current_index < len(text):
            code_block = HtmlFormatter.next_code_block(text, current_index, newline)
            if code_block is None:
                break
            code.append(code_block)
            current_index = code_block.end_index
        return code

    @staticmethod
    def next_code_block(text: str, start_index: int, newline: str = "\n") -> CodeBlock | None:
        """
        Extract the next code block from the given response, starting at the given index.

        :param text: The text to extract the code block from.
        :param start_index: The index to start searching for the code block at.
        :param newline: The newline character to expect in the input text.
        :return: The extracted code block. Null if no code block is found after the start index.
        """
        # Find the start of the next code block.
        start_tag = text.find("```", start_index)
        if start_tag == -1:
            return None

        # Extract the language from the starting tag of the code block.
        first_line = text.find(newline, start_tag)
        if first_line == -1:
            return None
        language = text[start_tag + 3:first_line].strip()
        first_line += len(newline)

        # Find the end of the code block.
        code: str
        end_tag = text.find("```", first_line)
        # If there is no end to the code block, just return the rest of the text as a code block.
        if end_tag == -1:
            end_tag = len(text)
            code = text[first_line:end_tag]
        else:
            code = text[first_line:end_tag]
            end_tag += 3
        return CodeBlock(code, language, start_tag, end_tag)

    @staticmethod
    def _convert_markdown_by_line(text: str) -> str:
        """
        Convert markdown to HTML for each line in the given markdown text.  Line breaks are expected to be represented
        by break tags already.

        :param text: The markdown text to convert.
        :return: The HTML text.
        """
        html = []
        lines = text.split("<br>")

        in_unordered_list = False
        in_ordered_list = False

        for line in lines:
            # Skip code blocks, as these have already been formatted.
            # Also skip empty lines.
            if "</code></pre>" in line or not line.strip():
                html.append(line + "<br>")
                continue
            processed_line = HtmlFormatter._process_line(line.strip())

            # Handle headings
            if processed_line.startswith("# "):
                HtmlFormatter._close_lists(html, in_unordered_list, in_ordered_list)
                in_unordered_list = False
                in_ordered_list = False
                html.append(HtmlFormatter.header_1(processed_line[2:].strip()) + "<br>")
            elif processed_line.startswith("## "):
                HtmlFormatter._close_lists(html, in_unordered_list, in_ordered_list)
                in_unordered_list = False
                in_ordered_list = False
                html.append(HtmlFormatter.header_2(processed_line[3:].strip()) + "<br>")
            elif processed_line.startswith("### "):
                HtmlFormatter._close_lists(html, in_unordered_list, in_ordered_list)
                in_unordered_list = False
                in_ordered_list = False
                html.append(HtmlFormatter.header_3(processed_line[4:].strip()) + "<br>")
            # Handle unordered lists
            elif processed_line.startswith("* "):
                if not in_unordered_list:
                    HtmlFormatter._close_lists(html, False, in_ordered_list)  # Close any previous ordered list.
                    in_ordered_list = False
                    html.append("<ul>")
                    in_unordered_list = True
                html.append("<li>" + HtmlFormatter.body(processed_line[2:].strip()) + "</li>")
            # Handle ordered lists
            elif re.match(r"^\d+\. .*", processed_line):  # Matches "1. text"
                if not in_ordered_list:
                    HtmlFormatter._close_lists(html, in_unordered_list, False)  # Close any previous unordered list.
                    in_unordered_list = False
                    html.append("<ol>")
                    in_ordered_list = True
                html.append(
                    "<li>" + HtmlFormatter.body(processed_line[processed_line.find('.') + 2:].strip()) + "</li>")

            # Handle regular paragraphs
            else:
                HtmlFormatter._close_lists(html, in_unordered_list, in_ordered_list)
                in_unordered_list = False
                in_ordered_list = False
                html.append(HtmlFormatter.body(processed_line.strip()) + "<br>")

        # Close any open lists at the end
        HtmlFormatter._close_lists(html, in_unordered_list, in_ordered_list)

        return "".join(html)

    @staticmethod
    def _close_lists(text: list, in_unordered_list: bool, in_ordered_list: bool):
        """
        Close any open unordered or ordered lists in the given HTML string.

        :param text: The HTML string to append to.
        :param in_unordered_list: Whether an unordered list is currently open.
        :param in_ordered_list: Whether an ordered list is currently open.
        """
        if in_unordered_list:
            text.append("</ul>")
        if in_ordered_list:
            text.append("</ol>")

    @staticmethod
    def _process_line(line: str) -> str:
        """
        Process a single line of markdown text and convert it to HTML.

        :param line: The line of markdown text to process.
        :return: The HTML formatted line.
        """
        # Bold: **text**
        line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)

        # Italic: *text*
        line = re.sub(r"\*(.*?)\*", r"<em>\1</em>", line)

        # Code: `text`
        line = re.sub(r"`(.*?)`", r"<code>\1</code>", line)

        return line


class CodeBlock:
    """
    A class representing a code block extracted from a response.
    """
    def __init__(self, code: str, language: str, start_index: int, end_index: int):
        """
        :param code: The text of the code block.
        :param language: The language of the code block.
        :param start_index: The index of the first character of the code block in the original response.
        :param end_index: The index after the last character of the code block in the original response.
        """
        if code is None:
            raise ValueError("Code cannot be None")
        if language is None:
            language = ""
        if start_index < 0 or end_index < 0 or start_index > end_index:
            raise ValueError("Invalid start or end index")

        # Replace em spaces within code blocks with quadruple spaces and break tags with newlines.
        # Code editors that the code is copy/pasted into might not recognize em spaces as valid indentation,
        # and the library that adds the language-specific syntax highlighting expects newlines instead of break
        # tags.
        if "<br>" in code:
            code = code.replace("<br>", "\n")
        if "&emsp;" in code:
            code = code.replace("&emsp;", "    ")
        # We don't want mixed whitespace, so replace all tabs with quad spaces.
        if "\t" in code:
            code = code.replace("\t", "    ")

        self.code = code
        self.language = language.strip()
        self.start_index = start_index
        self.end_index = end_index

    def to_html(self) -> str:
        """
        :return: The HTML representation of this code block.
        """
        start_tag: str
        if self.language:
            lang_class = f'class="language-{self.language}"'
            start_tag = f"<pre {lang_class}><code {lang_class}>"
        else:
            start_tag = "<pre><code>"
        end_tag = "</code></pre>"

        return start_tag + self.code + end_tag

    def to_markdown(self) -> str:
        """
        :return: The markdown representation of this code block.
        """
        start_tag = f"```{self.language}\n"
        end_tag = "```" if self.code.endswith("\n") else "\n```"

        return start_tag + self.code + end_tag
