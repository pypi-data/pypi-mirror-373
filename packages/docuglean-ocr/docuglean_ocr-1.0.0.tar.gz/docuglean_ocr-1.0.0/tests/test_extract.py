"""
Extraction tests for Docuglean Python SDK.
Real integration tests with actual files and API calls.
"""

import os

import pytest
from pydantic import BaseModel

from docuglean import ExtractConfig, extract


# Define example schema for structured extraction
class Receipt(BaseModel):
    """Receipt schema for structured extraction."""

    date: str
    total: float
    items: list[dict[str, str | float]]


# Test URLs
TEST_PDF_URL = "https://arxiv.org/pdf/2302.12854"

# Skip tests if no API key
pytestmark = pytest.mark.skipif(not os.getenv("MISTRAL_API_KEY"), reason="MISTRAL_API_KEY not set")


@pytest.mark.asyncio
async def test_mistral_unstructured_pdf_url():
    """Test Mistral unstructured extraction with PDF URL."""
    config = ExtractConfig(
        file_path=TEST_PDF_URL,
        provider="mistral",
        model="mistral-small-latest",
        api_key=os.getenv("MISTRAL_API_KEY"),
        prompt="Summarize the main findings of this research paper.",
    )

    result = await extract(config)

    assert isinstance(result, str)
    assert len(result) > 0
    print(f"URL PDF extraction result: {result[:200]}...")


@pytest.mark.asyncio
async def test_mistral_unstructured_local_pdf():
    """Test Mistral unstructured extraction with local PDF."""
    config = ExtractConfig(
        file_path="./tests/data/receipt.pdf",
        provider="mistral",
        model="mistral-small-latest",
        api_key=os.getenv("MISTRAL_API_KEY"),
        prompt="Extract and summarize the receipt details.",
    )

    result = await extract(config)

    assert isinstance(result, str)
    assert len(result) > 0
    print(f"Local PDF extraction result: {result[:200]}...")


@pytest.mark.asyncio
async def test_mistral_structured_local_pdf():
    """Test Mistral structured extraction with local PDF."""
    config = ExtractConfig(
        file_path="./tests/data/receipt.pdf",
        provider="mistral",
        model="mistral-small-latest",
        api_key=os.getenv("MISTRAL_API_KEY"),
        response_format=Receipt,
        system_prompt="Extract receipt information from the document in a structured format.",
        prompt="Please extract the receipt details including date, total amount, and itemized list with prices.",
    )

    result = await extract(config)

    # For structured output, result should be StructuredExtractionResult
    assert hasattr(result, "raw") or isinstance(result, str)
    if hasattr(result, "raw"):
        assert hasattr(result, "parsed")
        print(f"Structured extraction - Raw: {result.raw[:100]}...")
        print(f"Structured extraction - Parsed: {result.parsed}")
    else:
        print(f"Structured extraction result: {result[:200]}...")
