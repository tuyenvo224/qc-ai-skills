# Checklist Phân Tích & Ngân Hàng Câu Hỏi

Đọc file này khi thực hiện Step 2-4 trong workflow của `SKILL.md` (phân tích User Flow / Logic Flow / Database & Data Flow). Chứa checklist chi tiết, diagram template, các bảng tài liệu hóa (Conditional Logic, State Transition Matrix, Data Impact Matrix, Transaction Boundary), và ngân hàng câu hỏi để hỏi PO/BA cho từng chiều phân tích.

---

## Analysis Checklist

### General Requirements Analysis

- [ ] **Completeness (Đầy đủ):** Đã cung cấp đủ mọi chi tiết cần thiết chưa?
- [ ] **Clarity (Rõ ràng):** Ngôn ngữ có mơ hồ không?
- [ ] **Consistency (Nhất quán):** Có mâu thuẫn với requirement khác không?
- [ ] **Testability (Test được):** Acceptance criteria có verify được không?
- [ ] **Boundary conditions (Điều kiện biên):** Giới hạn và edge case đã được định nghĩa chưa?
- [ ] **Error handling (Xử lý lỗi):** Khi có sự cố thì hệ thống làm gì?
- [ ] **Data conditions (Điều kiện dữ liệu):** Trạng thái dữ liệu nào là valid/invalid?
- [ ] **User roles (Vai trò người dùng):** Ai được phép thực hiện hành động này?
- [ ] **Dependencies (Phụ thuộc):** Có điều kiện tiên quyết nào không?
- [ ] **Performance (Hiệu năng):** Có yêu cầu về thời gian phản hồi hoặc tải hệ thống không?

### User Flow Analysis

- [ ] **Entry points (Điểm vào):** Đã xác định hết mọi cách người dùng truy cập feature chưa?
- [ ] **User journey (Hành trình người dùng):** Đã map đầy đủ đường đi từ đầu đến cuối chưa?
- [ ] **Decision points (Điểm quyết định):** Đã tài liệu hóa hết mọi lựa chọn của người dùng và kết quả tương ứng chưa?
- [ ] **Alternative paths (Đường đi thay thế):** Đã xác định các cách khác để đạt cùng mục tiêu chưa?
- [ ] **Exit points (Điểm thoát):** Đã bao phủ hết các cách người dùng rời đi (thành công, hủy, lỗi) chưa?
- [ ] **Navigation (Điều hướng):** Đã hiểu hành vi của nút back/forward chưa?
- [ ] **Multi-session (Đa phiên):** Đã xem xét tình huống nhiều tab/nhiều thiết bị chưa?
- [ ] **Interruptions (Gián đoạn):** Đã xử lý tình huống logout, timeout, mất mạng chưa?
- [ ] **Flow dependencies (Phụ thuộc luồng):** Đã xác định các điều kiện tiên quyết từ feature khác chưa?

### Logic Flow Analysis

- [ ] **Process sequence (Thứ tự xử lý):** Đã tài liệu hóa các bước xử lý theo đúng thứ tự chưa?
- [ ] **Conditional logic (Logic điều kiện):** Đã xác định hết các nhánh if/else chưa?
- [ ] **Validation rules (Quy tắc validate):** Đã tài liệu hóa hết validation và thứ tự thực hiện chưa?
- [ ] **Calculations (Tính toán):** Công thức và phép tính đã được nêu rõ chưa?
- [ ] **State transitions (Chuyển trạng thái):** Đã map hết các thay đổi trạng thái và trigger chưa?
- [ ] **API sequence (Thứ tự gọi API):** Đã tài liệu hóa các API được gọi và phụ thuộc giữa chúng chưa?
- [ ] **Sync vs Async:** Đã xác định thao tác nào đồng bộ, thao tác nào bất đồng bộ chưa?
- [ ] **Retry logic (Logic thử lại):** Đã định nghĩa cách xử lý lỗi và đường phục hồi chưa?
- [ ] **Third-party integration (Tích hợp bên thứ ba):** Đã tài liệu hóa tương tác với hệ thống ngoài chưa?

### Database & Data Flow Analysis

