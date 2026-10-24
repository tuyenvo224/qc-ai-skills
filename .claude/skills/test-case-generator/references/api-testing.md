# TD REFERENCE: API TESTING

**Vai tro:** File tham khao chi tiet khi Test Case Generator can viet test cases cho API.
**Load khi:** Spec co API endpoints, webhooks, error codes, authentication.

**LƯU Ý NGÔN NGỮ:** ví dụ dưới đây bằng tiếng Anh chỉ minh họa pattern — TC thật phải viết bằng tiếng Việt (xem `writing-format.md` 7.0), giữ nguyên tiếng Anh cho endpoint/field/error code/HTTP status lấy từ spec.

---

## Table of Contents

1. [API Test Types](#1-api-test-types)
2. [API Test Case Format](#2-api-test-case-format)
3. [API Test Steps Structure](#3-api-test-steps-structure)
4. [API Expected Results Structure](#4-api-expected-results-structure)
5. [Positive Tests](#5-positive-tests)
6. [Negative Tests](#6-negative-tests)
7. [Boundary Tests](#7-boundary-tests)
8. [Security Tests for API](#8-security-tests-for-api)
9. [Database Tests](#9-database-tests)
10. [Response Validation Tests](#10-response-validation-tests)
11. [Pagination & Filtering Tests](#11-pagination--filtering-tests)
12. [Idempotency Tests](#12-idempotency-tests)
13. [Error Response Standardization](#13-error-response-standardization)
14. [Webhook Testing](#14-webhook-testing)
15. [API Test Grouping Strategy](#15-api-test-grouping-strategy)
16. [API Coverage Matrix](#16-api-coverage-matrix)
17. [HTTP Status Code Reference](#17-http-status-code-reference)

---

## 1. API Test Types

### 1.1 Core API Test Types

| Test Type | Mo ta | Priority | Techniques |
|-----------|-------|----------|------------|
| **Positive** | API hoat dong dung voi valid inputs | P1-P2 | `[EP]` `[UC]` `[CL]` |
| **Negative** | Error handling dung cho invalid inputs | P1-P2 | `[EP]` `[EG]` `[DT]` |
| **Boundary** | Test tai min/max limits cua fields | P2 | `[BVA]` |
| **Security** | Authentication, authorization, injection | P1 | `[EG]` `[CL]` `[EP]` |
| **Database** | Data persistence va constraints | P1-P2 | `[EP]` `[DT]` `[CL]` |
| **Concurrent** | Race conditions, double-submit, deadlock | P1 | `[EG]` `[ST]` |
| **State** | State machine transitions | P1 | `[ST]` `[DT]` |
| **Webhook** | Inbound/outbound webhook reliability & security | P1 | `[UC]` `[EG]` `[CL]` |

### 1.2 Extended API Test Types

| Test Type | Mo ta | Priority | Techniques |
|-----------|-------|----------|------------|
| **Response Validation** | Verify response schema, headers, Content-Type, pagination metadata | P1-P2 | `[CL]` `[EP]` |
| **Pagination & Filtering** | Test list endpoints: offset/limit, cursor, sort, search, filter | P2 | `[BVA]` `[EP]` `[PW]` |
| **Idempotency** | Verify safe retry behavior, requestId deduplication | P1 | `[EG]` `[EP]` |
| **Error Standardization** | Verify consistent error format across all endpoints | P2 | `[CL]` `[EP]` |
| **Performance Baseline** | Validate response time thresholds under normal load | P2-P3 | `[CL]` `[BVA]` |
| **File Upload/Download** | Test multipart/binary API, file size limits | P2 | `[BVA]` `[EP]` `[EG]` |

### 1.3 Technique-to-API Mapping

| Technique | Ap dung trong API context |
|-----------|--------------------------|
| `[EP]` | Group valid/invalid input classes per field. Moi enum value = 1 partition. Moi carrier = 1 partition |
| `[BVA]` | String length min/max, numeric min/max, array size, pagination offset/limit, file size, rate limit |
| `[DT]` | Multi-condition business rules (payment_type + carrier + region -> fee), permission matrix (role + resource + action) |
| `[ST]` | Order status flows, webhook state updates, token lifecycle, retry state machine |
| `[UC]` | End-to-end flows: create -> get -> update -> delete, webhook integration flows |
| `[PW]` | APIs voi nhieu optional params, filter combinations, carrier x payment x service type |
| `[EG]` | SQL injection, malformed JSON, race conditions, timeout, null/empty/special chars, oversized payloads |
| `[CL]` | Response schema validation, security headers, HTTP status codes, CORS headers |
| `[EXP]` | Undocumented behavior, unusual parameter combinations, API quirks |

---

## 2. API Test Case Format

**Format mo rong cho API (6 cot):**

| STT | Test Type | Technique | Priority | Test Objective | Test Steps | Expected Result |
|-----|-----------|-----------|----------|----------------|------------|-----------------|
| TC-001 | Positive | `[EP]` | P1 | [EP] Verify order creation with valid COD payload | Request details | Response + DB + Side effects |

**Rules:**
- **Technique column** la BAT BUOC
- **Test Objective** PHAI bat dau bang `[Technique Tag]` + verb
- Moi TC map chinh xac 1 primary technique
- Group TC by Test Type, then by Technique within each type

> **Luu y:** Format 6 cot nay la mo rong. Neu project dung format 4 cot (theo file chinh), co the gop Test Type va Technique vao Test Objective: `[EP][Positive] Verify...`

---

## 3. API Test Steps Structure

**Moi API test PHAI bao gom cac verification layers applicable:**

```
1.  [Precondition]    Setup data (create dependencies, seed DB, prepare tokens)
2.  [Request]         Send {METHOD} {endpoint}
3.  [Request]         Headers: Authorization, Content-Type, X-Request-Id
4.  [Request]         Body: {JSON body}
5.  [Verify-Status]   Check HTTP status code
6.  [Verify-Headers]  Check response headers (Content-Type, X-Request-Id, Rate-Limit, CORS)
7.  [Verify-Schema]   Validate response structure matches API spec
8.  [Verify-Data]     Check response body field values
9.  [Verify-DB]       Check database state (inserted/updated/deleted records, audit logs)
10. [Verify-SideEffect] Check side effects (webhook sent, queue job, email, cache invalidated)
11. [Verify-Idempotency] If applicable: retry same request -> same result, no duplicates
```

### Verification Priority by Test Type

| Test Type | MUST Verify | SHOULD Verify | MAY Verify |
|-----------|-------------|---------------|------------|
| Positive | Status + Schema + Data + DB | Headers + SideEffect | Idempotency |
| Negative | Status + Data (error code/msg) | Schema (error format) | DB (no change) |
| Boundary | Status + Data | DB | Headers |
| Security | Status + Data + DB (no leak) | Headers (security) | SideEffect |
| Database | DB (all tables) + Status | Data | SideEffect |
| Concurrent | DB (final state) + Status (each req) | SideEffect | Headers |
| State | Status + Data + DB (state change) | SideEffect (webhook/log) | Headers |
| Pagination | Status + Data (items + metadata) | Schema | DB |
| Idempotency | Status + Data + DB (no duplicates) | Headers (X-Request-Id) | SideEffect |

---

## 4. API Expected Results Structure

**Template day du:**

```
✓ HTTP Status: {200/201/400/401/403/404/409/422/429/500}
✓ Response Headers:
  - Content-Type: application/json; charset=utf-8
  - X-Request-Id: {echoed or generated UUID}
  - X-RateLimit-Limit: {max requests}
  - X-RateLimit-Remaining: {remaining}
  - Cache-Control: {no-cache | max-age=300}
  - Access-Control-Allow-Origin: {origin} (CORS)
✓ Response Schema: Matches API specification
✓ statusCode: {business code}
✓ statusMessage: "{message}"
✓ data.{field}: {expected value}
✓ data.pagination: {totalItems, totalPages, currentPage, pageSize}
✓ DB: {table}.{column} = {value}
✓ DB: {audit_table}.action = "{CREATE|UPDATE|DELETE}"
✓ Side effect: {webhook sent / queue job created / email triggered}
✓ Idempotency: Retry same request -> same response, no duplicate records
```

**Luu y:** Khong phai moi TC deu can tat ca layers. Chi verify layers applicable theo bang o Section 3.

---

## 5. Positive Tests

**Muc dich:** Verify API hoat dong dung voi valid inputs.
**Primary Techniques:** `[EP]` (valid partitions), `[UC]` (E2E flows), `[CL]` (response structure)

### Checklist

```
□ Happy path voi tat ca required fields                    → [EP] valid partition
□ Happy path voi tat ca optional fields included           → [EP] valid partition
□ Tat ca supported values cho enum fields                  → [EP] moi enum = 1 partition
□ Tat ca carriers/integrations (neu multi-carrier)         → [EP] moi carrier = 1 partition
□ Response structure match API spec                        → [CL] schema check
□ Response headers dung (Content-Type, X-Request-Id)       → [CL] header check
□ Data types trong response match spec                     → [CL] type check
□ Pagination metadata dung (cho list endpoints)            → [CL] structure check
□ E2E flow: create -> get -> verify data consistency       → [UC] main flow
```

### Ví dụ

```
TC-001 | Positive | [EP] | P1
Objective: [EP] Verify order creation with valid COD payment (valid partition: payment_type=COD)

Steps:
1. [Precondition] Authenticate with valid token for app 1
2. [Precondition] Ensure warehouse WH-001 exists, status=active, carrier=GHN
3. [Request] POST /v1.0/orders
4. [Request] Headers: { Authorization: Bearer {token}, Content-Type: application/json }
5. [Request] Body: { requestId: "ORD-001", warehouseCode: "WH-001", payment: { type: "cod", amount: 150000 }, ... }
6. [Verify-Status] Check HTTP status code
7. [Verify-Data] Check response body
8. [Verify-DB] Query: SELECT * FROM orders WHERE request_id = 'ORD-001'

Expected:
✓ HTTP 201
✓ Content-Type: application/json
✓ statusCode: 2001
✓ data.orderCode: returned (format: ORD-XXXXXXXX)
✓ DB orders: status='pending', payment_type='cod', cod_amount=150000
✓ DB order_logs: 1 entry, action='CREATE'
```

---

## 6. Negative Tests

**Muc dich:** Verify API tra dung error cho invalid inputs.
**Primary Techniques:** `[EP]` (invalid partitions), `[EG]` (common defects), `[DT]` (condition combos)

### Checklist

```
□ Missing moi required field (tung field mot)              → [EP] invalid: field=missing
□ Invalid field formats (wrong type, malformed)            → [EP] invalid: format
□ Invalid enum values (not in allowed list)                → [EP] invalid: enum
□ Referential integrity violations (FK not found)          → [EP] invalid: reference
□ Business rule violations                                 → [DT] condition combinations
□ Moi error code trong API spec da duoc test               → [CL] error code checklist
□ Empty string vs null vs missing field (3 cases rieng)    → [EP] 3 separate partitions
□ Malformed JSON body (syntax error)                       → [EG] common defect
□ Wrong Content-Type header                                → [EG] common defect
□ Extra/unknown fields trong request body                  → [EG] common defect
□ Combination nhieu invalid fields                         → [DT] multi-error response
```

### Ví dụ

```
TC-010 | Negative | [EP] | P1
Objective: [EP] Verify error 4005 when carrier field is missing (invalid partition: required field absent)

Steps:
1. [Precondition] Authenticate with valid token
2. [Request] POST /v1.0/warehouses (without "carrier" field in body)
3. [Verify-Status] Check HTTP status
4. [Verify-Data] Check error response
5. [Verify-DB] Verify no record created

Expected:
✓ HTTP 400
✓ statusCode: 4005
✓ statusMessage: "Carrier ID is required"
✓ DB: No warehouse record created
```

```
TC-011 | Negative | [EP] | P1
Objective: [EP] Verify distinction between null, empty string, and missing field for carrier.name

Steps:
1. POST with carrier.name = null -> Check error
2. POST with carrier.name = "" -> Check error
3. POST without carrier.name field -> Check error

Expected:
✓ Each case returns appropriate error (may differ or be same — document actual)
✓ DB: No record created in all 3 cases
```

```
TC-012 | Negative | [EG] | P2
Objective: [EG] Verify error when request body is malformed JSON

Steps:
1. [Request] POST /v1.0/orders with body: '{"requestId": "REQ-001", invalid}'
2. [Verify-Status] Check HTTP status

Expected:
✓ HTTP 400
✓ statusCode: 4001
✓ statusMessage: "Invalid JSON format"
```

---

## 7. Boundary Tests

**Muc dich:** Test tai limits cua field constraints.
**Primary Technique:** `[BVA]`

### BVA Test Points Template

| Field Type | Min | Max | Test Points (BVA) |
|-----------|-----|-----|-------------------|
| **String** | 1 | 255 | 0 (empty), 1 (min), 2 (min+1), 254 (max-1), 255 (max), 256 (max+1) |
| **Integer** | 0 | 999999999 | -1, 0, 1, 999999998, 999999999, 1000000000 |
| **Array** | 1 | 50 | 0 (empty), 1, 2, 49, 50, 51 |
| **Pagination offset** | 0 | totalItems | -1, 0, 1, totalItems-1, totalItems, totalItems+1 |
| **Pagination limit** | 1 | 100 | 0, 1, 2, 99, 100, 101 |
| **Decimal** | 0.00 | varies | 0.00, 0.01, -0.01, max, max+0.01 |
| **File size** | 0 | 10MB | 0 bytes, 1 byte, 9.99MB, 10MB, 10.01MB |
| **Date** | varies | varies | min date, min-1 day, max date, max+1 day, today |

### Checklist

```
□ String fields: min, min+1, max-1, max, max+1                → [BVA] 5 points
□ Numeric fields: 0, 1, -1, min, min-1, max, max+1            → [BVA] 7 points
□ Arrays: empty [], 1 item, max items, max+1 items             → [BVA] 4 points
□ Date fields: min date, max date, today, yesterday, future    → [BVA]
□ Decimal/float: 0.00, 0.01, max precision, beyond precision   → [BVA]
□ Pagination: offset=0, offset=max, limit=1, limit=max         → [BVA]
□ Rate limits: at limit, over limit                             → [BVA]
□ File size: 0 bytes, 1 byte, max size, max+1                  → [BVA]
```

### Ví dụ

```
TC-020 | Boundary | [BVA] | P2
Objective: [BVA] Verify warehouse name at max boundary (255 characters)

Steps:
1. [Precondition] Auth with valid token
2. [Request] POST /v1.0/warehouses with name = "A" x 255
3. [Verify-Status] Check status
4. [Verify-DB] Check warehouse created

Expected:
✓ HTTP 201
✓ statusCode: 2000, warehouse created
✓ DB: warehouse.name length = 255

---

TC-021 | Boundary | [BVA] | P2
Objective: [BVA] Verify error when warehouse name exceeds max (256 characters)

Steps:
1. [Request] POST /v1.0/warehouses with name = "A" x 256

Expected:
✓ HTTP 400
✓ statusCode: 4008
✓ statusMessage: "Warehouse Name invalid"
✓ DB: No warehouse created
```

---

## 8. Security Tests for API

**Muc dich:** Verify authentication, authorization, injection prevention.

### 8.1 Authentication Checklist

```
□ No token                    → 401 Unauthorized         [EG]
□ Invalid token (random)      → 401                      [EG]
□ Expired token               → 401                      [EG]
□ Malformed token             → 400/401                   [EG]
□ Token from different env    → 401                      [EG]
□ JWT manipulation (tampered) → detect and reject         [EG]
```

### 8.2 Authorization Checklist

```
□ Cross-application access (app 2 truy cap resource app 1) → 403/404    [EP]
□ Cross-user resource access (IDOR)                        → 403/404    [EP]
□ Parameter tampering (change applicationId in body)       → reject     [EG]
□ Privilege escalation attempts                            → block      [EG]
□ Permission bypass via direct API call (UI blocks)        → reject     [EG]
□ Access after permission revoked                          → 403        [EP]
```

### 8.3 Input Injection Checklist

```
□ SQL injection in string fields: '; DROP TABLE orders--       [EG]
□ XSS in text fields: <script>alert('xss')</script>           [EG]
□ Command injection: ; rm -rf /                                [EG]
□ Path traversal: ../../../etc/passwd                          [EG]
□ JSON injection in nested objects                             [EG]
□ LDAP injection (if applicable)                               [EG]
```

### 8.4 Rate Limiting Checklist

```
□ At limit (e.g., 100th request)     → 200 OK                 [BVA]
□ Over limit (101st request)         → 429 Too Many Requests   [BVA]
□ NOT 500 (server error)             → must be 429             [CL]
□ Rate limit headers present         → X-RateLimit-Remaining   [CL]
□ Rate limit reset behavior          → after window expires    [BVA]
```

### 8.5 Response Security Headers Checklist

```
□ X-Content-Type-Options: nosniff
□ X-Frame-Options: DENY or SAMEORIGIN
□ Strict-Transport-Security present (HSTS)
□ No sensitive data in error messages (no stack traces, no SQL)
□ No server version headers (Server, X-Powered-By)
□ CORS headers restrict allowed origins
```

### Ví dụ

```
TC-030 | Security | [EP] | P1
Objective: [EP] Verify cross-application access denied (wrong applicationId)

Steps:
1. [Precondition] Auth as app 2
2. [Request] GET /v1.0/warehouses/{id} where warehouse belongs to app 1
3. [Verify-Status] Check HTTP status
4. [Verify-Data] Check no data leak

Expected:
✓ HTTP 403 or 404
✓ No warehouse data in response body
✓ DB: No access log for app 2 reading app 1 data

---

TC-031 | Security | [EG] | P1
Objective: [EG] Verify SQL injection in warehouse name is rejected

Steps:
1. [Request] POST /v1.0/warehouses with name = "'; DROP TABLE warehouses; --"
2. [Verify-Status] Check HTTP status
3. [Verify-DB] Check warehouses table intact

Expected:
✓ HTTP 400 (validation error, NOT 500)
✓ No SQL error exposed in response
✓ DB: warehouses table intact, no record created
```

---

## 9. Database Tests

**Muc dich:** Verify data persistence va constraints cho API operations.

> **Checklist CREATE/UPDATE/DELETE:** Xem file chinh `Subagent_Test_Designer.md` Phan 7.7
> Phan nay chi bo sung **SQL query templates** dac thu cho API testing.

### DB Verification Query Templates (API-specific)

```sql
-- Sau khi tao record qua API
SELECT * FROM orders WHERE request_id = 'TEST-001';
SELECT * FROM order_items WHERE order_id = {order_id};
SELECT * FROM order_logs WHERE order_id = {order_id};

-- Verify counts (dac biet quan trong cho idempotency + concurrent tests)
SELECT COUNT(*) FROM orders WHERE request_id = 'TEST-001';  -- Should be 1

-- Check duplicates (bat buoc cho concurrent tests)
SELECT request_id, COUNT(*)
FROM orders
GROUP BY request_id
HAVING COUNT(*) > 1;  -- Should be empty

-- Verify FK integrity (bat buoc cho create tests)
SELECT o.* FROM orders o
LEFT JOIN warehouses w ON o.warehouse_id = w.id
WHERE w.id IS NULL;  -- Should be empty (no orphans)

-- Verify soft-delete (bat buoc cho delete tests)
SELECT * FROM orders WHERE id = {id} AND is_deleted = true;
SELECT deleted_at FROM orders WHERE id = {id};  -- Should be NOT NULL

-- Verify audit trail (bat buoc cho moi write operation)
SELECT * FROM audit_logs
WHERE entity_type = 'order' AND entity_id = {id}
ORDER BY created_at DESC LIMIT 5;
```

---

## 10. Response Validation Tests

**Muc dich:** Verify response schema, headers, Content-Type.
**Technique:** `[CL]` `[EP]`

### Checklist

```
□ Content-Type header dung (application/json)           [CL]
□ Response schema match API spec (required fields)      [CL]
□ Data types dung (string, number, boolean, array)      [CL]
□ Nullable fields xu ly dung                            [EP]
□ Empty arrays vs null (khi no items)                   [EP]
□ Date format consistent (ISO 8601)                     [CL]
□ Enum values trong allowed list                        [EP]
□ Nested objects structure dung                         [CL]
□ No extra unexpected fields (strict mode)              [CL]
```

---

## 11. Pagination & Filtering Tests

**Muc dich:** Test list endpoints voi offset/limit, sort, filter.
**Techniques:** `[BVA]` `[EP]` `[PW]`

### Checklist

```
□ Default pagination (no params)                        [EP]
□ offset=0, limit=10 (first page)                       [BVA]
□ offset=max (last page)                                [BVA]
□ offset beyond total (empty result)                    [BVA]
□ limit=1 (single item)                                 [BVA]
□ limit=0 (invalid?)                                    [BVA]
□ limit > max allowed                                   [BVA]
□ Sort ascending + descending                           [EP]
□ Sort by invalid field                                 [EP]
□ Filter by each filterable field                       [EP]
□ Filter with no matches (empty result)                 [EP]
□ Multiple filters combined                             [PW]
□ Search with partial match                             [EP]
□ Search with special characters                        [EG]
□ Pagination metadata dung (totalItems, totalPages)     [CL]
```

---

## 12. Idempotency Tests

**Muc dich:** Verify safe retry behavior, requestId deduplication.
**Techniques:** `[EG]` `[EP]`

### Checklist

```
□ Same requestId sent twice -> second returns same result    [EG]
□ Same requestId sent twice -> only 1 record in DB           [EG]
□ Different requestId -> creates new record                  [EP]
□ requestId missing -> behavior (error or auto-generate?)    [EP]
□ requestId format invalid (too long, special chars)         [EP]
□ Concurrent same requestId -> only 1 succeeds               [EG]
```

### Ví dụ

```
TC-050 | Idempotency | [EG] | P1
Objective: [EG] Verify duplicate requestId returns same result without creating new record

Steps:
1. [Request] POST /v1.0/orders with requestId = "IDEM-001" -> Success
2. [Request] POST /v1.0/orders with requestId = "IDEM-001" (same) -> Check result
3. [Verify-DB] Count records

Expected:
✓ Request 1: HTTP 201, statusCode: 2001, orderCode returned
✓ Request 2: HTTP 200, same orderCode returned (or HTTP 409 duplicate)
✓ DB: EXACTLY 1 order record with request_id = 'IDEM-001'
```

---

## 13. Error Response Standardization

**Muc dich:** Verify consistent error format across all endpoints.
**Technique:** `[CL]` `[EP]`

### Standard Error Format

```json
{
  "statusCode": 4005,
  "statusMessage": "Carrier ID is required",
  "errors": [
    {
      "field": "carrier.id",
      "message": "This field is required"
    }
  ]
}
```

### Checklist

```
□ All error responses follow same structure               [CL]
□ statusCode is consistent (same error -> same code)      [CL]
□ statusMessage is human-readable                         [CL]
□ Error field names match request field names              [CL]
□ No stack traces in error response                       [CL]
□ No SQL/internal details in error messages                [CL]
□ Error messages bilingual (EN + VI) if applicable         [CL]
□ Multiple validation errors return all at once            [EP]
```

---

## 14. Webhook Testing

### 14.1 Inbound Webhooks (Nhan webhook tu external)

**Checklist - Happy path:**
```
□ Valid webhook with correct signature -> processed         [UC]
□ Status updated correctly in DB                           [UC]
□ Webhook log/history recorded                             [CL]
□ Idempotent: same webhook sent twice -> no duplicate      [EG]
```

**Checklist - Security:**
```
□ Missing signature header -> 401 rejected                 [EG]
□ Invalid signature (wrong secret) -> 401 rejected         [EG]
□ Expired timestamp (too old) -> 401 rejected              [EG]
□ Replay attack (same signature reused) -> 401 rejected    [EG]
□ Payload tampering (modified after signing) -> rejected    [EG]
```

**Checklist - Error handling:**
```
□ Malformed webhook body -> 400 rejected                   [EG]
□ Unknown event type -> handled gracefully                 [EG]
□ Webhook for non-existent order -> 404                    [EG]
□ Out-of-order webhooks (status skip) -> handled           [ST]
```

### 14.2 Outbound Webhooks (Gui webhook ra external)

**Checklist:**
```
□ Webhook sent after event trigger                         [UC]
□ Webhook payload correct (all required fields)            [CL]
□ Signature included in headers                            [CL]
□ Retry on failure (3xx/4xx/5xx/timeout)                   [EG]
□ Retry count limit respected (max 3-5 retries)            [BVA]
□ Exponential backoff between retries                      [CL]
□ Dead Letter Queue after max retries                      [EG]
```

### Ví dụ

```
TC-060 | Webhook | [EG] | P1
Objective: [EG] Verify inbound webhook rejected without signature header

Steps:
1. [Request] POST /webhooks/carrier (without X-Signature header)
2. [Request] Body: valid webhook payload
3. [Verify-Status] Check HTTP status
4. [Verify-DB] Check order status unchanged

Expected:
✓ HTTP 401 Unauthorized
✓ Order status unchanged in DB
✓ Security log: "Missing signature" recorded

---

TC-061 | Webhook | [EG] | P1
Objective: [EG] Verify webhook replay attack prevention

Steps:
1. Capture valid webhook with signature at timestamp T
2. Wait 5 minutes (past expiry window)
3. Replay exact same webhook with original signature

Expected:
✓ HTTP 401 (timestamp expired)
✓ Order status unchanged
✓ Security log: "Expired timestamp" recorded
```

---

## 15. API Test Grouping Strategy

**Nhom test cases theo API endpoint, KHONG theo test type:**

```
## API Test Cases

### Group: POST /v1.0/warehouses (Create Warehouse)
| STT | Test Objective | Test Steps | Expected Result |
...

### Group: PUT /v1.0/warehouses/{id} (Update Warehouse)
| STT | Test Objective | Test Steps | Expected Result |
...

### Group: POST /v1.0/orders (Create Order)
| STT | Test Objective | Test Steps | Expected Result |
...

### Group: GET /v1.0/orders (List Orders)
| STT | Test Objective | Test Steps | Expected Result |
...

### Group: Inbound Webhooks
| STT | Test Objective | Test Steps | Expected Result |
...
```

**Trong moi nhom, thu tu:**
```
① UI Basic (neu co UI goi API)
② Positive tests (happy path)
③ Business logic tests
④ Negative tests (validation, error codes)
⑤ Boundary tests (min/max/length)
⑥ Permission tests (auth, cross-app)
⑦ Database tests (data integrity)
⑧ Security tests (injection, rate limiting)
⑨ Edge case / Concurrent / Idempotency
```

---

## 16. API Coverage Matrix

**Dung bang nay de dam bao moi endpoint duoc test day du:**

| Endpoint | Positive | Negative | Boundary | Security | DB | Concurrent | State | Webhook | Response | Total |
|----------|----------|----------|----------|----------|----|-----------|-------|---------|----------|-------|
| POST /warehouses | ✓ 3 | ✓ 8 | ✓ 6 | ✓ 4 | ✓ 3 | ✓ 2 | - | - | ✓ 2 | 28 |
| PUT /warehouses/{id} | ✓ 2 | ✓ 5 | ✓ 4 | ✓ 3 | ✓ 2 | ✓ 1 | - | - | ✓ 1 | 18 |
| POST /orders | ✓ 4 | ✓ 10 | ✓ 8 | ✓ 5 | ✓ 4 | ✓ 3 | ✓ 2 | ✓ 1 | ✓ 2 | 39 |
| GET /orders | ✓ 2 | ✓ 3 | ✓ 4 | ✓ 2 | - | - | - | - | ✓ 3 | 14 |
| Webhooks | ✓ 3 | ✓ 5 | - | ✓ 5 | ✓ 3 | ✓ 2 | ✓ 4 | - | - | 22 |

---

## 17. HTTP Status Code Reference

| HTTP Status | Meaning | Khi nao dung trong Expected Result |
|-------------|---------|-----------------------------------|
| **200** | OK | Successful GET, PUT, PATCH, DELETE |
| **201** | Created | Successful POST that creates resource |
| **204** | No Content | Successful DELETE with no response body |
| **400** | Bad Request | Validation errors, malformed JSON, missing required fields |
| **401** | Unauthorized | Missing/invalid/expired authentication token |
| **403** | Forbidden | Valid token but insufficient permissions (IDOR, cross-tenant) |
| **404** | Not Found | Resource not found, invalid endpoint |
| **409** | Conflict | Duplicate resource, version conflict (optimistic locking) |
| **422** | Unprocessable Entity | Business rule violation, invalid state transition |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Server Error | Server bug — KHONG BAO GIO expected (flag as defect) |
| **502/503** | Bad Gateway / Unavailable | Upstream service failure — test resilience |

---

**End of API Reference**
