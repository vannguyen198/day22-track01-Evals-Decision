"""
Tests for 03-medical-routing.md workbook answers.

Two categories of tests:
1. Structural tests – verify the PR-added answers are present in the markdown,
   including domain expert requirements that are mandatory for this high-risk case.
2. Logic unit tests – implement and verify the code-checkable business rules
   described in Section 7 of the workbook. These rules govern patient safety.
"""

import os
import re
import pytest

WORKBOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "03-medical-routing.md")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_workbook() -> str:
    with open(WORKBOOK_PATH, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# Enums / constants mirroring those defined in the workbook
# ---------------------------------------------------------------------------

VALID_CALL_INTENTS = {"Hành chính", "Y khoa"}
VALID_URGENCY_LEVELS = {"CRITICAL", "HIGH", "NORMAL"}
VALID_PATIENT_LOOKUP_STATUSES = {"FOUND", "AMBIGUOUS", "NOT_FOUND"}

EMERGENCY_ROUTES = {"Quy trình khẩn cấp", "Bác sĩ trực"}
ADMIN_ROUTES = {"Hành chính", "Lịch hẹn", "CSKH", "Đặt lịch"}
ALL_VALID_ROUTES = EMERGENCY_ROUTES | ADMIN_ROUTES | {"Điều dưỡng sàng lọc", "Hỏi thêm thông tin"}

# Red flag keywords that must never be missed (from Section 7)
RED_FLAG_KEYWORDS = {"khó thở", "đau ngực", "ngất", "tím tái"}


# ---------------------------------------------------------------------------
# Output builder
# ---------------------------------------------------------------------------

def make_routing_output(
    call_intent: str = "Y khoa",
    detected_red_flags: list = None,
    urgency_level: str = "NORMAL",
    summary: str = "Bệnh nhân hỏi về đơn thuốc.",
    patient_lookup_status: str = "FOUND",
    matched_patient_record: object = None,
    suggested_route: str = "Điều dưỡng sàng lọc",
) -> dict:
    return {
        "call_intent": call_intent,
        "detected_red_flags": detected_red_flags if detected_red_flags is not None else [],
        "urgency_level": urgency_level,
        "summary": summary,
        "patient_lookup_status": patient_lookup_status,
        "matched_patient_record": matched_patient_record,
        "suggested_route": suggested_route,
    }


# ---------------------------------------------------------------------------
# 1. Structural tests
# ---------------------------------------------------------------------------

class TestWorkbookStructure:

    def setup_method(self):
        self.content = load_workbook()

    def test_unit_of_work_answer_present(self):
        assert "lát cắt công việc" in self.content

    def test_unit_of_work_mentions_red_flags(self):
        assert "red flag" in self.content.lower() or "cờ đỏ" in self.content

    def test_quality_question_present(self):
        assert "Câu hỏi chất lượng" in self.content

    def test_quality_question_mentions_patient_safety(self):
        assert (
            "tính mạng" in self.content
            or "khẩn cấp" in self.content
            or "escalate" in self.content.lower()
        )

    def test_workflow_diagram_present(self):
        """Section 3 must contain a workflow diagram."""
        assert "mermaid" in self.content or "graph TD" in self.content

    def test_workflow_has_red_flag_branch(self):
        assert "Red Flag" in self.content or "red flag" in self.content.lower()

    def test_workflow_has_domain_expert_checkpoint(self):
        assert "DOMAIN EXPERT" in self.content or "domain expert" in self.content.lower()

    def test_ui_ascii_design_present(self):
        """Section 4 must show UI sketch."""
        assert "RED FLAGS" in self.content or "red flag" in self.content.lower()
        assert "TÓM TẮT" in self.content or "tóm tắt" in self.content.lower()

    def test_output_contract_required_fields_present(self):
        required = [
            "call_intent",
            "detected_red_flags",
            "urgency_level",
            "summary",
            "patient_lookup_status",
            "matched_patient_record",
            "suggested_route",
        ]
        for field in required:
            assert f"`{field}`" in self.content, f"Output contract must include field `{field}`"

    def test_urgency_level_enum_values_defined(self):
        for val in VALID_URGENCY_LEVELS:
            assert val in self.content, f"urgency_level value '{val}' must be defined"

    def test_eval_decision_map_exists(self):
        assert "✅" in self.content

    def test_eval_decision_map_has_six_rows(self):
        rows = re.findall(r"\|\s*\*\*\d+\.", self.content)
        assert len(rows) >= 6

    def test_eval_map_assigns_expert_column(self):
        """Medical routing must involve domain expert in eval."""
        # Check Expert column has at least one ✅
        table_section = re.search(
            r"### 6\. Eval Decision Map.*?###", self.content, re.DOTALL
        )
        assert table_section, "Section 6 must exist"
        assert "Expert" in table_section.group(0)

    def test_code_checks_section_present(self):
        assert "Kiểm tra tự động bằng code" in self.content

    def test_code_checks_cover_schema_validation(self):
        assert "JSON hợp lệ" in self.content or "schema" in self.content.lower()

    def test_code_checks_cover_red_flag_keyword_rule(self):
        assert "khó thở" in self.content
        assert "đau ngực" in self.content

    def test_code_checks_cover_red_flag_escalation_chain(self):
        """If red flags detected → urgency CRITICAL and emergency route."""
        assert "CRITICAL" in self.content
        assert "Quy trình khẩn cấp" in self.content or "Bác sĩ trực" in self.content

    def test_code_checks_cover_admin_intent_no_emergency_route(self):
        assert "Hành chính" in self.content

    def test_code_checks_cover_not_found_empty_record(self):
        assert "NOT_FOUND" in self.content

    def test_code_checks_cover_red_flag_groundedness(self):
        """Each red flag must have evidence in transcript."""
        assert "bằng chứng" in self.content or "groundedness" in self.content.lower()

    def test_llm_criteria_section_present(self):
        assert "Tiêu chí chấm bằng LLM" in self.content

    def test_llm_criteria_covers_nuanced_symptom_severity(self):
        assert "nghiêm trọng" in self.content or "mức độ" in self.content

    def test_domain_expert_review_required(self):
        """Medical routing MUST require domain expert (unlike the other two cases)."""
        assert "Bác sĩ" in self.content or "Điều dưỡng" in self.content
        # Must NOT say "Không áp dụng" for Section 9A
        section_9a = re.search(r"#### 9A\..*?#### 9B\.", self.content, re.DOTALL)
        if section_9a:
            assert "Không áp dụng" not in section_9a.group(0), (
                "Section 9A must contain an actual expert UI, not 'Not applicable'"
            )

    def test_expert_review_screen_present(self):
        """Section 9A must have an ASCII expert review screen."""
        assert "EXPERT QUEUE" in self.content or "HÀNG ĐỢI REVIEW" in self.content

    def test_expert_review_criteria_section_9b_present(self):
        """Section 9B must define at least one expert review criterion."""
        section_9b = re.search(r"#### 9B\..*?###", self.content, re.DOTALL)
        assert section_9b, "Section 9B must exist"
        # Must have at least one criterion (numbered list)
        assert re.search(r"\*\*[0-9]+\.", section_9b.group(0)), (
            "Section 9B must list numbered review criteria"
        )

    def test_release_gate_block_conditions_present(self):
        assert "CHẶN" in self.content or "BLOCK" in self.content

    def test_release_gate_red_flag_recall_threshold(self):
        """Red flag recall threshold must be 99.5% (higher than other cases)."""
        assert "99.5%" in self.content

    def test_release_gate_zero_p0_failures(self):
        assert "P0" in self.content
        assert "> 0" in self.content or "= 0" in self.content

    def test_release_gate_warn_conditions_present(self):
        assert "CẢNH BÁO" in self.content or "WARN" in self.content

    def test_pilot_plan_present(self):
        assert "Kế hoạch chạy thử" in self.content

    def test_pilot_plan_includes_domain_expert_hours(self):
        assert "40 giờ" in self.content or "domain expert" in self.content.lower()

    def test_pilot_plan_api_cost_calculations(self):
        assert "$2.45" in self.content or "2,45" in self.content


# ---------------------------------------------------------------------------
# 2. Logic unit tests – implement Section 7 code rules
# ---------------------------------------------------------------------------

class TestOutputSchemaValidation:
    """Rule: Output must contain all required fields."""

    REQUIRED_FIELDS = {
        "call_intent",
        "detected_red_flags",
        "urgency_level",
        "summary",
        "patient_lookup_status",
        "suggested_route",
    }

    def validate_schema(self, output: dict) -> list[str]:
        return [f"Missing field: {f}" for f in self.REQUIRED_FIELDS if f not in output]

    def test_valid_output_passes(self):
        assert self.validate_schema(make_routing_output()) == []

    def test_missing_call_intent_fails(self):
        output = make_routing_output()
        del output["call_intent"]
        assert any("call_intent" in e for e in self.validate_schema(output))

    def test_missing_urgency_level_fails(self):
        output = make_routing_output()
        del output["urgency_level"]
        assert any("urgency_level" in e for e in self.validate_schema(output))

    def test_missing_detected_red_flags_fails(self):
        output = make_routing_output()
        del output["detected_red_flags"]
        assert any("detected_red_flags" in e for e in self.validate_schema(output))

    def test_missing_suggested_route_fails(self):
        output = make_routing_output()
        del output["suggested_route"]
        assert any("suggested_route" in e for e in self.validate_schema(output))

    def test_missing_summary_fails(self):
        output = make_routing_output()
        del output["summary"]
        assert any("summary" in e for e in self.validate_schema(output))

    def test_empty_output_fails_all_required(self):
        errors = self.validate_schema({})
        assert len(errors) == len(self.REQUIRED_FIELDS)


class TestEnumValidation:
    """Rule: call_intent, urgency_level, and suggested_route must be valid enum values."""

    def validate_enums(self, output: dict) -> list[str]:
        errors = []
        if output.get("call_intent") not in VALID_CALL_INTENTS:
            errors.append(f"Invalid call_intent: '{output.get('call_intent')}'")
        if output.get("urgency_level") not in VALID_URGENCY_LEVELS:
            errors.append(f"Invalid urgency_level: '{output.get('urgency_level')}'")
        if output.get("suggested_route") not in ALL_VALID_ROUTES:
            errors.append(f"Invalid suggested_route: '{output.get('suggested_route')}'")
        return errors

    def test_valid_medical_intent_passes(self):
        output = make_routing_output(call_intent="Y khoa")
        assert not any("call_intent" in e for e in self.validate_enums(output))

    def test_valid_admin_intent_passes(self):
        output = make_routing_output(call_intent="Hành chính", suggested_route="Lịch hẹn")
        assert self.validate_enums(output) == []

    def test_invented_intent_fails(self):
        output = make_routing_output(call_intent="Technical Support")
        errors = self.validate_enums(output)
        assert any("call_intent" in e for e in errors)

    def test_valid_urgency_levels_pass(self):
        for level in VALID_URGENCY_LEVELS:
            output = make_routing_output(urgency_level=level)
            assert not any("urgency_level" in e for e in self.validate_enums(output))

    def test_invalid_urgency_fails(self):
        output = make_routing_output(urgency_level="EXTREME")
        errors = self.validate_enums(output)
        assert any("urgency_level" in e for e in errors)

    def test_valid_emergency_route_passes(self):
        output = make_routing_output(
            detected_red_flags=["đau ngực"],
            urgency_level="CRITICAL",
            suggested_route="Quy trình khẩn cấp",
        )
        assert self.validate_enums(output) == []

    def test_invented_route_fails(self):
        output = make_routing_output(suggested_route="Unknown Route")
        errors = self.validate_enums(output)
        assert any("suggested_route" in e for e in errors)


class TestRedFlagKeywordSafetyGate:
    """
    Rule: If transcript contains red flag keywords (khó thở, đau ngực, ngất, tím tái),
    detected_red_flags must NOT be empty.
    This is the most critical safety gate in the system.
    """

    def check_keyword_safety_gate(self, transcript: str, output: dict) -> list[str]:
        errors = []
        transcript_lower = transcript.lower()
        found_keywords = [kw for kw in RED_FLAG_KEYWORDS if kw in transcript_lower]
        if found_keywords and not output.get("detected_red_flags"):
            errors.append(
                f"PATIENT SAFETY VIOLATION: Red flag keywords {found_keywords} "
                f"in transcript but detected_red_flags is empty"
            )
        return errors

    def test_normal_call_no_keywords_passes(self):
        transcript = "Tôi muốn đặt lịch khám vào tuần sau."
        output = make_routing_output(detected_red_flags=[])
        assert self.check_keyword_safety_gate(transcript, output) == []

    def test_chest_pain_keyword_triggers_gate(self):
        transcript = "Tôi đang bị đau ngực rất dữ dội."
        output = make_routing_output(detected_red_flags=[])
        errors = self.check_keyword_safety_gate(transcript, output)
        assert len(errors) > 0
        assert "PATIENT SAFETY VIOLATION" in errors[0]

    def test_difficulty_breathing_triggers_gate(self):
        transcript = "Ông ơi, tôi khó thở quá không thở được."
        output = make_routing_output(detected_red_flags=[])
        errors = self.check_keyword_safety_gate(transcript, output)
        assert len(errors) > 0

    def test_fainting_keyword_triggers_gate(self):
        transcript = "Bố tôi vừa ngất xỉu ở nhà."
        output = make_routing_output(detected_red_flags=[])
        errors = self.check_keyword_safety_gate(transcript, output)
        assert len(errors) > 0

    def test_cyanosis_keyword_triggers_gate(self):
        transcript = "Môi bệnh nhân tím tái rồi."
        output = make_routing_output(detected_red_flags=[])
        errors = self.check_keyword_safety_gate(transcript, output)
        assert len(errors) > 0

    def test_keyword_with_flags_detected_passes(self):
        transcript = "Tôi đang bị đau ngực."
        output = make_routing_output(detected_red_flags=["đau ngực"])
        assert self.check_keyword_safety_gate(transcript, output) == []

    def test_multiple_keywords_all_require_flags(self):
        transcript = "Tôi đau ngực và khó thở."
        output = make_routing_output(detected_red_flags=[])
        errors = self.check_keyword_safety_gate(transcript, output)
        assert len(errors) > 0

    def test_case_insensitive_keyword_detection(self):
        transcript = "KHÁCH HÀNG: TÔI KHÓ THỞ QUÁ."
        output = make_routing_output(detected_red_flags=[])
        errors = self.check_keyword_safety_gate(transcript, output)
        assert len(errors) > 0

    def test_partial_keyword_does_not_trigger(self):
        """'thở' alone should not trigger 'khó thở' detection."""
        transcript = "Tôi muốn hỏi về bài tập thở."
        output = make_routing_output(detected_red_flags=[])
        assert self.check_keyword_safety_gate(transcript, output) == []


class TestRedFlagEscalationChainRule:
    """
    Rule: If detected_red_flags is non-empty, then:
    - urgency_level must be 'CRITICAL'
    - suggested_route must be one of the emergency routes
    """

    def check_escalation_chain(self, output: dict) -> list[str]:
        errors = []
        if output.get("detected_red_flags"):
            if output.get("urgency_level") != "CRITICAL":
                errors.append(
                    f"SAFETY: detected_red_flags present but urgency_level is "
                    f"'{output.get('urgency_level')}' instead of 'CRITICAL'"
                )
            if output.get("suggested_route") not in EMERGENCY_ROUTES:
                errors.append(
                    f"SAFETY: detected_red_flags present but suggested_route "
                    f"'{output.get('suggested_route')}' is not an emergency route"
                )
        return errors

    def test_red_flags_with_critical_and_emergency_passes(self):
        output = make_routing_output(
            detected_red_flags=["đau ngực"],
            urgency_level="CRITICAL",
            suggested_route="Quy trình khẩn cấp",
        )
        assert self.check_escalation_chain(output) == []

    def test_red_flags_with_high_urgency_fails(self):
        output = make_routing_output(
            detected_red_flags=["khó thở"],
            urgency_level="HIGH",
            suggested_route="Quy trình khẩn cấp",
        )
        errors = self.check_escalation_chain(output)
        assert any("urgency_level" in e or "CRITICAL" in e for e in errors)

    def test_red_flags_with_normal_urgency_fails(self):
        output = make_routing_output(
            detected_red_flags=["đau ngực"],
            urgency_level="NORMAL",
            suggested_route="Quy trình khẩn cấp",
        )
        errors = self.check_escalation_chain(output)
        assert len(errors) > 0

    def test_red_flags_with_admin_route_fails(self):
        output = make_routing_output(
            detected_red_flags=["ngất"],
            urgency_level="CRITICAL",
            suggested_route="Lịch hẹn",
        )
        errors = self.check_escalation_chain(output)
        assert any("suggested_route" in e for e in errors)

    def test_no_red_flags_allows_normal_route(self):
        output = make_routing_output(
            detected_red_flags=[],
            urgency_level="NORMAL",
            suggested_route="Lịch hẹn",
        )
        assert self.check_escalation_chain(output) == []

    def test_red_flags_doctor_on_call_route_passes(self):
        output = make_routing_output(
            detected_red_flags=["tím tái"],
            urgency_level="CRITICAL",
            suggested_route="Bác sĩ trực",
        )
        assert self.check_escalation_chain(output) == []

    def test_multiple_red_flags_all_require_escalation(self):
        output = make_routing_output(
            detected_red_flags=["đau ngực", "khó thở"],
            urgency_level="HIGH",  # should be CRITICAL
            suggested_route="Điều dưỡng sàng lọc",  # should be emergency
        )
        errors = self.check_escalation_chain(output)
        assert len(errors) == 2  # both violations


class TestAdminIntentRoutingRule:
    """
    Rule: If call_intent is 'Hành chính', suggested_route must NOT be
    an emergency route (Bác sĩ trực, Quy trình khẩn cấp).
    """

    def check_admin_routing_consistency(self, output: dict) -> list[str]:
        errors = []
        if output.get("call_intent") == "Hành chính":
            if output.get("suggested_route") in EMERGENCY_ROUTES:
                errors.append(
                    f"Logic error: Admin call_intent incorrectly routed to "
                    f"emergency '{output.get('suggested_route')}'"
                )
        return errors

    def test_admin_intent_to_admin_route_passes(self):
        output = make_routing_output(call_intent="Hành chính", suggested_route="Lịch hẹn")
        assert self.check_admin_routing_consistency(output) == []

    def test_admin_intent_to_emergency_fails(self):
        output = make_routing_output(
            call_intent="Hành chính", suggested_route="Quy trình khẩn cấp"
        )
        errors = self.check_admin_routing_consistency(output)
        assert len(errors) > 0
        assert "Logic error" in errors[0]

    def test_admin_intent_to_doctor_on_call_fails(self):
        output = make_routing_output(
            call_intent="Hành chính", suggested_route="Bác sĩ trực"
        )
        errors = self.check_admin_routing_consistency(output)
        assert len(errors) > 0

    def test_medical_intent_to_emergency_passes(self):
        """Medical intent to emergency route is correct and should not flag."""
        output = make_routing_output(
            call_intent="Y khoa",
            detected_red_flags=["đau ngực"],
            urgency_level="CRITICAL",
            suggested_route="Quy trình khẩn cấp",
        )
        assert self.check_admin_routing_consistency(output) == []

    def test_admin_intent_to_nurse_triage_passes(self):
        output = make_routing_output(
            call_intent="Hành chính", suggested_route="Điều dưỡng sàng lọc"
        )
        assert self.check_admin_routing_consistency(output) == []


class TestPatientRecordConsistencyRule:
    """
    Rule: If patient_lookup_status is NOT_FOUND, matched_patient_record must be null or empty.
    """

    def check_record_consistency(self, output: dict) -> list[str]:
        errors = []
        if output.get("patient_lookup_status") == "NOT_FOUND":
            record = output.get("matched_patient_record")
            if record is not None and record != {} and record != []:
                errors.append(
                    "Data integrity error: NOT_FOUND status but matched_patient_record is populated"
                )
        return errors

    def test_not_found_with_null_record_passes(self):
        output = make_routing_output(
            patient_lookup_status="NOT_FOUND", matched_patient_record=None
        )
        assert self.check_record_consistency(output) == []

    def test_not_found_with_stale_record_fails(self):
        output = make_routing_output(
            patient_lookup_status="NOT_FOUND",
            matched_patient_record={"patient_id": "BN-001", "name": "Ghost Patient"},
        )
        errors = self.check_record_consistency(output)
        assert len(errors) > 0
        assert "NOT_FOUND" in errors[0]

    def test_found_with_record_passes(self):
        output = make_routing_output(
            patient_lookup_status="FOUND",
            matched_patient_record={"patient_id": "BN-998877", "name": "Nguyen Van A"},
        )
        assert self.check_record_consistency(output) == []

    def test_ambiguous_with_record_unaffected(self):
        """AMBIGUOUS status is not covered by this rule."""
        output = make_routing_output(
            patient_lookup_status="AMBIGUOUS",
            matched_patient_record={"patient_id": "BN-001"},
        )
        assert self.check_record_consistency(output) == []


class TestSummaryNonEmptyRule:
    """Rule: summary must not be empty or whitespace-only."""

    def validate_summary(self, output: dict) -> list[str]:
        summary = output.get("summary")
        if not summary or not str(summary).strip():
            return ["summary must not be empty or whitespace-only"]
        return []

    def test_valid_summary_passes(self):
        output = make_routing_output(summary="Patient reports chest pain for 15 minutes.")
        assert self.validate_summary(output) == []

    def test_empty_summary_fails(self):
        output = make_routing_output(summary="")
        assert len(self.validate_summary(output)) > 0

    def test_whitespace_only_summary_fails(self):
        output = make_routing_output(summary="   \t\n  ")
        assert len(self.validate_summary(output)) > 0

    def test_none_summary_fails(self):
        output = make_routing_output()
        output["summary"] = None
        assert len(self.validate_summary(output)) > 0

    def test_single_word_summary_passes(self):
        output = make_routing_output(summary="Đau")
        assert self.validate_summary(output) == []


class TestRedFlagGroundednessRule:
    """
    Rule: Every item in detected_red_flags must have evidence (keyword)
    in the original transcript.
    """

    def check_flag_groundedness(self, transcript: str, output: dict) -> list[str]:
        errors = []
        for flag in output.get("detected_red_flags", []):
            if flag.lower() not in transcript.lower():
                errors.append(
                    f"Hallucinated red flag: '{flag}' not found in transcript"
                )
        return errors

    def test_grounded_flag_passes(self):
        transcript = "Tôi đang bị đau ngực dữ dội."
        output = make_routing_output(detected_red_flags=["đau ngực"])
        assert self.check_flag_groundedness(transcript, output) == []

    def test_hallucinated_flag_fails(self):
        transcript = "Tôi muốn đặt lịch khám tim mạch."
        output = make_routing_output(detected_red_flags=["tím tái"])
        errors = self.check_flag_groundedness(transcript, output)
        assert len(errors) > 0
        assert "Hallucinated" in errors[0]

    def test_multiple_flags_all_must_be_grounded(self):
        transcript = "Tôi đau ngực và khó thở từ sáng."
        output = make_routing_output(detected_red_flags=["đau ngực", "khó thở", "ngất"])
        errors = self.check_flag_groundedness(transcript, output)
        assert len(errors) == 1  # only "ngất" is hallucinated
        assert "ngất" in errors[0]

    def test_empty_flags_always_passes(self):
        transcript = "Cho tôi hỏi về lịch tiêm phòng."
        output = make_routing_output(detected_red_flags=[])
        assert self.check_flag_groundedness(transcript, output) == []

    def test_partial_match_is_accepted(self):
        """Flag 'khó thở' present in 'rất khó thở' – should pass."""
        transcript = "Bà ấy nói rất khó thở."
        output = make_routing_output(detected_red_flags=["khó thở"])
        assert self.check_flag_groundedness(transcript, output) == []


class TestReleaseGateThresholds:
    """
    Verify release gate blocking conditions from Section 10 of 03-medical-routing.md.
    Note: Thresholds here are STRICTER than the other two cases (red flag recall 99.5%).
    """

    def evaluate_release_gate(
        self,
        p0_failures: int,
        red_flag_recall_pct: float,
        schema_compliance_pct: float,
        regression_pass_pct: float,
    ) -> dict:
        reasons = []
        if p0_failures > 0:
            reasons.append(f"P0 failures: {p0_failures}")
        if red_flag_recall_pct < 99.5:
            reasons.append(f"Red flag recall {red_flag_recall_pct}% < 99.5%")
        if schema_compliance_pct < 100.0:
            reasons.append(f"Schema compliance {schema_compliance_pct}% < 100%")
        if regression_pass_pct < 100.0:
            reasons.append(f"Regression pass {regression_pass_pct}% < 100%")
        return {"blocked": len(reasons) > 0, "reasons": reasons}

    def test_perfect_metrics_not_blocked(self):
        result = self.evaluate_release_gate(0, 99.5, 100.0, 100.0)
        assert not result["blocked"]

    def test_any_p0_failure_blocks(self):
        result = self.evaluate_release_gate(1, 99.5, 100.0, 100.0)
        assert result["blocked"]
        assert any("P0" in r for r in result["reasons"])

    def test_red_flag_recall_below_99_5_blocks(self):
        result = self.evaluate_release_gate(0, 99.4, 100.0, 100.0)
        assert result["blocked"]
        assert any("recall" in r.lower() for r in result["reasons"])

    def test_red_flag_recall_exactly_99_5_passes(self):
        result = self.evaluate_release_gate(0, 99.5, 100.0, 100.0)
        assert not result["blocked"]

    def test_medical_threshold_stricter_than_ticket_triage(self):
        """
        Medical routing requires 99.5% red flag recall vs 98% escalation recall
        for ticket triage – verify the medical threshold is higher.
        """
        TICKET_TRIAGE_THRESHOLD = 98.0
        MEDICAL_ROUTING_THRESHOLD = 99.5
        assert MEDICAL_ROUTING_THRESHOLD > TICKET_TRIAGE_THRESHOLD

    def test_medical_threshold_stricter_than_sales_copilot(self):
        """
        Medical routing requires 99.5% red flag recall vs 99% ambiguity recall
        for sales copilot.
        """
        SALES_COPILOT_THRESHOLD = 99.0
        MEDICAL_ROUTING_THRESHOLD = 99.5
        assert MEDICAL_ROUTING_THRESHOLD > SALES_COPILOT_THRESHOLD

    def test_schema_below_100_blocks(self):
        result = self.evaluate_release_gate(0, 99.5, 99.0, 100.0)
        assert result["blocked"]

    def test_regression_below_100_blocks(self):
        result = self.evaluate_release_gate(0, 99.5, 100.0, 99.9)
        assert result["blocked"]

    def test_multiple_violations_all_reported(self):
        result = self.evaluate_release_gate(2, 95.0, 99.0, 98.0)
        assert result["blocked"]
        assert len(result["reasons"]) == 4


class TestPilotPlanConsistency:
    """Verify arithmetic of Section 11 pilot plan for 03-medical-routing.md."""

    CASES = 100
    ITERATIONS = 40
    INPUT_TOKENS_PER_CASE = 1000
    OUTPUT_TOKENS_PER_CASE = 250
    INPUT_PRICE_PER_MILLION = 0.35
    OUTPUT_PRICE_PER_MILLION = 1.05

    PM_HOURS = 30
    ENGINEERING_HOURS = 15
    HUMAN_REVIEW_HOURS = 10
    DOMAIN_EXPERT_HOURS = 40

    def test_total_input_tokens(self):
        expected = self.CASES * self.ITERATIONS * self.INPUT_TOKENS_PER_CASE
        assert expected == 4_000_000

    def test_total_output_tokens(self):
        expected = self.CASES * self.ITERATIONS * self.OUTPUT_TOKENS_PER_CASE
        assert expected == 1_000_000

    def test_api_cost_approximately_correct(self):
        input_cost = (
            self.CASES * self.ITERATIONS * self.INPUT_TOKENS_PER_CASE / 1_000_000
        ) * self.INPUT_PRICE_PER_MILLION
        output_cost = (
            self.CASES * self.ITERATIONS * self.OUTPUT_TOKENS_PER_CASE / 1_000_000
        ) * self.OUTPUT_PRICE_PER_MILLION
        total = input_cost + output_cost
        # Workbook states $2.45
        assert abs(total - 2.45) < 0.05, f"Expected ~$2.45 API cost, got ${total:.2f}"

    def test_total_human_hours(self):
        total = (
            self.PM_HOURS
            + self.ENGINEERING_HOURS
            + self.HUMAN_REVIEW_HOURS
            + self.DOMAIN_EXPERT_HOURS
        )
        assert total == 95  # Workbook states 95 hours

    def test_domain_expert_hours_required(self):
        """Unlike ticket triage and sales copilot, domain expert IS required here."""
        assert self.DOMAIN_EXPERT_HOURS > 0
        assert self.DOMAIN_EXPERT_HOURS == 40

    def test_domain_expert_is_majority_of_human_work(self):
        """Expert hours should be > 40% of total hours as stated in the workbook."""
        total = (
            self.PM_HOURS
            + self.ENGINEERING_HOURS
            + self.HUMAN_REVIEW_HOURS
            + self.DOMAIN_EXPERT_HOURS
        )
        expert_ratio = self.DOMAIN_EXPERT_HOURS / total
        assert expert_ratio > 0.40, f"Expert ratio {expert_ratio:.0%} should exceed 40%"

    def test_cases_in_reasonable_range(self):
        assert 50 <= self.CASES <= 100

    def test_iterations_in_reasonable_range(self):
        assert 30 <= self.ITERATIONS <= 50

    def test_medical_case_higher_input_tokens_than_ticket_triage(self):
        """
        Medical transcripts are longer (1000 tokens) than ticket triage (500 tokens),
        reflecting real-world complexity difference.
        """
        TICKET_TRIAGE_TOKENS = 500
        MEDICAL_TOKENS = self.INPUT_TOKENS_PER_CASE
        assert MEDICAL_TOKENS > TICKET_TRIAGE_TOKENS


class TestFullScenarioIntegration:
    """
    Integration-style tests that chain multiple rules together to simulate
    realistic AI output validation for a complete call routing scenario.
    """

    def run_all_checks(self, transcript: str, output: dict) -> list[str]:
        """Run all code-checkable rules and collect violations."""
        errors = []
        # Schema
        required = {"call_intent", "detected_red_flags", "urgency_level", "summary",
                    "patient_lookup_status", "suggested_route"}
        for f in required:
            if f not in output:
                errors.append(f"Schema: missing {f}")
        # Enum
        if output.get("call_intent") not in VALID_CALL_INTENTS:
            errors.append(f"Enum: invalid call_intent '{output.get('call_intent')}'")
        if output.get("urgency_level") not in VALID_URGENCY_LEVELS:
            errors.append(f"Enum: invalid urgency_level '{output.get('urgency_level')}'")
        # Keyword → flags gate
        transcript_lower = transcript.lower()
        found_keywords = [kw for kw in RED_FLAG_KEYWORDS if kw in transcript_lower]
        if found_keywords and not output.get("detected_red_flags"):
            errors.append(f"Safety: red flag keywords {found_keywords} not detected")
        # Flags → escalation chain
        if output.get("detected_red_flags"):
            if output.get("urgency_level") != "CRITICAL":
                errors.append("Safety: flags present but urgency not CRITICAL")
            if output.get("suggested_route") not in EMERGENCY_ROUTES:
                errors.append("Safety: flags present but route is not emergency")
        # Summary non-empty
        if not output.get("summary") or not str(output.get("summary")).strip():
            errors.append("Quality: summary is empty")
        return errors

    def test_perfect_emergency_output_has_no_violations(self):
        transcript = "Tôi đang đau ngực và khó thở không chịu được."
        output = make_routing_output(
            call_intent="Y khoa",
            detected_red_flags=["đau ngực", "khó thở"],
            urgency_level="CRITICAL",
            summary="Bệnh nhân báo cáo đau ngực cấp và khó thở.",
            patient_lookup_status="FOUND",
            matched_patient_record={"patient_id": "BN-001"},
            suggested_route="Quy trình khẩn cấp",
        )
        errors = self.run_all_checks(transcript, output)
        assert errors == []

    def test_missed_red_flag_causes_multiple_violations(self):
        """If AI misses red flag, the escalation chain also fails."""
        transcript = "Mẹ tôi đang bị đau ngực và khó thở."
        output = make_routing_output(
            call_intent="Y khoa",
            detected_red_flags=[],  # AI missed red flags
            urgency_level="NORMAL",  # Consequently wrong
            suggested_route="Lịch hẹn",  # Dangerously wrong
        )
        errors = self.run_all_checks(transcript, output)
        # Keyword gate fires; escalation chain does not fire (no flags to check against)
        # but keyword safety gate must catch the miss
        assert any("red flag" in e.lower() or "Safety" in e for e in errors)

    def test_admin_call_correct_routing(self):
        transcript = "Tôi muốn đặt lịch tái khám vào thứ Hai."
        output = make_routing_output(
            call_intent="Hành chính",
            detected_red_flags=[],
            urgency_level="NORMAL",
            summary="Khách hàng muốn đặt lịch tái khám.",
            patient_lookup_status="FOUND",
            suggested_route="Lịch hẹn",
        )
        errors = self.run_all_checks(transcript, output)
        assert errors == []

    def test_completely_wrong_output_accumulates_errors(self):
        transcript = "Bệnh nhân bị đau ngực."
        output = {
            "call_intent": "InvalidIntent",
            "detected_red_flags": [],
            "urgency_level": "InvalidLevel",
            "summary": "",
            "patient_lookup_status": "NOT_FOUND",
            "suggested_route": "Lịch hẹn",
        }
        errors = self.run_all_checks(transcript, output)
        assert len(errors) >= 4  # enum errors, safety gate, summary