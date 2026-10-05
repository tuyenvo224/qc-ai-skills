# Thinking Framework — 6 Lăng Kính Phân Tích

Đọc file này khi thực hiện phân tích chính trong workflow của `SKILL.md`. Với MỌI phân tích, áp dụng đủ 6 lăng kính dưới đây — không bỏ qua lăng kính nào, kể cả khi nó không tìm ra bug nào (ghi nhận "không phát hiện rủi ro đáng kể ở lăng kính này" thay vì bỏ qua).

---

## 1. Break the Flow (Phá vỡ luồng)

Tìm lỗ hổng khi trình tự thao tác kỳ vọng bị gián đoạn.

| Attack Vector | Ví dụ |
|---------------|----------|
| Interrupted steps (gián đoạn giữa chừng) | Đóng app giữa transaction, mất mạng, process bị kill |
| Double actions (thao tác lặp) | Double-click submit, refresh rồi resubmit, mở nhiều tab |
| Out-of-order requests (request sai thứ tự) | Bỏ qua bước bằng cách gọi API trực tiếp, back rồi forward, deeplink giữa luồng |

**Câu hỏi chính:** Nếu user không hoàn thành luồng đúng như thiết kế thì sao?

## 2. Break the Data (Phá vỡ dữ liệu)

Tìm dữ liệu trông có vẻ hợp lệ nhưng gây ra behavior sai.

| Attack Vector | Ví dụ |
|---------------|----------|
| Boundary values (giá trị biên) | 0, -1, MAX_INT, empty string, null |
| Valid format, invalid meaning (đúng format, sai nghĩa) | Ngày trong tương lai, ID đã hết hạn, tham chiếu đã bị xóa |
| Context mismatch (sai ngữ cảnh) | Dữ liệu của User A bị dùng trong context của User B |

**Câu hỏi chính:** Dữ liệu nào có thể qua được validation nhưng phá vỡ business logic?

## 3. Break the State (Phá vỡ trạng thái)

Tìm sự không nhất quán giữa trạng thái hệ thống kỳ vọng và trạng thái thực tế.

| Attack Vector | Ví dụ |
|---------------|----------|
| Old state + new action (state cũ + hành động mới) | Dùng session token cũ, cached data, tham chiếu đã stale |
| Partial success/failure (thành công/thất bại một phần) | Payment OK nhưng order fail, API timeout sau khi DB đã commit |
| Race conditions | Hai request cùng sửa một resource đồng thời |

**Câu hỏi chính:** Nếu trạng thái hệ thống không như ta giả định thì sao?

## 4. Break the Rules (Phá vỡ luật nghiệp vụ)

Tìm cách lách qua business rule mà không cần "hack" hệ thống.

| Attack Vector | Ví dụ |
|---------------|----------|
| Business logic abuse (lạm dụng logic nghiệp vụ) | Áp dụng discount 2 lần, stack các promo không cho phép stack |
| Retry/resend/replay | Gửi lại request đã thành công, replay token cũ |
| Rule bypass (lách rule) | Đổi quantity sau khi giá đã lock, sửa cart sau khi checkout đã bắt đầu |

**Câu hỏi chính:** User có thể nhận được nhiều hơn mức được phép bằng cách nào?

## 5. Break Assumptions (Phá vỡ giả định)

Thách thức các giả định ngầm định mà hệ thống đang dựa vào.

| Assumption (Giả định) | Reality (Thực tế) |
|------------|---------|
| Hệ thống luôn online | Mạng lỗi, service crash, DB timeout |
| API luôn phản hồi đúng | Response sai định dạng, sai status code, callback bị delay |
| Thời gian tuyến tính | Đổi timezone, daylight saving, clock skew |
| User luôn theo đúng luồng | Truy cập API trực tiếp, sửa request, dùng script tự động |

**Câu hỏi chính:** Hệ thống đang giả định điều gì mà có thể sai?

## 6. Think Like a Bad User (Nghĩ như một user xấu)

Đặt mình vào tư duy đối kháng (adversarial).

| User Type | Attack Pattern |
|-----------|----------------|
| **Greedy (tham lam)** | Làm sao để nhận đồ miễn phí, double reward, né thanh toán |
| **Cheater (gian lận)** | Làm sao để khai thác promotion, lạm dụng referral, giả hành động |
| **Abuser (phá hoại)** | Làm sao để hại user khác, spam hệ thống, denial of service |
| **Fraudster (lừa đảo)** | Làm sao để được refund mà vẫn giữ hàng, lạm dụng chargeback |

**Câu hỏi chính:** Nếu tôi muốn lạm dụng hệ thống này, tôi sẽ làm như thế nào?
