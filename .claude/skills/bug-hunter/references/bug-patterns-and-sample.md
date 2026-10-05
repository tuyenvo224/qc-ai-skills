# Pattern Lỗi Thường Gặp & Ví Dụ Phân Tích Mẫu

Đọc file này để tham khảo các pattern lỗi nghiêm trọng hay gặp (dùng để đối chiếu khi phân tích một flow mới) và một ví dụ phân tích đầy đủ theo đúng Output Format của `SKILL.md`.

---

## Common High-Impact Bug Patterns

### Pattern 1: Double Submit / Replay

```
Vulnerability: Cùng một hành động bị xử lý nhiều lần
Impact: Charge 2 lần, double reward, tạo record trùng lặp
Where to look: Bất kỳ nút submit nào, xác nhận thanh toán, claim reward
```

### Pattern 2: Race Condition trên tài nguyên giới hạn

```
Vulnerability: Nhiều user cùng claim món hàng cuối cùng đồng thời
Impact: Overselling, tồn kho âm, thất hứa với khách
Where to look: Flash sale, voucher giới hạn, đặt chỗ (seat booking)
```

### Pattern 3: State Mismatch sau khi lỗi

```
Vulnerability: Transaction thất bại một phần để lại trạng thái không nhất quán
Impact: Đã trừ tiền nhưng chưa giao dịch vụ, hoặc ngược lại
Where to look: Bất kỳ transaction nhiều bước nào, payment + fulfillment
```

### Pattern 4: Khai thác dữ liệu cũ (Stale Data)

```
Vulnerability: Dữ liệu cached/cũ được dùng để ra quyết định
Impact: Bỏ qua thay đổi giá, áp dụng promo đã hết hạn, order sản phẩm đã bị xóa
Where to look: Cart, checkout, pricing, khuyến mãi
```

### Pattern 5: Business Rule Edge Case

```
Vulnerability: Rule không xử lý điều kiện biên
Impact: Nhận hàng miễn phí, discount không giới hạn, lách rule
Where to look: Stack discount, đơn hàng tối thiểu, giới hạn số lượng
```

### Pattern 6: Async Callback Manipulation

```
Vulnerability: Callback có thể bị delay, bị gửi trùng, hoặc bị giả mạo
Impact: Giao dịch vụ mà không có thanh toán, xử lý trùng lặp
Where to look: Payment webhook, tích hợp bên thứ ba
```

---

## Sample Analysis: Payment Flow

### Core Flow Summary

User chọn item → thêm vào cart → tiến hành checkout → nhập thanh toán → ngân hàng xử lý → nhận callback → order được confirm → giao hàng.

### High-Risk Points

1. **Double payment submission** — User click pay 2 lần liên tiếp nhanh
2. **Callback timing** — Nếu callback đến trước/sau khi user quay lại thì sao?
3. **Cart modification** — User có thể đổi cart sau khi đã khởi tạo thanh toán không?
4. **Price consistency** — Giá có bị lock ở checkout hay có thể đổi?
5. **Partial failure** — Payment thành công nhưng tạo order thất bại

### Bug Hypotheses

| Bug ID | Bug Hypothesis | Vì sao xảy ra | Impact | Vì sao hay bị bỏ sót |
|---|----------------|-------------------|--------|-------------------|
| BUG-001 | User bị charge 2 lần cho 1 order | Double-click nút pay, không có idempotency | Critical | Tester chỉ click 1 lần, thao tác sạch sẽ |
| BUG-002 | Nhận hàng miễn phí qua việc sửa cart | Thêm item sau khi số tiền thanh toán đã bị lock | Critical | Tester không sửa cart giữa lúc thanh toán |
| BUG-003 | Order bị treo (limbo) vĩnh viễn | Callback bị mất, không có timeout handler | High | Tester luôn thấy callback về đúng lúc |
| BUG-004 | Khai thác giảm giá giữa checkout | Giá bị cache ở cart, giá giảm, user vẫn được hưởng giá cũ | High | Tester không giả lập việc đổi giá |

### Reproduction Ideas

**BUG-001 — Double Charge Bug:**
- Preconditions: User đang ở bước xác nhận thanh toán
- Actions: Click "Pay Now" → click lại ngay lập tức
- Conditions: Mạng chậm tới ngân hàng, frontend không chặn double-click

**BUG-002 — Cart Modification Bug:**
- Preconditions: Mở 2 tab trình duyệt
- Actions: Tab 1 bắt đầu thanh toán → Tab 2 thêm item đắt tiền → Tab 1 hoàn tất
- Conditions: Cart không bị lock trong lúc thanh toán
