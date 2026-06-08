#!/usr/bin/env bash
# ------------------------------------------------------------------
# smoke-test.sh
# Automated post-deployment smoke tests for Personal Finance System.
# Intended for CI/CD pipelines (GitHub Actions, GitLab CI, etc.).
# Fails if any check fails, so the pipeline can roll back.
# ------------------------------------------------------------------
set -euo pipefail

# ---- Configuration (override via environment) --------------------
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
TEST_USER="${SMOKE_TEST_USER:-smoketest}"
TEST_PASS="${SMOKE_TEST_PASS:-smoketest123}"
EXIT_CODE=0

echo "============================================"
echo " Smoke Tests - Personal Finance System"
echo "============================================"
echo "Frontend: ${FRONTEND_URL}"
echo "Backend:  ${BACKEND_URL}"
echo ""

# ---- Helper -----------------------------------------------------
pass()  { echo "[PASS] $1"; }
fail()  { echo "[FAIL] $1"; EXIT_CODE=1; }

# ---- 1. Frontend health check ------------------------------------
echo "--- 1. Frontend responds with 200 ---"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "${FRONTEND_URL}" || true)
if [ "$HTTP_CODE" = "200" ]; then
    pass "Frontend returned HTTP 200"
else
    fail "Frontend returned HTTP ${HTTP_CODE} (expected 200)"
fi
echo ""

# ---- 2. Backend health check (with DB verification) -------------
echo "--- 2. Backend /api/health/ ---"
HEALTH=$(curl -s --max-time 10 "${BACKEND_URL}/api/health/" || true)
if echo "$HEALTH" | grep -q '"status":"healthy"'; then
    pass "Backend health check passed (both databases reachable)"
else
    echo "  Response: ${HEALTH:-<empty>}"
    fail "Backend health check failed"
fi
echo ""

# ---- 3. E2E API test - Login ------------------------------------
echo "--- 3. E2E API: Login ---"
# Try to create test user silently first (ignore if exists)
curl -s -X POST "${BACKEND_URL}/admin/login/" \
    -d "username=${TEST_USER}&password=${TEST_PASS}" \
    -o /dev/null 2>/dev/null || true

LOGIN_RESP=$(curl -s --max-time 10 -X POST "${BACKEND_URL}/api/auth/login/" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"${TEST_USER}\",\"password\":\"${TEST_PASS}\"}" || true)

if echo "$LOGIN_RESP" | grep -q '"username"'; then
    pass "Login API returned user profile"
    echo "  User: $(echo "$LOGIN_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('username','?'))" 2>/dev/null || echo "${TEST_USER}")"
else
    echo "  Response: ${LOGIN_RESP:-<empty>}"
    fail "Login API test failed"
fi
echo ""

# ---- 4. E2E API test - Dashboard --------------------------------
echo "--- 4. E2E API: Dashboard ---"
# Reuse session cookie from login
DASHBOARD_RESP=$(curl -s --max-time 10 -b /tmp/smoke_cookies -c /tmp/smoke_cookies \
    "${BACKEND_URL}/api/dashboard/" || true)
if echo "$DASHBOARD_RESP" | grep -q '"total_income"'; then
    pass "Dashboard API returned summary data"
else
    echo "  Response: ${DASHBOARD_RESP:-<empty>}"
    fail "Dashboard API test failed"
fi
echo ""

# ---- Summary ----------------------------------------------------
echo "============================================"
if [ "$EXIT_CODE" -eq 0 ]; then
    echo " All smoke tests passed!"
else
    echo " Some smoke tests FAILED. Check logs above."
fi
echo "============================================"
exit "$EXIT_CODE"
