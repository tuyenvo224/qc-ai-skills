# Agent prompts

Fill in the placeholders before spawning: `{OUT}`, `{BA}` (BA feature .md), `{TA_DIR}`, `{QC_DIR}`, `{CODE}` (dirs or "none"), `{R_FROM}`, `{R_TO}`, `{N}`.
Order: P1 → P1b → then P2 ×n, P3, P4 and P5 ×n in parallel.
Add this common header to every prompt:

> Read-only. No network. Do not edit anything outside {OUT}. Never open .env*, variables/*.env, .gitlab or other secret files. Use python with encoding='utf-8' (set PYTHONIOENCODING=utf-8). CSV output: UTF-8, `;`-separated, exact headers as given. The FRD is the source of truth. Judge by meaning (values, thresholds, conditions, per-type branches, actors, order), never by keyword match.

---

## P1 — Extract FRD requirements (foreground)

Input: {OUT}/frd.html (authoritative, keep table structure) and {OUT}/frd.txt.
Write {OUT}/frd-reqs.md with these parts:

0. `## Danh mục nhóm`. Write this **before** the list, once you have read the whole FRD. It has two tables:
   - `| Chủ đề | Nhóm chức năng | Mô tả |` with 10–20 topics covering the whole FRD, listed in FRD order.
     - `Chủ đề` is a lowercase ascii snake_case key, such as `consent`, `field_validation`, `mst`, `existing_client`, `otp`, `integration_failure`, `logging`, `scope`.
     - `Nhóm chức năng` is the name a QC reads in the Excel and the report: short Vietnamese that a non-developer understands, such as "Xác thực OTP", "Mã số thuế (MST)", "Tổ chức đã là khách hàng (Existing Client)". Keep an English domain term in brackets when the FRD uses it.
   - `| Nhóm | Chủ đề | Mô tả ngắn |` with every grouping key used in the list below.
   Key format is `<chủ đề>.<khía cạnh>[.<chi tiết>]`: lowercase ascii, snake_case segments, joined by dots, using readable English words and no cryptic abbreviations.
   The same testable meaning repeated in different FRD sections (goals, use cases, flow, FR, VR, AC…) **must** share one key. Different testable points get different keys, even inside one topic.
1. `## Danh sách yêu cầu`. A markdown table with the header exactly
   `| ID | FRD mục | Loại | Trích nguyên văn | Ghi chú | Nhóm |`
   - `Nhóm` is a key from the catalog above, and every row has one.
   - One row per atomic testable statement: field rule, validation, message, state transition, per-type branch, notification, integration effect, permission, limit, UI behaviour, NFR.
   - Split compound sentences. Do not merge statements, paraphrase them or invent new ones.
   - The same statement repeated in different sections gets separate rows.
   - `ID` = R-001… in document order.
   - `Loại` ∈ Field/Validation/Message/Flow/State/Integration/Notification/UI/NFR/Rule.
   - `Trích nguyên văn` = an exact quote of at most 300 characters. Join non-adjacent pieces with ` … ` and table cells with ` \| `.
   - Put conditions and "differs per type" details in `Ghi chú`.
2. `## Câu hỏi mở / TBD trong FRD`. A table with the header `| ID | Loại | Nội dung | Trích | Ảnh hưởng test |`.
   - ID prefixes: `OP-` for questions the FRD itself marks open or TBD, `C-` for internal contradictions (quote both sides), and `G-` for missing definitions such as error texts or formats that no rule defines.
3. `## Lịch sử phiên bản FRD`. A table with the header `| Version | Ngày | Thay đổi |`.
4. `## Thống kê`. Row counts per FRD section, including sections with 0 rows and the reason, counts per Loại, and the total.

Reply briefly: the total, the counts per section, the number of OP/C/G items and any parsing doubts.

---

## P1b — Coverage audit (foreground, a **new** agent, never the P1 agent)

Inputs: {OUT}/frd.html (authoritative), {OUT}/frd-reqs.md (produced by another agent) and {OUT}/coverage-sections.json (leaf sections with 0 rows, and requirement density).

Your job is to find what the extraction **missed**. Do not re-grade what it already has. Read the FRD section by section, including tables, bullet lists, notes, diagrams and "Lưu ý" boxes. For each testable statement, check whether some R row carries the same meaning (a different wording is fine). Then write {OUT}/coverage-gaps.md with these sections:

1. `## Kết luận`. One line: `Trạng thái: PASS` or `Trạng thái: GAPS`, plus counts.
2. `## Ý bị sót`. A table with the header `| # | FRD mục | Trích nguyên văn | Loại | Nhóm | Xử lý |`.
   - One row per missed testable statement, quoted exactly (at most 300 characters).
   - `Nhóm` is an existing key from frd-reqs.md §Danh mục nhóm. Propose a new key only when no existing key fits, and mark it `(mới)`.
   - Leave `Xử lý` empty; the main thread fills it in.
3. `## Dòng gộp nhiều ý`. A table with the header `| R | Vấn đề | Xử lý |`, for rows that combine 2 or more testable statements that should be split.
4. `## Mục FRD 0 dòng`. A table with the header `| Mục | Hợp lý? | Lý do |`, covering every entry in coverage-sections.json `empty`. `Hợp lý?` = `Có` means background only, nothing testable. `Không` means its content must be added to "Ý bị sót".

Be exhaustive but precise. A missed item must be testable and must really be absent. Don't list a statement another row already covers, and don't list pure repetition. Reply with the counts only.

---

## P2 — FRD → BA, range {R_FROM}…{R_TO} (background, one agent per range)

Inputs: {OUT}/frd-reqs.md, {OUT}/frd.html and the BA doc {BA}.

**Task A.** For each requirement from R-{R_FROM} to R-{R_TO}, write {OUT}/map-ba-{N}.csv with the header
`R;Nhóm;BA IDs;BA dòng;Trạng thái;Chênh lệch`
- `Nhóm` is copied as-is from the `Nhóm` column of frd-reqs.md. Never invent or rename a key.
- `BA IDs` are the BA ids that express the requirement (BR/VR/AC/UC/AF or the doc's own scheme).
- `BA dòng` is the line numbers of those ids in the BA doc.
- `Trạng thái` is exactly one of:
  - `Đủ`
  - `Lệch`: BA says something different. Quote both sides briefly in Chênh lệch.
  - `Thiếu`: the BA doc has nothing for it.
  - `Một phần`: say which part is missing.
  - `N/A`: not testable.

**Task B, only for the agent with the last range.** Go through the whole BA doc and list every BA rule, validation, AC or flow that has no basis in the FRD. Write {OUT}/ba-extra.csv with the header
`BA ID;BA dòng;Nội dung;Loại;FRD liên quan`
- `Loại` ∈ `Thêm mới` / `Tự chốt câu hỏi mở FRD` / `Trái FRD`. For `Tự chốt câu hỏi mở FRD`, cite the OP/C/G id.
- Also report which FRD version the BA header says it is based on, and compare that with the version in {OUT}/frd-meta.json.

Reply with: the counts per status, every Lệch and Thiếu row on one line each, and the top items in ba-extra.

---

## P3 — BA → QC (background)

Inputs: the BA doc {BA}, the TA docs in {TA_DIR}, and the QC docs in {QC_DIR} (test-cases, security-cases, test-flow, e2e-tests, or whatever files exist).

Write these files:

1. {OUT}/qc-cases.csv, one row per case definition (TC/SEC/E2E/TF or the suite's own scheme). Header:
   `ID;File;Dòng;Tiêu đề;Traces;Layer;Trạng thái;Phụ thuộc;Có input+expected;Đại diện`
   - `Traces` is the BA ids the case cites.
   - `Trạng thái` ∈ normal/BLOCKED/optional/withdrawn.
   - `Phụ thuộc` is the P-*/A-*/OQ-* items the case depends on.
   - `Đại diện` = Y marks a minimal set of cases that still covers every BA id at least once. Build it with a greedy set cover that prefers E2E/UI-visible cases with concrete data; exclude withdrawn and BLOCKED cases. Put TF flows in the set only when no other case covers an id.
