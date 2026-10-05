# Format file input — compare-campaign-config

Mô tả cấu trúc 2 file input. File mẫu (dữ liệu giả, đúng cấu trúc) nằm ở `../examples/`:
`sample_brief.xlsx`, `sample_config.json`. Không dùng file mẫu làm input thật.

Cấu trúc dưới đây lấy từ 1 campaign Scan It thực tế. Campaign khác có thể thêm/bớt sheet hoặc
key — **cấu trúc của file đang xét mới là chuẩn**, tài liệu này chỉ để định hướng.

---

## 1. File brief (.xlsx)

- Tên file thường dạng: `[<Mã>]<Khách hàng> <Tên CT>_CAMPAIGN SCAN IT_BRIEF BA.xlsx`.
- Có thể có sheet **ẩn** (vd `AUDIT`) — vẫn phải đọc.
- Nhiều sheet có header không nằm ở dòng 1, có ô merge, có nhiều bảng con xếp chồng trong
  cùng 1 sheet → xác định đúng dòng header trước khi đọc dữ liệu.

| Sheet | Dòng header | Nội dung chính | Đối chiếu với config |
|---|---|---|---|
| `BRIEF` | 3 (`STT \| Items \| Mô tả \| Nội dung Sales cần input`) | **Sheet chính.** ~35 mục: tên CT, loại campaign, thời gian CT/bill/chụp bill, phương thức thông báo, khu vực, SKU, điều kiện tham gia, giới hạn lượt/ngày, T&C, whitelist/blacklist, landing page, hotline, các bước tham gia… Giá trị nằm ở **cột D**; cột B có ô merge gom nhóm mục 14–23, 24–27 | `campaign.*`, `take_pic_rule_validation`, `campaign_setting`, `game_rule`, `scheme.limit`, `form_element[phone].rules` |
| `Scheme CT` | 2 (`HỆ THỐNG \| THỜI GIAN TRIỂN KHAI \| MAIN SCHEME \| NGÀY - GIỜ VÀNG \| RULE \| Note giờ vàng`) | Scheme theo từng chuỗi: ngưỡng bill, thời gian, giờ vàng, giới hạn lượt quay. Cột D–G merge theo nhóm chuỗi | `game[is_primary=1].scheme[]` (`name`, `value`, `limit`, `metadata`, `scheme_detail[date_and_time_bill]`) |
| `Allocation` | 3 (tên giải ngắn), 4 (tên giải đầy đủ); dòng 1–2 là ghi chú/nhóm | Số lượng từng giải theo chuỗi (KA) + cột `Tỷ lệ trúng`. Có thêm bảng con phía dưới (merge ở dòng ~22, 43, 70) | `game[].prize[].quantity`, `award_mechanism[].mechanism_prize_rate[].rate` |
| `Prize Rate` | 3–4 (giống `Allocation`) + cột `Total`, `Tỷ lệ trúng` | Tổng giải + tỷ lệ trúng theo chuỗi, giờ thường/giờ vàng | `award_mechanism[]` (mặc định vs HAPPYHOUR) |
| `Thông tin giải thưởng` | 2 (`STT \| TÊN GIẢI THƯỞNG \| SỐ LƯỢNG \| ÁP DỤNG RULE LIMIT… \| ĐƠN GIÁ \| Thành Tiền \| SKU`) | Danh sách giải theo từng chuỗi (dòng chỉ có cột A = tên chuỗi là dòng nhóm), rule limit 1 SĐT/thiết bị/quà | `prize[].name`, `prize[].promotion_rule[]` |
| `Quà Lớn` | 8; dòng 7 là nhóm cột, dòng 8 từ cột P là **ngày** | Phân bổ giải lớn theo store + khung giờ ra giải theo từng ngày | Tool giải lớn / phân bổ — thường ngoài config JSON |
| `Quà AI Voteing` | 8 | Phân bổ quà AI Voting theo store | Phân bổ theo store — thường ngoài config JSON |
| `STORELIST` | 7 (`STT \| Tên hệ thống \| STORE LIST (Tên Ekoin) \| Region \| Province… \| Tên trên bill \| Code \| AGENCY`) | Danh sách siêu thị tham gia (hàng nghìn dòng) | `list_store_not_auto`, OCR/rule siêu thị |
| `SKU Threshold` | 1 (`name \| price_threshold \| alternative_name`) | Ngưỡng giá theo SKU trên bill | `sku_suggestion_keywords`, rule OCR |
| `ZNS-SMS` | 1 (`STT \| Tên mẫu tin \| Nội dung… \| CTA… \| SMS fail over \| Brandname \| Note \| Temp ID \| Đơn giá`); dòng 2 là ví dụ | Mẫu ZNS/SMS theo từng loại giải, template ID PROD/STG | `prize[].zns_msg_content` (`template_id`, `zns_failover`), `campaign.notify_prize_by`, `provider_zns/sms` |
| `Blacklist` | 1 (`Số điện thoại \| Hệ thống \| Giải thưởng \| CT`) | SĐT bị chặn nhận giải | `form_element[phone].rules` (`not_exists_blacklist:<slug>`) |
| `Blacklist k đc tham gia` | không có header | Chỉ 1 cột SĐT không được tham gia (vd nhân sự) | như trên |
| `Phân quyền` | 3 (`Tên đăng nhập \| Họ tên \| Tên siêu thị \| Tên campaign \| SDT \| Agency \| Ghi chú`); cột J là email CS | Tài khoản nhân sự/CS | Ngoài config JSON |
| `T&C` | không cố định | Thể lệ, email alert (vd dòng "Alert qua mail" + ngưỡng % giải) | `alert_prize_info`, `level_gift_out_info`, `command_configs` |
| `Thể lệ Voucher` | không có header | Thể lệ từng loại voucher (text) | `voucher_expired` (một phần) |
| `IVR` | 1 (`Tổng đài … \| Nội dung`) | Kịch bản tổng đài | Ngoài config JSON |
| `QR CODE`, `Demo Voucher` | dòng 1 là nhãn | Ảnh QR PROD/STG, voucher demo (chủ yếu là ảnh/link) | Ngoài config JSON |
| `AUDIT` (ẩn) | 4 | Kết quả audit brief trước đó (mức độ, sheet, vị trí, mô tả sai lệch, status) | Tham khảo — không phải yêu cầu |
| `Sheet1` | — | Thường rỗng | — |

