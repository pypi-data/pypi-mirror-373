"""
Tests for logging configuration functionality.
"""
from ss_utils_safe_python import to_snake_case

def test_snake_case_converter():
    """Test the snake_case converter with various report section examples."""
    test_cases = [
        # Basic cases
        ("Executive Summary", "executive_summary"),
        ("Introduction", "introduction"),
        # CamelCase
        ("FinancialPerformance", "financial_performance"),
        ("CompanyOverview", "company_overview"),
        ("RiskAssessment", "risk_assessment"),
        # Title Case with spaces
        ("Market Analysis", "market_analysis"),
        ("Business Strategy", "business_strategy"),
        ("Corporate Governance", "corporate_governance"),
        # UPPER CASE
        ("FINANCIAL STATEMENTS", "financial_statements"),
        ("RISK FACTORS", "risk_factors"),
        # kebab-case
        ("sustainability-report", "sustainability_report"),
        ("cash-flow-analysis", "cash_flow_analysis"),
        # Mixed formats
        ("Section 1.2: Company Overview", "section_1_2_company_overview"),
        ("Part A - Financial Results", "part_a_financial_results"),
        ("Chapter 3: Market Position", "chapter_3_market_position"),
        # Special characters
        ("ESG & Sustainability", "esg_sustainability"),
        ("P&L Statement", "p_l_statement"),
        ("Q1/Q2 Performance", "q1_q2_performance"),
        ("Cost-Benefit Analysis", "cost_benefit_analysis"),
        # Numbers and mixed
        ("2023 Annual Report", "2023_annual_report"),
        ("Q4 2023 Results", "q4_2023_results"),
        ("5-Year Plan", "5_year_plan"),
        # Complex real-world examples
        ("Environmental, Social & Governance (ESG) Report", "environmental_social_governance_esg_report"),
        ("Management's Discussion & Analysis", "management_s_discussion_analysis"),
        ("Notes to Financial Statements", "notes_to_financial_statements"),
        ("Independent Auditor's Report", "independent_auditor_s_report"),
        # Edge cases
        ("", ""),
        ("   ", ""),
        ("___", ""),
        ("A", "a"),
        ("ABC", "abc"),
        ("a_b_c", "a_b_c"),  # Already snake_case
    ]

    for input_text, expected in test_cases:
        result = to_snake_case(input_text)
        assert result == expected, f"Failed for '{input_text}': got '{result}', expected '{expected}'"
