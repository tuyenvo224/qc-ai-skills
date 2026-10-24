# Done Criteria & Quantitative Coverage Thresholds

Read this at Step 7 of `SKILL.md`'s workflow (Coverage Verification) — the full done-criteria checklist plus the quantitative pass/fail/conditional-pass thresholds and how to report them.

---

## 9. Done Criteria

**PHẢI đạt TẤT CẢ criteria trước khi submit output.**

### 9.1 Coverage Check

```
□ MỌI feature/function trong spec đều có test case
□ MỌI business rule có ≥1 positive TC + ≥1 negative TC
□ MỌI error code trong spec có ≥1 TC trigger chính xác error đó
□ MỌI DB table liên quan có verify data integrity
□ MỌI workflow/state machine có test valid + invalid transitions
□ MỌI API endpoint có test positive + negative + boundary
□ P1 features: exhaustive coverage (mọi path, mọi boundary)
□ P2 features: thorough coverage (main paths, key boundaries)
□ P3 features: standard coverage (happy path, obvious boundaries)
```

### 9.2 Technique Check

```
□ MỌI test case có [Technique Tag] trong Test Objective
□ P1 features: ≥6 techniques applied
□ P2 features: ≥4 techniques applied
□ P3 features: ≥3 techniques applied
□ P4 features: ≥1 technique applied
□ MỌI input fields: EP + BVA applied
□ MỌI business rules ≥2 conditions: DT applied
□ MỌI workflow features: ST applied
□ Các TC từ techniques khác nhau KHÔNG trùng nội dung
```

### 9.3 Quality Check

```
□ MỌI TC có đúng 1 objective duy nhất
□ MỌI TC có test data cụ thể (không "valid data" mà phải có giá trị)
□ MỌI TC có expected result đo lường được
□ MỌI TC liên quan data change có DB verification trong expected result
□ KHÔNG có TC trùng lặp (cùng scenario, khác wording)
□ KHÔNG có TC mơ hồ (pass/fail không rõ ràng)
```

### 9.4 Structure Check

```
□ TC nhóm theo chức năng (KHÔNG theo test type)
□ Trong mỗi nhóm: đúng thứ tự 9 loại (UI→Happy→BL→NEG→BVA→PM→DB→SEC→Edge)
□ Các nhóm sắp xếp theo flow nghiệp vụ
□ Test IDs theo naming convention (AREA-NUMBER)
```

### 9.5 Output Check

```
□ Đúng format 4 cột (STT | Test Objective | Test Steps | Expected Result)
□ Coverage Summary Table 1 (Test Type) có ở cuối document
□ Coverage Summary Table 2 (Technique) có ở cuối document
□ Assumptions list có ở cuối (nếu spec mơ hồ)
□ Không còn TODO, placeholder, hoặc "TBD"
```

### 9.6 End-User Check

```
□ Đã chạy End-User Thinking Checklist (Phần 6.1) cho mọi feature
□ Adhoc cases từ góc nhìn end-user đã được bổ sung
□ Double-click / double-submit scenarios đã cover (cho create operations)
□ Cross-user / cross-tenant scenarios đã cover (nếu multi-user)
```

### 9.7 Quantitative Coverage Thresholds ✨ NEW

**CRITICAL:** Section này define số liệu cụ thể để xác định test suite đạt chuẩn hay chưa.

#### 9.7.0 KHÔNG tự đếm coverage bằng tay — dùng `scripts/compute_coverage.py`

Một agent tự viết test case rồi tự đếm/tự báo cáo "P1 coverage = 100%" là **không đáng tin** (self-verification bias) — dễ đếm nhầm hoặc lạc quan hóa để đạt PASS. Vì vậy, các con số ở 9.7.1-9.7.7 **PHẢI được tính bằng script**, không được ước lượng thủ công:

