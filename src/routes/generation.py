from flask import Blueprint, request, jsonify
from google.cloud import firestore
from src.config import SIZE_COST, VALID_STYLES, VALID_COLORS, MODELS
import random
from src.repository.user_repository import get_user, update_user_credits, create_transaction
from src.repository.generation_repository import create_generation_request, update_generation_request_status
from src.models.generation_request import GenerationRequest

generation_bp = Blueprint('generation', __name__)

def get_db():
    # Kept for transactional context
    from src.firestore_client import get_db as _get_db
    return _get_db()

generation_db = get_db()

@generation_bp.route('/createGenerationRequest', methods=['POST'])
def create_generation_request():
    data = request.get_json()
    required = ["userId","model","style","color","size","prompt"]
    for r in required:
        if r not in data:
            return jsonify({"error": f"missing {r}"}), 400

    user_id = data["userId"]
    model = data["model"]
    style = data["style"]
    color = data["color"]
    size = data["size"]
    prompt = data["prompt"]

    # validation
    if model not in MODELS:
        return jsonify({"error":"invalid model"}), 400
    if style not in VALID_STYLES:
        return jsonify({"error":"invalid style"}), 400
    if color not in VALID_COLORS:
        return jsonify({"error":"invalid color"}), 400
    if size not in SIZE_COST:
        return jsonify({"error":"invalid size"}), 400

    cost = SIZE_COST[size]

    @firestore.transactional
    def txn_func(transaction):
        user = get_user(user_id)
        if user is None:
            raise RuntimeError("user_not_found")
        current = user.credits or 0
        if current < cost:
            raise RuntimeError("insufficient_credits")
        new_credits = current - cost
        update_user_credits(user_id, new_credits, transaction)
        gen_model = GenerationRequest(
            generation_request_id=None,  # Let Firestore auto-generate ID
            user_id=user_id,
            model=model,
            style=style,
            color=color,
            size=size,
            prompt=prompt,
            status="pending",
            image_url=None,
            cost=cost,
            created_at=firestore.SERVER_TIMESTAMP,
            completed_at=None
        )
        gen_ref = create_generation_request(gen_model, transaction)
        create_transaction(user_id, "deduction", cost, gen_ref.id, transaction)
        return new_credits, gen_ref.id

    transaction = generation_db.transaction()
    try:
        new_credits, gen_id = txn_func(transaction)
    except Exception as e:
        msg = str(e)
        if msg == "insufficient_credits":
            return jsonify({"error":"insufficient credits"}), 400
        elif msg == "user_not_found":
            return jsonify({"error":"user not found"}), 404
        else:
            return jsonify({"error":"transaction failed", "detail": msg}), 500

    from threading import Thread
    Thread(target=process_generation, args=(gen_id,)).start()

    return jsonify({
        "generationRequestId": gen_id,
        "deductedCredits": cost,
        "currentCredits": new_credits
    }), 201

def process_generation(gen_id):
    db = get_db()
    gen_ref = db.collection("generationRequests").document(gen_id)
    gen_snap = gen_ref.get()
    if not gen_snap.exists:
        return
    data = gen_snap.to_dict()
    model = data["model"]
    cost = data["cost"]
    user_id = data["userId"]
    model_cfg = MODELS[model]
    import time; time.sleep(1)
    if random.random() < model_cfg["failRate"]:
        @firestore.transactional
        def refund_txn(transaction):
            user_snap = get_user(user_id)
            current = user_snap.get("credits") or 0
            update_user_credits(user_id, current + cost, transaction)
            create_transaction(user_id, "refund", cost, gen_id, transaction)
            update_generation_request_status(gen_id, "failed", error="simulated_failure", transaction=transaction)
        try:
            t = db.transaction()
            refund_txn(t)
        except Exception:
            pass
    else:
        update_generation_request_status(gen_id, "success", image_url=model_cfg["placeholderUrl"])
