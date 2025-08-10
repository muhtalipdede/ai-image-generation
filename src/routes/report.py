from flask import Blueprint, jsonify
from google.cloud import firestore
from src.repository.report_repository import add_report
from src.firestore_client import get_db
import datetime

report_bp = Blueprint('report', __name__)

@report_bp.route('/scheduleWeeklyReport', methods=['POST'])
def schedule_weekly_report():
    now = datetime.datetime.now(datetime.timezone.utc)
    week_ago = now - datetime.timedelta(days=7)
    db = get_db()
    gen_query = db.collection("generationRequests").where("createdAt", ">=", week_ago)
    gens = list(gen_query.stream())
    stats = {}
    for g in gens:
        d = g.to_dict()
        model = d.get("model")
        style = d.get("style")
        size = d.get("size")
        status = d.get("status")
        key = (model, style, size)
        if key not in stats:
            stats[key] = {"count":0, "success":0, "failed":0}
        stats[key]["count"] += 1
        if status == "success":
            stats[key]["success"] += 1
        elif status == "failed":
            stats[key]["failed"] += 1
    txn_query = db.collection("transactions").where("timestamp", ">=", week_ago)
    txns = list(txn_query.stream())
    credit_summary = {"deducted":0, "refunded":0}
    for t in txns:
        d = t.to_dict()
        if d.get("type") == "deduction":
            credit_summary["deducted"] += d.get("credits",0)
        elif d.get("type") == "refund":
            credit_summary["refunded"] += d.get("credits",0)
    stats_str_keys = {f"{k[0]}|{k[1]}|{k[2]}": v for k, v in stats.items()}
    report_doc = {
        "generatedAt": now,
        "stats": stats_str_keys,
        "creditSummary": credit_summary
    }
    add_report(report_doc)

    # --- Anomaly Detection ---
    # Count generations for this week
    this_week_count = sum([v["count"] for v in stats.values()])
    # Calculate previous 4 weeks' average
    prev_counts = []
    for i in range(1, 5):
        start = week_ago - datetime.timedelta(days=7*i)
        end = week_ago - datetime.timedelta(days=7*(i-1))
        prev_gens = db.collection("generationRequests").where("createdAt", ">=", start).where("createdAt", "<", end).stream()
        prev_counts.append(len(list(prev_gens)))
    prev_avg = sum(prev_counts)/len(prev_counts) if prev_counts else 0
    anomaly = None
    if prev_avg > 0 and this_week_count > 2 * prev_avg:
        anomaly = f"Usage spike detected: {this_week_count} generations this week (avg: {int(prev_avg)})"
    response = {"reportStatus": "success"}
    if anomaly:
        response["anomaly"] = anomaly
    return jsonify(response)
