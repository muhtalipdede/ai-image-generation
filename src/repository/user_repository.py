from src.firestore_client import get_db
from src.models.user import User
from src.models.transaction import Transaction
from typing import Optional

def get_user(user_id) -> Optional[User]:
    db = get_db()
    doc = db.collection("users").document(user_id).get()
    if not doc.exists:
        return None
    return user_from_dict(doc.id, doc.to_dict())

def update_user_credits(user_id, new_credits, transaction=None):
    db = get_db()
    user_ref = db.collection("users").document(user_id)
    if transaction:
        transaction.update(user_ref, {"credits": new_credits})
    else:
        user_ref.update({"credits": new_credits})

def create_transaction(user_id, txn_type, credits, generation_request_id, transaction=None):
    db = get_db()
    txn_ref = db.collection("transactions").document()
    txn = Transaction(
        transaction_id=txn_ref.id,
        user_id=user_id,
        type=txn_type,
        credits=credits,
        generation_request_id=generation_request_id,
        timestamp=db._client.SERVER_TIMESTAMP if hasattr(db._client, 'SERVER_TIMESTAMP') else None
    )
    txn_data = transaction_to_dict(txn)
    if transaction:
        transaction.set(txn_ref, txn_data)
    else:
        txn_ref.set(txn_data)

def user_from_dict(doc_id, data) -> User:
    return User(
        user_id=doc_id,
        display_name=data.get("displayName", ""),
        credits=data.get("credits", 0)
    )

def transaction_to_dict(txn: Transaction) -> dict:
    return {
        "userId": txn.user_id,
        "type": txn.type,
        "credits": txn.credits,
        "generationRequestId": txn.generation_request_id,
        "timestamp": txn.timestamp
    }

def transaction_from_dict(doc_id, data) -> Transaction:
    return Transaction(
        transaction_id=doc_id,
        user_id=data.get("userId"),
        type=data.get("type"),
        credits=data.get("credits"),
        generation_request_id=data.get("generationRequestId"),
        timestamp=data.get("timestamp")
    )
