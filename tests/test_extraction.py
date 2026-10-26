"""Extraction: few-shot prompts, chain-of-thought template, field parsing."""

from finance_data_validation import extraction as ex


def test_few_shot_examples_are_synthetic_and_complete():
    assert len(ex.FEW_SHOT_EXAMPLES) >= 3
    for example in ex.FEW_SHOT_EXAMPLES:
        assert example["text"] and example["fields"]


def test_prompt_contains_examples_then_target():
    prompt = ex.build_few_shot_prompt("Revenue was $10,000.")
    assert "Example 1 input:" in prompt
    assert "Target input: Revenue was $10,000." in prompt
    assert prompt.index("Example 1 input:") < prompt.index("Target input:")


def test_prompt_includes_cot_steps():
    prompt = ex.build_few_shot_prompt("Revenue was $10,000.")
    for step in ex.chain_of_thought_template():
        assert step in prompt


def test_cot_template_is_ordered_and_fixed():
    steps = ex.chain_of_thought_template()
    assert len(steps) == 5
    assert steps[0].startswith("1.")
    assert steps[-1].startswith("5.")
    steps.append("tampered")
    assert len(ex.chain_of_thought_template()) == 5


def test_extract_revenue_expenses_net_income():
    result = ex.extract_fields(
        "Revenue was $500,000 and expenses were $320,000, "
        "net income $180,000. Source: Q3 ledger note 2026-07.")
    assert result.fields == {"revenue": 500000.0, "expenses": 320000.0,
                             "net_income": 180000.0}
    assert result.source_citation == "Q3 ledger note 2026-07"


def test_extract_balance_sheet_fields():
    result = ex.extract_fields(
        "Total assets $2,400,000; total liabilities $900,000. "
        "Source: balance sheet draft 2026-06.")
    assert result.fields == {"total_assets": 2400000.0,
                             "total_liabilities": 900000.0}


def test_extract_negative_net_income():
    result = ex.extract_fields(
        "Revenue $120,000, expenses $150,000, net income -$30,000.")
    assert result.fields["net_income"] == -30000.0


def test_extract_emits_only_found_fields():
    result = ex.extract_fields("Revenue was $42,000.")
    assert result.fields == {"revenue": 42000.0}
    assert "net_income" not in result.fields


def test_extract_missing_citation_recorded():
    result = ex.extract_fields("Revenue was $42,000.")
    assert result.source_citation is None
    assert any("No source citation" in step for step in result.reasoning)


def test_extract_period_found():
    result = ex.extract_fields("Revenue was $42,000 in 2026-Q3.")
    assert result.period == "2026-Q3"


def test_extract_reasoning_names_each_field():
    result = ex.extract_fields("Revenue was $42,000, expenses $10,000.")
    assert any("revenue" in step for step in result.reasoning)
    assert any("expenses" in step for step in result.reasoning)


def test_extract_ignores_unlabelled_numbers():
    # A bare year/number with no label must not become a field.
    result = ex.extract_fields("Note 2026: revenue was $42,000.")
    assert result.fields == {"revenue": 42000.0}
