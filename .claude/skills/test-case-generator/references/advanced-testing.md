# TD REFERENCE: ADVANCED TESTING

**Vai tro:** File tham khao khi Test Case Generator gap cac scenario phuc tap.
**Load khi:** Spec co concurrent, multi-carrier, financial, state machine, OWASP, infrastructure failure.

**LƯU Ý NGÔN NGỮ:** ví dụ dưới đây bằng tiếng Anh chỉ minh họa pattern — TC thật phải viết bằng tiếng Việt (xem `writing-format.md` 7.0), giữ nguyên tiếng Anh cho endpoint/field/error code/HTTP status lấy từ spec.

---

## Table of Contents

1. [Business Flow Testing](#1-business-flow-testing)
2. [Logic Flow Testing](#2-logic-flow-testing)
3. [State Machine Testing](#3-state-machine-testing)
4. [Race Condition & Concurrent Testing](#4-race-condition--concurrent-testing)
5. [Retry Mechanism Testing](#5-retry-mechanism-testing)
6. [Integration Testing](#6-integration-testing)
7. [Carrier-Specific Testing](#7-carrier-specific-testing)
8. [Financial Data Testing](#8-financial-data-testing)
9. [Permission & Authorization Testing (Deep)](#9-permission--authorization-testing-deep)
10. [Exploratory & Ad-hoc Testing](#10-exploratory--ad-hoc-testing)
11. [Abuse & Cheating Testing](#11-abuse--cheating-testing)
12. [Data Integrity Testing](#12-data-integrity-testing)
13. [OWASP API Security Top 10](#13-owasp-api-security-top-10)
14. [Infrastructure Failure Testing](#14-infrastructure-failure-testing)
15. [Network & Timeout Scenario Testing](#15-network--timeout-scenario-testing)
16. [Bug Hypothesis to Test Case Mapping](#16-bug-hypothesis-to-test-case-mapping)
17. [Coverage Gap Analysis Checklist](#17-coverage-gap-analysis-checklist)

---

## 1. Business Flow Testing

**Muc dich:** Test toan bo business flow tu dau den cuoi.

### Cach thiet ke

1. Ve lai toan bo flow tu spec (start -> end)
2. Xac dinh: Main flow + Alternative flows + Exception flows
3. Moi unique path = 1 test case `[UC]`

### Template

```
TC: [UC] Verify complete [flow name] - main success path

Steps:
1. [Start] User/System initiates flow
2. [Step] Action 1 -> verify intermediate state
3. [Step] Action 2 -> verify intermediate state
...
N. [End] Flow completes -> verify final state

Expected:
✓ Each step: correct intermediate state
✓ Final state: [expected end state]
✓ DB: all records created/updated correctly through entire flow
✓ Side effects: all notifications/webhooks triggered at correct points
```

### Checklist

```
□ Main flow (happy path) E2E                               [UC]
□ Moi alternative flow (branching points)                   [UC]
□ Moi exception flow (error recovery)                       [UC]
□ Flow bi interrupted giua chung (user cancel, timeout)     [EG]
□ Flow voi data edge cases (empty, max, special)            [EG]
□ Cross-feature flow (feature A -> feature B)               [UC]
□ Reverse flow (undo, rollback, return)                     [UC]
```

---

## 2. Logic Flow Testing

**Muc dich:** Test tat ca logic branches, conditions, calculations.

### Cach thiet ke

**Tu IF/THEN/ELSE:**
```
Logic: IF condition THEN result_A ELSE result_B

Test cases:
1. [DT] condition = TRUE  -> verify result_A
2. [DT] condition = FALSE -> verify result_B
```

**Tu multi-condition rules:**
```
Logic: IF cond1 AND cond2 THEN result_A
       ELIF cond1 AND NOT cond2 THEN result_B
       ELIF NOT cond1 AND cond2 THEN result_C
       ELSE result_D

Decision Table:
| cond1 | cond2 | Expected |
|-------|-------|----------|
| T     | T     | result_A |
| T     | F     | result_B |
| F     | T     | result_C |
| F     | F     | result_D |

-> 4 test cases [DT]
```

**Tu calculations:**
```
Formula: total = subtotal * (1 - discount_rate) + shipping_fee

Test cases [EP] + [BVA]:
1. Normal values: subtotal=100, discount=10%, shipping=20 -> total=110
2. Zero discount: subtotal=100, discount=0%, shipping=20 -> total=120
3. Max discount: subtotal=100, discount=100%, shipping=20 -> total=20
4. Zero subtotal: subtotal=0, discount=10%, shipping=20 -> total=20
5. Boundary: subtotal at discount threshold
```

### Checklist

```
□ Moi IF/THEN/ELSE -> 2+ TC (true + false)                [DT]
□ Moi multi-condition rule -> decision table                [DT]
□ Moi calculation -> normal + boundary + edge values        [EP][BVA]
□ Moi eligibility criteria -> du dieu kien + thieu tung DK  [DT]
□ Nested conditions -> test inner + outer                   [DT]
□ Short-circuit logic -> verify evaluation order            [DT]
□ Rounding logic -> verify precision (0.5 round up/down?)   [BVA]
```

---

## 3. State Machine Testing

**Muc dich:** Test tat ca state transitions.

### Cach thiet ke

1. List tat ca states tu spec
2. List tat ca valid transitions (from -> to)
3. Xac dinh invalid transitions (should be rejected)
4. Xac dinh terminal states (cannot transition out)

### Template

**Valid transition:**
```
TC: [ST] Verify order transition from {state_A} to {state_B}

Steps:
1. Create/setup record with status = '{state_A}'
2. Trigger transition action (API call, webhook, event)
3. Verify transition allowed

Expected:
✓ Status updated: {state_A} -> {state_B}
✓ DB: status_logs new entry (from='{state_A}', to='{state_B}')
✓ Timestamp recorded
✓ Side effects triggered (webhook, notification)
```

**Invalid transition:**
```
TC: [ST] Verify INVALID transition from {state_A} directly to {state_C} is rejected

Steps:
1. Record status = '{state_A}'
2. Attempt to update directly to '{state_C}' (skipping state_B)
3. Verify rejection

Expected:
✓ Transition REJECTED
✓ Status remains '{state_A}' (unchanged)
✓ Error: "Invalid state transition"
✓ DB: status_logs records attempted but rejected transition
```

### Checklist

```
□ Tat ca valid transitions tested (it nhat 1 lan moi transition)    [ST]
□ Invalid transition attempts rejected (3-5 critical cases)         [ST]
□ Terminal states cannot change (delivered, cancelled, returned)    [ST]
□ No backward transitions (unless spec allows)                     [ST]
□ Concurrent state changes handled (lock or version)               [ST][EG]
□ Entry/exit actions executed correctly                            [ST]
□ Tat ca transitions logged for audit                              [ST]
□ Out-of-order events handled (webhook arrive out of sequence)     [EG]
```

---

## 4. Race Condition & Concurrent Testing

**Muc dich:** Test scenarios nhieu requests dong thoi.

### RULES QUAN TRONG

**DO:**
```
✅ Dung true parallel execution (multi-threading, async requests)
✅ Launch requests trong tight window (< 10ms cho race conditions)
✅ Specify exact timing: "simultaneously", "within 10ms", "< 100ms apart"
✅ Test voi actual concurrent threads, KHONG sequential
✅ Monitor database transaction isolation level
✅ Verify BOTH requests' responses (success AND failure)
✅ Count exact records in DB sau concurrent test
✅ Tools: JMeter, k6, Locust, hoac custom multi-threaded scripts
```

**DON'T:**
```
❌ Execute "concurrent" tests sequentially (request 1 -> wait -> request 2)
❌ Assume "fast sequential" = concurrent
❌ Skip timing verification
❌ Only check 1 request's result
❌ Forget to verify database final state
```

### Template

```
TC: [EG] Verify duplicate prevention with concurrent requests

Steps:
1. Prepare 2 identical POST /orders requests with requestId="RACE-001"
2. Launch BOTH requests in parallel threads (within 10ms)
3. Monitor database transaction log
4. Verify responses for BOTH requests
5. Query DB: SELECT COUNT(*) FROM orders WHERE request_id='RACE-001'

Expected:
✓ Request A: HTTP 200/201, statusCode 2001 (success)
✓ Request B: HTTP 400/409, duplicate error
✓ DB: EXACTLY 1 order (COUNT = 1)
✓ Unique constraint enforced under race condition
```

**SAI (Sequential, KHONG phai concurrent):**
```
❌ Steps:
1. POST /orders requestId="SAME" -> wait for response
2. POST /orders requestId="SAME" -> check duplicate

-> Day la sequential, KHONG catch duoc race conditions
```

### Scenarios can test

```
□ Duplicate creation (same requestId/unique field)          [EG]
□ Overselling (concurrent purchases, stock=1)               [EG]
□ Double payment/refund (concurrent financial transactions)  [EG]
□ Concurrent state changes (2 webhooks cho 1 order)         [EG][ST]
□ Double-click prevention (UI submit twice)                 [EG]
□ Concurrent file upload (same filename)                    [EG]
□ Session conflicts (login/logout dong thoi)                [EG]
□ Queue job duplication (same job picked twice)             [EG]
```

---

## 5. Retry Mechanism Testing

**Muc dich:** Test retry logic khi co failure.

### Template

```
TC: Verify retry on carrier API timeout

Steps:
1. Order job picked from queue
2. Worker calls carrier API
3. Simulate: carrier timeout after 30 seconds
4. Log timestamps of each attempt
5. Verify retry triggered

Expected:
✓ Attempt 1: timeout at ~30s
✓ retry_count: 0 -> 1
✓ Retry delay: {expected backoff} seconds
✓ Attempt 2: request sent to carrier
```

### Checklist

```
□ Success on attempt 1 (no retry needed)                    [UC]
□ Fail attempt 1, success attempt 2                         [EG]
□ Fail attempt 1-2, success attempt 3                       [EG]
□ Fail all attempts (max retries exhausted)                 [EG]
□ Verify retry count increments correctly                   [CL]
□ Verify backoff timing (linear or exponential)             [BVA]
□ Verify max retry limit enforced                           [BVA]
□ Verify Dead Letter Queue after max retries                [EG]
□ Verify no duplicate side effects across retries           [EG]
□ Verify idempotency of retried operations                  [EG]
```

### Timing Verification

```
Linear backoff (5s intervals):
  Attempt 1: T+0s
  Attempt 2: T+5s
  Attempt 3: T+10s

Exponential backoff (base 2s):
  Attempt 1: T+0s
  Attempt 2: T+2s
  Attempt 3: T+4s
  Attempt 4: T+8s

Verify: timestamp(attempt_N) - timestamp(attempt_N-1) = expected_interval ± tolerance
```

---

## 6. Integration Testing

**Muc dich:** Test giao tiep giua cac systems.

### 6.1 API-to-API Integration

```
□ Request payload sent correctly to external service        [UC]
□ Response parsed correctly from external service           [UC]
□ Timeout scenarios (before and after processing)           [EG]
□ Retry mechanism on failure                                [EG]
□ Error propagation (external error -> internal handling)   [EG]
□ Circuit breaker behavior (if applicable)                  [EG]
```

### 6.2 Queue Integration

```
□ Job pushed to queue correctly                             [UC]
□ Job payload structure correct                             [CL]
□ Queue unavailable -> graceful handling                    [EG]
□ Queue full -> graceful handling                           [EG]
□ Worker picks job correctly                                [UC]
□ Job retry after worker crash                              [EG]
□ Dead Letter Queue for failed jobs                         [EG]
```

### 6.3 Webhook Integration

> **Chi tiet webhook testing (checklists, vi du, security):** Xem `TD_Reference_API.md` Section 14
> Phan nay chi luu y ve **integration context** cua webhooks.

**Integration-specific concerns:**
```
□ Webhook delivery order co match voi business flow?        [ST]
□ Out-of-order webhooks xu ly dung (event B truoc event A)? [EG]
□ Webhook failure co anh huong den integration flow?        [EG]
□ Carrier-specific webhook format khac nhau xu ly dung?     [EP]
```

### Integration Test Template

```
TC: [UC] Verify order creation triggers carrier API call

Steps:
1. POST /v1.0/orders with valid data
2. Order saved to DB (status='pending')
3. Queue job created
4. Worker picks job (status -> 'processing')
5. Worker calls carrier API: POST {carrier_url}/CreateOrder
6. Monitor network traffic
7. Carrier responds: 201, {shippingCode: "GHN123"}
8. Verify system updates order

Expected:
✓ Network: POST to carrier API confirmed
✓ Request payload: correct format per carrier spec
✓ Response received: 201, shippingCode present
✓ DB orders: status='created', shipping_code='GHN123'
✓ DB order_logs: 2 entries (pending, created)
✓ Outbound webhook triggered to client
```

---

## 7. Carrier-Specific Testing

**Muc dich:** Xu ly behaviors khac nhau giua cac carriers.

### Carrier Behavior Matrix

| Feature | GHN | Lex | Viettel Post | 247 |
|---------|-----|-----|--------------|-----|
| Create Warehouse | ✅ Call API | ✅ Call API | ❌ Local only (NO API) | ✅ Call API |
| Update Warehouse | ❌ NOT SUPPORTED (error 4022) | ✅ Full support | ⚠️ Local only | ⚠️ Limited (contactName + phone) |
| Get Tracking | ✅ Can call API | ✅ Can call API | ❌ Local DB only | ✅ Can call API |
| Get Final Fee | ✅ Call GetFee API | ✅ Call API | ❌ From webhook MONEY_TOTAL | ✅ Call Tracking API |

### Rules

**MỌI test case cho carrier-specific feature PHAI:**
- Chi ro carrier trong TC (hoac "All" neu apply tat ca)
- Verify behavior dung theo matrix tren

**VTP (Viettel Post) - CRITICAL:**
```
□ Create warehouse: PHAI verify NO external API calls
□ Update warehouse: PHAI verify NO external API calls
□ Tracking: PHAI verify NO external API calls (local DB only)
□ Final fee: CHI tu webhook MONEY_TOTAL, KHONG API call
□ Expected Result PHAI include: "Network monitor: NO calls to VTP API"
□ Neu VTP API bi goi -> CRITICAL BUG (vi pham spec)
```

**GHN:**
```
□ Update warehouse PHAI return error 4022 (not supported)
□ Neu return 2000 (success) -> BUG (silent fail)
```

**247:**
```
□ Update warehouse: CHI contactName va phone duoc update
□ Neu name/email/address updated -> BUG (should ignore or error)
```

**Lex:**
```
□ Full feature support, khong co special limitations
```

### Template

```
TC: [EP] Verify VTP warehouse creation does NOT call external API

Carrier: Viettel Post
Priority: P1

Steps:
1. POST /v1.0/warehouses with carrier="Viettel Post"
2. Monitor ALL network traffic
3. Check application logs
4. Verify database state

Expected:
✓ statusCode: 2000 (warehouse created)
✓ DB warehouses: 1 record
✓ DB: carrier_warehouse_id = NULL
✓ Network Monitor: NO calls to VTP API endpoints
✓ Application logs: "VTP local creation" or similar
✓ Per spec: "VTP doesn't provide create warehouse API"

Note: Neu co API call den VTP -> CRITICAL BUG
```

---

## 8. Financial Data Testing

**Muc dich:** Bao ve financial data integrity.

### COD Amount Immutability Rules

```
CRITICAL: COD amount set tai order creation KHONG BAO GIO thay doi.

□ COD amount tu request -> stored correctly in DB              [EP]
□ COD amount passed correctly to carrier API                   [UC]
□ Webhook voi different money amount -> COD UNCHANGED          [EG]
□ COD vs Shipping Fee clearly distinguished (separate fields)  [EP]
□ Reconciliation data available (expected vs actual)           [CL]
□ Negative COD rejected (amount >= 0)                          [BVA]
□ Very large COD tested (business limit validation)            [BVA]
□ COD = 0 (no collection) -> handled correctly                 [BVA]
```

### Template

```
TC: [EG] Verify COD amount NOT overwritten by webhook

Steps:
1. Create order: cod_amount = 150000
2. Verify DB: orders.cod_amount = 150000
3. Worker calls carrier with COD = 150000
4. Carrier webhook arrives: {money: 140000} (mismatch 10000 VND)
5. Webhook processed
6. Verify DB after webhook

Expected:
✓ DB orders.cod_amount = 150000 (UNCHANGED)
✓ COD integrity maintained
✓ Alert triggered: COD mismatch 10000 VND
✓ final_fee can be different (shipping fee, not COD)
✓ Reconciliation: expected 150000, carrier reported 140000

Impact if failed: Financial loss 10000 VND per order
```

### Fee Distinction

```
Required in Expected Result cho financial tests:
✓ cod_amount = 150000 (tien thu ho khach hang)
✓ estimated_fee = 25000 (phi van chuyen uoc tinh)
✓ final_fee = 27500 (phi van chuyen thuc te)
✓ 3 gia tri doc lap, KHONG confusion
```

---

## 9. Permission & Authorization Testing (Deep)

**Muc dich:** Test access control toan dien.

### 9.1 Role-Based Access Control (RBAC)

```
Voi moi role x resource combination:
□ Admin -> full access (CRUD all)                           [EP]
□ User -> own resources only                                [EP]
□ Viewer -> read only                                       [EP]
□ Guest/Anonymous -> public resources only                  [EP]
□ Disabled user -> no access                                [EP]
```

### 9.2 Permission Test Matrix Template

| Resource | Action | Admin | Manager | User | Viewer | Guest |
|----------|--------|-------|---------|------|--------|-------|
| Orders | Create | ✓ | ✓ | ✓ | ✗ | ✗ |
| Orders | Read own | ✓ | ✓ | ✓ | ✓ | ✗ |
| Orders | Read all | ✓ | ✓ | ✗ | ✗ | ✗ |
| Orders | Update | ✓ | ✓ | Own only | ✗ | ✗ |
| Orders | Delete | ✓ | ✗ | ✗ | ✗ | ✗ |
| Settings | Read | ✓ | ✓ | ✗ | ✗ | ✗ |
| Settings | Update | ✓ | ✗ | ✗ | ✗ | ✗ |

**Moi ✗ trong matrix = 1 negative test case (verify 403/404)**
**Moi ✓ = 1 positive test case (verify access granted)**

### 9.3 Multi-Tenant Isolation

```
□ App 1 KHONG the truy cap data cua App 2                  [EP]
□ List API chi tra records cua app hien tai                  [EP]
□ Create voi foreign applicationId -> rejected               [EG]
□ Direct object reference (IDOR) -> 403/404                  [EG]
□ Admin override: super admin co the truy cap cross-app?     [EP]
```

### 9.4 Vulnerability Tests

```
□ IDOR: Thay doi resource ID de truy cap resource nguoi khac  [EG]
□ Privilege escalation: User tu nang quyen len Admin           [EG]
□ Forced browsing: Truy cap endpoint khong co trong menu       [EG]
□ Mass assignment: Gui them field role=admin trong request      [EG]
□ Token reuse after logout                                     [EG]
□ Permission after role change (dang login roi bi ha quyen)    [EG]
```

---

## 10. Exploratory & Ad-hoc Testing

**Muc dich:** Discover unexpected issues.

### Session Template

```
SESSION: {Name} Tour
Charter: {Clear objective - what to explore}
Duration: {60-120 minutes}
Focus Risks: {RISK-XX, RISK-YY}

Test Ideas:
1. {Specific scenario 1}
2. {Specific scenario 2}
...
10. {Specific scenario 10}

Expected Findings:
- {Bug type 1}
- {Bug type 2}

Report:
- Bugs found: {with repro steps}
- Questions: {unclear behaviors}
- Observations: {usability, performance}
- Coverage: {areas explored}
```

### Tour Types

| Tour | Focus | Khi nao dung |
|------|-------|--------------|
| **Money Tour** | Revenue-critical features (payments, fees, COD) | Financial features |
| **Saboteur Tour** | Try to break system (security, abuse, exploits) | P1/P2 features |
| **FedEx Tour** | Follow data flow end-to-end | Integration features |
| **Bad Neighborhood** | Historical bug areas, complex logic | Areas voi nhieu bug truoc |
| **Back Alley** | Rarely used features, edge configs | P3/P4 features |
| **Guidebook Tour** | Follow documentation exactly | New features |

### API-Specific Ad-hoc Scenarios

```
□ Send request voi Content-Type: text/xml (thay vi json)
□ Send request voi body la empty object {}
□ Send request voi array thay vi object (hoac nguoc lai)
□ Send request voi Unicode characters trong field names
□ Send request voi very deep nested objects
□ Send concurrent requests voi slightly different data
□ Send request ngay sau khi server restart
□ Send request voi expired + valid token dong thoi
```

---

## 11. Abuse & Cheating Testing

**Muc dich:** Verify system resists malicious behavior.

### Categories

| Category | Test Scenarios |
|----------|---------------|
| **Gaming the System** | Reuse promo codes, stack discounts, fake referrals, exploit free trials |
| **Resource Abuse** | API flooding, large payloads, rapid submissions |
| **Financial Fraud** | Double refund, price manipulation, fake payments |
| **Inventory Manipulation** | Cart hoarding, overselling exploit, stock locking |
| **Data Scraping** | Rapid sequential requests, bot patterns |
| **Bot/Automation** | Scripted form submissions, automated purchases |

### Checklist

```
□ Rate limiting enforced (exceed limit -> 429)              [BVA]
□ Large payload attack (> 1MB body) -> rejected             [BVA]
□ Rapid repeated submissions -> deduplicated                [EG]
□ Promo code reuse -> rejected on second use                [EG]
□ Promo code stacking (multiple codes) -> rules enforced    [DT]
□ Price tampering (modify amount in request) -> rejected     [EG]
□ Stock quantity manipulation -> not oversold                [EG]
□ Referral self-refer -> rejected                           [EG]
□ Free trial abuse (re-register) -> detected                [EG]
```

---

## 12. Data Integrity Testing

**Muc dich:** Ensure data accuracy va consistency.

### Integrity Types

| Type | Test Focus | Test Count |
|------|-----------|------------|
| **Entity Integrity** | Primary keys: uniqueness, NOT NULL, auto-increment | 3 tests/table |
| **Referential Integrity** | FK constraints: cascade, orphan prevention, update | 4 tests/FK |
| **Domain Integrity** | Data types, check constraints, enum values | 2-3 tests/constraint |
| **User-Defined Integrity** | Custom business rules at DB level | 2-4 tests/rule |
| **Transaction Integrity** | ACID properties for multi-step operations | 4 tests (Atomicity, Consistency, Isolation, Durability) |
| **Cross-System** | DB -> API -> UI consistency, cache sync | 3 tests/integration |

### ACID Testing

```
Atomicity: Multi-step operation fails midway -> ALL steps rolled back
Consistency: DB constraints maintained before and after transaction
Isolation: Concurrent transactions don't interfere
Durability: Committed data survives system crash/restart
```

### Checklist

```
□ Unique constraints enforced (duplicate -> error)          [EP]
□ FK constraints enforced (orphan -> error)                 [EP]
□ NOT NULL constraints enforced (null -> error)             [EP]
□ Check constraints enforced (invalid value -> error)       [EP]
□ Cascade delete/update works correctly                     [UC]
□ Transaction rollback on partial failure                   [EG]
□ Data consistent across DB, API response, and UI           [UC]
□ Soft-delete preserves data (is_deleted flag)              [EP]
□ Audit trail maintained (created_at, updated_at, actor)    [CL]
```

---

## 13. OWASP API Security Top 10

**Muc dich:** Dam bao P1 features duoc test theo OWASP API Security Top 10.

> **Chi tiet security checklists (auth, injection, rate limiting, headers):** Xem `TD_Reference_API.md` Section 8
> Phan nay chi liet ke **10 vulnerability categories** va cach ap dung.

| # | Vulnerability | Test Focus | Vi du |
|---|--------------|-----------|-------|
| API1 | **BOLA** (Broken Object Level Auth) | Thay ID de truy cap resource nguoi khac | GET /orders/{other_user_id} -> 403/404 |
| API2 | **Broken Authentication** | Brute force, weak tokens | Login rate limit, token rotation |
| API3 | **Broken Object Property Auth** | Mass assignment, sensitive field exposure | Send role=admin trong body -> ignored |
| API4 | **Unrestricted Resource Consumption** | Rate limiting, large payloads | 1MB body -> rejected, rate limit -> 429 |
| API5 | **BFLA** (Broken Function Level Auth) | User goi admin endpoints | User call DELETE /users -> 403 |
| API6 | **Unrestricted Sensitive Flow Access** | Abuse business flows | Bot automated purchase, mass coupon use |
| API7 | **SSRF** (Server Side Request Forgery) | URL field voi internal IP | URL = "http://localhost:8080" -> rejected |
| API8 | **Security Misconfiguration** | Verbose errors, default creds | Stack trace in 500 response -> BUG |
| API9 | **Improper Inventory Management** | Old API versions accessible | /v1/endpoint deprecated nhung van hoat dong |
| API10 | **Unsafe API Consumption** | Trust third-party blindly | Carrier response co malicious data -> sanitized |

**Rule:** Voi moi P1 feature, review bang nay va tao it nhat **1 TC cho moi vulnerability applicable**.

---

## 14. Infrastructure Failure Testing

**Muc dich:** Test system behavior khi infrastructure gaps.

### 14.1 Queue System Failure

```
TC: [EG] Verify graceful handling when queue is unavailable

Steps:
1. POST /v1.0/orders with valid data
2. Simulate: Queue service unavailable
3. Verify system behavior

Expected:
✓ HTTP 500 or 503 (NOT silent success)
✓ DB: order created with status='failed' or 'queue_error'
✓ Retry mechanism triggered
✓ Alert/notification sent to operations team
✓ Order NOT marked as success if queue push failed
```

### 14.2 Carrier API Failure

```
-- CRITICAL: Timeout AFTER carrier already processed --

TC: [EG] Verify handling when carrier timeout AFTER processing

Steps:
1. Order job picked from queue
2. Worker calls carrier CreateOrder API
3. Carrier RECEIVES and CREATES order successfully
4. BUT response times out (network issue on return)
5. Worker marks as timeout/failed
6. Retry mechanism creates SECOND order at carrier

Expected (Correct behavior):
✓ System detects potential duplicate
✓ Check with carrier before retry (GetOrder or dedup check)
✓ DB reflects actual carrier state
✓ No duplicate orders at carrier

Bug scenario (if not handled):
✗ Carrier has 2 orders for same request
✗ Customer charged/shipped twice
✗ Financial loss
```

### 14.3 Database Failure

```
□ DB connection lost during transaction -> rollback          [EG]
□ DB timeout during write -> no partial write                [EG]
□ DB read replica lag -> stale data handling                  [EG]
□ DB disk full -> graceful error (not crash)                  [EG]
```

### 14.4 Cache Failure

```
□ Cache unavailable -> fallback to DB (slower but works)     [EG]
□ Cache stale -> data inconsistency handling                 [EG]
□ Cache full -> eviction policy works correctly               [EG]
```

---

## 15. Network & Timeout Scenario Testing

### Timeout Scenario Matrix

| Scenario | Timeout | What Happens | Test Focus |
|----------|---------|-------------|------------|
| Client -> Server | Client timeout | Server may still process | Idempotency |
| Server -> Carrier | 30s | Carrier may have processed | Duplicate prevention |
| Server -> Queue | 5s | Order may be orphaned | Retry/cleanup |
| Carrier -> Webhook | Carrier timeout | Webhook not received | Retry from carrier |

### Checklist

```
□ Client timeout BEFORE server processes -> no side effect   [EG]
□ Client timeout AFTER server processes -> idempotent retry  [EG]
□ Server timeout BEFORE carrier processes -> safe retry      [EG]
□ Server timeout AFTER carrier processes -> CRITICAL: check  [EG]
□ Slow network (high latency) -> UI/API still functional     [EG]
□ Network disconnect mid-request -> proper error handling    [EG]
□ DNS failure -> graceful error message                      [EG]
□ SSL certificate expired -> connection refused (not bypass) [EG]
```

### Timeout Test Template

```
TC: [EG] Verify carrier API timeout after 30 seconds

Steps:
1. Worker picks order job from queue
2. Worker calls carrier CreateOrder API
3. Simulate: carrier takes 31 seconds to respond
4. Log timestamp: request sent
5. Log timestamp: timeout triggered
6. Verify retry mechanism

Expected:
✓ Timeout triggers at ~30 seconds (± 2s tolerance)
✓ retry_count increments from 0 to 1
✓ Retry request sent to carrier
✓ Timing: timeout at 30s ± 2s
```

---

## 16. Bug Hypothesis to Test Case Mapping

**Muc dich:** Moi bug hypothesis tu Risk Analysis PHAI co test case.

### Mapping Template

| Bug Hypothesis ID | Description | Test Case ID | Test Approach | Status |
|-------------------|-------------|-------------|---------------|--------|
| BH-01 | Concurrent requestId creates duplicate | BUG-HUNT-001 | True parallel threads | Mapped |
| BH-02 | COD overwritten by webhook | BUG-HUNT-002 | Webhook with different amount | Mapped |
| BH-03 | Retry creates duplicate at carrier | BUG-HUNT-003 | Simulate timeout after process | Mapped |
| BH-04 | Token expires mid-flow | BUG-HUNT-004 | Long-running operation | Mapped |

### Bug Hypothesis Test Template

```
TC: BUG-HUNT-001
Priority: P1
Risk: RISK-01
Bug Hypothesis: #1 from Risk List

Objective: [EG] Test bug hypothesis - Double order for same requestId

Steps (exact reproduction):
1. Prepare 2 identical POST /orders: requestId="BUG-RACE-001"
2. Launch TRUE parallel (multi-threaded, < 5ms apart)
3. Monitor DB transaction isolation
4. Verify unique constraint

Expected (Correct behavior):
✓ 1 request: success (statusCode 2001)
✓ 1 request: duplicate error
✓ DB: EXACTLY 1 order

Bug Scenario (if bug exists):
✗ Both return 2001
✗ DB: 2 orders created
✗ Double shipping charge
```

### Rules

```
□ Moi bug hypothesis -> it nhat 1 executable test case
□ Test case ID format: BUG-HUNT-{number}
□ PHAI attempt reproduce exact bug scenario
□ Expected result show BOTH: correct behavior + bug scenario
□ Reproduction ideas tu risk analysis -> convert thanh test steps cu the
```

---

## 17. Coverage Gap Analysis Checklist

**BAT BUOC: Chay checklist nay truoc khi submit test design.**

### Pre-Release Checklist

**Bug Hypothesis Coverage:**
```
□ List tat ca bug hypotheses tu Risk Analysis
□ Moi hypothesis co it nhat 1 test case
□ Test case co specific reproduction conditions (timing, data, env)
□ Gaps da duoc identified va test cases da duoc tao
```

**Infrastructure Failure Coverage:**
```
□ Queue unavailable test exists
□ Carrier timeout (AFTER processing) test exists ← #1 risk
□ Database transaction failure test exists
□ Cache failure test exists
```

**Security Coverage:**
```
□ Webhook signature verification test exists
□ Replay attack prevention test exists
□ Cross-application access (IDOR) test exists
□ Rate limiting with correct error code (429) test exists
□ Token expiration mid-flow test exists
```

**Concurrent Testing Coverage:**
```
□ All unique constraints co concurrent test
□ Timing precision specified in test steps
□ Expected behavior for BOTH requests documented
□ Database verification query included
```

### When to Block Release

**KHONG approve test design neu:**

1. **Critical bug hypothesis khong co test case** — bat ky BH nao marked "Critical"
2. **Carrier timeout after processing chua duoc test** — #1 source of duplicate orders
3. **Webhook security chua duoc test** — signature + replay attack
4. **Concurrent duplicate prevention chua duoc test** — API tao records voi unique constraints
5. **Coverage < 80% cho P1 features** — P1 PHAI co comprehensive coverage

---

**End of Advanced Reference**
