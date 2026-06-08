import io
import csv
from datetime import datetime


def parse_csv(file_content: str, user_id: int) -> list[dict]:
    """
    Parse CSV content into transaction dicts.
    Expected columns: date, description, amount, type (income/expense), category
    """
    reader = csv.DictReader(io.StringIO(file_content))
    transactions = []
    for row in reader:
        try:
            amount = float(row.get("amount", "0").replace(",", ""))
        except (ValueError, KeyError):
            continue
        transactions.append(
            {
                "user_id": user_id,
                "date": row.get("date", datetime.utcnow().strftime("%Y-%m-%d")),
                "description": row.get("description", "").strip(),
                "amount": amount,
                "type": row.get("type", "expense").strip().lower(),
                "category": row.get("category", "other").strip().lower(),
                "original_file": "csv_upload",
                "is_recurring": False,
                "next_execution_date": None,
            }
        )
    return transactions


def parse_ofx(file_content: str, user_id: int) -> list[dict]:
    """
    Parse OFX/QFX content into transaction dicts using ofxparse.
    Fallback to simple text parsing if ofxparse is unavailable.
    """
    try:
        import ofxparse
        ofx = ofxparse.OfxParser.parse(io.StringIO(file_content))
        transactions = []
        for account in ofx.accounts:
            for t in account.statement.transactions:
                transactions.append(
                    {
                        "user_id": user_id,
                        "date": t.date.strftime("%Y-%m-%d") if hasattr(t, "date") else "",
                        "description": t.memo or t.payee or "",
                        "amount": float(t.amount),
                        "type": "expense" if float(t.amount) < 0 else "income",
                        "category": "other",
                        "original_file": "ofx_upload",
                        "is_recurring": False,
                        "next_execution_date": None,
                    }
                )
        return transactions
    except ImportError:
        return _parse_ofx_fallback(file_content, user_id)


def _parse_ofx_fallback(file_content: str, user_id: int) -> list[dict]:
    transactions = []
    current_tran = {}
    for line in file_content.splitlines():
        line = line.strip()
        if line.upper().startswith("<STMTTRN>"):
            current_tran = {}
        elif line.upper().startswith("<DTPOSTED>"):
            raw = line.split(">", 1)[-1].strip()
            if len(raw) >= 8:
                current_tran["date"] = f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
        elif line.upper().startswith("<NAME>"):
            current_tran["description"] = line.split(">", 1)[-1].strip()
        elif line.upper().startswith("<TRNAMT>"):
            try:
                current_tran["amount"] = float(line.split(">", 1)[-1].strip())
            except ValueError:
                current_tran["amount"] = 0.0
        elif line.upper().startswith("<MEMO>"):
            desc = line.split(">", 1)[-1].strip()
            if desc:
                current_tran.setdefault("description", desc)
        elif line.upper().startswith("</STMTTRN>"):
            if "amount" in current_tran:
                transactions.append(
                    {
                        "user_id": user_id,
                        "date": current_tran.get("date", ""),
                        "description": current_tran.get("description", ""),
                        "amount": abs(current_tran["amount"]),
                        "type": "expense" if current_tran["amount"] < 0 else "income",
                        "category": "other",
                        "original_file": "ofx_upload",
                        "is_recurring": False,
                        "next_execution_date": None,
                    }
                )
            current_tran = {}
    return transactions