2. {OUT}/ba-to-qc.csv with the header `BA ID;QC cases;Count`. Include every BA id, even those with 0 cases.
3. {OUT}/qc-extra.csv with the header `ID;Lý do`. List cases whose traces point to nothing in the BA doc, or that rest only on TA ids or assumptions.
4. {OUT}/qc-prereq.md, short. Cover prerequisite tables and whether they are stale, the A-* assumptions and which cases they affect, the BLOCKED cases and why, and the setup, test data and config pins.

Reply with: the counts, the BA ids with 0 cases, the size of the Đại diện set, and the top qc-extra items.

---

## P5 — FRD → TA, range {R_FROM}…{R_TO} (background, one agent per range, same ranges as P2)

Inputs: {OUT}/frd-reqs.md and the TA docs in {TA_DIR} (normally `analysis.md`, `design.md` and `ui-contract.md`; use whatever files exist). The TA docs carry ids such as API-*, ENT-*, EVT-*, SEQ-*, STATE-*, CF-*, TD-*, RSK-*, A-*, EL-* and message codes.

**Task A.** For each requirement from R-{R_FROM} to R-{R_TO}, write {OUT}/ta-map-{N}.csv with the header
`R;TA IDs;TA dòng;Trạng thái;Chênh lệch`
- `TA IDs` are the TA ids that design the requirement.
- `TA dòng` is `file:line` for each id.
- `Trạng thái` is exactly one of:
  - `Đủ`
  - `Lệch`: TA designs it differently. Covers values, thresholds, error or message codes, state transitions, order of steps, integration target and rollback. Quote both sides briefly.
  - `Thiếu`: no TA design at all.
  - `Một phần`: say which part is missing.
  - `N/A`: nothing technical to design, for example pure wording or out-of-scope labels.