1. Trước khi tính coverage, dựng **Traceability Matrix** tường minh — mỗi Requirement/Risk phải trỏ tới ≥1 Test Case ID cụ thể (không chỉ nói "đã cover" mà không chỉ ra TC nào).
2. Ghi lại `requirements`, `risks`, `features` (tên + priority) và mỗi `test_cases[].requirement` / `.risk` / `.feature` vào cùng file JSON đã dùng cho `generate_testcase_excel.py` (xem schema trong `excel-export.md`). Nếu các mã này đến từ `requirement-analyzer`/`risk-scout-analyzer`/`bug-hunter`, xem "Input từ pipeline QA" trong `SKILL.md` để map đúng — không tự đặt lại mã hay đổi priority/category đã có sẵn.
3. Chạy, ghi thẳng `--matrix-out`/`--report-out` vào **cùng thư mục output** (`test-case-designed/`, xem "Output location" trong `SKILL.md`) với **cùng tiền tố tên file** như file `.xlsx` (`yyyy-mm-dd_{ProjectName}_{FeatureName}_`) — không dùng tên file trần, vì tên trần sẽ bị ghi vào working directory hiện tại (không rõ nơi):
   ```bash
   python .claude/skills/test-case-generator/scripts/compute_coverage.py <input.json> \
       --matrix-out test-case-designed/yyyy-mm-dd_{ProjectName}_{FeatureName}_traceability-matrix.md \
       --report-out test-case-designed/yyyy-mm-dd_{ProjectName}_{FeatureName}_coverage-report.md
   ```
4. Script tự tính: % coverage requirement/risk theo priority, số kỹ thuật theo từng feature, % assumptions, duplicate TC, TC thiếu tag/priority — và ra verdict PASS/CONDITIONAL PASS/FAIL kèm lý do cụ thể (không chỉ nói "FAIL", mà liệt kê chính xác requirement/risk/feature nào chưa đạt).
5. Nếu script trả FAIL → quay lại Step 5, bổ sung TC cho đúng chỗ script chỉ ra, rồi chạy lại script — không tự sửa số liệu trong report bằng tay.
6. Đính kèm cả `traceability-matrix.md` và `coverage-report.md` (2 file thật đã ghi ra ở bước 3, cùng thư mục với `.xlsx`) vào output cuối cùng (Step 8), không chỉ đưa ra con số % trần trụi.

Các mục 9.7.1-9.7.7 dưới đây mô tả **luật tính** mà script áp dụng — dùng để hiểu/kiểm tra/mở rộng script, không phải để tự tính tay thay cho nó.

#### 9.7.1 Requirements Coverage Thresholds

**MANDATORY Minimums:**

| Requirement Priority | Coverage Threshold | Consequence if Below |
|---------------------|-------------------|----------------------|
| **P1 (Critical)** | **100%** - No exception | FAIL - Cannot release without P1 coverage |
| **P2 (High)** | **≥95%** | CONDITIONAL - Explain missing 5%, get approval |
| **P3 (Medium)** | **≥80%** | WARN - Acceptable if justified |
| **P4 (Low)** | **≥60%** | ACCEPTABLE - Low priority features |

**Calculation:**
```
Coverage % = (Requirements với ≥1 test case / Total Requirements) × 100%

Example:
- Total P1 requirements: 25
- P1 requirements covered: 25
- Coverage: 25/25 = 100% ✅ PASS

- Total P2 requirements: 40  
- P2 requirements covered: 38
- Coverage: 38/40 = 95% ✅ PASS (exactly at threshold)

- Total P3 requirements: 30
- P3 requirements covered: 22
- Coverage: 22/30 = 73% ❌ FAIL (below 80% threshold)
```

**Action if Below Threshold:**
- P1 below 100%: **BLOCK SUBMISSION** - Bổ sung test cases cho missing requirements
- P2 below 95%: **CONDITIONAL** - List missing requirements, justify, get QA Lead approval
- P3 below 80%: **WARN** - Document missing requirements, plan for next iteration

#### 9.7.2 Risk Coverage Thresholds

**MANDATORY Minimums:**

| Risk Priority | Coverage Threshold | Consequence |
|--------------|-------------------|-------------|
| **P1 (Critical Risk)** | **100%** - Every P1 risk has ≥1 test case | FAIL if not met |
| **P2 (High Risk)** | **≥90%** | CONDITIONAL |
| **P3 (Medium Risk)** | **≥70%** | ACCEPTABLE |

