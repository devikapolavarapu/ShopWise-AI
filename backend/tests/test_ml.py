from app.ml.model import predictor

def test_ml_stockout_prediction_high_stock():
    avail_conf, stockout_risk = predictor.predict_availability(
        current_stock=40,
        daily_sales_average=10.0,
        recent_sales=10.0,
        store_reliability=0.98
    )
    assert avail_conf >= 0.70
    assert stockout_risk <= 0.30

def test_ml_stockout_prediction_low_stock():
    avail_conf, stockout_risk = predictor.predict_availability(
        current_stock=2,
        daily_sales_average=25.0,
        recent_sales=30.0,
        store_reliability=0.85
    )
    assert stockout_risk >= 0.40
