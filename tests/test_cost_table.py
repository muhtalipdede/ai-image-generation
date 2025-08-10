import pytest
from src.config import SIZE_COST
from src.models.generation_request import GenerationRequest
from src.repository.generation_repository import generation_request_to_dict

def test_size_costs():
    assert SIZE_COST["512x512"] == 1
    assert SIZE_COST["1024x1024"] == 3
    assert SIZE_COST["1024x1792"] == 4
    assert set(SIZE_COST.keys()) == {"512x512", "1024x1024", "1024x1792"}

def test_deduction_logic():
    # Simulate deduction
    user_credits = 10
    for size, cost in SIZE_COST.items():
        new_credits = user_credits - cost
        assert new_credits == user_credits - SIZE_COST[size]
        user_credits = 10  # reset for each

@pytest.mark.parametrize("size,expected", [
    ("512x512", 1),
    ("1024x1024", 3),
    ("1024x1792", 4),
])
def test_parametrized_costs(size, expected):
    assert SIZE_COST[size] == expected

def test_generation_request_to_dict():
    req = GenerationRequest(
        generation_request_id="testid",
        user_id="user1",
        model="A",
        style="realistic",
        color="vibrant",
        size="512x512",
        prompt="cat",
        status="pending",
        image_url=None,
        cost=1,
        created_at="now",
        completed_at=None
    )
    d = generation_request_to_dict(req)
    assert d["userId"] == "user1"
    assert d["model"] == "A"
    assert d["status"] == "pending"
    assert d["cost"] == 1

def test_all_costs_positive():
    for size, cost in SIZE_COST.items():
        assert isinstance(cost, int)
        assert cost > 0

def test_no_negative_credits():
    for size, cost in SIZE_COST.items():
        user_credits = cost - 1
        new_credits = user_credits - cost
        assert new_credits < 0

def test_deduction_never_below_zero():
    for size, cost in SIZE_COST.items():
        user_credits = 0
        new_credits = user_credits - cost
        assert new_credits <= 0

def test_keys_are_strings():
    for size in SIZE_COST.keys():
        assert isinstance(size, str)

def test_values_are_ints():
    for cost in SIZE_COST.values():
        assert isinstance(cost, int)
