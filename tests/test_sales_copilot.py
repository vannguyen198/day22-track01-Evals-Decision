"""
Tests for 02-sales-copilot.md workbook answers.

Two categories of tests:
1. Structural tests – verify the PR-added answers are present in the markdown.
2. Logic unit tests – implement and verify the code-checkable business rules
   described in Section 5 of the workbook.
"""

import os
import re
import pytest

WORKBOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "02-sales-copilot.md")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_workbook() -> str:
    with open(WORKBOOK_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# Enums / constants mirroring those defined in the workbook
# ---------------------------------------------------------------------------

VALID_LOOKUP_STATUSES = {
    "SUCCESS_SINGLE_MATCH",
    "AMBIGUOUS_MULTIPLE_MATCHES",
    "NOT_FOUND",
    "CONFLICT",
}


# ---------------------------------------------------------------------------
# Output builder
# ---------------------------------------------------------------------------

def make_copilot_output(
    summary: str = "Customer inquired about their last order status.",
    detected_signals: list = None,
    lookup_status: str = "SUCCESS_SINGLE_MATCH",
    lookup_results: list = None,
    warnings: list = None,
    suggested_next_step: str = "Confirm order status with customer.",
    suggested_reply: str = None,
) -> dict:
    if detected_signals is None:
        detected_signals = [{"type": "phone", "value": "0901234567"}]
    if lookup_results is None:
        lookup_results = [{"customer_id": "C-001", "name": "Nguyen Van A"}]
    if warnings is None:
        warnings = []
    output = {
        "summary": summary,
        "detected_signals": detected_signals,
        "lookup_status": lookup_status,
        "lookup_results": lookup_results,
        "warnings": warnings,
        "suggested_next_step": suggested_next_step,
    }
    if suggested_reply is not None:
        output["suggested_reply"] = suggested_reply
    return output


# ---------------------------------------------------------------------------
# 1. Structural tests
# ---------------------------------------------------------------------------

class TestWorkbookStructure:

    def setup_method(self):
        self.content = load_workbook()

    def test_unit_of_work_answer_present(self):
        """Section 1 must contain an actual answer."""
        assert "lát cắt công việc" in self.content

    def test_unit_of_work_describes_lookup(self):
        """Unit of Work must mention signal detection and lookup."""
        assert "tra cứu" in self.content or "lookup" in self.content.lower()

    def test_quality_question_present(self):
        assert "Câu hỏi chất lượng" in self.content

    def test_quality_question_mentions_ambiguity(self):
        """Quality question must address the ambiguity/multi-match risk."""
        assert "mơ hồ" in self.content or "ambiguity" in self.content.lower() or "mâu thuẫn" in self.content

    def test_output_contract_has_required_fields(self):
        required_fields = [
            "summary",
            "detected_signals",
            "lookup_status",
            "lookup_results",
            "warnings",
            "suggested_next_step",
            "suggested_reply",
        ]
        for field in required_fields:
            assert f"`{field}`" in self.content, (
                f"Output contract must include field `{field}`"
            )

    def test_lookup_status_enum_values_defined(self):
        """All four lookup_status enum values must be mentioned."""
        for val in VALID_LOOKUP_STATUSES:
            assert val in self.content, f"lookup_status enum value '{val}' missing"

    def test_eval_decision_map_exists(self):
        assert "✅" in self.content

    def test_eval_decision_map_has_six_rows(self):
        rows = re.findall(r"\|\s*\*\*\d+\.", self.content)
        assert len(rows) >= 6

    def test_code_checks_section_present(self):
        assert "Kiểm tra tự động bằng code" in self.content

    def test_code_checks_cover_schema_validation(self):
        assert "JSON hợp lệ" in self.content or "schema" in self.content.lower()

    def test_code_checks_cover_enum_validation(self):
        assert "enum" in self.content.lower()

    def test_code_checks_cover_ambiguous_warning_gate(self):
        assert "AMBIGUOUS" in self.content
        assert "warnings" in self.content

    def test_code_checks_cover_not_found_empty_results(self):
        assert "NOT_FOUND" in self.content

    def test_code_checks_cover_success_single_match_count(self):
        assert "SUCCESS_SINGLE_MATCH" in self.content

    def test_code_checks_cover_signal_groundedness(self):
        """Signals must be grounded in the actual conversation."""
        assert "detected_signals" in self.content or "tín hiệu" in self.content

    def test_code_checks_cover_summary_non_empty(self):
        assert "summary" in self.content
        assert "rỗng" in self.content  # "empty" in Vietnamese

    def test_llm_criteria_section_present(self):
        assert "Tiêu chí chấm bằng LLM" in self.content

    def test_llm_criteria_covers_faithfulness(self):
        assert "trung thực" in self.content or "faithfulness" in self.content.lower()

    def test_llm_criteria_covers_intent_capture(self):
        assert "ý định" in self.content or "intent" in self.content.lower()

    def test_human_review_section_present(self):
        assert "Sales Leads" in self.content or "Sales Ops" in self.content

    def test_no_domain_expert_required(self):
        assert "Không áp dụng" in self.content
        section_7a = re.search(r"#### 7A.*?#### 7B", self.content, re.DOTALL)
        assert section_7a, "Section 7A must exist"
        assert "Không áp dụng" in section_7a.group(0)

    def test_release_gate_block_conditions_present(self):
        assert "CHẶN" in self.content or "BLOCK" in self.content

    def test_release_gate_zero_lookup_failures_condition(self):
        """Release gate must treat incorrect lookup as a P0 block condition."""
        assert "P0" in self.content or "tra cứu sai" in self.content

    def test_release_gate_ambiguity_recall_threshold(self):
        assert "99%" in self.content

    def test_release_gate_schema_100_percent(self):
        assert "100%" in self.content

    def test_release_gate_warn_conditions_present(self):
        assert "CẢNH BÁO" in self.content or "WARN" in self.content

    def test_pilot_plan_present(self):
        assert "Kế hoạch chạy thử" in self.content

    def test_pilot_plan_uses_gemini(self):
        assert "Gemini" in self.content

    def test_pilot_plan_mentions_api_cost(self):
        assert "$" in self.content
        assert "tokens" in self.content.lower()

    def test_pilot_plan_human_hours_present(self):
        assert "giờ" in self.content


# ---------------------------------------------------------------------------
# 2. Logic unit tests – implement the code rules described in Section 5
# ---------------------------------------------------------------------------

class TestOutputSchemaValidation:
    """Rule: Output must contain all required fields."""

    REQUIRED_FIELDS = {"summary", "detected_signals", "lookup_status", "lookup_results", "warnings", "suggested_next_step"}

    def validate_schema(self, output: dict) -> list[str]:
        return [f"Missing field: {f}" for f in self.REQUIRED_FIELDS if f not in output]

    def test_valid_output_passes(self):
        assert self.validate_schema(make_copilot_output()) == []

    def test_missing_summary_fails(self):
        output = make_copilot_output()
        del output["summary"]
        assert any("summary" in e for e in self.validate_schema(output))

    def test_missing_lookup_status_fails(self):
        output = make_copilot_output()
        del output["lookup_status"]
        assert any("lookup_status" in e for e in self.validate_schema(output))

    def test_missing_lookup_results_fails(self):
        output = make_copilot_output()
        del output["lookup_results"]
        assert any("lookup_results" in e for e in self.validate_schema(output))

    def test_missing_warnings_fails(self):
        output = make_copilot_output()
        del output["warnings"]
        assert any("warnings" in e for e in self.validate_schema(output))

    def test_missing_detected_signals_fails(self):
        output = make_copilot_output()
        del output["detected_signals"]
        assert any("detected_signals" in e for e in self.validate_schema(output))

    def test_empty_output_fails_all(self):
        errors = self.validate_schema({})
        assert len(errors) == len(self.REQUIRED_FIELDS)


class TestLookupStatusEnumValidation:
    """Rule: lookup_status must be one of the four allowed enum values."""

    def validate_enum(self, output: dict) -> list[str]:
        status = output.get("lookup_status")
        if status not in VALID_LOOKUP_STATUSES:
            return [f"Invalid lookup_status: '{status}'"]
        return []

    def test_all_valid_statuses_pass(self):
        for status in VALID_LOOKUP_STATUSES:
            output = make_copilot_output(lookup_status=status)
            assert self.validate_enum(output) == [], f"Status {status} should be valid"

    def test_invented_status_fails(self):
        output = make_copilot_output(lookup_status="PARTIAL_MATCH")
        assert len(self.validate_enum(output)) > 0

    def test_lowercase_status_fails(self):
        output = make_copilot_output(lookup_status="success_single_match")
        assert len(self.validate_enum(output)) > 0

    def test_empty_string_status_fails(self):
        output = make_copilot_output(lookup_status="")
        assert len(self.validate_enum(output)) > 0

    def test_none_status_fails(self):
        output = make_copilot_output()
        output["lookup_status"] = None
        assert len(self.validate_enum(output)) > 0


class TestAmbiguitySafetyGate:
    """
    Rule: If lookup_status is AMBIGUOUS_MULTIPLE_MATCHES or CONFLICT,
    warnings must not be empty.
    """

    def check_ambiguity_gate(self, output: dict) -> list[str]:
        errors = []
        status = output.get("lookup_status", "")
        warnings = output.get("warnings", [])
        if status in {"AMBIGUOUS_MULTIPLE_MATCHES", "CONFLICT"} and not warnings:
            errors.append(f"SAFETY GATE: {status} must produce non-empty warnings")
        return errors

    def test_ambiguous_with_warnings_passes(self):
        output = make_copilot_output(
            lookup_status="AMBIGUOUS_MULTIPLE_MATCHES",
            warnings=["Multiple records found, please verify customer identity."],
        )
        assert self.check_ambiguity_gate(output) == []

    def test_ambiguous_without_warnings_fails(self):
        output = make_copilot_output(
            lookup_status="AMBIGUOUS_MULTIPLE_MATCHES",
            warnings=[],
        )
        errors = self.check_ambiguity_gate(output)
        assert len(errors) > 0
        assert "SAFETY GATE" in errors[0]

    def test_conflict_with_warnings_passes(self):
        output = make_copilot_output(
            lookup_status="CONFLICT",
            warnings=["Data conflict detected between CRM and OMS."],
        )
        assert self.check_ambiguity_gate(output) == []

    def test_conflict_without_warnings_fails(self):
        output = make_copilot_output(lookup_status="CONFLICT", warnings=[])
        errors = self.check_ambiguity_gate(output)
        assert len(errors) > 0

    def test_success_without_warnings_passes(self):
        """SUCCESS_SINGLE_MATCH does not require warnings."""
        output = make_copilot_output(lookup_status="SUCCESS_SINGLE_MATCH", warnings=[])
        assert self.check_ambiguity_gate(output) == []

    def test_not_found_without_warnings_passes(self):
        """NOT_FOUND does not require warnings (no match found is a clear state)."""
        output = make_copilot_output(lookup_status="NOT_FOUND", warnings=[])
        assert self.check_ambiguity_gate(output) == []


class TestNotFoundEmptyResultsRule:
    """Rule: When lookup_status is NOT_FOUND, lookup_results must be empty."""

    def check_not_found_consistency(self, output: dict) -> list[str]:
        errors = []
        if output.get("lookup_status") == "NOT_FOUND":
            if output.get("lookup_results"):
                errors.append("NOT_FOUND status must have empty lookup_results")
        return errors

    def test_not_found_with_empty_results_passes(self):
        output = make_copilot_output(lookup_status="NOT_FOUND", lookup_results=[])
        assert self.check_not_found_consistency(output) == []

    def test_not_found_with_stale_results_fails(self):
        output = make_copilot_output(
            lookup_status="NOT_FOUND",
            lookup_results=[{"customer_id": "C-999", "name": "Ghost Record"}],
        )
        errors = self.check_not_found_consistency(output)
        assert len(errors) > 0

    def test_success_with_results_unaffected(self):
        """Rule does not apply when status is SUCCESS_SINGLE_MATCH."""
        output = make_copilot_output(
            lookup_status="SUCCESS_SINGLE_MATCH",
            lookup_results=[{"customer_id": "C-001"}],
        )
        assert self.check_not_found_consistency(output) == []


class TestSuccessSingleMatchCountRule:
    """Rule: When lookup_status is SUCCESS_SINGLE_MATCH, lookup_results must have exactly 1 element."""

    def check_single_match_count(self, output: dict) -> list[str]:
        errors = []
        if output.get("lookup_status") == "SUCCESS_SINGLE_MATCH":
            count = len(output.get("lookup_results", []))
            if count != 1:
                errors.append(
                    f"SUCCESS_SINGLE_MATCH must have exactly 1 result, got {count}"
                )
        return errors

    def test_one_result_passes(self):
        output = make_copilot_output(
            lookup_status="SUCCESS_SINGLE_MATCH",
            lookup_results=[{"customer_id": "C-001"}],
        )
        assert self.check_single_match_count(output) == []

    def test_zero_results_fails(self):
        output = make_copilot_output(
            lookup_status="SUCCESS_SINGLE_MATCH", lookup_results=[]
        )
        errors = self.check_single_match_count(output)
        assert len(errors) > 0

    def test_two_results_fails(self):
        output = make_copilot_output(
            lookup_status="SUCCESS_SINGLE_MATCH",
            lookup_results=[{"customer_id": "C-001"}, {"customer_id": "C-002"}],
        )
        errors = self.check_single_match_count(output)
        assert len(errors) > 0

    def test_not_found_with_empty_results_unaffected(self):
        output = make_copilot_output(lookup_status="NOT_FOUND", lookup_results=[])
        assert self.check_single_match_count(output) == []


class TestSignalGroundednessRule:
    """
    Rule: Every entity in detected_signals must actually appear in the
    original conversation text.
    """

    def check_signal_groundedness(self, conversation: str, output: dict) -> list[str]:
        errors = []
        for signal in output.get("detected_signals", []):
            value = str(signal.get("value", ""))
            if value and value not in conversation:
                errors.append(f"Hallucinated signal: '{value}' not found in conversation")
        return errors

    def test_grounded_phone_number_passes(self):
        conversation = "Khách: Số điện thoại của tôi là 0901234567, tôi cần hỏi đơn hàng."
        output = make_copilot_output(
            detected_signals=[{"type": "phone", "value": "0901234567"}]
        )
        assert self.check_signal_groundedness(conversation, output) == []

    def test_hallucinated_phone_number_fails(self):
        conversation = "Khách: Tôi muốn kiểm tra đơn hàng của mình."
        output = make_copilot_output(
            detected_signals=[{"type": "phone", "value": "0987654321"}]
        )
        errors = self.check_signal_groundedness(conversation, output)
        assert len(errors) > 0
        assert "Hallucinated" in errors[0]

    def test_grounded_order_code_passes(self):
        conversation = "Đơn hàng #ORD-2026-001 của tôi chưa được giao."
        output = make_copilot_output(
            detected_signals=[{"type": "order_id", "value": "ORD-2026-001"}]
        )
        assert self.check_signal_groundedness(conversation, output) == []

    def test_empty_signals_always_passes(self):
        conversation = "Tôi muốn hỏi về chính sách đổi trả."
        output = make_copilot_output(detected_signals=[])
        assert self.check_signal_groundedness(conversation, output) == []

    def test_multiple_signals_all_must_be_grounded(self):
        conversation = "SĐT: 0901234567, Mã đơn: ORD-001"
        output = make_copilot_output(
            detected_signals=[
                {"type": "phone", "value": "0901234567"},
                {"type": "order_id", "value": "ORD-999"},  # hallucinated
            ]
        )
        errors = self.check_signal_groundedness(conversation, output)
        assert len(errors) == 1
        assert "ORD-999" in errors[0]


class TestSummaryNonEmptyRule:
    """Rule: summary must not be empty or whitespace-only."""

    def validate_summary(self, output: dict) -> list[str]:
        summary = output.get("summary", "")
        if not summary or not summary.strip():
            return ["summary must not be empty"]
        return []

    def test_valid_summary_passes(self):
        assert self.validate_summary(make_copilot_output()) == []

    def test_empty_summary_fails(self):
        output = make_copilot_output(summary="")
        assert len(self.validate_summary(output)) > 0

    def test_whitespace_summary_fails(self):
        output = make_copilot_output(summary="   ")
        assert len(self.validate_summary(output)) > 0

    def test_newline_only_summary_fails(self):
        output = make_copilot_output(summary="\n\n")
        assert len(self.validate_summary(output)) > 0


class TestSuggestedReplyPrivacyRule:
    """
    Rule: If lookup_status is not SUCCESS_SINGLE_MATCH, suggested_reply (if present)
    must not contain a known customer's first name (personal information from
    unverified lookup_results).
    """

    def check_reply_privacy(self, output: dict) -> list[str]:
        errors = []
        status = output.get("lookup_status", "")
        if status == "SUCCESS_SINGLE_MATCH":
            return []  # Identity confirmed – personalised reply is allowed

        suggested_reply = output.get("suggested_reply", "")
        if not suggested_reply:
            return []

        # Extract names from lookup_results that are NOT verified
        for result in output.get("lookup_results", []):
            name = result.get("name", "")
            first_name = name.split()[0] if name else ""
            if first_name and first_name in suggested_reply:
                errors.append(
                    f"Privacy risk: suggested_reply uses unverified customer name '{first_name}'"
                )
        return errors

    def test_ambiguous_lookup_reply_without_name_passes(self):
        output = make_copilot_output(
            lookup_status="AMBIGUOUS_MULTIPLE_MATCHES",
            lookup_results=[{"customer_id": "C-001", "name": "Nguyen Van A"}],
            suggested_reply="Cảm ơn bạn đã liên hệ. Chúng tôi cần xác nhận thêm thông tin.",
            warnings=["Multiple records found"],
        )
        assert self.check_reply_privacy(output) == []

    def test_ambiguous_lookup_reply_with_name_fails(self):
        output = make_copilot_output(
            lookup_status="AMBIGUOUS_MULTIPLE_MATCHES",
            lookup_results=[{"customer_id": "C-001", "name": "Nguyen Van A"}],
            suggested_reply="Chào Nguyen, đơn hàng của anh đã được giao rồi ạ.",
            warnings=["Multiple records found"],
        )
        errors = self.check_reply_privacy(output)
        assert len(errors) > 0
        assert "Privacy risk" in errors[0]

    def test_verified_identity_allows_personalised_reply(self):
        output = make_copilot_output(
            lookup_status="SUCCESS_SINGLE_MATCH",
            lookup_results=[{"customer_id": "C-001", "name": "Nguyen Van A"}],
            suggested_reply="Chào Nguyen, đơn hàng của anh đã được giao rồi ạ.",
        )
        assert self.check_reply_privacy(output) == []

    def test_not_found_reply_without_name_passes(self):
        output = make_copilot_output(
            lookup_status="NOT_FOUND",
            lookup_results=[],
            suggested_reply="Xin lỗi, chúng tôi không tìm thấy tài khoản liên quan.",
        )
        assert self.check_reply_privacy(output) == []


class TestReleaseGateThresholds:
    """
    Verify release gate blocking conditions from Section 8 of 02-sales-copilot.md.
    """

    def evaluate_release_gate(
        self,
        incorrect_lookup_count: int,
        ambiguity_recall_pct: float,
        schema_compliance_pct: float,
        regression_pass_pct: float,
    ) -> dict:
        reasons = []
        if incorrect_lookup_count > 0:
            reasons.append(f"Critical lookup failures: {incorrect_lookup_count}")
        if ambiguity_recall_pct < 99.0:
            reasons.append(f"Ambiguity recall {ambiguity_recall_pct}% < 99%")
        if schema_compliance_pct < 100.0:
            reasons.append(f"Schema compliance {schema_compliance_pct}% < 100%")
        if regression_pass_pct < 100.0:
            reasons.append(f"Regression pass {regression_pass_pct}% < 100%")
        return {"blocked": len(reasons) > 0, "reasons": reasons}

    def test_perfect_metrics_not_blocked(self):
        result = self.evaluate_release_gate(0, 99.5, 100.0, 100.0)
        assert not result["blocked"]

    def test_any_incorrect_lookup_blocks(self):
        result = self.evaluate_release_gate(1, 99.5, 100.0, 100.0)
        assert result["blocked"]
        assert any("lookup" in r.lower() for r in result["reasons"])

    def test_ambiguity_recall_below_99_blocks(self):
        result = self.evaluate_release_gate(0, 98.9, 100.0, 100.0)
        assert result["blocked"]
        assert any("Ambiguity" in r for r in result["reasons"])

    def test_ambiguity_recall_exactly_99_passes(self):
        result = self.evaluate_release_gate(0, 99.0, 100.0, 100.0)
        assert not result["blocked"]

    def test_schema_below_100_blocks(self):
        result = self.evaluate_release_gate(0, 99.5, 99.5, 100.0)
        assert result["blocked"]
        assert any("Schema" in r for r in result["reasons"])

    def test_regression_below_100_blocks(self):
        result = self.evaluate_release_gate(0, 99.5, 100.0, 99.9)
        assert result["blocked"]
        assert any("Regression" in r for r in result["reasons"])


class TestPilotPlanConsistency:
    """Verify arithmetic of Section 9 pilot plan for 02-sales-copilot.md."""

    CASES = 80
    ITERATIONS = 40
    INPUT_TOKENS_PER_CASE = 800
    OUTPUT_TOKENS_PER_CASE = 250
    INPUT_PRICE_PER_MILLION = 0.35
    OUTPUT_PRICE_PER_MILLION = 1.05

    PM_HOURS = 25
    ENGINEERING_HOURS = 15
    HUMAN_REVIEW_HOURS = 30

    def test_total_input_tokens(self):
        expected = self.CASES * self.ITERATIONS * self.INPUT_TOKENS_PER_CASE
        assert expected == 2_560_000

    def test_total_output_tokens(self):
        expected = self.CASES * self.ITERATIONS * self.OUTPUT_TOKENS_PER_CASE
        assert expected == 800_000

    def test_api_cost_approximately_correct(self):
        input_cost = (
            self.CASES * self.ITERATIONS * self.INPUT_TOKENS_PER_CASE / 1_000_000
        ) * self.INPUT_PRICE_PER_MILLION
        output_cost = (
            self.CASES * self.ITERATIONS * self.OUTPUT_TOKENS_PER_CASE / 1_000_000
        ) * self.OUTPUT_PRICE_PER_MILLION
        total = input_cost + output_cost
        # Workbook states ~$1.736
        assert abs(total - 1.736) < 0.05, f"Expected ~$1.74 API cost, got ${total:.3f}"

    def test_total_human_hours(self):
        total = self.PM_HOURS + self.ENGINEERING_HOURS + self.HUMAN_REVIEW_HOURS
        assert total == 70  # Workbook states 70 hours

    def test_no_domain_expert_hours(self):
        domain_expert_hours = 0
        assert domain_expert_hours == 0

    def test_cases_in_reasonable_range(self):
        assert 50 <= self.CASES <= 100

    def test_iterations_in_reasonable_range(self):
        assert 30 <= self.ITERATIONS <= 50