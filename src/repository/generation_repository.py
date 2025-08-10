from src.firestore_client import get_db
from src.models.generation_request import GenerationRequest
from typing import Optional

def create_generation_request(model: GenerationRequest, transaction=None):
    db = get_db()
    # If model.generation_request_id is None, let Firestore auto-generate the ID
    if model.generation_request_id:
        gen_ref = db.collection("generationRequests").document(model.generation_request_id)
    else:
        gen_ref = db.collection("generationRequests").document()
    data = generation_request_to_dict(model)
    # Always set the document ID in the data for consistency
    data["id"] = gen_ref.id
    if transaction:
        transaction.set(gen_ref, data)
    else:
        gen_ref.set(data)
    return gen_ref

def update_generation_request_status(gen_id, status, image_url=None, error=None, transaction=None):
    db = get_db()
    gen_ref = db.collection("generationRequests").document(gen_id)
    update_data = {"status": status}
    if image_url is not None:
        update_data["imageUrl"] = image_url
    if error is not None:
        update_data["error"] = error
    if transaction:
        transaction.update(gen_ref, update_data)
    else:
        gen_ref.update(update_data)

def generation_request_to_dict(model: GenerationRequest) -> dict:
    return {
        "userId": model.user_id,
        "model": model.model,
        "style": model.style,
        "color": model.color,
        "size": model.size,
        "prompt": model.prompt,
        "status": model.status,
        "imageUrl": model.image_url,
        "cost": model.cost,
        "createdAt": model.created_at,
        "completedAt": model.completed_at,
    }

def generation_request_from_dict(doc_id: str, data: dict) -> GenerationRequest:
    return GenerationRequest(
        generation_request_id=doc_id,
        user_id=data.get("userId"),
        model=data.get("model"),
        style=data.get("style"),
        color=data.get("color"),
        size=data.get("size"),
        prompt=data.get("prompt"),
        status=data.get("status"),
        image_url=data.get("imageUrl"),
        cost=data.get("cost"),
        created_at=data.get("createdAt"),
        completed_at=data.get("completedAt"),
    )