- [ ] **Tables affected (Bảng bị ảnh hưởng):** Đã xác định hết table/collection liên quan chưa?
- [ ] **CRUD operations:** Đã tài liệu hóa hành động Create, Read, Update, Delete chưa?
- [ ] **Data relationships (Quan hệ dữ liệu):** Đã map foreign key và tham chiếu chưa?
- [ ] **Constraints (Ràng buộc):** Đã xác định constraint unique, not-null, check chưa?
- [ ] **Transformations (Biến đổi dữ liệu):** Đã tài liệu hóa việc biến đổi từ input sang định dạng lưu trữ chưa?
- [ ] **Transaction boundaries (Ranh giới transaction):** Các thao tác atomic đã được nhóm lại chưa?
- [ ] **Cascade effects (Hiệu ứng lan truyền):** Đã hiểu rõ việc update/delete lan truyền ra sao chưa?
- [ ] **Soft vs Hard delete:** Hành vi xóa đã được làm rõ chưa (xóa mềm hay xóa cứng)?
- [ ] **Audit trail (Nhật ký kiểm toán):** Đã xác định các thay đổi cần log lại chưa?
- [ ] **Caching:** Đã tài liệu hóa chiến lược cache và quy tắc invalidate chưa?
- [ ] **Concurrency (Đồng thời):** Đã định nghĩa cách xử lý truy cập đồng thời chưa?
- [ ] **Data retention (Lưu trữ dữ liệu):** Đã xác định thời gian giữ dữ liệu và chính sách dọn dẹp chưa?

---

## User Flow Analysis

Hiểu đầy đủ hành trình người dùng là yếu tố then chốt để test bao phủ toàn diện.

### User Flow Checklist

| # | Điểm phân tích | Câu hỏi cần trả lời |
|---|----------------|---------------------|
| 1 | **Entry Points** | Người dùng tiếp cận feature này bằng cách nào? (menu, link, deeplink, redirect) |
| 2 | **User Journey** | Đường đi đầy đủ từ đầu đến cuối là gì? |
| 3 | **Decision Points** | Ở đâu người dùng đưa ra lựa chọn làm thay đổi luồng? |
| 4 | **Alternative Paths** | Người dùng có thể đi đường nào khác để đạt cùng mục tiêu? |
| 5 | **Exit Points** | Người dùng có thể rời đi bằng cách nào? (thành công, hủy, lỗi, timeout, bỏ dở) |
| 6 | **Navigation** | Nút back/forward của trình duyệt hoạt động ra sao? |
| 7 | **Multi-Session** | Điều gì xảy ra khi mở nhiều tab hoặc nhiều thiết bị? |
| 8 | **Interruptions** | Điều gì xảy ra khi logout, hết phiên (session timeout), hoặc mất mạng? |
| 9 | **Dependencies** | Luồng này có phụ thuộc vào việc hoàn thành luồng khác trước không? |
| 10 | **Post-Flow** | Sau khi hoàn thành luồng này, người dùng đi đến đâu? |

### User Flow Diagram Template

```
┌─────────────────┐
│   Entry Point   │ ◄── Cách người dùng đến
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Step 1        │
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │Decision │ ◄── Lựa chọn của người dùng
    └────┬────┘
    ┌────┴────┐
    │    │    │
    ▼    ▼    ▼
  [A]  [B]  [C]  ◄── Các đường đi thay thế
    │    │    │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│   Exit Point    │ ◄── Thành công / Hủy / Lỗi
└─────────────────┘
```

### Câu hỏi User Flow để hỏi PO/BA

**Entry & Navigation (Điểm vào & Điều hướng):**
- Có bao nhiêu cách để người dùng truy cập feature này?
- Người dùng có thể bookmark hoặc chia sẻ link trực tiếp đến trang này không?
- Điều gì xảy ra nếu người dùng vào trang này mà không có context phù hợp (vd truy cập trực tiếp bằng URL)?

**Flow Behavior (Hành vi luồng):**
- Người dùng có thể lưu tiến trình và tiếp tục sau không?
- Điều gì xảy ra nếu người dùng refresh trang giữa chừng luồng?
- Luồng này có giới hạn thời gian hoàn thành không?