**Lưu ý dễ nhầm:**
- Nhiều sheet copy từ campaign trước còn sót dữ liệu cũ (vd hướng dẫn "Mini Tet 1/2025",
  blacklist ghi CT cũ) → đối chiếu tên CT/ngày trong từng sheet.
- Giá trị ở cột D của `BRIEF` hay viết dạng "xem sheet X" → phải mở sheet đó để lấy giá trị thật.
- Công thức có thể ra `#REF!` → ghi nhận là lỗi brief, không suy đoán giá trị.

---

## 2. File config (.json)

- Tên file thường dạng: `config-<id>-<slug><timestamp>.json`.
- Kích thước có thể vài trăm KB do mảng `game` / `prize` lớn.

```
{
  "campaign":                 { ... },      // thông tin chung
  "landing_page":             [ { ... } ],  // thường 1 phần tử
  "campaign_setting":         [ {key, display_name, value, status}, ... ],  // ~70 key
  "take_pic_rule_validation": [ {rules, value, status, message}, ... ]
}
```

### 2.1 `campaign`
`name`, `type` (vd `scanit`), `slug`, `status`, `verify_otp`, `biz_order_name`, `provider`,
`notify_by_otp`, `notify_gameplay_by`, `notify_prize_by` (vd `["NotifyPrizeByZns"]`),
`notify_bill_fail_by`, `notify_bill_success_by`, `hide_landing_page`, `domain`, `keys`,
`is_show_winner`, `is_show_result`, `tc_template`.