**Special Rules:**
- **Security risks (any priority):** 100% coverage (no exception)
- **Financial risks:** 100% coverage
- **Data integrity risks:** 100% coverage
- **Bug hypotheses (if provided):** 100% coverage

**Calculation:**
```
Risk Coverage % = (Risks có ≥1 TC mapping / Total Risks) × 100%

Example:
- P1 risks: 7 total, 7 covered → 100% ✅
- P2 risks: 12 total, 11 covered → 92% ✅ (≥90%)
- Security risks: 5 total, 5 covered → 100% ✅ (mandatory)
```

#### 9.7.3 Technique Application Thresholds

**Per-Feature Minimums (ENFORCED):**

| Feature Priority | Minimum Techniques | Failure Consequence |
|-----------------|-------------------|---------------------|
| **P1** | ≥6 techniques | FAIL - Feature under-tested |
| **P2** | ≥4 techniques | FAIL - Insufficient depth |
| **P3** | ≥3 techniques | WARN - Should improve |
| **P4** | ≥1 technique | ACCEPTABLE |

**Overall Suite Minimum:**
- **All 9 techniques** must be used at least once across entire test suite
- If any technique missing (0 count) → WARN (except PW and EXP for simple projects)

**Mandatory Techniques per Feature Type:**
- Features with **input fields:** EP + BVA (no exception)
- Features with **≥2 conditions:** DT (no exception)
- Features with **state/status:** ST (no exception)
- Features với **workflow:** UC (no exception)
- **P1/P2 features:** EG (no exception)

**Calculation:**
```
Technique Count per Feature = Count unique technique tags in that feature's TCs

Example Feature "Login" (P1):
- TC-001 [UC], TC-002 [EP], TC-003 [EP], TC-004 [BVA], TC-005 [BVA], 
  TC-006 [DT], TC-007 [ST], TC-008 [EG], TC-009 [CL]
- Unique techniques: UC, EP, BVA, DT, ST, EG, CL = 7 techniques
- Requirement: P1 needs ≥6
- Result: 7 ≥ 6 ✅ PASS
```

#### 9.7.4 Test Case Quality Thresholds

**Mandatory Quality Standards:**

| Quality Metric | Threshold | Check Method |
|----------------|-----------|--------------|
| **Technique tags present** | 100% (every TC must have) | Scan Test Objective column for [TAG] |
| **Specific test data** | 100% (no "valid data", must have actual values) | Manual review or regex check |
| **Measurable expected results** | 100% (no "it works", must be specific) | Manual review |
| **DB verification (for data changes)** | 100% (CREATE/UPDATE/DELETE must verify DB) | Check Expected Result for "DB:" entries |
| **Duplicate test cases** | 0% (after deduplication) | Compare Test Objective + Steps |
| **Test cases without priority** | 0% (all must have P1-P4) | Check Priority column |
| **Vague objectives** | <5% | Manual review quality |

#### 9.7.5 Assumptions Threshold

**Maximum Allowable:**
- **Assumptions ≤10% of total test cases**
  - If assumptions > 10% → **FAIL** (spec quá unclear, không thể viết test tốt)
  - Example: 100 TCs, max 10 assumptions OK. 15 assumptions = FAIL.

**Assumption Impact Distribution:**
- **Critical impact assumptions:** ≤3 (nếu >3 = too many unknowns)
- **High impact assumptions:** ≤10
- **Medium/Low impact:** Unlimited (acceptable)

**Action if Exceed:**
- STOP test case writing
- Document all unclear points
- Request BA/PO clarification
- Resume after clarification

#### 9.7.6 Coverage Summary Table Requirements

**Table 1: Test Type Coverage (MANDATORY)**
```
Minimum test types covered:
- P1 features: ≥6 types (FN, NEG, DI + at least 3 others applicable)
- P2 features: ≥4 types
- P3 features: ≥3 types
```

**Table 2: Technique Coverage (MANDATORY)**
```
All features meet minimum:
- 100% P1 features have ≥6 techniques
- 100% P2 features have ≥4 techniques  
- 100% P3 features have ≥3 techniques
- Status column: ALL show "PASS"
```