**Edge Cases:**
- Điều gì xảy ra nếu người dùng mở luồng này ở nhiều tab cùng lúc?
- Điều gì xảy ra nếu session hết hạn giữa luồng?
- Người dùng có thể quay lại và sửa các bước trước đó không?

---

## Logic Flow Analysis

Hiểu rõ business logic đảm bảo test verify đúng behavior.

### Logic Flow Checklist

| # | Điểm phân tích | Câu hỏi cần trả lời |
|---|----------------|---------------------|
| 1 | **Process Sequence** | Thứ tự các bước xử lý là gì? |
| 2 | **Conditional Logic** | Những điều kiện if/else nào làm thay đổi behavior? |
| 3 | **Validation Rules** | Những validation nào chạy, theo thứ tự nào? |
| 4 | **Calculations** | Công thức hoặc phép tính nào được thực hiện? |
| 5 | **State Transitions** | Những thay đổi trạng thái nào xảy ra, khi nào? |
| 6 | **Triggers** | Sự kiện nào gây ra hành động? |
| 7 | **API Sequence** | Những API nào được gọi, theo thứ tự nào? |
| 8 | **Sync vs Async** | Thao tác nào đồng bộ, thao tác nào bất đồng bộ? |
| 9 | **Retry Logic** | Điều gì xảy ra khi thất bại? Tự động retry? Retry thủ công? |
| 10 | **Third-Party** | Hệ thống bên ngoài nào liên quan, tương tác ra sao? |

### Logic Flow Diagram Template

```
┌─────────────────────────────────────────────────────────┐
│                    LOGIC FLOW                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [Input] ──► [Validate] ──► [Process] ──► [Output]      │
│                  │              │                       │
│                  ▼              ▼                       │
│             [Error?]      [Side Effects]                │
│                  │              │                       │
│                  ▼              ▼                       │
│           [Error Handler]  [Notifications]              │
│                           [Audit Logs]                  │
│                           [Cache Update]                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Conditional Logic Documentation

| Condition (Điều kiện) | Khi True | Khi False | Edge Cases |
|-----------|-----------|------------|------------|
| [Condition 1] | [Action A] | [Action B] | [Nếu null/undefined thì sao?] |
| [Condition 2] | [Action C] | [Action D] | [Giá trị biên?] |

### State Transition Matrix

| Trạng thái hiện tại | Event/Action | Trạng thái mới | Side Effects |
|---------------|--------------|-----------|--------------|
| Draft | Submit | Pending Review | Gửi notification |
| Pending Review | Approve | Active | Cập nhật timestamp |
| Pending Review | Reject | Draft | Gửi email từ chối |
| Active | Deactivate | Inactive | Clear cache |

### Câu hỏi Logic Flow để hỏi PO/BA

**Processing Logic (Logic xử lý):**
- Thứ tự chính xác của các thao tác là gì?
- Có thao tác nào chạy song song không?
- Quy tắc ưu tiên nào áp dụng khi có xung đột?

**Validation:**
- Những validation nào được thực hiện ở mỗi bước?
- Validation được thực hiện theo thứ tự nào?
- Validation dừng lại ở lỗi đầu tiên hay thu thập hết tất cả lỗi?

**State Management (Quản lý trạng thái):**
- Entity này có những trạng thái nào?
- Điều gì trigger mỗi lần chuyển trạng thái?
- Có trạng thái nào không thể đảo ngược không?

**Error Handling (Xử lý lỗi):**
- Điều gì xảy ra khi mỗi bước thất bại?
- Lỗi có được tự động retry không?
- Lỗi một phần (partial failure) được xử lý ra sao?

---

## Database & Data Flow Analysis

Hiểu rõ tác động lên dữ liệu đảm bảo test được tính toàn vẹn dữ liệu (data integrity).

### Database Analysis Checklist

| # | Điểm phân tích | Câu hỏi cần trả lời |
|---|----------------|---------------------|
| 1 | **Tables Affected** | Table/collection nào bị đọc hoặc sửa? |
| 2 | **CRUD Operations** | Hành động Create, Read, Update, Delete nào xảy ra? |
| 3 | **Data Relationships** | Foreign key, tham chiếu, hoặc join nào tồn tại? |
| 4 | **Constraints** | Constraint unique, not-null, hoặc check nào áp dụng? |
| 5 | **Transformations** | Dữ liệu input được biến đổi ra sao trước khi lưu? |
| 6 | **Transactions** | Thao tác nào phải atomic (tất cả hoặc không gì cả)? |
| 7 | **Cascade Effects** | Dữ liệu liên quan bị ảnh hưởng gì khi update/delete? |
| 8 | **Soft vs Hard Delete** | Dữ liệu bị xóa thật hay chỉ đánh dấu (flag)? |
| 9 | **Audit Trail** | Thay đổi dữ liệu nào cần được log lại? |
| 10 | **Caching** | Dữ liệu nào được cache và khi nào cache bị invalidate? |
| 11 | **Concurrency** | Cập nhật đồng thời được xử lý ra sao? |
| 12 | **Data Retention** | Dữ liệu được giữ bao lâu? Có chính sách dọn dẹp nào không? |

### Data Flow Diagram Template

```
┌──────────────────────────────────────────────────────────────┐
│                      DATA FLOW                                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  [User Input]                                                │
│       │                                                      │
│       ▼                                                      │
│  [Validation Layer]                                          │
│       │                                                      │
│       ▼                                                      │
│  [Transform/Sanitize]                                        │
│       │                                                      │
│       ├──────────────────┬───────────────────┐               │
│       ▼                  ▼                   ▼               │
│  [Primary Table]    [Related Table]    [Audit Log]           │
│       │                  │                   │               │
│       ▼                  ▼                   ▼               │
│  [Cache Update]    [Index Update]     [Event Publish]        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Data Impact Matrix

