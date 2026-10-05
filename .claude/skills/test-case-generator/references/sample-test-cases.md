# TD REFERENCE: SAMPLE TEST CASES

**Vai tro:** Mau test cases tham khao de Test Case Generator hoc format va cach viet.
**Load khi:** Can tham khao mau, gap feature type chua co kinh nghiem, lan dau dung format.

**LƯU Ý NGÔN NGỮ:** các mẫu dưới đây viết bằng tiếng Anh chỉ để minh họa FORMAT/PATTERN (cấu trúc 4 cột, cách đặt tag, cách viết Expected Result đo lường được). Khi viết test case thật, áp dụng đúng pattern nhưng **dịch câu sang tiếng Việt** — xem quy tắc bắt buộc ở `writing-format.md` mục 7.0. KHÔNG copy nguyên văn tiếng Anh từ các mẫu này vào output thật.

---

## Table of Contents

1. [Sample: Login Feature (UI + Function)](#1-sample-login-feature)
2. [Sample: CRUD API (Create Order)](#2-sample-crud-api-create-order)
3. [Sample: Business Logic (Discount Calculation)](#3-sample-business-logic-discount-calculation)
4. [Sample: Permission Matrix](#4-sample-permission-matrix)
5. [Sample: Concurrent / Race Condition](#5-sample-concurrent--race-condition)
6. [Sample: Webhook Testing](#6-sample-webhook-testing)
7. [Sample: State Machine (Order Status)](#7-sample-state-machine-order-status)
8. [Sample: Coverage Summary Tables](#8-sample-coverage-summary-tables)

---

## 1. Sample: Login Feature

**Requirement:** REQ-101 - Users can log in with email and password
**Priority:** P1 (Critical)
**Techniques Applied:** EP(3) + BVA(3) + DT(1) + UC(2) + EG(2) + CL(1) = 12 TC, 6 techniques

### Group: Login Screen

**① UI Basic**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| AUTH-001 | [CL] Verify login screen displays correctly with all required elements | 1. Navigate to https://app.example.com/login 2. Observe page layout | ✓ UI: Email field visible with placeholder "Enter your email" ✓ UI: Password field visible with placeholder "Enter your password" ✓ UI: "Sign In" button visible and enabled ✓ UI: "Forgot Password?" link visible ✓ UI: "Remember me" checkbox visible |

**② Happy path / Positive**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| AUTH-002 | [EP] Verify successful login with valid credentials (valid partition) | 1. Navigate to login page 2. Enter email: "user@test.com" 3. Enter password: "ValidPass123!" 4. Click "Sign In" button | ✓ UI: User redirected to /dashboard ✓ UI: Header displays "Hello, user@test.com" ✓ Session cookie created ✓ DB: users.last_login_at updated |
| AUTH-003 | [UC] Verify complete login flow - main success path | 1. Navigate to login page 2. Enter valid credentials 3. Click "Sign In" 4. Verify dashboard loads 5. Refresh page | ✓ Full journey: page loads -> credentials -> redirect -> dashboard ✓ Session persists after refresh ✓ User stays logged in |
| AUTH-004 | [UC] Verify login flow - alternative path: remember me | 1. Navigate to login page 2. Enter valid credentials 3. Check "Remember me" checkbox 4. Click "Sign In" 5. Close browser 6. Reopen and navigate to app | ✓ Session persists after browser close ✓ User auto-logged in without re-entering credentials ✓ DB: users.remember_token generated |

**③ Business logic**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| AUTH-005 | [DT] Verify account lockout after 5 failed attempts (condition: attempts >= 5) | 1. Navigate to login page 2. Enter email: "user@test.com" 3. Enter wrong password 4. Click "Sign In" 5. Repeat steps 3-4 five times total | ✓ Attempts 1-4: Error "Invalid email or password" ✓ Attempt 5: Error "Account locked. Try again in 15 minutes" ✓ Attempt 6 with CORRECT password: still shows locked message ✓ DB: users.locked_until = now + 15 minutes ✓ DB: users.failed_attempts = 5 |

**④ Negative / Validation**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| AUTH-006 | [EP] Validate error for incorrect password (invalid partition) | 1. Navigate to login page 2. Enter email: "user@test.com" 3. Enter password: "WrongPassword" 4. Click "Sign In" | ✓ UI: Error "Invalid email or password" (generic for security) ✓ UI: User remains on login page ✓ UI: Password field cleared ✓ DB: users.failed_attempts incremented |
| AUTH-007 | [EP] Validate error for non-existent email (invalid partition) | 1. Navigate to login page 2. Enter email: "notexist@test.com" 3. Enter password: "AnyPass123" 4. Click "Sign In" | ✓ UI: Error "Invalid email or password" (SAME message for security) ✓ UI: User remains on login page ✓ No timing difference vs wrong password (prevent enumeration) |
| AUTH-008 | [EP] Validate error for empty email field (invalid partition: empty) | 1. Navigate to login page 2. Leave email field empty 3. Enter password: "AnyPass123" 4. Click "Sign In" | ✓ UI: Validation error below email field: "Email is required" ✓ Form NOT submitted to server |

**⑤ Boundary**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| AUTH-009 | [BVA] Verify password at minimum length boundary (8 characters) | 1. Navigate to login page 2. Enter email: "user@test.com" 3. Enter password: "Abcd123!" (exactly 8 chars) 4. Click "Sign In" | ✓ Login succeeds (assuming valid credentials) |
| AUTH-010 | [BVA] Verify password below minimum length (7 characters) | 1. Navigate to login page 2. Enter email: "user@test.com" 3. Enter password: "Abcd12!" (7 chars) 4. Click "Sign In" | ✓ Error: "Password must be at least 8 characters" |
| AUTH-011 | [BVA] Verify password at maximum length boundary (128 characters) | 1. Navigate to login page 2. Enter email: "user@test.com" 3. Enter password: 128-character valid string 4. Click "Sign In" | ✓ Login succeeds (assuming valid credentials) ✓ No truncation or error |

**⑧ Security**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| AUTH-012 | [EG] Verify login rejects SQL injection in email field | 1. Navigate to login page 2. Enter email: "' OR 1=1 --" 3. Enter password: "any" 4. Click "Sign In" | ✓ Login rejected: "Invalid email or password" ✓ No SQL error exposed ✓ No data leak ✓ DB: No unauthorized access |
| AUTH-013 | [EG] Verify login rejects XSS in email field | 1. Navigate to login page 2. Enter email: "<script>alert('xss')</script>" 3. Click "Sign In" | ✓ Input sanitized, no script execution ✓ Error: "Invalid email format" |

**Technique Coverage: EP(3) + BVA(3) + DT(1) + UC(2) + EG(2) + CL(1) = 12 TC, 6 techniques -> P1 requirement MET**

---

## 2. Sample: CRUD API (Create Order)

**Requirement:** REQ-ORDER-001 - Create shipping order via API
**Priority:** P1 (Critical)
**Techniques Applied:** EP(5) + BVA(4) + DT(2) + ST(1) + UC(2) + EG(4) + CL(2) = 20 TC, 7 techniques

### Group: POST /v1.0/orders (Create Order)

**② Happy path / Positive**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| ORD-CREATE-001 | [EP] Verify order creation with valid COD payment (valid partition: payment=COD) | 1. [Precondition] Auth with valid token, app 1 2. [Precondition] Warehouse WH-001 exists, active, carrier=GHN 3. [Request] POST /v1.0/orders 4. [Request] Body: { requestId: "ORD-001", warehouseCode: "WH-001", payment: { type: "cod", amount: 150000 }, receiver: { name: "Nguyen Van A", phone: "0901234567", address: "123 Le Loi, Q1, HCM" }, items: [{ name: "Product A", quantity: 2 }] } 5. [Verify] Check response 6. [Verify] Query DB | ✓ HTTP 201 ✓ statusCode: 2001 ✓ statusMessage: "Order creation is processing" ✓ data.orderCode: non-empty string (format: ORD-XXXXXXXX) ✓ DB orders: 1 record, status='pending', payment_type='cod', cod_amount=150000 ✓ DB order_items: 1 record, quantity=2 ✓ DB order_logs: 1 entry, action='CREATE' |
| ORD-CREATE-002 | [EP] Verify order creation with prepaid payment (valid partition: payment=prepaid) | 1. [Precondition] Same setup 2. [Request] POST /v1.0/orders with payment.type="prepaid", amount=0 3. [Verify] Check response + DB | ✓ HTTP 201 ✓ statusCode: 2001 ✓ DB orders: payment_type='prepaid', cod_amount=0 |
| ORD-CREATE-003 | [UC] Verify complete order lifecycle: create -> get -> verify | 1. POST /v1.0/orders -> get orderCode 2. GET /v1.0/orders/{orderCode} 3. Compare response data with creation payload | ✓ Step 1: HTTP 201, orderCode returned ✓ Step 2: HTTP 200, all fields match creation payload ✓ data.status = "pending" ✓ data.receiver.name = "Nguyen Van A" |

**③ Business logic**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| ORD-CREATE-004 | [DT] Verify COD amount required when payment_type=COD (condition: type=COD AND amount missing) | 1. POST /v1.0/orders with payment.type="cod", amount missing 2. [Verify] Check error | ✓ HTTP 400 ✓ statusCode: 4XXX ✓ statusMessage: "COD amount is required for COD payment" ✓ DB: No order created |
| ORD-CREATE-005 | [DT] Verify COD amount=0 accepted when payment_type=prepaid (condition: type=prepaid AND amount=0) | 1. POST /v1.0/orders with payment.type="prepaid", amount=0 2. [Verify] Check response | ✓ HTTP 201 ✓ DB orders: cod_amount=0 |

**④ Negative / Validation**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| ORD-CREATE-006 | [EP] Verify error when requestId is missing (invalid partition: required field absent) | 1. POST /v1.0/orders without requestId field 2. [Verify] Check error | ✓ HTTP 400 ✓ statusCode: 4005 ✓ statusMessage: "Request ID is required" ✓ DB: No order created |
| ORD-CREATE-007 | [EP] Verify error when warehouseCode invalid (invalid partition: FK not found) | 1. POST /v1.0/orders with warehouseCode="NONEXISTENT" 2. [Verify] Check error | ✓ HTTP 400 ✓ statusCode: 4XXX ✓ statusMessage: "Warehouse not found" ✓ DB: No order created |
| ORD-CREATE-008 | [EP] Verify error when receiver.phone format invalid (invalid partition: format) | 1. POST /v1.0/orders with receiver.phone="abc123" 2. [Verify] Check error | ✓ HTTP 400 ✓ statusCode: 4013 ✓ statusMessage: "Phone invalid" ✓ DB: No order created |

**⑤ Boundary**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| ORD-CREATE-009 | [BVA] Verify receiver.name at max boundary (255 characters) | 1. POST /v1.0/orders with receiver.name = "A" x 255 2. [Verify] Check response + DB | ✓ HTTP 201 ✓ DB: receiver_name length = 255 |
| ORD-CREATE-010 | [BVA] Verify receiver.name exceeds max (256 characters) | 1. POST /v1.0/orders with receiver.name = "A" x 256 2. [Verify] Check error | ✓ HTTP 400 ✓ statusMessage: "Receiver name too long" ✓ DB: No order created |
| ORD-CREATE-011 | [BVA] Verify COD amount at boundary 0 (minimum) | 1. POST /v1.0/orders with payment.type="cod", amount=0 2. [Verify] Check behavior | ✓ HTTP 201 (or 400 depending on business rule) ✓ Document actual behavior |
| ORD-CREATE-012 | [BVA] Verify COD amount negative (-1) below boundary | 1. POST /v1.0/orders with payment.amount=-1 2. [Verify] Check error | ✓ HTTP 400 ✓ statusMessage: "Amount must be >= 0" ✓ DB: No order created |

**⑥ Permission**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| ORD-CREATE-013 | [EP] Verify order creation rejected without auth token | 1. POST /v1.0/orders (no Authorization header) 2. [Verify] Check error | ✓ HTTP 401 ✓ statusMessage: "Unauthorized" ✓ DB: No order created |
| ORD-CREATE-014 | [EP] Verify cross-app warehouse access denied | 1. Auth as app 2 2. POST /v1.0/orders with warehouse belonging to app 1 3. [Verify] Check error | ✓ HTTP 403 or 400 ✓ Cannot create order with other app's warehouse ✓ DB: No order created |

**⑧ Security**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| ORD-CREATE-015 | [EG] Verify SQL injection in receiver.name rejected | 1. POST /v1.0/orders with receiver.name="'; DROP TABLE orders; --" 2. [Verify] Check response + DB | ✓ HTTP 400 (or 201 with sanitized name) ✓ No SQL error exposed ✓ DB: orders table intact |
| ORD-CREATE-016 | [EG] Verify XSS in receiver.address rejected | 1. POST /v1.0/orders with receiver.address="<script>alert(1)</script>" 2. [Verify] Check response | ✓ Input sanitized or rejected ✓ No script stored in DB |

**⑨ Edge case / Ad-hoc**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| ORD-CREATE-017 | [EG] Verify duplicate requestId returns idempotent result | 1. POST /v1.0/orders with requestId="DUP-001" -> success 2. POST /v1.0/orders with requestId="DUP-001" (same) -> check | ✓ Request 1: HTTP 201, order created ✓ Request 2: HTTP 200 (same orderCode) or HTTP 409 (duplicate) ✓ DB: EXACTLY 1 order with request_id='DUP-001' |
| ORD-CREATE-018 | [EG] Verify concurrent duplicate prevention (race condition) | 1. Prepare 2 identical POST /orders: requestId="RACE-001" 2. Launch BOTH in parallel (within 10ms) 3. Verify BOTH responses 4. Count DB records | ✓ 1 request: HTTP 201 (success) ✓ 1 request: HTTP 409 (duplicate) ✓ DB: EXACTLY 1 order ✓ No duplicate shipping created |
| ORD-CREATE-019 | [UC] Verify order with Vietnamese characters in all text fields | 1. POST /v1.0/orders with: receiver.name="Nguyen Thi Phuong Anh" receiver.address="123 Le Loi, Phuong Ben Nghe, Quan 1, TP.HCM" items[0].name="Ao thun cotton size L" 2. GET /v1.0/orders/{orderCode} | ✓ HTTP 201 ✓ All Vietnamese chars stored correctly ✓ GET response returns exact same text (no encoding issues) ✓ DB: UTF-8 stored correctly |
| ORD-CREATE-020 | [EG] Verify behavior when user submits order with emoji in note | 1. POST /v1.0/orders with note: "Giao truoc 5h chieu nhe! 🙏📦" 2. [Verify] Check response + DB | ✓ HTTP 201 (or 400 if emoji not allowed) ✓ Document actual behavior ✓ DB: emoji stored correctly (if accepted) |

---

## 3. Sample: Business Logic (Discount Calculation)

**Requirement:** REQ-205 - Apply tiered discount based on order total
**Priority:** P2 (High)
**Techniques Applied:** EP(3) + BVA(5) + DT(3) + EG(2) = 13 TC, 4 techniques

### Group: Discount Calculation

**Business Rules:**
- Order < $100: No discount
- Order $100 - $499: 10% discount
- Order $500 - $999: 15% discount
- Order >= $1000: 20% discount

**② Happy path**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| DISC-001 | [EP] Verify 10% discount for order $100-$499 (valid partition: tier 2) | 1. Add products totaling $150.00 2. Navigate to cart | ✓ Subtotal: $150.00 ✓ Discount (10%): -$15.00 ✓ Total: $135.00 |

**③ Business logic (Decision Table)**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| DISC-002 | [DT] Verify no discount when order < $100 (tier 1 condition) | 1. Add products totaling $50.00 2. Navigate to cart | ✓ Subtotal: $50.00 ✓ No discount line ✓ Total: $50.00 |
| DISC-003 | [DT] Verify 15% discount when $500-$999 (tier 3 condition) | 1. Add products totaling $600.00 2. Navigate to cart | ✓ Subtotal: $600.00 ✓ Discount (15%): -$90.00 ✓ Total: $510.00 |
| DISC-004 | [DT] Verify 20% discount when >= $1000 (tier 4 condition) | 1. Add products totaling $1200.00 2. Navigate to cart | ✓ Subtotal: $1200.00 ✓ Discount (20%): -$240.00 ✓ Total: $960.00 |

**⑤ Boundary**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| DISC-005 | [BVA] Verify boundary $99.99 (just below tier 2) | 1. Add products = $99.99 | ✓ No discount ✓ Total: $99.99 |
| DISC-006 | [BVA] Verify boundary $100.00 (exact tier 2 start) | 1. Add products = $100.00 | ✓ Discount 10%: -$10.00 ✓ Total: $90.00 |
| DISC-007 | [BVA] Verify boundary $499.99 (just below tier 3) | 1. Add products = $499.99 | ✓ Discount 10%: -$50.00 ✓ Total: $449.99 |
| DISC-008 | [BVA] Verify boundary $500.00 (exact tier 3 start) | 1. Add products = $500.00 | ✓ Discount 15%: -$75.00 ✓ Total: $425.00 |
| DISC-009 | [BVA] Verify boundary $999.99 vs $1000.00 (tier 3/4 boundary) | 1. Test $999.99 -> 15% 2. Test $1000.00 -> 20% | ✓ $999.99: Discount 15% = -$150.00, Total = $849.99 ✓ $1000.00: Discount 20% = -$200.00, Total = $800.00 |

**⑨ Edge case**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| DISC-010 | [EG] Verify discount recalculates when item removed (cross threshold) | 1. Cart = $120 (10% discount active) 2. Remove item worth $30 3. Cart = $90 (below threshold) | ✓ Discount line disappears ✓ Total: $90.00 (no discount) |
| DISC-011 | [EG] Verify discount with very large order ($999,999.99) | 1. Add products = $999,999.99 | ✓ Discount 20%: -$200,000.00 ✓ Total: $799,999.99 ✓ No overflow/rounding error |

---

## 4. Sample: Permission Matrix

**Requirement:** REQ-PERM-001 - Role-based access control for orders
**Priority:** P1

### Group: Order Permission

**Permission Matrix:**

| Action | Admin | Manager | User | Viewer | No Auth |
|--------|-------|---------|------|--------|---------|
| Create Order | ✓ | ✓ | ✓ | ✗ 403 | ✗ 401 |
| View Own Order | ✓ | ✓ | ✓ | ✓ | ✗ 401 |
| View All Orders | ✓ | ✓ | ✗ 403 | ✗ 403 | ✗ 401 |
| Cancel Order | ✓ | ✓ | Own only | ✗ 403 | ✗ 401 |
| Delete Order | ✓ | ✗ 403 | ✗ 403 | ✗ 403 | ✗ 401 |

**Test cases generated from matrix (moi ✗ = 1 test):**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| PERM-001 | [EP] Verify Viewer cannot create order (403) | 1. Auth as Viewer role 2. POST /v1.0/orders with valid data | ✓ HTTP 403 ✓ statusMessage: "Insufficient permissions" ✓ DB: No order created |
| PERM-002 | [EP] Verify no auth cannot create order (401) | 1. POST /v1.0/orders (no token) | ✓ HTTP 401 ✓ statusMessage: "Unauthorized" |
| PERM-003 | [EP] Verify User cannot view all orders (403) | 1. Auth as User role 2. GET /v1.0/orders (list all) | ✓ HTTP 403 or returns only own orders |
| PERM-004 | [EP] Verify User can cancel own order but not others | 1. Auth as User A 2. Cancel User A's order -> success 3. Cancel User B's order -> denied | ✓ Step 2: HTTP 200, order cancelled ✓ Step 3: HTTP 403 or 404 |
| PERM-005 | [EP] Verify Manager cannot delete order (403) | 1. Auth as Manager 2. DELETE /v1.0/orders/{id} | ✓ HTTP 403 ✓ DB: Order still exists |
| PERM-006 | [EG] Verify IDOR - User A cannot access User B's order by changing ID | 1. Auth as User A 2. Note User B's order ID 3. GET /v1.0/orders/{userB_orderId} | ✓ HTTP 403 or 404 ✓ No data leaked |

---

## 5. Sample: Concurrent / Race Condition

### Group: Concurrent Order Creation

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| RACE-001 | [EG] Verify duplicate prevention with 2 concurrent identical requests | 1. Prepare 2 identical POST /orders: requestId="RACE-001" 2. Launch BOTH in parallel threads (within 10ms) 3. Monitor DB transactions 4. Verify BOTH responses 5. Query: SELECT COUNT(*) FROM orders WHERE request_id='RACE-001' | ✓ Request A: HTTP 201, statusCode 2001 ✓ Request B: HTTP 409, duplicate error ✓ DB: EXACTLY 1 order (COUNT = 1) ✓ Unique constraint enforced |
| RACE-002 | [EG] Verify no overselling with concurrent purchases (stock=1) | 1. Product X: stock = 1 2. Prepare 2 purchase requests for Product X 3. Launch BOTH in parallel (within 10ms) 4. Verify BOTH responses 5. Query: SELECT stock FROM products WHERE id = X | ✓ 1 request: success (order created) ✓ 1 request: error "Out of stock" ✓ DB products: stock = 0 (NOT negative) ✓ DB orders: EXACTLY 1 order for Product X |
| RACE-003 | [EG] Verify concurrent state changes handled (2 webhooks for 1 order) | 1. Order status = 'picked' 2. Prepare webhook A: status -> 'delivering' 3. Prepare webhook B: status -> 'delivered' 4. Send BOTH within 10ms 5. Verify final state | ✓ State machine enforced: picked -> delivering -> delivered ✓ If both arrive simultaneously: one processed, one queued or rejected ✓ DB: final status is valid (no corrupted state) ✓ DB order_logs: transitions recorded correctly |

---

## 6. Sample: Webhook Testing

### Group: Inbound Carrier Webhooks

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| WH-IN-001 | [UC] Verify valid webhook updates order status successfully | 1. Order exists: status='picked' 2. POST /webhooks/carrier with valid payload: { orderId: "ORD-001", status: "delivering", timestamp: "2026-02-13T10:00:00Z" } 3. Include valid X-Signature header 4. Verify response + DB | ✓ HTTP 200 ✓ DB orders: status updated 'picked' -> 'delivering' ✓ DB order_logs: new entry (action='STATUS_UPDATE', source='webhook') ✓ Outbound webhook sent to client |
| WH-IN-002 | [EG] Verify webhook rejected without signature | 1. POST /webhooks/carrier (NO X-Signature header) 2. Body: valid payload | ✓ HTTP 401 ✓ DB: order status UNCHANGED ✓ Security log: "Missing signature" |
| WH-IN-003 | [EG] Verify webhook rejected with invalid signature | 1. POST /webhooks/carrier 2. X-Signature: "invalid_signature_abc123" 3. Body: valid payload | ✓ HTTP 401 ✓ DB: order status UNCHANGED ✓ Security log: "Invalid signature" |
| WH-IN-004 | [EG] Verify webhook replay attack prevented | 1. Capture valid webhook (signature + timestamp T) 2. Wait 5 minutes (past expiry window) 3. Replay exact same request | ✓ HTTP 401 (timestamp expired) ✓ DB: order status UNCHANGED |
| WH-IN-005 | [EG] Verify duplicate webhook handled (idempotent) | 1. Send valid webhook (status: delivering) -> success 2. Send SAME webhook again (exact same payload + signature) | ✓ First: HTTP 200, status updated ✓ Second: HTTP 200 (OK) but no duplicate update ✓ DB: order_logs has only 1 entry (not 2) |
| WH-IN-006 | [ST] Verify webhook with invalid state transition rejected | 1. Order status = 'pending' 2. Webhook arrives: status = 'delivered' (skip states) | ✓ Transition rejected or queued ✓ DB: status remains 'pending' or goes through valid path ✓ Log: "Invalid state transition attempted" |
| WH-IN-007 | [EG] Verify webhook with COD mismatch does NOT overwrite COD | 1. Order created: cod_amount = 150000 2. Webhook arrives: { money: 140000, status: "delivered" } 3. Verify DB after processing | ✓ DB orders.cod_amount = 150000 (UNCHANGED) ✓ Status updated to 'delivered' ✓ Alert: COD mismatch detected (150000 vs 140000) ✓ Reconciliation record created |

---

## 7. Sample: State Machine (Order Status)

### State Diagram

```
pending -> processing -> created -> picked -> delivering -> delivered
                |                                    |
                v                                    v
             failed                              returned
                |
                v
            cancelled
```

### Group: Order State Transitions

**Valid Transitions:**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| ORD-STATE-001 | [ST] Verify transition pending -> processing | 1. Order status='pending' 2. Queue worker picks job 3. Verify transition | ✓ Status: pending -> processing ✓ DB order_logs: new entry ✓ Timestamp recorded |
| ORD-STATE-002 | [ST] Verify transition processing -> created | 1. Order status='processing' 2. Carrier API returns success 3. Verify transition | ✓ Status: processing -> created ✓ DB: shipping_code populated ✓ DB order_logs: new entry |
| ORD-STATE-003 | [ST] Verify transition created -> picked | 1. Order status='created' 2. Carrier webhook: "picked" 3. Verify transition | ✓ Status: created -> picked ✓ DB order_logs: source='webhook' |
| ORD-STATE-004 | [ST] Verify transition picked -> delivering | ... | ✓ Status: picked -> delivering |
| ORD-STATE-005 | [ST] Verify transition delivering -> delivered | ... | ✓ Status: delivering -> delivered ✓ Terminal state reached |
| ORD-STATE-006 | [ST] Verify transition processing -> failed | 1. Order status='processing' 2. Carrier API returns error 3. Verify transition | ✓ Status: processing -> failed ✓ DB: error_message populated |

**Invalid Transitions:**

| STT | Test Objective | Test Steps | Expected Result |
|-----|----------------|------------|-----------------|
| ORD-STATE-007 | [ST] Verify INVALID: pending -> delivered (skip states) | 1. Order status='pending' 2. Attempt update to 'delivered' | ✓ Transition REJECTED ✓ Status remains 'pending' ✓ Error: "Invalid state transition" |
| ORD-STATE-008 | [ST] Verify INVALID: delivered -> pending (backward) | 1. Order status='delivered' (terminal) 2. Attempt update to 'pending' | ✓ Transition REJECTED ✓ Status remains 'delivered' ✓ Terminal state protected |
| ORD-STATE-009 | [ST] Verify INVALID: cancelled -> processing (from terminal) | 1. Order status='cancelled' (terminal) 2. Attempt any transition | ✓ Transition REJECTED ✓ Terminal state cannot change |

---

## 8. Sample: Coverage Summary Tables

### Table 1: Test Type Coverage

| Group Name | UI | FN | BL | NEG | EC | PM | DI | CN | IT | SEC | Total |
|------------|----|----|----|----|-----|----|----|----|----|-----|-------|
| Login Screen (P1) | 1 | 3 | 1 | 3 | - | - | - | - | - | 2 | 10 |
| POST /orders (P1) | - | 3 | 2 | 3 | 4 | 2 | - | 2 | - | 2 | 18 |
| Discount Calc (P2) | - | 1 | 3 | - | 5 | - | - | - | - | - | 9 |
| Permissions (P1) | - | - | - | 4 | - | 6 | - | - | - | - | 10 |
| Webhooks (P1) | - | 1 | - | 1 | - | - | 1 | 1 | 1 | 3 | 8 |
| Order States (P1) | - | 6 | - | 3 | - | - | - | - | - | - | 9 |
| **Total** | **1** | **14** | **6** | **14** | **9** | **8** | **1** | **3** | **1** | **7** | **64** |

### Table 2: Technique Coverage

| Group Name | EP | BVA | DT | ST | UC | PW | EG | CL | EXP | Total | Min Req | Status |
|------------|----|----|----|----|----|----|----|----|-----|-------|---------|--------|
| Login (P1) | 3 | 3 | 1 | - | 2 | - | 2 | 1 | - | 12 | ≥6 | ✓ PASS (6 tech) |
| POST /orders (P1) | 5 | 4 | 2 | - | 2 | - | 4 | 2 | - | 19 | ≥6 | ✓ PASS (6 tech) |
| Discount (P2) | 3 | 5 | 3 | - | - | - | 2 | - | - | 13 | ≥4 | ✓ PASS (4 tech) |
| Permissions (P1) | 5 | - | - | - | - | - | 1 | - | - | 6 | ≥6 | ⚠️ FAIL (2 tech) |
| Webhooks (P1) | - | - | - | 1 | 1 | - | 4 | - | - | 6 | ≥6 | ⚠️ FAIL (3 tech) |
| States (P1) | - | - | - | 9 | - | - | - | - | - | 9 | ≥6 | ⚠️ FAIL (1 tech) |
| **Total** | **16** | **12** | **6** | **10** | **5** | **0** | **13** | **3** | **0** | **65** | | |

**Gaps Identified:**
- Permissions group: Need to add BVA, DT, ST, UC, EG tests -> toi thieu 4 techniques nua
- Webhooks group: Need to add EP, BVA, DT, UC, CL tests -> toi thieu 3 techniques nua
- States group: Need to add EP, BVA, DT, UC, EG tests -> toi thieu 5 techniques nua
- **Action:** Quay lai Step 5 bo sung test cases cho cac nhom nay

### Technique Coverage Summary (Per Feature)

```
┌──────────────────────────────────────────────────────────────────────┐
│              TEST DESIGN TECHNIQUE COVERAGE SUMMARY                   │
├──────────────────────────────────────────────────────────────────────┤
│ Feature: Login Screen              Priority: P1                      │
├──────────────────────────────────────────────────────────────────────┤
│ Technique          │ Applied? │ # Test Cases │ Notes                 │
│────────────────────│──────────│──────────────│───────────────────────│
│ Equivalence Part.  │ ✓ Yes    │ 3            │ Valid + invalid email  │
│ Boundary Value     │ ✓ Yes    │ 3            │ Password length        │
│ Decision Table     │ ✓ Yes    │ 1            │ Lockout after 5 fails  │
│ State Transition   │ ☐ N/A    │ -            │ No state in login      │
│ Use Case           │ ✓ Yes    │ 2            │ Main + remember me     │
│ Pairwise           │ ☐ N/A    │ -            │ <3 parameters          │
│ Error Guessing     │ ✓ Yes    │ 2            │ SQL injection, XSS     │
│ Checklist-Based    │ ✓ Yes    │ 1            │ Password masking       │
│ Exploratory        │ ☐ Skip   │ -            │ Could add session      │
├──────────────────────────────────────────────────────────────────────┤
│ TOTAL              │ 6/9      │ 12 TC        │                       │
│ Min Required (P1)  │ ≥6       │              │ ✓ PASS                │
└──────────────────────────────────────────────────────────────────────┘
```

---

**End of Samples Reference**