**If ANY feature shows "FAIL" in Status → ENTIRE TEST SUITE = FAIL**

#### 9.7.7 Pass/Fail Decision Logic

**Overall Test Suite Evaluation:**

```
PASS CONDITIONS (ALL must be TRUE):
✅ P1 requirements coverage = 100%
✅ P2 requirements coverage ≥ 95%
✅ P1 risk coverage = 100%
✅ Security risk coverage = 100%
✅ All P1 features meet ≥6 techniques
✅ All P2 features meet ≥4 techniques
✅ 100% TCs have technique tags
✅ 100% TCs have priorities
✅ Assumptions ≤ 10% of TCs
✅ Duplicate TCs = 0
✅ Coverage tables present and complete

FAIL CONDITIONS (ANY is TRUE):
❌ Any P1 requirement without test case
❌ Any P1 risk without test case  
❌ Any P1 feature < 6 techniques
❌ Any P2 feature < 4 techniques
❌ Any TC missing technique tag
❌ Assumptions > 10% of TCs
❌ Coverage tables missing

CONDITIONAL PASS:
⚠️ P2 coverage 90-94% (below 95% but above 90%)
⚠️ P3 coverage 70-79% (below 80% but above 70%)
→ Require: Document gaps + Get QA Lead approval
```

#### 9.7.8 Minimum Test Case Counts

**Rough Guidelines (not hard rules, but useful estimates):**

| Feature Complexity | Minimum TCs | Typical Range |
|-------------------|-------------|---------------|
| **Very Simple** (1 field, 1 action) | 5-8 TCs | Happy + Negative + Boundary |
| **Simple** (2-3 fields, basic validation) | 10-15 TCs | + Security + Permission |
| **Medium** (5+ fields, business logic) | 20-30 TCs | + Decision table + Edge cases |
| **Complex** (Workflow, state machine, integration) | 30-50 TCs | + State transitions + Concurrent |
| **Very Complex** (Payment, multi-step, critical) | 50-80 TCs | + All patterns + Exhaustive |

**By Priority:**
- **P1 Feature:** Expect 20-50 TCs (exhaustive testing)
- **P2 Feature:** Expect 10-25 TCs (thorough testing)
- **P3 Feature:** Expect 5-12 TCs (standard testing)
- **P4 Feature:** Expect 2-5 TCs (smoke testing)

**Sanity Check:**
- If P1 feature only has 5 TCs → **SUSPICIOUS** (likely under-tested)
- If P4 feature has 50 TCs → **SUSPICIOUS** (likely over-tested or wrong priority)

#### 9.7.9 Example Pass/Fail Scenarios

**Scenario 1: PASS**
```
Project: GiftPort Category Management
- Total requirements: 23 (P1: 10, P2: 8, P3: 5)
- Requirements covered: 23 (100% P1, 100% P2, 100% P3) ✅
- Total risks: 10 (P1: 3, P2: 5, P3: 2)
- Risks covered: 10 (100% all) ✅
- Feature "Create Category" (P1): 8 techniques applied ✅ (≥6)
- Feature "Search" (P2): 5 techniques applied ✅ (≥4)
- All TCs have tags: 100% ✅
- Assumptions: 5 out of 65 TCs = 7.7% ✅ (<10%)
- Coverage tables: Present ✅

VERDICT: ✅ PASS - Test suite meets all thresholds
```

**Scenario 2: FAIL**
```
Project: Brand Management
- P1 requirements: 12 total, 11 covered = 92% ❌ (need 100%)
- Missing: REQ-P1-007 "Code immutability backend check"
- Feature "Create Brand" (P1): 5 techniques ❌ (need ≥6)
  - Missing: DT (decision table for triple uniqueness)
- Assumptions: 18 out of 82 TCs = 22% ❌ (exceed 10%)

VERDICT: ❌ FAIL - Must fix:
1. Add test case for REQ-P1-007
2. Add [DT] test case for Create Brand
3. STOP - Get clarifications to reduce assumptions to <10%
```

