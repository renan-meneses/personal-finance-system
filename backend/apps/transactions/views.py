import json
from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.conf import settings
from . import models as tx_models
from . import parsers
from mongodb_utils.client import get_mongo_db, ping_mongo


@api_view(["GET", "POST"])
def transaction_list(request):
    user_id = request.user.id
    if request.method == "GET":
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 50))
        filters = {}
        if "type" in request.query_params:
            filters["type"] = request.query_params["type"]
        if "category" in request.query_params:
            filters["category"] = request.query_params["category"]
        items, total = tx_models.list_transactions(
            user_id, filters=filters, page=page, page_size=page_size
        )
        return Response({"count": total, "results": items, "page": page})

    data = request.data
    if isinstance(data, str):
        data = json.loads(data)
    data["user_id"] = user_id
    data["type"] = data.get("type", "expense")
    data["category"] = data.get("category", "other")
    data["is_recurring"] = data.get("is_recurring", False)
    data["next_execution_date"] = data.get("next_execution_date")
    data["original_file"] = "manual"
    result = tx_models.create_transaction(data)

    audit = tx_models.get_audit_collection()
    audit.insert_one(
        {
            "user_id": user_id,
            "action": "create_transaction",
            "transaction_id": result["_id"],
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    return Response(result, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def transaction_detail(request, transaction_id):
    user_id = request.user.id
    tx = tx_models.get_transaction(transaction_id)
    if not tx or tx.get("user_id") != user_id:
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(tx)

    if request.method == "PUT":
        data = request.data
        if isinstance(data, str):
            data = json.loads(data)
        result = tx_models.update_transaction(transaction_id, data)
        return Response(result)

    if request.method == "DELETE":
        tx_models.delete_transaction(transaction_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
def upload_file(request):
    user_id = request.user.id
    file = request.FILES.get("file")
    if not file:
        return Response(
            {"detail": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    content = file.read().decode("utf-8", errors="replace")
    name = file.name.lower()

    if name.endswith(".csv"):
        transactions = parsers.parse_csv(content, user_id)
    elif name.endswith(".ofx") or name.endswith(".qfx"):
        transactions = parsers.parse_ofx(content, user_id)
    else:
        return Response(
            {"detail": "Unsupported file format. Use CSV or OFX/QFX."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not transactions:
        return Response(
            {"detail": "No transactions could be parsed from the file."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    count = tx_models.bulk_insert(transactions)

    audit = tx_models.get_audit_collection()
    audit.insert_one(
        {
            "user_id": user_id,
            "action": "file_upload",
            "filename": file.name,
            "transaction_count": count,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    return Response(
        {"imported": count, "filename": file.name}, status=status.HTTP_201_CREATED
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    db_status = {"postgresql": False, "mongodb": False}
    status_code = status.HTTP_200_OK

    # Check PostgreSQL
    from django.db import connections
    try:
        connections["default"].cursor().execute("SELECT 1")
        db_status["postgresql"] = True
    except Exception:
        db_status["postgresql"] = False
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    # Check MongoDB
    try:
        mongo_ok = ping_mongo()
        db_status["mongodb"] = mongo_ok
        if not mongo_ok:
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    except Exception:
        db_status["mongodb"] = False
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return Response(
        {
            "status": "healthy" if status_code == status.HTTP_200_OK else "unhealthy",
            "databases": db_status,
        },
        status=status_code,
    )