| Operation (Thao tác) | Table bị ảnh hưởng | Field thay đổi | Cascade Effects |
|-----------|-----------------|----------------|-----------------|
| Create Order | orders, order_items, inventory | status, quantity, stock | Cập nhật số lượng tồn kho |
| Cancel Order | orders, order_items, payments | status, refund_status | Hoàn lại tồn kho, khởi tạo refund |
| Delete User | users, orders, preferences | tất cả | Ẩn danh hóa (anonymize) orders, xóa preferences |

### Transaction Boundary Documentation

| Tên Transaction | Các thao tác gồm | Rollback Trigger | Recovery Action |
|------------------|---------------------|------------------|-----------------|
| Place Order | Tạo order, Trừ tồn kho, Charge thanh toán | Thanh toán thất bại | Hoàn tồn kho, Xóa order |
| Transfer Funds | Trừ tiền nguồn, Cộng tiền đích | Không đủ số dư | Hoàn lại thao tác trừ tiền |

### Câu hỏi Database để hỏi PO/BA

**Data Creation (Tạo dữ liệu):**
- Feature này tạo ra những record mới nào?
- Giá trị mặc định nào được áp dụng?
- Constraint unique nào cần được enforce?

**Data Relationships (Quan hệ dữ liệu):**
- Dữ liệu liên quan nào phải tồn tại trước khi tạo record này?
- Record con (child record) bị ảnh hưởng gì khi record cha bị sửa/xóa?
- Có tham chiếu vòng (circular reference) nào cần lưu ý không?

**Data Integrity (Toàn vẹn dữ liệu):**
- Thao tác nào phải thành công hoặc thất bại cùng nhau (transaction)?
- Thay đổi đồng thời (concurrent modification) được xử lý ra sao?
- Validation nào diễn ra ở tầng database?

**Data Lifecycle (Vòng đời dữ liệu):**
- Dữ liệu bị xóa mềm (soft-delete) hay xóa cứng (hard-delete)?
- Thông tin audit nào được ghi lại?
- Dữ liệu được giữ bao lâu trước khi archive/xóa?

**Caching:**
- Dữ liệu nào được cache?
- Khi nào cache cần được invalidate?
- Điều gì xảy ra nếu dữ liệu cache bị cũ (stale)?

---
