#!/usr/bin/env python3
"""
File Path Handling Best Practices for Agentle Static Knowledge

This example demonstrates proper file path handling when using static_knowledge
with Agentle agents. It shows various approaches for different scenarios and
how to handle potential errors gracefully.
"""

from pathlib import Path
from typing import List
from dotenv import load_dotenv

from agentle.agents.agent import Agent
from agentle.agents.knowledge.static_knowledge import StaticKnowledge
from agentle.generations.providers.google.google_generation_provider import (
    GoogleGenerationProvider,
)
from agentle.parsing.parsers.file_parser import FileParser

load_dotenv()


def demonstrate_file_path_best_practices():
    """
    Demonstrates various file path handling approaches for static_knowledge.
    """
    print("=== Agentle File Path Best Practices Demo ===")
    print()

    # Initialize provider
    google_provider = GoogleGenerationProvider()

    # ========================================
    # 1. RECOMMENDED: Using absolute paths with Path
    # ========================================
    print("1. Using absolute paths with pathlib.Path (RECOMMENDED)")

    # Get the directory where this script is located
    script_dir = Path(__file__).parent

    # Build absolute paths to documents
    curriculum_path = script_dir / "curriculum.pdf"

    # Check if file exists before creating agent
    if curriculum_path.exists():
        print(f"✓ Found curriculum file: {curriculum_path}")

        agent_with_absolute_path = Agent(
            name="Document Expert",
            generation_provider=google_provider,
            model="gemini-2.5-flash",
            static_knowledge=[
                StaticKnowledge(
                    content=str(curriculum_path),  # Convert Path to string
                    cache=3600,  # Cache for 1 hour
                    parse_timeout=60,
                )
            ],
            document_parser=FileParser(
                strategy="high",
                visual_description_provider=google_provider,
            ),
            instructions="You are a helpful assistant with access to curriculum documents.",
        )

        try:
            response = agent_with_absolute_path.run(
                "What topics are covered in the curriculum?"
            )
            print(f"Response: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ Error processing document: {e}")
    else:
        print(f"⚠️  Curriculum file not found: {curriculum_path}")

    print()

    # ========================================
    # 2. Using relative paths (with caution)
    # ========================================
    print("2. Using relative paths (handle with care)")

    # Relative paths work but are less reliable
    relative_path = "./curriculum.pdf"

    try:
        _ = Agent(
            name="Relative Path Agent",
            generation_provider=google_provider,
            model="gemini-2.5-flash",
            static_knowledge=[
                StaticKnowledge(
                    content=relative_path,
                    cache=1800,  # Cache for 30 minutes
                )
            ],
            instructions="You are a helpful assistant.",
        )
        print(f"✓ Successfully created agent with relative path: {relative_path}")
    except ValueError as e:
        print(f"❌ Failed to create agent with relative path: {e}")

    print()

    # ========================================
    # 3. Multiple documents with mixed sources
    # ========================================
    print("3. Multiple documents with mixed sources")

    # Mix of local files, URLs, and raw text
    mixed_knowledge: List[StaticKnowledge] = []

    # Local file (absolute path)
    local_doc = script_dir / "curriculum.pdf"
    if local_doc.exists():
        mixed_knowledge.append(
            StaticKnowledge(
                content=str(local_doc),
                cache=7200,  # Cache for 2 hours
                parse_timeout=90,
            )
        )

    # URL (no file validation needed)
    mixed_knowledge.append(
        StaticKnowledge(
            content="https://example.com/public-document.pdf",
            cache=3600,  # Cache for 1 hour
            parse_timeout=120,
        )
    )

    # Raw text content
    mixed_knowledge.append(
        StaticKnowledge(
            content="This is important context: Always validate file paths before processing.",
            cache="infinite",  # Cache indefinitely
        )
    )

    if mixed_knowledge:
        try:
            _ = Agent(
                name="Multi-Source Agent",
                generation_provider=google_provider,
                model="gemini-2.5-flash",
                static_knowledge=mixed_knowledge,
                document_parser=FileParser(
                    strategy="low",  # Faster processing for demo
                ),
                instructions="You have access to multiple knowledge sources including local files, web documents, and contextual information.",
            )
            print(
                f"✓ Successfully created agent with {len(mixed_knowledge)} knowledge sources"
            )
        except Exception as e:
            print(f"❌ Failed to create multi-source agent: {e}")

    print()

    # ========================================
    # 4. Error handling and validation
    # ========================================
    print("4. Error handling and validation examples")

    # Example of handling non-existent files
    non_existent_file = script_dir / "non_existent_document.pdf"

    try:
        _ = Agent(
            name="Missing File Agent",
            generation_provider=google_provider,
            model="gemini-2.5-flash",
            static_knowledge=[
                StaticKnowledge(content=str(non_existent_file), cache=3600)
            ],
            instructions="This agent will fail due to missing file.",
        )
        print("❌ This should not succeed")
    except ValueError as e:
        print(f"✓ Properly caught file validation error: {e}")

    # Example of handling permission errors (simulated)
    print("\n5. Best practices summary:")
    print("   • Use absolute paths with pathlib.Path")
    print("   • Check file existence before creating agents")
    print("   • Handle ValueError exceptions for file validation errors")
    print("   • Use appropriate cache settings for different content types")
    print("   • Set reasonable parse_timeout values for large documents")
    print("   • Mix local files, URLs, and raw text as needed")


def demonstrate_path_utilities():
    """
    Shows how to use path utilities for robust file handling.
    """
    print("\n=== Path Utilities Demo ===")

    # Get current script directory
    script_dir = Path(__file__).parent
    print(f"Script directory: {script_dir}")

    # Build paths relative to script
    data_dir = script_dir / "data"
    config_file = script_dir / "config.json"

    print(f"Data directory: {data_dir}")
    print(f"Config file: {config_file}")

    # Check existence
    print(f"Data directory exists: {data_dir.exists()}")
    print(f"Config file exists: {config_file.exists()}")

    # Get absolute paths
    print(f"Absolute data path: {data_dir.resolve()}")
    print(f"Absolute config path: {config_file.resolve()}")

    # Safe file listing
    if script_dir.exists():
        print(f"\nFiles in script directory:")
        for file_path in script_dir.iterdir():
            if file_path.is_file():
                print(f"  - {file_path.name} ({file_path.stat().st_size} bytes)")


if __name__ == "__main__":
    try:
        demonstrate_file_path_best_practices()
        demonstrate_path_utilities()
    except Exception as e:
        print(f"Demo failed: {e}")
        print("\nNote: This demo requires a valid Google API key in your environment.")
        print("Set GOOGLE_API_KEY in your .env file or environment variables.")
