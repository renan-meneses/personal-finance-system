import re
from django.core.management.base import BaseCommand
from mongodb_utils.client import get_mongo_db

CATEGORY_RULES = [
    (r"(?i)\b(uber|lyft|taxi|99|cabify)\b", "transport"),
    (r"(?i)\b(ifood|ubereats|rapp[ií]|menulog|delivery)\b", "food"),
    (r"(?i)\b(amazon|mercadolibre|shopee|aliexpress|magazine)\b", "shopping"),
    (r"(?i)\b(netflix|spotify|prime.?video|hbo|disney.?plus|youtube.?premium)\b", "entertainment"),
    (r"(?i)\b(aluguel|rent|condom[ií]nio)\b", "housing"),
    (r"(?i)\b(energia|energisa|light|enel|water|sabesp|g[aá]s|comg[aá]s)\b", "utilities"),
    (r"(?i)\b(farmacia|drogasil|droga.?raia|hospital|m[eé]dico|plano.?sa[uú]de)\b", "health"),
    (r"(?i)\b(sal[aá]rio|salary|wage|payroll)\b", "salary"),
    (r"(?i)\b(escola|faculdade|curso|udemy|coursera|alura)\b", "education"),
    (r"(?i)\b(investimento|invest|renda.?fixa|acoes|stocks|cdb|lci)\b", "investment"),
    (r"(?i)\b(pix|ted|doc|transferencia|transfer)\b", "transfer"),
]


class Command(BaseCommand):
    help = "Auto-categorize uncategorized transactions based on description rules"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true", help="Only show what would be updated"
        )
        parser.add_argument(
            "--user-id", type=int, default=None, help="Limit to a specific user"
        )

    def handle(self, *args, **options):
        db = get_mongo_db()
        collection = db["transactions"]

        query = {"category": {"$in": ["other", "", None]}}
        if options["user_id"]:
            query["user_id"] = options["user_id"]

        uncategorized = list(collection.find(query))
        self.stdout.write(f"Found {len(uncategorized)} uncategorized transactions")

        updated = 0
        for tx in uncategorized:
            desc = tx.get("description", "")
            matched_category = None
            for pattern, category in CATEGORY_RULES:
                if re.search(pattern, desc):
                    matched_category = category
                    break

            if matched_category:
                if not options["dry_run"]:
                    collection.update_one(
                        {"_id": tx["_id"]},
                        {"$set": {"category": matched_category}},
                    )
                self.stdout.write(
                    f"  [{tx['_id']}] '{desc[:50]}...' -> {matched_category}"
                )
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(f"Categorized {updated} transactions")
        )
