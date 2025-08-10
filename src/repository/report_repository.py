from src.firestore_client import get_db
from src.models.report import Report
from typing import Dict, Any

def add_report(report):
    db = get_db()
    # Accept both dict and Report dataclass for flexibility
    if isinstance(report, dict):
        db.collection("reports").add(report)
    else:
        db.collection("reports").add(report_to_dict(report))

def report_to_dict(report: Report) -> Dict[str, Any]:
    return {
        "generatedAt": report.generated_at,
        "stats": report.stats,
        "creditSummary": report.credit_summary
    }

def report_from_dict(data: Dict[str, Any]) -> Report:
    return Report(
        generated_at=data.get("generatedAt"),
        stats=data.get("stats", {}),
        credit_summary=data.get("creditSummary", {})
    )
