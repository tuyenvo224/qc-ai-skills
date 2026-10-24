# Grouping & Ordering Rules

Read this when structuring the output (Step 4 of `SKILL.md`'s workflow) — how to group test cases by feature, the mandatory 9-category order within each group, group ordering, and Test ID naming convention.

---

## 8. Grouping & Ordering Rules

### 8.1 Quy tắc nhóm

- Nhóm theo **CHỨC NĂNG** (KHÔNG nhóm theo test type)
- Mỗi nhóm = 1 feature / 1 screen / 1 API endpoint / 1 user flow
- Đặt tên nhóm rõ ràng: `### Group: [Tên chức năng]`

**Ví dụ nhóm đúng:**
```
### Group: Login Screen
### Group: POST /api/orders (Create Order)
### Group: User Profile Management
### Group: Order Approval Workflow
```

**Ví dụ nhóm SAI:**
```
### Group: Positive Tests        ← KHÔNG nhóm theo test type
### Group: Security Tests         ← KHÔNG nhóm theo test type
### Group: Boundary Tests         ← KHÔNG nhóm theo test type
```

### 8.2 Thứ tự viết TC trong mỗi nhóm (BẮT BUỘC)

```
① UI Basic          → Layout, hiển thị, elements cơ bản
② Happy path        → Chức năng hoạt động đúng với data valid
③ Business logic    → Logic nghiệp vụ, tính toán, rules, conditions
④ Negative          → Input sai, thiếu field, format sai, validation
⑤ Boundary          → Giá trị biên: min, max, min±1, max±1
⑥ Permission        → Phân quyền, access control, cross-user
⑦ DB verification   → Data lưu đúng, constraints, relationships
⑧ Security          → Injection, auth bypass, webhook tampering
⑨ Edge case/Ad-hoc  → Tình huống đặc biệt từ End-User Mindset (Phần 6)
```

**Lưu ý:**
- KHÔNG phải mọi nhóm đều có đủ 9 loại (ví dụ API-only feature không có UI Basic), tùy thuộc vào nội dung task mà vận đụng cho phù hợp
- Bỏ qua loại không applicable, nhưng KHÔNG thay đổi thứ tự
- Trong mỗi loại, viết P1 TC trước, P4 sau
- Loại bỏ testcase trùng

### 8.3 Thứ tự các nhóm

- Sắp xếp theo **flow nghiệp vụ tự nhiên**:
  - Authentication → User Management → Core Feature 1 → Core Feature 2 → Reports → Admin
- P1 features trước, P4 sau
- Feature dependencies: feature prerequisite trước

**Ví dụ:**
```
## Test Cases

### Group: Authentication (P1)
### Group: Warehouse Management (P1)
### Group: Create Order (P1)
### Group: Order Tracking (P2)
### Group: Order Reports (P3)
### Group: Settings (P4)
```

### 8.4 Đánh số Test Case

**Format:** `{AREA}-{NUMBER}` hoặc `{AREA}-{SUBAREA}-{NUMBER}`

**Quy tắc:**
- Sử dụng descriptive area codes
- Sequential numbering trong mỗi area: 001, 002, 003...
- Include subarea khi nhóm lớn

**Area codes phổ biến:**

| Area Code | Mô tả |
|-----------|--------|
| AUTH | Authentication & Authorization |
| USER | User management |
| WH-CREATE | Warehouse creation |
| WH-UPDATE | Warehouse update |
| ORD-CREATE | Order creation |
| ORD-STATE | Order state transition |
| ORD-TRACK | Order tracking |
| WH-IN | Inbound webhooks |
| WH-OUT | Outbound webhooks |
| SEARCH | Search & filter |
| RPT | Reports |
| PERM | Permission specific |
| SEC | Security specific |

**Ví dụ:**
```
AUTH-001, AUTH-002
WH-CREATE-001, WH-CREATE-027
ORD-CREATE-001, ORD-STATE-005
SEC-001, PERM-012
```

---

