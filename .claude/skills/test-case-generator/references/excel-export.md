# Excel Export Format

Read this when producing the final `.xlsx` deliverable (Step 8 of `SKILL.md`'s workflow) — required sheet structure, column layout, and formatting spec. **Do not hand-build this formatting in Excel or hand-roll a new export script** — feed the test cases as JSON to `scripts/generate_testcase_excel.py`, which already implements everything below (see "Generation method" in `SKILL.md`).

---

### 7.10 Excel Export Format & Instructions ✨ NEW

**CRITICAL:** Mọi test case document PHẢI xuất ra file Excel (.xlsx) theo format chuẩn dưới đây.

#### 7.10.1 Excel File Structure

**File Requirements:**
- **Format:** .xlsx (Excel 2007+ format)
- **Encoding:** UTF-8 (support Vietnamese, emoji, special characters)
- **Minimum Sheets:** 2 sheets (Test Cases + Summary)
- **File Naming:** `{ProjectName}_{FeatureName}_TestCases.xlsx`
  - Example: `GiftPort_CategoryManagement_TestCases.xlsx`

#### 7.10.2 Sheet 1 - Test Cases (Main Sheet)

**Column Structure (10 columns):**

| Column | Header | Width | Format | Content |
|--------|--------|-------|--------|---------|
| **A** | STT | 5 | Number | Sequential: 1, 2, 3... |
| **B** | Test ID | 15 | Text | TC-XXX-NNN |
| **C** | Technique | 10 | Text | [EP], [BVA], [DT], [ST], [UC], [PW], [EG], [CL], [EXP] |
| **D** | Priority | 8 | Text + Color | P1, P2, P3, P4 (với color-coding bên dưới) |
| **E** | Test Objective | 38-40 | Text wrap | Full objective including [Tag] |
| **F** | Test Steps | 45-50 | Text wrap | Numbered steps với test data cụ thể |
| **G** | Expected Result | 45-50 | Text wrap | Specific outcomes (UI + API + DB) |
| **H** | Requirement | 14 | Text | REQ-XXX, UC3.1-R01, etc. |
| **I** | Risk/Bug | 15 | Text wrap | R-001, BUG-XXX-NNN (separated by newline) |
| **J** | Status | 12 | Text + Color | Pass / Fail / Blocked / Deprecated / Not Run (để trống = Not Run; `Deprecated` dùng khi update test suite cũ — xem `updating-existing-suite.md`) |

#### 7.10.3 Formatting Specifications

**Header Row (Row 3 nếu có title rows, hoặc Row 1):**
```
Background Color: Blue (#4472C4)
Font: Bold, White (#FFFFFF), Size 11pt
Alignment: Horizontal Center, Vertical Center
Border: All sides, Thin, Black
Row Height: 30px
Text Wrap: Enabled
```

**Priority Column (Column D) - Color Coding (BẮT BUỘC):**
```
P1 (Critical):
  - Background: Red (#FF0000)
  - Font: Bold, White (#FFFFFF), Size 10pt
  - Alignment: Center
  
P2 (High):
  - Background: Orange (#FFC000)
  - Font: Bold, Black (#000000), Size 10pt
  - Alignment: Center
  
P3 (Medium):
  - Background: Light Green (#92D050)
  - Font: Bold, Black (#000000), Size 10pt
  - Alignment: Center
  
P4 (Low):
  - Background: Light Gray (#D9D9D9)
  - Font: Regular, Black (#000000), Size 10pt
  - Alignment: Center
```

**Status Column (Column J) - Color Coding (BẮT BUỘC, dùng Conditional Formatting):**
```
Pass:
  - Background: Light Green (#C6EFCE)
  - Font: Bold, Dark Green (#006100), Size 10pt
  - Alignment: Center

Fail:
  - Background: Light Red (#FFC7CE)
  - Font: Bold, Dark Red (#9C0006), Size 10pt
  - Alignment: Center

Blocked:
  - Background: Light Yellow (#FFEB9C)
  - Font: Bold, Dark Yellow (#9C5700), Size 10pt
  - Alignment: Center

Not Run / Empty:
  - Background: Light Gray (#F2F2F2)
  - Font: Regular, Gray (#595959), Size 10pt
  - Alignment: Center

QUAN TRỌNG: Dùng Conditional Formatting (openpyxl: ConditionalFormattingList + FormulaRule)
để color tự động cập nhật khi tester nhập giá trị vào Excel.
```

**Data Rows (All Test Cases):**
```
Border: All sides, Thin, Black
Alignment:
  - Columns A, B, C, D, J: Center horizontal, Top vertical
  - Columns E, F, G, H, I: Left horizontal, Top vertical
Text Wrap: Enabled for E, F, G, I, J
Row Height: Auto-adjust based on content
  - Minimum: 35px
  - Maximum: 500px
  - Formula: based on estimated wrapped-line count per cell (accounts for
    explicit "\n" line breaks AND word-wrap at each column's width — a plain
    character-count/8 estimate undercounts multi-step "1...\n2...\n3..." text
    and truncates it), not a plain character-count heuristic
    (see `_autofit_row_height`/`_wrapped_line_count` in generate_testcase_excel.py)
```

**Excel Features (BẮT BUỘC):**
- ✅ **Frozen Panes:** Freeze at cell E4 (freeze headers + ID columns A-D)
- ✅ **Auto-Filter:** Enable on header row (allow filter by Priority, Technique, etc.)
- ✅ **Column Widths:** Set as specified (don't use default)
- ✅ **Text Wrap:** Enable for long-text columns

#### 7.10.3b BẮT BUỘC — Rows 1-8: Company Form Header Block

**Mọi file Excel xuất ra ĐỀU PHẢI có khối metadata dạng "KỊCH BẢN KIỂM THỬ" ở đầu Sheet 1** (giống `assets/Template_TCs.xlsx`) — script `generate_testcase_excel.py` tự chèn khối này (rows 1-8) và đẩy Title/Meta/Header/Data xuống 8 hàng (Title → row 9, Meta → row 10, Header → row 11, Data → row 12+) **luôn luôn, không cần chờ người dùng yêu cầu và không có cách tắt**. Không cần làm gì thêm để khối này xuất hiện — nó tự động có mặt trong mọi lần chạy script.

Key `"metadata"` trong JSON input (xem schema dưới) chỉ dùng để **điền giá trị** cho các cell của khối (link spec, redmine, prototype, domain, account, người tạo TCs...) — nếu không đưa key này (hoặc thiếu field), các cell tương ứng vẫn xuất hiện nhưng để trống, riêng `screen_name` tự fallback về `feature_name` ở top-level JSON.

**Layout (cố định, giống template):**
```
E1                : "KỊCH BẢN KIỂM THỬ *"   (title, bold size 20, center)
E2 / F2           : "Tên màn hình/Tên chức năng" (label) / giá trị (metadata.screen_name)
H2:J2             : "QC thực hiện" (label, nền vàng #FFFF00)
E3 / F3           : "Link spec" (label) / giá trị (metadata.spec_link)
H3 / I3 / J3      : Tên QC (metadata.qc_name) / Ngày (metadata.qc_date, mặc định hôm nay) / Loại công việc (metadata.work_type, mặc định "Tạo TCs")
E4 / F4           : "Link redmine" (label) / giá trị (metadata.redmine_link)
E5 / F5           : "Prototype" (label) / giá trị (metadata.prototype)
E6 / F6           : "Domain" (label) / giá trị (metadata.domain)
E7 / F7           : "Account" (label) / giá trị (metadata.account)
Row 8             : hàng đóng khung (border only, không có nội dung)
```

**JSON schema bổ sung** (thêm vào object gốc, ngang hàng với `test_cases`):
```json
"metadata": {
  "screen_name": "Đăng nhập",
  "spec_link": "",
  "redmine_link": "",
  "prototype": "",
  "domain": "",
  "account": "",
  "qc_name": "",
  "qc_date": "",
  "work_type": "Tạo TCs"
}
```
Mọi field trong `metadata` là optional — thiếu field nào thì cell tương ứng để trống (trừ `screen_name` fallback về `feature_name`, `qc_date` mặc định hôm nay, `work_type` mặc định `"Tạo TCs"`). Nếu không có thông tin thật cho Link spec/redmine/Prototype/Domain/Account/QC name — **không tự bịa giá trị**, để trống là đúng (người dùng sẽ điền tay sau); nhưng khối 8 hàng vẫn phải xuất hiện dù `metadata` bị bỏ qua hoàn toàn khỏi JSON input.

#### 7.10.4 Optional Title Rows (Recommended)

**Row 1 - Main Title:**
```
Merged Cells: A1:J1
Content: "{Project Name} - {Feature Name} - Test Cases"
Font: Bold, Size 14pt, White (#FFFFFF)
Background: Dark Blue (#203864)
Alignment: Center horizontal, Center vertical
Row Height: 25px
```

**Row 2 - Meta Information:**
```
Merged Cells: A2:J2
Content: "Generated: YYYY-MM-DD | Total: {XX} TCs | P1: {XX} | P2: {XX} | P3: {XX}"
Font: Italic, Size 10pt, Black
Alignment: Center horizontal
Row Height: 18px
```

**Row 3 - Headers (as described above)**

#### 7.10.5 Sheet 2 - Summary & Statistics

**Required Content (Structured Format):**

**Block A: Project Information**
```
A1: "Project Summary"  (Merged A1:B1, Bold, Size 14)
A3: "Project Name"     B3: {value}
A4: "Feature/Module"   B4: {value}
A5: "Generated Date"   B5: YYYY-MM-DD
A6: "Version"          B6: v1.0
A7: "Total Test Cases" B7: {count}
```

**Block B: Priority Distribution**
```
A9:  "By Priority"     B9: "Count"  (Bold, Gray bg #D9E1F2)
A10: "P1 (Critical)"   B10: {count}
A11: "P2 (High)"       B11: {count}
A12: "P3 (Medium)"     B12: {count}
A13: "P4 (Low)"        B13: {count}
```

**Block C: Technique Coverage**
```
A15: "By Technique"           B15: "Count"  (Bold, Gray bg)
A16: "[EP] Equivalence Part." B16: {count}
A17: "[BVA] Boundary Value"   B17: {count}
A18: "[DT] Decision Table"    B18: {count}
A19: "[ST] State Transition"  B19: {count}
A20: "[UC] Use Case"          B20: {count}
A21: "[PW] Pairwise"          B21: {count}
A22: "[EG] Error Guessing"    B22: {count}
A23: "[CL] Checklist"         B23: {count}
A24: "[EXP] Exploratory"      B24: {count}
```

**Block D: Test Type Distribution**
```
A26: "By Test Type"     B26: "Count"
A27: "Functional (FN)"  B27: {count}
A28: "Business Logic (BL)" B28: {count}
A29: "Negative (NEG)"   B29: {count}
A30: "Security (SEC)"   B30: {count}
A31: "Edge Cases (EC)"  B31: {count}
... (list all applicable)
```

**Column Widths:**
- Column A: 30-35
- Column B: 12-15

#### 7.10.6 Sheet 3 - Assumptions Tracking (Optional)

**Create chỉ khi:** Spec có unclear points và có assumptions được document

**Column Structure:**
| Column | Header | Width | Content |
|--------|--------|-------|---------|
| A | Assumption ID | 12 | ASM-001, ASM-002 |
| B | Category | 15 | Data Format, Business Rule, Error Handling, Security |
| C | Description | 40 | Chi tiết assumption |
| D | Impact | 10 | Critical, High, Medium, Low |
| E | Test Cases Affected | 20 | TC-001, TC-022, TC-035 |
| F | Status | 12 | Pending, Confirmed, Rejected, Modified |
| G | Verified By | 15 | BA, Dev Team, PO |
| H | Date | 12 | YYYY-MM-DD |
| I | Resolution | 30 | Details of confirmation/rejection |

**Formatting:**
- Header: Blue bg, White text, Bold
- Status colors:
  - Pending: Yellow (#FFFF00)
  - Confirmed: Green (#00FF00)
  - Rejected: Red (#FF0000)

#### 7.10.7 Implementation — use the provided script

**Do NOT hand-write openpyxl code and do NOT hand-roll a new export script.** A ready-made, tested generator already exists at `scripts/generate_testcase_excel.py`. It implements every formatting rule in 7.10.1-7.10.6 (title rows, header styling, priority color-coding for P1-P4, Status conditional formatting, frozen panes, auto-filter, Summary sheet, optional Assumptions sheet).

**Step A — write the test cases (and assumptions, if any) to a JSON file** matching this schema:

```json
{
  "project_name": "GiftPort",
  "feature_name": "Category Management",
  "version": "v1.0",
  "test_cases": [
    {
      "id": "TC-CAT-001",
      "technique": "UC",
      "priority": "P2",
      "objective": "[UC] Verify danh sách displays correctly",
      "steps": "1. Navigate to list screen\n2. Observe grid",
      "expected": "Grid shows 10 records\nSorted DESC by created_at",
      "requirement": "UC3.1-R01",
      "risk": "",
      "status": "",
      "test_type": "FN,UI"
    }
  ],
  "assumptions": [
    {
      "id": "ASM-001",
      "category": "Data Format",
      "description": "Spec does not specify max length, assumed 255",
      "impact": "Medium",
      "test_cases_affected": "TC-CAT-003",
      "status": "Pending"
    }
  ]
}
```

Notes on the schema:
- `objective`, `steps`, `expected`, and `assumptions[].description` — write in **Vietnamese** (see `writing-format.md` 7.0). The script transcribes these fields into the Excel file verbatim, it does not translate — the language must already be correct at Step 5 when these strings are authored, not fixed later at export time.
- `status` — leave `""` (Not Run); do not pre-fill Pass/Fail unless a tester has actually reported that result.
- `test_type` — comma-separated test-type tags (`FN,BL,NEG,EC,PM,DI,ST,CN,IT,SEC,UI,A11Y,COMPAT`, see `techniques-and-coverage.md`). Optional, but required for the Summary sheet's "By Test Type" block to be populated — if omitted, the script fills that block with a placeholder instead of counts.
- `assumptions` — optional; the script only creates the Assumptions sheet when this array is non-empty.
- `metadata` — optional; the company form header block (rows 1-8, see 7.10.3b) is written on every export regardless of this key. Add `metadata` only to fill in its values (spec link, redmine link, QC name...) — omit it and the block still appears, just with blank value cells.

**Step B — run the script:**

```bash
python .claude/skills/test-case-generator/scripts/generate_testcase_excel.py <input.json> [output.xlsx]
```

`output.xlsx` is optional; when omitted the script writes next to the input file with the same base name.

If the script errors or produces wrong output for a given case, fix `scripts/generate_testcase_excel.py` itself rather than working around it with a new one-off script — keep a single source of truth for the export logic.

#### 7.10.8 Export Checklist (Verification)

**Trước khi submit Excel file, verify:**
```
□ File format: .xlsx (NOT .xls, NOT .csv)
□ UTF-8 encoding (Vietnamese characters hiển thị đúng)
□ Sheet 1 "Test Cases" exists với all test cases
□ Sheet 2 "Summary" exists với statistics
□ Headers formatted (Blue background, White text, Bold)
□ Priority color-coded correctly (P1=Red, P2=Orange, P3=Green)
□ All 10 columns present (A-J), bao gồm cột Status (J)
□ Status column (J) có Conditional Formatting cho Pass/Fail/Blocked/Not Run
□ Column widths set appropriately (không để default)
□ Text wrap enabled cho columns E, F, G, I, J
□ Frozen panes at E4 (headers + ID columns frozen)
□ Auto-filter enabled on header row (A3:J{n})
□ Merged title cells đúng: A1:J1 và A2:J2
□ Row heights auto-adjusted theo số dòng nội dung thực tế (min 35px, không quá cao >500px), không bị cắt chữ ở các step nhiều dòng
□ No empty rows between test cases
□ No formatting errors (merged cells không đúng chỗ)
□ File mở được trong Excel (test trước khi submit)
□ Vietnamese text hiển thị đúng (không bị lỗi font)
□ Status column để trống (Not Run) — tester sẽ điền sau khi execute
□ Khối metadata "KỊCH BẢN KIỂM THỬ" ở rows 1-8 (xem 7.10.3b) đã có mặt — BẮT BUỘC trên mọi file, không cần đợi yêu cầu; Title/Header/Data đã tự dịch xuống đúng row (row 9/10/11+, không tự tay chèn row)
□ Test Objective/Test Steps/Expected Result/Assumption description viết bằng TIẾNG VIỆT (xem `writing-format.md` 7.0) — không còn câu tiếng Anh nào lẫn vào, trừ [Technique Tag], tên field/API/DB, mã ID, Priority, Status
```

#### 7.10.9 Alternative: draft in Markdown first

For a quick human review pass before the final Excel export, you may draft test cases as Markdown tables first (format in `writing-format.md`, Section 7.1-7.9), let the user review/edit them, then convert:

- Preferred: transcribe the reviewed rows into the JSON schema above and run `scripts/generate_testcase_excel.py` (gives full Priority/Status color-coding + Summary sheet).
- Generic fallback (loses Priority/Status color-coding and the Summary sheet, use only if the user explicitly wants a quick plain conversion): the project's `markdown-to-excel` skill — `python .claude/skills/markdown-to-excel/scripts/md_to_xlsx.py <input.md> [output.xlsx]`.

#### 7.10.10 Troubleshooting Excel Export

**Common Issues:**

| Issue | Cause | Solution |
|-------|-------|----------|
| Vietnamese corrupted (???) | Wrong encoding | Use UTF-8, save with encoding='utf-8' |
| Priority không màu | Forgot apply PatternFill | Apply fill + font to column D cells |
| Status không đổi màu khi nhập | Conditional Formatting không được add | Add FormulaRule cho range J4:J{n} với công thức `$J4="Pass"` v.v. |
| Status color không cập nhật tự động | Dùng static fill thay vì ConditionalFormatting | Dùng `ws.conditional_formatting.add()` + `FormulaRule` |
| Text overflow (không wrap) | Text wrap not enabled | ws.cell.alignment = Alignment(wrap_text=True) |
| Frozen panes không work | Wrong freeze position | Use ws.freeze_panes = 'E4' (not 'A4') |
| Auto-filter chỉ cover 9 cột | Dùng `A3:I{n}` thay vì `A3:J{n}` | Update ref: `ws.auto_filter.ref = f'A3:J{last_row}'` |
| Merged title sai (chỉ đến cột I) | Dùng A1:I1 thay vì A1:J1 | `ws.merge_cells('A1:J1')` và `ws.merge_cells('A2:J2')` |
| File cannot open | Corrupted workbook | Check all cells valid, no None values |
| Too slow (large file) | Inefficient cell access | Use ws.append() instead of cell-by-cell |

---

