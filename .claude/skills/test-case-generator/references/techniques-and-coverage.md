# Test Design Techniques & Coverage Strategy

Read this when planning which techniques and test types to apply per feature (Step 2 of `SKILL.md`'s workflow) — the 9 black-box/experience-based techniques, minimum technique count per priority, and the test-type coverage matrix.

---

## 4. Test Design Techniques

### 4.1 Bảng kỹ thuật

#### Black-Box Techniques

| Tag | Tên | Mô tả | Cách áp dụng |
|-----|-----|--------|---------------|
| `[EP]` | Equivalence Partitioning | Chia input thành nhóm valid/invalid. 1 test per nhóm đại diện | Age: Valid (18-65), Invalid-low (<18), Invalid-high (>65), Invalid-type (text) → 4 TC |
| `[BVA]` | Boundary Value Analysis | Test tại biên: min, min-1, min+1, max, max-1, max+1 | Age 18-65: test 17, 18, 19, 64, 65, 66 → 6 TC |
| `[DT]` | Decision Table | Tổ hợp tất cả conditions → actions. Mỗi cột = 1 TC | VIP=Y/N AND order>$100=Y/N → 4 tổ hợp → 4 TC |
| `[ST]` | State Transition | Test chuyển trạng thái valid + verify invalid bị reject | Order: Draft→Confirmed→Shipped, verify Draft→Delivered bị block |
| `[UC]` | Use Case Testing | Test E2E flow: main flow + alternative flows + exception flows | Checkout: Main (success) + Alt (coupon) + Exception (payment fail) |
| `[PW]` | Pairwise Testing | Giảm tổ hợp khi ≥3 params. Test tất cả cặp giá trị | OS(3)×Browser(4)×Lang(5) = 60 full → ~15-20 pairwise |

#### Experience-Based Techniques

| Tag | Tên | Mô tả | Cách áp dụng |
|-----|-----|--------|---------------|
| `[EG]` | Error Guessing | Đoán lỗi dựa kinh nghiệm, tập trung nơi hay bug | null, empty, special chars, SQL injection, 0/negative, concurrent |
| `[CL]` | Checklist-Based | Dùng checklist chuẩn kiểm tra | Login checklist: valid, invalid password, locked, remember me, timeout |
| `[EXP]` | Exploratory | Khám phá tự do có định hướng, session-based | Charter: "Explore payment flow edge cases, 30 min, focus rounding" |

### 4.2 Quy tắc áp dụng tối thiểu theo Priority

| Feature Priority | Min. Techniques | Techniques bắt buộc |
|-----------------|-----------------|---------------------|
| **P1 - Critical** | ≥6 | EP + BVA + DT + ST + UC + EG (+ EXP khuyến khích) |
| **P2 - High** | ≥4 | EP + BVA + (DT hoặc ST) + EG |
| **P3 - Medium** | ≥3 | EP + BVA + (UC hoặc CL) |
| **P4 - Low** | ≥1 | EP hoặc CL |

### 4.3 Mapping tự động: Đặc điểm feature → Technique bắt buộc

| Đặc điểm feature | Technique bắt buộc |
|-------------------|-------------------|
| Có input fields / parameters | EP + BVA |
| Có business rules với ≥2 conditions | DT |
| Có workflow / status changes | ST |
| Có multi-step user flow | UC |
| Có ≥3 params độc lập | PW (recommended) |
| Là P1 hoặc P2 | EG + EXP |
| Có historical bug patterns | CL + EG |

### 4.4 Quy tắc tag

- **MỌI** test case PHẢI có `[Technique Tag]` trong cột Test Objective
- Nếu TC không có tag → **INVALID**, phải sửa
- Mỗi TC chỉ gắn **1 primary technique tag**
- Các TC từ technique khác nhau KHÔNG được trùng nội dung (EP test ≠ BVA test ≠ EG test)

---

## 5. Coverage Strategy

### 5.1 Test Types phải cover

**Bắt buộc cho MỌI chức năng:**

| Test Type | Ký hiệu | Mô tả | Luôn bắt buộc? |
|-----------|----------|--------|-----------------|
| Function Testing | FN | Chức năng hoạt động đúng (happy path) | BẮT BUỘC |
| Business Logic | BL | Logic nghiệp vụ, tính toán, rules đúng | BẮT BUỘC (khi có logic) |
| Negative Testing | NEG | Xử lý input sai, thiếu, format sai | BẮT BUỘC |
| Data Integrity | DI | DB lưu đúng, constraints enforce đúng | BẮT BUỘC |

**Bắt buộc theo đặc điểm feature:**

| Test Type | Ký hiệu | Áp dụng khi |
|-----------|----------|-------------|
| UI Basic | UI | Feature có giao diện người dùng |
| Edge Case | EC | P1/P2 features, fields có boundaries |
| Permission | PM | Feature có phân quyền / multi-role / multi-tenant |
| State Testing | ST | Feature có workflow / status changes |
| Concurrent | CN | Feature có create/update shared resources |
| Integration | IT | Feature gọi external service / carrier / webhook |
| Security | SEC | Feature có auth, payment, sensitive data, public API |
| Accessibility | A11Y | Feature có UI public-facing / spec yêu cầu WCAG / dùng bởi end-user bên ngoài |
| Compatibility | COMPAT | Spec yêu cầu hỗ trợ đa trình duyệt (Chrome/Firefox/Safari/Edge), đa OS, hoặc đa device (desktop/mobile/tablet) |

### 5.1b Accessibility (A11Y) & Compatibility (COMPAT) — chi tiết

Hai test type này KHÔNG áp dụng mặc định cho mọi feature (khác với FN/BL/NEG/DI) — chỉ bắt buộc khi feature có UI public-facing hoặc spec nêu rõ yêu cầu đa nền tảng. Khi áp dụng được, tối thiểu:

**A11Y — mỗi màn hình/form:**
```
□ Toàn bộ action chính thao tác được bằng keyboard (Tab/Enter/Esc), không bẫy focus (focus trap)
□ Input/button quan trọng có label/aria-label rõ ràng cho screen reader
□ Độ tương phản màu chữ/nền đạt tối thiểu (không chữ xám nhạt trên nền trắng cho text quan trọng)
□ Thứ tự focus (tab order) đi theo đúng luồng đọc tự nhiên của form
□ Thông báo lỗi/thành công không chỉ dựa vào màu sắc (kèm icon/text rõ ràng)
```

**COMPAT — theo phạm vi spec yêu cầu:**
```
□ Render đúng trên các trình duyệt chính được spec liệt kê (vd Chrome, Firefox, Safari, Edge)
□ Render đúng trên các OS/device chính (Desktop, iOS, Android) nếu spec yêu cầu responsive/mobile
□ Không vỡ layout ở các độ phân giải phổ biến (desktop, tablet, mobile)
□ Hành vi nhất quán giữa các nền tảng (không khác chức năng, chỉ khác trình bày)
```

**Priority:** A11Y/COMPAT case thường P3 trừ khi spec/khách hàng nêu rõ đây là yêu cầu bắt buộc (compliance/contract) → khi đó nâng lên P1/P2 và áp dụng ngưỡng coverage như mọi risk/requirement khác (xem `done-criteria.md`).

### 5.2 Feature-Coverage Matrix

**Tra bảng này để biết feature cần test types nào:**

| Feature Type | FN | BL | NEG | EC | PM | DI | ST | CN | IT | SEC | UI |
|-------------|----|----|-----|----|----|----|----|----|----|-----|-----|
| **Authentication** | ✓ | - | ✓ | ✓ | ✓ | ✓ | - | - | - | ✓ | ✓ |
| **Payment/Financial** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Order/Transaction** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Inventory/Stock** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | - | ✓ | - | - | ✓ |
| **User Profile/CRUD** | ✓ | - | ✓ | ✓ | ✓ | ✓ | - | - | - | - | ✓ |
| **Search/Filter** | ✓ | - | ✓ | ✓ | ✓ | - | - | - | - | - | ✓ |
| **Reports/Export** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | - | - | - | - | ✓ |
| **Notifications** | ✓ | ✓ | ✓ | - | - | ✓ | - | - | ✓ | - | - |
| **Admin Functions** | ✓ | - | ✓ | - | ✓ | ✓ | - | - | - | - | ✓ |
| **Webhook Receiving** | ✓ | ✓ | ✓ | ✓ | - | ✓ | ✓ | ✓ | ✓ | ✓ | - |
| **Settings/Config** | ✓ | - | ✓ | - | ✓ | ✓ | - | - | - | - | ✓ |

**A11Y và COMPAT không nằm trong bảng trên** (chúng là overlay cắt ngang mọi feature type, không riêng theo type) — áp dụng theo điều kiện ở mục 5.1b, bất kể feature thuộc type nào.

### 5.3 Risk-Based Test Depth

| Priority | Test Depth | Nghĩa là |
|----------|-----------|-----------|
| **P1 - Critical** | Exhaustive | MỌI path, MỌI boundary, MỌI error condition, MỌI combination |
| **P2 - High** | Thorough | Main paths, key boundaries, common errors, important combinations |
| **P3 - Medium** | Standard | Happy path, obvious boundaries, basic negative cases |
| **P4 - Low** | Minimal | Happy path only, smoke test level |

### 5.4 UI Basic Test Checklist

**Áp dụng cho MỌI feature có giao diện. Chỉ test cơ bản, KHÔNG đi sâu UI.**

```
Cho mỗi màn hình / form:
□ Layout hiển thị đúng, không vỡ, không mất elements
□ Các field bắt buộc có dấu * hoặc indicator rõ ràng
□ Label và placeholder đúng nội dung
□ Validation message hiển thị đúng vị trí, đúng nội dung
□ Button disabled/loading khi đang xử lý (prevent double-click)
□ Loading indicator hiển thị khi gọi API
□ Toast/notification hiển thị sau thành công hoặc thất bại
□ Navigation đúng sau action (redirect đúng page)
□ Data hiển thị đúng sau khi load (match với DB/API response)
□ Responsive cơ bản trên mobile (nếu có yêu cầu)
```

**Lưu ý:** UI Basic test nằm ĐẦU mỗi nhóm TC (trước Happy path). Chỉ viết các case cơ bản, KHÔNG viết chi tiết từng pixel.

### 5.5 Coverage Tracking

**Cuối mỗi test document phải có 2 bảng:**

**Table 1: Test Type Coverage**

| Group Name | UI | FN | BL | NEG | EC | PM | DI | CN | IT | SEC | A11Y | COMPAT | Total |
|------------|----|----|----|----|-----|----|----|----|----|-----|------|--------|-------|
| [Feature A] | 3 | 4 | 2 | 5 | 3 | 2 | 3 | - | - | 2 | 1 | - | 25 |
| [Feature B] | 2 | 3 | 3 | 4 | 2 | 2 | 2 | 2 | 2 | 3 | - | 1 | 26 |
| **Total** | 5 | 7 | 5 | 9 | 5 | 4 | 5 | 2 | 2 | 5 | 1 | 1 | 51 |

Cột A11Y/COMPAT có thể để `-` (N/A) nếu feature đó không áp dụng — không bắt buộc phải có ở mọi feature như các cột còn lại.

**Table 2: Technique Coverage**

| Group Name | EP | BVA | DT | ST | UC | PW | EG | CL | EXP | Total | Min Req | Status |
|------------|----|----|----|----|----|----|----|----|-----|-------|---------|--------|
| [Feature A] (P1) | 5 | 6 | 3 | 2 | 2 | - | 4 | 2 | 1s | 24+1s | ≥6 | PASS |
| [Feature B] (P2) | 4 | 4 | 2 | - | 1 | - | 3 | - | - | 14 | ≥4 | PASS |

---

