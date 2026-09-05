import pytest
from datetime import date, timedelta
from app.services.freshness import calculate_freshness

def test_freshness_fresh_product():
    today = date.today()
    mfd = (today - timedelta(days=2)).strftime("%Y-%m-%d")
    exp = (today + timedelta(days=20)).strftime("%Y-%m-%d")

    res = calculate_freshness(mfd_str=mfd, exp_str=exp)
    assert res.status == "FRESH"
    assert res.freshness_percentage > 60.0
    assert res.remaining_shelf_life_days == 20

def test_freshness_expired_product():
    today = date.today()
    mfd = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    exp = (today - timedelta(days=2)).strftime("%Y-%m-%d")

    res = calculate_freshness(mfd_str=mfd, exp_str=exp)
    assert res.status == "EXPIRED"
    assert res.freshness_percentage == 0.0
    assert res.remaining_shelf_life_days == -2

def test_freshness_invalid_dates_expiry_before_mfd():
    today = date.today()
    mfd = today.strftime("%Y-%m-%d")
    exp = (today - timedelta(days=5)).strftime("%Y-%m-%d")

    res = calculate_freshness(mfd_str=mfd, exp_str=exp)
    assert res.status == "INVALID_DATES"
    assert "Invalid dates" in res.evidence[0]

def test_freshness_missing_expiry():
    res = calculate_freshness(mfd_str="2026-08-01", exp_str=None)
    assert res.status == "MISSING_EXPIRY"
