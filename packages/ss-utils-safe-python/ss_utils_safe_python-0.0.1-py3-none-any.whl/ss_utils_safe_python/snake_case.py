import re
import unicodedata


def to_snake_case(text: str) -> str:
    """
    Convert any string to snake_case format.

    This function handles various input formats including:
    - CamelCase / PascalCase
    - kebab-case
    - Title Case
    - UPPER CASE
    - Mixed formats
    - Special characters and numbers
    - Unicode characters

    Args:
        text (str): The input string to convert

    Returns:
        str: The snake_case version of the input string

    Examples:
        >>> to_snake_case("Executive Summary")
        'executive_summary'
        >>> to_snake_case("FinancialPerformance")
        'financial_performance'
        >>> to_snake_case("risk-assessment")
        'risk_assessment'
        >>> to_snake_case("MARKET ANALYSIS")
        'market_analysis'
        >>> to_snake_case("Section 1.2: Company Overview")
        'section_1_2_company_overview'
        >>> to_snake_case("ESG & Sustainability Report")
        'esg_sustainability_report'
    """
    if not text or not isinstance(text, str):
        return ""

    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)

    # Remove or replace common punctuation and special characters
    # Keep alphanumeric characters and some separators temporarily
    text = re.sub(r"[^\w\s\-_.]", " ", text)

    # Handle CamelCase by inserting spaces before uppercase letters
    # This regex looks for lowercase followed by uppercase
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)

    # Replace multiple separators (spaces, hyphens, underscores, dots) with single space
    text = re.sub(r"[\s\-_.]+", " ", text)

    # Split into words, filter empty strings, and convert to lowercase
    words = [word.lower() for word in text.split() if word]

    # Join with underscores
    return "_".join(words)
