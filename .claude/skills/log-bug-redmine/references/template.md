# Template log bug trên Redmine

Output luôn gồm 2 codeblock: **codeblock 1** là tiêu đề, **codeblock 2** là nội dung.

Tiêu đề luôn bắt đầu bằng `[STG]` + một tag loại bug `[UI]` hoặc `[Function]` (quy tắc phân loại xem SKILL.md), sau đó tới `[Sản phẩm] [Module]`.

## Khung nội dung (codeblock 2)

```
**I. Môi trường (Environment)**
- **URL / Build:**
- **OS:**
- **Browser / Device:**
- **Tài khoản test:**

**II. Điều kiện tiên quyết (Preconditions)**
-

**III. Các bước tái hiện (Steps to Reproduce)**
1.
2.
3.

**IV. Kết quả thực tế (Actual Result)**
-

**V. Kết quả mong đợi (Expected Result)**
-

**VI. Tần suất (Reproducibility)**
Always / Sometimes / Rarely

**VII. Ghi chú (Notes)**
-
```

## Ví dụ ngắn (do người dùng cung cấp)

**Subject:** [STG][Function][Biz Order] [Login] Không đăng nhập được khi mật khẩu chứa ký tự đặc biệt

**Environment:**
- URL: https://staging.example.com
- OS: Windows 10
- Browser: Chrome 128

**Preconditions:**
- Tài khoản `test01@example.com` có mật khẩu `Abc@123#`

**Steps to Reproduce:**
1. Truy cập trang Login
2. Nhập email `test01@example.com`
3. Nhập mật khẩu `Abc@123#`
4. Click nút **Đăng nhập**

**Actual Result:**
- Hiển thị thông báo "Sai mật khẩu"

**Expected Result:**
- Đăng nhập thành công, chuyển đến trang Dashboard

**Reproducibility:** Always

## Ví dụ đầy đủ (có đối chiếu spec, có case đối chứng)

Input của người dùng: *"TD1 login có tick remember rồi tắt TD1. Case 1: TD2 login KHÔNG tick thì remember TD1 vẫn còn hiệu lực (bug). Case 2: TD2 login có tick thì remember TD1 mất hiệu lực (ok)."* Spec: FRD Đăng nhập tài khoản Biz Client v1.4 trên BookStack.

**Tiêu đề:**
```
[STG][Function][Biz Client] [Login] Đăng nhập ở trình duyệt khác mà không tick "Ghi nhớ đăng nhập" thì Remember của trình duyệt cũ không bị vô hiệu hóa
```

**Nội dung:**
```
**I. Môi trường (Environment)**
- **URL / Build:** <URL môi trường test / build>
- **OS:** <vd: Windows 10>
- **Browser / Device:** TD1: <vd: Chrome 1xx> · TD2: <vd: Edge 1xx / máy khác>
- **Tài khoản test:** <email tài khoản test>

**II. Điều kiện tiên quyết (Preconditions)**
- Có tài khoản Biz Client, trạng thái Active
- Chuẩn bị 2 trình duyệt/thiết bị khác nhau: TD1 và TD2
- Cả 2 trình duyệt chưa đăng nhập tài khoản này

**III. Các bước tái hiện (Steps to Reproduce)**
1. Mở TD1, vào trang Login của Biz Client
2. Nhập Email + Password đúng, **tick** "Ghi nhớ đăng nhập", bấm **Đăng nhập** → đăng nhập thành công
3. Đóng hẳn TD1
4. Mở TD2, vào trang Login
5. Nhập cùng Email + Password, **KHÔNG tick** "Ghi nhớ đăng nhập", bấm **Đăng nhập** → đăng nhập thành công
6. Mở lại TD1, vào Biz Client

**IV. Kết quả thực tế (Actual Result)**
- TD1 vẫn tự đăng nhập bằng Remember, không yêu cầu nhập lại Email + Password
- Tức là Remember của TD1 **không bị vô hiệu hóa** sau khi tài khoản đăng nhập thành công ở TD2

**V. Kết quả mong đợi (Expected Result)**
- Ở bước 5, khi đăng nhập thành công ở TD2 thì phiên và Remember của TD1 phải bị vô hiệu hóa, **dù TD2 có tick hay không tick** "Ghi nhớ đăng nhập"
- Ở bước 6, TD1 không được tự đăng nhập, phải hiện màn Login và yêu cầu nhập Email + Password
- Căn cứ FRD Đăng nhập tài khoản Biz Client v1.4:
  - BR-SESSION-04: Khi Login mới thành công, trạng thái Ghi nhớ đăng nhập trên device cũ cũng phải bị vô hiệu hóa
  - FR-27, FR-43: Vô hiệu hóa Remember của browser/device cũ khi Account Login thành công trên device khác
  - §5.8.4: Remember mất hiệu lực khi "Account Login thành công trên browser/device khác"
  - UC-09: Chỉ được Auto Login khi "Không có Login mới hơn trên browser/device khác"
  - AC-29: Device A có Remember → Login thành công Device B → Remember Device A mất hiệu lực
  → Không rule nào yêu cầu TD2 phải tick Remember thì mới vô hiệu hóa Remember của TD1

**VI. Tần suất (Reproducibility)**
Always

**VII. Ghi chú (Notes)**
- Case so sánh: làm y hệt các bước trên nhưng ở bước 5 **có tick** "Ghi nhớ đăng nhập" → Remember của TD1 bị vô hiệu hóa đúng như mong đợi (PASS)
- Nghi ngờ: logic vô hiệu hóa Remember của device cũ đang chỉ chạy khi tạo Remember mới, thay vì chạy mỗi khi Login thành công
- Cần kiểm tra thêm: sau khi TD1 tự đăng nhập lại ở bước 6, phiên của TD2 có bị thay thế không (theo BR-SESSION-01, mỗi Account chỉ có 1 phiên hoạt động)
- Spec tham khảo: [C] FRD – Đăng nhập tài khoản Biz Client (BookStack, v1.4, 01/10/2026)
```

**Kiểm tra trước khi post:**
- Điền các ô `<...>` ở mục I.
- Bước 6 đang ghi là TD1 tự đăng nhập vào được. Nếu thực tế khác thì sửa mục IV.
- Nếu đã thấy TD2 bị đá ra khi TD1 tự đăng nhập lại thì chuyển ý đó từ Notes lên Actual Result.