- Be concrete. Where TA fixes a number the FRD also fixes (TTL, limits, lengths), compare the numbers. Where FRD says TBD and TA fixes a value, use `Lệch` and write `TA tự chốt: <value>` in Chênh lệch.

**Task B, only for the agent with the last range.**
1. {OUT}/ta-notes.csv with the header `ID;Loại;Nội dung;R liên quan;Kết luận;Ảnh hưởng test`.
   - Include every TA `CF-*`, `A-*`, `RSK-*` and `TD-*` item that touches an FRD requirement.
   - `Loại` is the prefix.
   - `Kết luận` ∈ `Phù hợp FRD` / `Trái FRD` / `Tự chốt câu hỏi mở FRD` (cite the OP/T/C/G id) / `Chỉ kỹ thuật`.
   - `Ảnh hưởng test` is one line on what QC must know, for example "code đang trái, case sẽ đỏ tới khi sửa" or "ngưỡng do TA tự đặt".
2. {OUT}/ui-vs-frd.csv with the header `R;Màn hình / phần tử;Trạng thái;Ghi chú`.
   - Include every FRD requirement of Loại `UI` or `Message`, and every requirement that shows a popup, screen, message or confirmation to the user.
   - Check that `ui-contract.md` has the screen (`SC-*`), the elements (`EL-*` / `data-testid`) and a message region or message code for it.
   - `Trạng thái` ∈ `Đủ` / `Thiếu màn hình` / `Thiếu phần tử` / `Thiếu vùng message` / `Lệch`.
3. One line on which FRD version the TA docs say they are based on.

Reply with: the counts per status, every Lệch and Thiếu row on one line each, the `Trái FRD` notes, and the UI gaps.

---

## P4 — Redmine + code (background)

Inputs: {OUT}/frd-reqs.md, the {OUT}/rm_*.md files (Textile, with journals), and the code in {CODE}.

Write these files:

1. {OUT}/redmine-vs-frd.csv with the header `Chủ đề;Redmine nói;FRD nói;Kết luận`.
   - `Redmine nói` is the issue number plus a quote of at most 150 characters. `FRD nói` is the R id plus a quote.
   - `Kết luận` ∈ `Khớp`/`Lệch`/`Redmine thiếu`/`Redmine thêm`.
   - Focus on behaviour QC will test: fields, validations, limits, duplicate checks, integration side effects, messages, error branches and states.
2. {OUT}/redmine-decisions.md. A journal timeline listing who changed scope and when, plus which FRD version the issues follow.
3. {OUT}/impl-status.csv, only if code is available. Header:
   `Nhóm;R ids;BE evidence;FE evidence;Trạng thái;Ghi chú`
   - Group by the FRD's own grouping: `Nhóm` is a `Mã yêu cầu` or a `Nhóm chức năng` from frd-reqs.md §Danh mục nhóm. Split a group when code status differs inside it. Every R id must be covered. R ids may be written as ranges, like `R-195..R-203`.
   - The report computes status **per requirement** from this file, so be precise about which R ids each row covers.
   - `Trạng thái` ∈ `Có`/`Một phần`/`Chưa có`/`Khác FRD`.
   - Evidence is `file:line`. Check config defaults, DTO validators, message codes and integration adapters.
   - Note anything that affects how tests run: mocked senders, rate limits, feature flags.

Reply with: the top Lệch items, the key journal decisions, the implementation counts, and the most test-relevant `Khác FRD` items.
