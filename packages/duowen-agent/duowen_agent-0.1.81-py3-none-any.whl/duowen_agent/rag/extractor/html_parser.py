import re
import xml.etree.ElementTree as ET
from typing import List, Union

import html2text
import trafilatura
from bs4 import BeautifulSoup, Tag


class TrafilaturaExtends:

    @staticmethod
    def extract(
        html: str,
    ) -> str | None:
        """
        Extracts content from HTML using Trafilatura library.
        Args:
            html: The HTML string to extract content from.
        Returns:
            The extracted content as a string.
        """
        data = trafilatura.extract(
            html,
            output_format="xml",
            include_tables=True,
            include_images=True,
            include_links=True,
        )

        if data is None:
            return None
        data = TrafilaturaExtends._replace_tags(data)
        data = TrafilaturaExtends._convert_xml_to_html(data)
        return data

    @staticmethod
    def _replace_function(match) -> str:
        # dd-1 などの-1を取り除く
        rend_value = match.group(1)
        if "-" in rend_value:
            rend_value = rend_value.split("-")[0]
        return f"<{rend_value}>{match.group(2)}</{rend_value}>"

    @staticmethod
    def _replace_tags(input_string: str):
        patterns = [
            (r'<list rend="([^"]*)">([\s\S]*?)</list>', r"<\1>\2</\1>"),
            (
                r'<item rend="([^"]+)">([\s\S]*?)</item>',
                TrafilaturaExtends._replace_function,
            ),
            (r"<item>([\s\S]*?)</item>", r"<li>\1</li>"),
            (r"<lb\s*/>", "<br />"),
            (r'<head rend="([^"]+)">([\s\S]*?)</head>', r"<\1>\2</\1>"),
            (r"<row.*?>([\s\S]*?)</row>", r"<tr>\1</tr>"),
            (r'<cell role="head">([\s\S]*?)</cell>', r"<th>\1</th>"),
            (r"<cell>([\s\S]*?)</cell>", r"<td>\1</td>"),
            (r"<graphic (.*?)>", lambda match: f"<img {match.group(1)}>"),
            (r'<ref target="([\s\S]*?)">([\s\S]*?)</ref>', r'<a href="\1">\2</a>'),
            (r"<main>([\s\S]*?)</main>", r"\1"),
            (r"<main\s*/>", ""),
            (r"<comments>([\s\S]*?)</comments>", r"\1"),
            (r"<comments\s*/>", ""),
        ]

        for pattern, replacement in patterns:
            input_string = re.sub(pattern, replacement, input_string)

        return input_string

    @staticmethod
    def _convert_xml_to_html(xml_string: str) -> str:
        root = ET.fromstring(xml_string)
        title = root.get("title") or ""
        author = root.get("author") or ""
        date = root.get("date") or ""
        url = root.get("url") or ""
        description = root.get("description") or ""
        categories = root.get("categories") or ""
        tags = root.get("tags") or ""
        fingerprint = root.get("fingerprint") or ""

        content = "".join(ET.tostring(child, encoding="unicode") for child in root)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            {''.join(f'<meta name="{key}" content="{value}">' for key, value in [
                ("title", title),
                ("author", author),
                ("date", date),
                ("url", url),
                ("description", description),
                ("categories", categories),
                ("tags", tags),
                ("fingerprint", fingerprint)
            ] if value)}
            <title>{title}</title>
        </head>
        <body>
            {content}
        </body>
        </html>
        """

        return html_content


REMOVE_ELEMENT_LIST_DEFAULT: List[str] = [
    "script",
    "style",
    "aside",
    "footer",
    "header",
    "hgroup",
    "nav",
    "search",
]


class MainContentExtractor:

    @staticmethod
    def extract(
        html: str,
        output_format: str = "html",
        include_links: bool = True,
        ref_extraction_method=None,
        **html2text_kwargs,
    ) -> str:
        """
        Extracts the main content from an HTML string.

        Args:
            html: The HTML string to extract the main content from.
            output_format: The format of the extracted content (html, text, markdown).
            include_links: Whether to include links in the extracted content.
            ref_extraction_method: A dictionary to store the reference to the extraction method.
            **html2text_kwargs: Additional keyword arguments to be passed to the html2text library for markdown conversion.
                View options here: https://github.com/Alir3z4/html2text/blob/master/docs/usage.md

        Returns:
            The extracted main content as a string.
        """
        if ref_extraction_method is None:
            ref_extraction_method = {}
        valid_formats = ["html", "text", "markdown"]

        if output_format not in valid_formats:
            raise ValueError(
                f"Invalid output_format: {output_format}. Valid formats are: "
                f"{', '.join(valid_formats)}."
            )

        soup = BeautifulSoup(html, "html.parser")
        soup = MainContentExtractor._remove_elements(soup, REMOVE_ELEMENT_LIST_DEFAULT)

        main_content = soup.find("main")

        result_html = None
        extraction_method = None

        if main_content:
            extraction_method = "main_element"
            articles = main_content.find_all("article")

            if articles:
                result_html = "".join(str(article) for article in articles)
            else:
                result_html = str(main_content)
        else:
            extraction_method = "article_element"
            articles = soup.find_all("article")

            if articles:
                result_html = "".join(str(article) for article in articles)
            else:
                main_content = MainContentExtractor._get_deepest_element_data(
                    soup, ["contents", "main"]
                )
                if main_content:
                    extraction_method = "deepest_element_data"
                    result_html = str(main_content)
                else:
                    extraction_method = "trafilatura_extract"
                    result_html = TrafilaturaExtends.extract(str(soup))

        if result_html:
            soup = BeautifulSoup(result_html, "html.parser")

            if ref_extraction_method is not None:
                ref_extraction_method["extraction_method"] = extraction_method

            if output_format == "text":
                return soup.get_text(strip=True)

            if not include_links:
                soup = MainContentExtractor._remove_elements_keep_text(
                    soup, ["a", "img"]
                )
            if output_format == "html":
                return soup.prettify()
            elif output_format == "markdown":
                # Convert HTML to Markdown using html2text with configuration
                mdconverter = html2text.HTML2Text(**html2text_kwargs)
                return mdconverter.handle(str(soup))

    @staticmethod
    def extract_links(html_content: str, **kwargs) -> dict:
        """
        Extracts links from HTML content and returns a dictionary with link information.

        Args:
            html_content (str): The HTML content from which to extract links.

        Returns:
            dict: A dictionary containing link information with link URLs as keys and a dictionary
            with link text and URL as values.
        """
        extracted_html = MainContentExtractor.extract(html_content, **kwargs)
        soup = BeautifulSoup(extracted_html, "html.parser")

        links = {}
        for a_tag in soup.find_all("a"):
            link_text = a_tag.get_text(strip=True)
            if not link_text:
                continue
            link_url = a_tag.get("href")
            if not link_url:
                continue
            links[link_url] = {"text": link_text, "url": link_url}

        return links

    @staticmethod
    def extract_images(html_content: str, **kwargs) -> dict:
        """
        Extracts images from HTML content and returns a dictionary with image information.

        Args:
            html_content (str): The HTML content from which to extract images.

        Returns:
            dict: A dictionary containing image information with image URLs as keys and a dictionary
            with image alt text and URL as values.
        """
        extracted_html = MainContentExtractor.extract(html_content, **kwargs)
        soup = BeautifulSoup(extracted_html, "html.parser")

        images = {}
        for img_tag in soup.find_all("img"):
            image_alt = img_tag.get("alt", "")
            image_url = img_tag.get("src")
            images[image_url] = {"alt": image_alt, "url": image_url}

        return images

    @staticmethod
    def _remove_elements(soup: BeautifulSoup, elements: List[str]) -> BeautifulSoup:
        """
        Removes specified elements from a BeautifulSoup object.
        Args:
            soup (BeautifulSoup): The BeautifulSoup object to modify.
            elements (List[str]): The list of elements to remove.
        Returns:
            BeautifulSoup: The modified BeautifulSoup object.
        """

        def remove_element(element: Tag) -> None:
            if element.name in elements:
                element.decompose()

        for element in soup.find_all():
            remove_element(element)

        return soup

    @staticmethod
    def _remove_elements_keep_text(
        soup: BeautifulSoup, target_element_list: List[str]
    ) -> BeautifulSoup:
        for element in soup.find_all():
            if element.name in target_element_list:
                element.unwrap()
        return soup

    def _get_deepest_element_data(
        soup: BeautifulSoup, target_ids: List[str]
    ) -> Union[BeautifulSoup, None]:
        """
        Finds the deepest element in the given BeautifulSoup object with the specified target IDs.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object representing the HTML.
            target_ids (List[str]): The list of target IDs to search for.

        Returns:
            Union[BeautifulSoup, None]: The deepest element found, or None if no matching element is found.
        """
        deepest_element = None
        deepest_depth = 0

        def find_deepest_element(element: BeautifulSoup, current_depth: int) -> None:
            nonlocal deepest_element, deepest_depth

            if element.has_attr("id") and element["id"] in target_ids:
                if current_depth > deepest_depth:
                    deepest_element = element
                    deepest_depth = current_depth

            for child in element.children:
                if child.name is not None:
                    find_deepest_element(child, current_depth + 1)

        find_deepest_element(soup, 0)

        return deepest_element
