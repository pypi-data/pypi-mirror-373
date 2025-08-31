"""
Text File Parser Module

This module provides functionality for parsing plain text files (.txt, .alg)
into structured document representations.
"""

import logging
from pathlib import Path
from typing import Literal

from agentle.parsing.document_parser import DocumentParser
from agentle.parsing.parsed_file import ParsedFile
from agentle.parsing.section_content import SectionContent
from agentle.utils.file_validation import (
    FileValidationError,
    resolve_file_path,
    validate_file_exists,
)

logger = logging.getLogger(__name__)


class TxtFileParser(DocumentParser):
    """
    Parser for processing plain text files (.txt, .alg).

    This parser provides a simple implementation for reading text files and converting
    them into a structured ParsedFile representation. The parser reads the entire
    file content and places it into a single section. It handles both .txt files and
    .alg (algorithm) files.

    This parser is one of the simplest implementations in the framework, as it doesn't
    require any special processing like OCR, media analysis, or structural parsing.

    **Usage Examples:**

    Basic parsing of a text file:
    ```python
    from agentle.parsing.parsers.txt import TxtFileParser

    # Create a parser
    parser = TxtFileParser()

    # Parse a text file
    parsed_doc = parser.parse("notes.txt")

    # Access the text content
    print(parsed_doc.sections[0].text)
    ```

    Using the parser through the facade:
    ```python
    from agentle.parsing.parse import parse

    # Parse a text file using the facade
    parsed_doc = parse("algorithm.alg")

    # Access the content
    content = parsed_doc.sections[0].text
    print(f"Algorithm content:\n{content}")
    ```
    """

    type: Literal["txt"] = "txt"

    async def parse_async(self, document_path: str) -> ParsedFile:
        """
        Asynchronously parse a text file into a structured representation.

        This method reads the content of a text file and converts it into a ParsedFile
        with a single section containing the file's text.

        Args:
            document_path (str): Path to the text file to be parsed

        Returns:
            ParsedFile: A structured representation of the text file with a
                single section containing the entire file content

        Example:
            ```python
            import asyncio
            from agentle.parsing.parsers.txt import TxtFileParser

            async def process_text_file():
                parser = TxtFileParser()
                result = await parser.parse_async("instructions.txt")
                print(f"File name: {result.name}")
                print(f"Content: {result.sections[0].text}")

            asyncio.run(process_text_file())
            ```

        Note:
            This parser handles UTF-8 encoded text files and uses error replacement
            for any characters that cannot be decoded properly.
        """
        try:
            # Validate and resolve the file path
            resolved_path = resolve_file_path(document_path)
            validate_file_exists(resolved_path)

            path = Path(resolved_path)
            logger.debug(f"Reading text file: {resolved_path}")

            # Read file content with comprehensive error handling
            try:
                text_content = path.read_text(encoding="utf-8", errors="replace")
            except PermissionError as e:
                logger.error(f"Permission denied reading file: {resolved_path}")
                raise ValueError(
                    f"Permission denied: Cannot read file '{document_path}'. Please check file permissions."
                ) from e
            except OSError as e:
                logger.error(f"OS error reading file: {resolved_path} - {e}")
                raise ValueError(f"Failed to read file '{document_path}': {e}") from e
            except UnicodeDecodeError as e:
                logger.warning(f"Unicode decode error in file: {resolved_path} - {e}")
                # Try with different encodings as fallback
                try:
                    text_content = path.read_text(encoding="latin-1", errors="replace")
                    logger.info(
                        f"Successfully read file using latin-1 encoding: {resolved_path}"
                    )
                except Exception as fallback_error:
                    logger.error(
                        f"Failed to read file with fallback encoding: {fallback_error}"
                    )
                    raise ValueError(
                        f"Cannot decode text file '{document_path}': {e}"
                    ) from e

            if not text_content.strip():
                logger.warning(f"File appears to be empty: {resolved_path}")

            page_content = SectionContent(
                number=1,
                text=text_content,
                md=text_content,
            )

            logger.debug(
                f"Successfully parsed text file: {resolved_path} ({len(text_content)} characters)"
            )

            return ParsedFile(
                name=path.name,
                sections=[page_content],
            )

        except FileValidationError as e:
            logger.error(f"File validation failed for text file: {e}")
            raise ValueError(f"Text file validation failed: {e}") from e
