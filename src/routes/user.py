from flask import Blueprint, request, jsonify
from src.repository.user_repository import get_user
from src.firestore_client import get_db

user_bp = Blueprint('user', __name__)

def get_transactions_for_user(user_id, limit=50):
    db = get_db()
    txns = db.collection("transactions").where("userId","==",user_id).order_by("timestamp",direction=2).limit(limit).stream()
    txns_list = []
    for t in txns:
        d = t.to_dict()
        d["id"] = t.id
        txns_list.append({
            "id": d["id"],
            "type": d.get("type"),
            "credits": d.get("credits"),
            "generationRequestId": d.get("generationRequestId"),
            "timestamp": d.get("timestamp")
        })
    return txns_list

@user_bp.route('/getUserCredits', methods=['GET'])
def get_user_credits():
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify({"error":"userId required"}), 400
    user = get_user(user_id)
    if user is None:
        return jsonify({"error":"user not found"}), 404
    current_credits = user.credits or 0
    txns_list = get_transactions_for_user(user_id)
    return jsonify({"currentCredits":current_credits, "transactions": txns_list})
