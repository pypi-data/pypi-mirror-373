"""
XML File Parser Module

This module provides functionality for parsing XML files into structured document
representations, converting XML structures into readable markdown format.
"""

import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Literal
from xml.etree.ElementTree import Element

from rsb.models.config_dict import ConfigDict
from rsb.models.field import Field

from agentle.parsing.document_parser import DocumentParser
from agentle.parsing.parsed_file import ParsedFile
from agentle.parsing.section_content import SectionContent
from agentle.utils.file_validation import (
    FileValidationError,
    resolve_file_path,
    validate_file_exists,
)

logger = logging.getLogger(__name__)


class XMLFileParser(DocumentParser):
    """
    Parser for processing XML files into structured document representations.

    This parser reads XML files and converts them into a ParsedFile representation,
    transforming the XML structure into a nested markdown format for better readability.
    The parser attempts to preserve the hierarchical structure of the XML by using
    indented markdown lists, making complex XML documents easier to navigate and understand.

    **Attributes:**

    *   `type` (Literal["xml"]):
        Constant that identifies this as an XML parser. Always set to "xml".

    **Usage Examples:**

    Basic parsing of an XML file:
    ```python
    from agentle.parsing.parsers.xml import XMLFileParser

    # Create a parser
    parser = XMLFileParser()

    # Parse an XML file
    parsed_doc = parser.parse("config.xml")

    # Access the structured content
    print(parsed_doc.sections[0].md)  # Outputs formatted markdown representation
    ```

    Using the parser through the facade:
    ```python
    from agentle.parsing.parse import parse

    # Parse an XML file
    parsed_doc = parse("data.xml")

    # Get original XML content
    raw_xml = parsed_doc.sections[0].text

    # Get markdown representation
    markdown_format = parsed_doc.sections[0].md

    print(f"First 100 chars of markdown representation:\n{markdown_format[:100]}...")
    ```
    """

    type: Literal["xml"] = Field(default="xml")

    async def parse_async(self, document_path: str) -> ParsedFile:
        """
        Asynchronously parse an XML file into a structured representation.

        This method reads an XML file, attempts to parse its structure, and converts it
        into a ParsedFile with a single section containing both the raw XML text
        and a markdown representation of the XML structure.

        Args:
            document_path (str): Path to the XML file to be parsed

        Returns:
            ParsedFile: A structured representation of the XML file with:
                - text: The raw XML text content
                - md: A markdown representation of the XML structure

        Example:
            ```python
            import asyncio
            from agentle.parsing.parsers.xml import XMLFileParser

            async def process_xml_file():
                parser = XMLFileParser()
                result = await parser.parse_async("settings.xml")

                # Print the formatted markdown representation
                print(result.sections[0].md)

            asyncio.run(process_xml_file())
            ```
        """
        try:
            # Validate and resolve the file path
            resolved_path = resolve_file_path(document_path)
            validate_file_exists(resolved_path)

            file = Path(resolved_path)
            logger.debug(f"Reading XML file: {resolved_path}")

            # Read file bytes with comprehensive error handling
            try:
                raw_bytes = file.read_bytes()
            except PermissionError as e:
                logger.error(f"Permission denied reading XML file: {resolved_path}")
                raise ValueError(
                    f"Permission denied: Cannot read XML file '{document_path}'. Please check file permissions."
                ) from e
            except OSError as e:
                logger.error(f"OS error reading XML file: {resolved_path} - {e}")
                raise ValueError(
                    f"Failed to read XML file '{document_path}': {e}"
                ) from e

            # Decode bytes to string with encoding fallback
            try:
                raw_xml = raw_bytes.decode("utf-8", errors="replace")
            except UnicodeDecodeError as e:
                logger.warning(
                    f"Unicode decode error in XML file: {resolved_path} - {e}"
                )
                # Try with different encodings as fallback
                try:
                    raw_xml = raw_bytes.decode("latin-1", errors="replace")
                    logger.info(
                        f"Successfully read XML file using latin-1 encoding: {resolved_path}"
                    )
                except Exception as fallback_error:
                    logger.error(
                        f"Failed to decode XML file with fallback encoding: {fallback_error}"
                    )
                    raise ValueError(
                        f"Cannot decode XML file '{document_path}': {e}"
                    ) from e

            if not raw_xml.strip():
                logger.warning(f"XML file appears to be empty: {resolved_path}")

            # Convert XML to markdown with error handling
            try:
                md_content = self.xml_to_md(raw_xml)
            except Exception as e:
                logger.error(
                    f"Failed to convert XML to markdown: {resolved_path} - {e}"
                )
                # Fallback to raw XML if conversion fails
                md_content = f"```xml\n{raw_xml}\n```"
                logger.info(
                    f"Using raw XML as fallback for markdown conversion: {resolved_path}"
                )

            section_content = SectionContent(
                number=1,
                text=raw_xml,
                md=md_content,
                images=[],
                items=[],
            )

            logger.debug(
                f"Successfully parsed XML file: {resolved_path} ({len(raw_xml)} characters)"
            )

            return ParsedFile(
                name=file.name,
                sections=[section_content],
            )

        except FileValidationError as e:
            logger.error(f"File validation failed for XML file: {e}")
            raise ValueError(f"XML file validation failed: {e}") from e

    def xml_to_md(self, xml_str: str) -> str:
        """
        Converts XML content into a nested Markdown list structure.

        This method parses XML content and transforms it into a markdown format
        that preserves the hierarchical structure by using nested lists with
        appropriate indentation. The resulting markdown is more readable and
        navigable than raw XML.

        Args:
            xml_str (str): XML content as a string

        Returns:
            str: Markdown representation of the XML content, or raw XML in a code
                block if parsing fails

        Example:
            ```python
            from agentle.parsing.parsers.xml import XMLFileParser

            parser = XMLFileParser()
            xml_content = '<root><item>Value</item><nested><child>Data</child></nested></root>'
            markdown = parser.xml_to_md(xml_content)
            print(markdown)
            # Output:
            # - **root**
            #   - **item**
            #     - *Text*: Value
            #   - **nested**
            #     - **child**
            #       - *Text*: Data
            ```
        """
        try:
            root: Element = ET.fromstring(xml_str)
            return self._convert_element_to_md(root, level=0)
        except ET.ParseError as e:
            logger.exception("Error parsing XML: %s", e)
            return "```xml\n" + xml_str + "\n```"  # Fallback to raw XML in code block

    def _convert_element_to_md(self, element: Element, level: int) -> str:
        """
        Recursively converts an XML element and its children to Markdown.

        This helper method handles the conversion of a single XML element to markdown,
        then recursively processes all child elements, maintaining appropriate indentation
        for each level of nesting.

        Args:
            element (Element): The XML element to convert
            level (int): Current nesting level for indentation

        Returns:
            str: Markdown representation of the element and its children

        Note:
            This method is intended for internal use by the xml_to_md method.
        """
        indent = "  " * level
        lines: list[str] = []

        # Element tag as bold item
        lines.append(f"{indent}- **{element.tag}**")

        # Attributes as sub-items
        if element.attrib:
            lines.append(f"{indent}  - *Attributes*:")
            for key, value in element.attrib.items():
                lines.append(f"{indent}    - `{key}`: `{value}`")

        # Text content
        if element.text and element.text.strip():
            text = element.text.strip().replace("\n", " ")
            lines.append(f"{indent}  - *Text*: {text}")

        # Process child elements recursively
        for child in element:
            lines.append(self._convert_element_to_md(child, level + 1))

        return "\n".join(lines)

    model_config = ConfigDict(frozen=True)
