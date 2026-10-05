# Khung Output

Đọc file này ở Step 9 trong workflow của `SKILL.md` (viết bản phân tích cuối cùng) — copy khung này và điền vào, không tự bịa ra cấu trúc khác. Cả 7 mục đều bắt buộc phải có, kể cả khi một mục ngắn gọn (vd "Không phát hiện điểm chưa rõ").

---

```markdown
# Phân Tích Requirement: [Tên Feature]

**Ngày:** YYYY-MM-DD
**Người phân tích:** Requirement Analyzer Skill
**Trạng thái:** Pending Clarification / Clarified / Ready for Testing (chọn theo Status Decision Rule trong `SKILL.md`)

---

## 1. Requirement Summary

[Diễn đạt lại requirement rõ ràng, testable]

### Requirement Breakdown

| Requirement ID | Mô tả | Perspective | Priority |
|---|---|---|---|
| REQ-001 | [Mô tả ngắn gọn 1 ý/chức năng con] | Admin/CMS / Frontend / Transaction | P1/P2/P3/P4 |

---

## 2. User Flow Analysis

*Perspective: [Admin/CMS / Frontend / Transaction — lặp lại mục 2-4 cho mỗi Perspective có nội dung ở Step 1]*

### Entry Points (Điểm vào)
- [Cách người dùng truy cập feature này]

### User Journey (Hành trình người dùng)
```
[Bắt đầu] → [Bước 1] → [Điểm quyết định] → [Bước 2] → [Kết thúc]
                          ↓
                    [Đường đi thay thế]
```

### Exit Points (Điểm thoát)
| Loại thoát | Điều kiện | Đích đến |
|-----------|-----------|-------------|
| Thành công | [Khi nào] | [Người dùng đi đâu] |
| Hủy | [Khi nào] | [Người dùng đi đâu] |
| Lỗi | [Khi nào] | [Xử lý lỗi ra sao] |

### Edge Cases
- Hành vi multi-tab: [Mô tả]
- Session timeout: [Mô tả]
- Gián đoạn mạng: [Mô tả]

---

## 3. Logic Flow Analysis

### Process Sequence (Thứ tự xử lý)
1. [Bước 1]: [Mô tả]
2. [Bước 2]: [Mô tả]
3. [Bước 3]: [Mô tả]

### Conditional Logic (Logic điều kiện)
| Điều kiện | Khi True | Khi False |
|-----------|-----------|------------|
| [Điều kiện] | [Hành động] | [Hành động] |

### State Transitions (Chuyển trạng thái)
| Trạng thái hiện tại | Trigger | Trạng thái mới |
|---------------|---------|-----------|
| [Trạng thái A] | [Sự kiện] | [Trạng thái B] |

### Error Handling (Xử lý lỗi)
| Loại lỗi | Cách xử lý | Cách phục hồi |
|------------|----------|----------|
| [Lỗi] | [Xử lý ra sao] | [Phục hồi ra sao] |

---

## 4. Database & Data Flow Analysis

### Tables/Entities Affected (Table/Entity bị ảnh hưởng)
| Table | Thao tác | Field | Constraint |
|-------|-----------|--------|-------------|
| [Tên table] | Create/Read/Update/Delete | [Field] | [Unique, Not Null, v.v.] |

### Data Relationships (Quan hệ dữ liệu)
- [Cha] → [Con]: [Loại quan hệ]

### Transaction Boundaries (Ranh giới transaction)
| Transaction | Thao tác gồm | Điều kiện Rollback |
|-------------|------------|-------------------|
| [Tên] | [Các thao tác trong đó] | [Khi nào rollback] |

### Cache Considerations (Cân nhắc về Cache)
- Dữ liệu được cache: [Cái gì được cache]
- Invalidation: [Khi nào cache bị xóa]

---

## 5. Unclear / Risky Points (Điểm chưa rõ / Rủi ro)

| Unclear ID | Điểm | Loại gap | Mức độ rủi ro | Ảnh hưởng |
|---|-------|----------|------------|--------|
| UNC-001 | [Mô tả] | Ambiguity/Missing/Conflict/Assumption/Testability | High/Medium/Low | [Ảnh hưởng đến việc test] |

---

## 6. Clarification Questions (Câu hỏi làm rõ)

### High Priority
- QH-001: [Câu hỏi]

### Medium Priority
- QM-001: [Câu hỏi]

### Low Priority
- QL-001: [Câu hỏi]

---

## 7. Temporary Assumptions (Assumption tạm thời)

| Assumption ID | Assumption | Category | Impact | Cần validate |
|---|------------|----------|--------|------------------|
| ASM-001 | [Assumption] | Data Format / Business Rule / Error Handling / Security | Critical / High / Medium / Low | Yes/No |
```

---
