#!/usr/bin/env bash
# ------------------------------------------------------------------
# deploy-verify.sh
# Deployment verification script for CI/CD pipelines.
# Runs smoke tests and triggers rollback on failure.
# ------------------------------------------------------------------
set -euo pipefail

NAMESPACE="${NAMESPACE:-personal-finance}"
DEPLOYMENT_NAME="${DEPLOYMENT_NAME:-backend}"

echo "============================================"
echo " Deployment Verification"
echo "============================================"
echo ""

# ---- 1. Verify pods are ready -----------------------------------
echo "--- 1. Checking Kubernetes pod status ---"
READY_PODS=$(kubectl get pods -n "${NAMESPACE}" -l "app=${DEPLOYMENT_NAME}" \
    -o jsonpath='{.items[*].status.containerStatuses[0].ready}' | tr ' ' '\n' | grep -c "true" || echo "0")
TOTAL_PODS=$(kubectl get pods -n "${NAMESPACE}" -l "app=${DEPLOYMENT_NAME}" \
    --no-headers 2>/dev/null | wc -l)

if [ "$TOTAL_PODS" -gt 0 ] && [ "$READY_PODS" -eq "$TOTAL_PODS" ]; then
    echo "[PASS] All ${TOTAL_PODS} pod(s) are ready"
else
    echo "[FAIL] Only ${READY_PODS}/${TOTAL_PODS} pods ready"
    echo "       Triggering rollback..."
    kubectl rollout undo deployment/"${DEPLOYMENT_NAME}" -n "${NAMESPACE}"
    exit 1
fi
echo ""

# ---- 2. Verify service endpoints ---------------------------------
echo "--- 2. Checking Service endpoints ---"
kubectl get svc -n "${NAMESPACE}" -o wide
echo ""

# ---- 3. Run smoke tests -----------------------------------------
echo "--- 3. Running smoke tests ---"
SMOKE_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if bash "${SMOKE_SCRIPT_DIR}/smoke-test.sh"; then
    echo ""
    echo "[PASS] Smoke tests passed. Deployment verified."
else
    echo ""
    echo "[FAIL] Smoke tests failed. Triggering rollback..."
    kubectl rollout undo deployment/"${DEPLOYMENT_NAME}" -n "${NAMESPACE}"
    exit 1
fi

echo ""
echo "============================================"
echo " Deployment verified successfully!"
echo "============================================"