**Scenario 3: CONDITIONAL PASS**
```
Project: User Profile
- P1 requirements: 100% ✅
- P2 requirements: 18/20 = 90% ⚠️ (below 95%, but above 90%)
- Missing P2 requirements:
  - REQ-P2-015: "Export to PDF"
  - REQ-P2-018: "Dark mode toggle"
- All other criteria: PASS ✅

VERDICT: ⚠️ CONDITIONAL PASS
- Can proceed if: QA Lead approves skipping 2 P2 requirements
- Justification: "PDF export and dark mode = low user impact, defer to v2.0"
- Document: Add to known limitations section
```

#### 9.7.10 Quality Gate Enforcement

**When to Apply:**

**Gate 1: After Step 5 (Writing)** - Self-check
- Quick scan: All TCs have tags? All have priorities?
- If basic issues found → Fix immediately

**Gate 2: After Step 7 (Coverage Verification)** - Comprehensive check
- Run full quantitative analysis
- Calculate all percentages
- Decide PASS/FAIL/CONDITIONAL
- **If FAIL:** Loop back to Step 5, add missing TCs

**Gate 3: Before Step 8 (Output)** - Final verification
- Re-verify all thresholds
- Double-check calculations
- Confirm PASS status
- **Only submit if PASS or CONDITIONAL PASS with approval**

#### 9.7.11 Reporting Format

**Output của `scripts/compute_coverage.py` đã đúng format này — dùng nguyên output đó, không viết tay lại:**

```markdown
## Coverage Analysis Report

### Requirements Coverage:
- P1: 25/25 (100%) ✅ PASS
- P2: 38/40 (95%) ✅ PASS
- P3: 24/30 (80%) ✅ PASS
- P4: 12/20 (60%) ✅ PASS

### Risk Coverage:
- P1 Risks: 7/7 (100%) ✅ PASS
- P2 Risks: 11/12 (92%) ✅ PASS (≥90%)
- P3 Risks: 8/10 (80%) ✅ PASS (≥70%)
- Security Risks: 5/5 (100%) ✅ PASS (mandatory)

### Technique Application:
- Login (P1): 7 techniques ✅ PASS (≥6)
- Create Order (P1): 8 techniques ✅ PASS (≥6)
- Search (P2): 5 techniques ✅ PASS (≥4)
- Settings (P3): 3 techniques ✅ PASS (≥3)

### Quality Metrics:
- Technique tags: 147/147 (100%) ✅
- Specific test data: 147/147 (100%) ✅
- DB verification: 95/95 applicable (100%) ✅
- Duplicate TCs: 0 ✅
- Assumptions: 8/147 (5.4%) ✅ (<10%)

### Overall Verdict: ✅ PASS
- All quantitative thresholds met
- Test suite approved for execution
- No blockers identified
```

**If FAIL:**
```markdown
### Overall Verdict: ❌ FAIL

Failures:
1. P1 requirements: 23/25 (92%) - Below 100% threshold
   - Missing: REQ-P1-012, REQ-P1-019
   - Action: Add test cases for these requirements

2. Feature "Payment" (P1): 5 techniques - Below ≥6 threshold
   - Missing: DT (decision table)
   - Action: Add [DT] test case for payment conditions

3. Assumptions: 18/82 (22%) - Exceeds 10% threshold
   - Action: Get clarifications from BA to reduce assumptions

STATUS: BLOCKED - Cannot proceed until failures resolved
```

#### 9.7.12 Threshold Exceptions (Rare Cases)

**Khi nào cho phép exceptions:**

**Exception 1: P1 Requirement impossible to test**
```
Example: "System uptime 99.9%" (infrastructure, not functional test)
- Document as "Non-testable requirement (infrastructure/SLA)"
- Exclude from coverage calculation
- Get QA Lead + PO approval
```

**Exception 2: Technique không applicable**
```
Example: Static content page (About Us) - No BVA applicable (no boundaries)
- Document: "BVA not applicable (no input fields)"  
- Adjust minimum: P3 feature with 2 techniques OK (instead of 3)
- Get QA Lead approval
```

**Exception Process:**
1. Document exception với justification rõ ràng
2. List in "Exceptions & Justifications" section
3. Get approval từ QA Lead hoặc QA Manager
4. Include trong coverage report

**Maximum exceptions allowed: ≤5% of total thresholds**

---

