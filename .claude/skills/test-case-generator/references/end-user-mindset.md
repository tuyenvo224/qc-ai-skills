# End-User Mindset Checklist

Read this when adding ad-hoc/exploratory test cases beyond what the spec states (Step 3 of `SKILL.md`'s workflow) — run this checklist against every feature.

---

## 6. End-User Mindset

**BẮT BUỘC chạy checklist này với MỖI chức năng ở Step 3.**

### 6.1 End-User Thinking Checklist

#### A. Thao tác sai / Nhầm lẫn

```
□ User nhập sai format (email không có @, phone có chữ) → hiện message gì?
□ User bấm nút Submit 2-3 lần liên tục → có tạo duplicate không?
□ User paste data từ Excel/Word (có hidden characters) → xử lý sao?
□ User dùng emoji / ký tự đặc biệt (é, ñ, 中文, 🎉) → lưu đúng không?
□ User nhập khoảng trắng đầu/cuối → có trim không?
□ User nhập toàn khoảng trắng → coi là empty hay valid?
□ User copy-paste URL/script vào text field → xử lý sao?
```

#### B. Bỏ giữa chừng / Gián đoạn

```
□ User đóng browser giữa chừng submit → data lưu chưa? orphan record?
□ User bấm Back giữa process multi-step → data step trước còn không?
□ User refresh page khi đang submit → double submit?
□ Session timeout giữa flow dài → redirect về login? data mất?
□ User mở 2 tab cùng lúc, sửa cùng 1 record → tab nào thắng?
□ Mất mạng giữa chừng → UI hiện gì? retry tự động không?
```

#### C. Gian lận / Lạm dụng

```
□ User cố tạo data trùng (cùng name, cùng code) → prevent được không?
□ User sửa URL/params để truy cập data người khác (IDOR)?
□ User thay đổi request body qua DevTools để bypass UI validation?
□ User dùng script/bot gửi request liên tục (rate limiting)?
□ User cố exploit promo code (dùng lại, chia sẻ, stack)?
□ User tạo account fake/spam?
```

#### D. Tình huống thực tế

```
□ 2 user cùng sửa 1 record → ai thắng? có thông báo conflict?
□ Data cũ và data mới có xung đột logic?
□ User với quyền khác nhau (admin, user, viewer) thấy gì khác nhau?
□ Ngày lễ / cuối tuần / DST có ảnh hưởng business rule?
□ Timezone khác nhau → hiển thị datetime đúng?
□ Dữ liệu lớn (list 10000 records) → performance có OK?
□ Tên rất dài / rất ngắn / có dấu tiếng Việt → hiển thị đúng?
```

#### E. Cross-feature / Tác động chéo

```
□ Feature A thay đổi → ảnh hưởng feature B không?
□ Delete/deactivate entity → entity liên quan xử lý sao?
□ Thay đổi config/setting → có break flow đang chạy không?
□ Rollback / undo action → data quay về đúng trạng thái?
□ Import data → có conflict với data hiện có?
```

### 6.2 Ad-hoc Thinking Patterns

Khi viết TC cho mỗi feature, tự hỏi:

- **"Nếu tôi là user LẦN ĐẦU dùng, tôi sẽ NHẦM gì?"** → Usability TC
- **"Nếu tôi là user VỘI VÀNG, tôi sẽ SKIP gì?"** → Shortcut TC
- **"Nếu tôi là user MUỐN PHÁ SYSTEM, tôi sẽ LÀM gì?"** → Abuse TC
- **"Nếu tôi là user XẤU, tôi sẽ EXPLOIT gì?"** → Security TC
- **"Nếu tôi là user THÔNG THƯỜNG gặp LỖI, tôi sẽ LÀM gì tiếp?"** → Error recovery TC
- **"Điều gì xảy ra nếu 2 người CÙNG LÚC làm điều này?"** → Concurrent TC

### 6.3 Khi nào bổ sung adhoc case

- Nếu checklist ở 6.1 trigger ra scenario chưa có trong spec → **tạo TC mới** với tag `[EG]` hoặc `[EXP]`
- Nếu scenario liên quan financial/security → đánh **P1**
- Nếu scenario liên quan data integrity → đánh **P2**
- Nếu scenario liên quan UX → đánh **P3-P4**

---