### 2.2 `landing_page[0]`
- `name`, `title`, `status`, `is_confirm`, `limit_change_phone`, `position`
- `form.form_element[]`: `name`, `type`, `rules` (vd phone: `CheckPhone|not_exists_blacklist:<slug>`),
  `display_name`, `required`, `order`, `status`, `is_customer_attribute`
- `game[]` — 1 game **primary** (`is_primary=1`, type `award_prize_multi`) + mỗi chuỗi 1 game
  lượt quay (`lucky_draw_liteview`, `lucky_draw2`…). Mỗi game gồm:
  - `game_rule[]`: `rule_type` (`limit_by_total_gameplay`, `limit_by_time` + `start_date`/`end_date`…), `value`, `status`
  - `prize[]`: `name`, `quantity`, `used`, `remaining`, `rate`, `type` (`increment_gameplay`, `gift`…),
    `zns_msg_content` (JSON string: `template_id`, `template_data`, `zns_failover`), `has_delivery_info`,
    `metadata.prefix`, `promotion_rule[]` (giới hạn quà theo SĐT/thiết bị)
  - `award_mechanism[]`: `name` (vd tỉ lệ mặc định / `HAPPYHOUR-<chuỗi>`), `rate_type`,
    `mechanism_prize_rate[]` (rate theo **thứ tự** `prize[]`), `mechanism_modifier[]` (khung ngày/giờ áp dụng)
  - `scheme[]` (chỉ game primary): `name` (vd `[<CHUỖI>] Hóa đơn 139k… (20/08 - 08/09)`), `value` (ngưỡng bill),
    `type`, `status`, `limit`, `metadata` (`limit_prize_per_device`, `limit_prize_per_customer`),
    `scheme_detail[]` (`bill_attribute`, `run_time_scheme`, `date_and_time_bill` → ngày/giờ vàng)

### 2.3 `campaign_setting[]`
Mảng `{key, display_name, value, status}` (~70 phần tử). `value` có thể là chuỗi JSON lồng.
Nhóm key thường gặp:

| Nhóm | Key ví dụ |
|---|---|
| OTP / thông báo | `otp_expired`, `sms_otp_message`, `provider_sms`, `provider_zns`, `zns_*`, `zns_param_default_value` |
| Upload / chụp bill | `multi_snap`, `allow_choose_file_from_library`, `limit_*_file_choose`, `content_guide_choose_file`, `is_upload_via_ai`, `allow_zalo` |
| Duyệt bill / AI | `is_automation`, `list_brand_not_auto*`, `list_store_not_auto`, `cp005_supermarket_ordernumber_date`, `customize_params_approve_bill`, `llm_vote_check_precision_*`, `sku_suggestion_keywords` |
| Giải lớn / alert | `confirm_award_prize_*`, `level_gift_out_info`, `level_gift_out_notification_status`, `alert_prize_info`, `command_configs` |
| Hiển thị | `hotline`, `scanit_background_home`, `is_show_none_prize`, `show_all_remaining_play_times*`, `game_result_*`, `error_messages`, `game_congratulate_message_limit_promotion` |
| Hệ thống | `company_id`, `account_id`, `voucher_expired`, `campaign_mode_test`, `is_hard_bill`, `webhook_*`, `integrate_accessing_type` |

Lưu ý: `status = 0` nghĩa là setting đang **tắt**, dù `value` có giá trị (vd `is_hard_bill`).

### 2.4 `take_pic_rule_validation[]`
`{rules, value, status, message}` — vd `available_campaign` = `06:00 - 22:00` (khung giờ chụp bill),
`device_unknown`.

---

## 3. Bảo mật

File config thật có chứa secret (vd `webhook_ekoin_value`), email nội bộ, ID công ty/tài khoản;
file brief thật có SĐT, họ tên nhân sự. **Không commit file thật vào repo**, không trích nguyên
văn secret vào báo cáo (ghi "có giá trị / rỗng" là đủ).
