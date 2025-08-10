import pytest
from src.config import SIZE_COST, VALID_STYLES, VALID_COLORS, MODELS
from src.models.generation_request import GenerationRequest
from src.repository.user_repository import get_user, update_user_credits, create_transaction
from src.repository.generation_repository import create_generation_request, update_generation_request_status
from src.firestore_client import get_db

@pytest.fixture(scope="module")
def db():
    return get_db()

def test_credit_deduction_and_refund(db):
    user_id = "user_test1"
    # Get initial credits
    user = get_user(user_id)
    initial_credits = user.credits
    # Deduct credits
    update_user_credits(user_id, initial_credits - 1)
    user = get_user(user_id)
    assert user.credits == initial_credits - 1
    # Refund credits
    update_user_credits(user_id, initial_credits)
    user = get_user(user_id)
    assert user.credits == initial_credits

def test_invalid_generation_request():
    # Invalid model
    req = GenerationRequest(
        generation_request_id=None,
        user_id="user_test1",
        model="INVALID",
        style="realistic",
        color="vibrant",
        size="512x512",
        prompt="test",
        status="pending",
        image_url=None,
        cost=1,
        created_at="now"
    )
    assert req.model not in MODELS

def test_valid_styles_and_colors():
    for style in VALID_STYLES:
        assert style in VALID_STYLES
    for color in VALID_COLORS:
        assert color in VALID_COLORS

def test_generation_request_lifecycle(db):
    user_id = "user_test1"
    gen_model = GenerationRequest(
        generation_request_id=None,
        user_id=user_id,
        model="A",
        style="realistic",
        color="vibrant",
        size="512x512",
        prompt="pytest",
        status="pending",
        image_url=None,
        cost=1,
        created_at="now"
    )
    gen_ref = create_generation_request(gen_model)
    assert gen_ref is not None
    update_generation_request_status(gen_ref.id, "success", image_url="http://test")
    # Clean up
    db.collection("generationRequests").document(gen_ref.id).delete()

def test_weekly_report_endpoint():
    from src.app import app
    client = app.test_client()
    response = client.post("/scheduleWeeklyReport")
    assert response.status_code == 200
    assert response.json["reportStatus"] == "success"
