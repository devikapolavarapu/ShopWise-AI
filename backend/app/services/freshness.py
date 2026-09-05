from datetime import datetime, date
from typing import Optional, List, Dict, Tuple
from app.schemas.entities import FreshnessCalculateResponse

def calculate_freshness(
    mfd_str: Optional[str] = None,
    exp_str: Optional[str] = None,
    scanned_date_str: Optional[str] = None
) -> FreshnessCalculateResponse:
    """
    Deterministically computes remaining shelf life and freshness classification.
    Date formats expected: YYYY-MM-DD or DD/MM/YYYY.
    """
    evidence: List[str] = []
    
    current_dt = date.today()
    if scanned_date_str:
        try:
            current_dt = datetime.strptime(scanned_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    if not exp_str:
        return FreshnessCalculateResponse(
            manufacturing_date=mfd_str,
            expiry_date=None,
            total_shelf_life_days=None,
            remaining_shelf_life_days=None,
            freshness_percentage=0.0,
            status="MISSING_EXPIRY",
            evidence=["Expiry date is missing or unreadable on product label."]
        )

    # Parse Expiry Date
    exp_dt = parse_date_string(exp_str)
    if not exp_dt:
        return FreshnessCalculateResponse(
            manufacturing_date=mfd_str,
            expiry_date=exp_str,
            total_shelf_life_days=None,
            remaining_shelf_life_days=None,
            freshness_percentage=0.0,
            status="INVALID_DATES",
            evidence=[f"Expiry date '{exp_str}' could not be parsed into a valid calendar date."]
        )

    # Parse Manufacturing Date if present
    mfd_dt = parse_date_string(mfd_str) if mfd_str else None

    # Check for invalid condition: Expiry before MFD
    if mfd_dt and exp_dt < mfd_dt:
        return FreshnessCalculateResponse(
            manufacturing_date=mfd_dt.strftime("%Y-%m-%d"),
            expiry_date=exp_dt.strftime("%Y-%m-%d"),
            total_shelf_life_days=None,
            remaining_shelf_life_days=None,
            freshness_percentage=0.0,
            status="INVALID_DATES",
            evidence=["Invalid dates: Expiry date is recorded prior to Manufacturing date."]
        )

    # Calculate remaining shelf life
    remaining_days = (exp_dt - current_dt).days

    if remaining_days < 0:
        return FreshnessCalculateResponse(
            manufacturing_date=mfd_dt.strftime("%Y-%m-%d") if mfd_dt else None,
            expiry_date=exp_dt.strftime("%Y-%m-%d"),
            total_shelf_life_days=(exp_dt - mfd_dt).days if mfd_dt else None,
            remaining_shelf_life_days=remaining_days,
            freshness_percentage=0.0,
            status="EXPIRED",
            evidence=[f"Product expired {abs(remaining_days)} days ago on {exp_dt.strftime('%d-%b-%Y')}."]
        )

    # If MFD is available, calculate exact percentage of total shelf life
    if mfd_dt:
        total_days = (exp_dt - mfd_dt).days
        if total_days <= 0:
            total_days = 1
        freshness_pct = round(max(0.0, min(100.0, (remaining_days / total_days) * 100.0)), 1)
        evidence.append(f"Total shelf life: {total_days} days. Remaining: {remaining_days} days.")
    else:
        # Default assume 14-day standard dairy/bakery shelf life if MFD missing
        total_days = 14
        freshness_pct = round(max(0.0, min(100.0, (remaining_days / total_days) * 100.0)), 1)
        evidence.append(f"Manufacturing date missing. Estimated from {remaining_days} days remaining to expiry.")

    # Status classification
    if freshness_pct > 70.0:
        status = "FRESH"
    elif freshness_pct >= 30.0:
        status = "GOOD"
    elif freshness_pct >= 10.0:
        status = "USE_SOON"
    else:
        status = "NEAR_EXPIRY"

    evidence.append(f"{freshness_pct}% shelf life remaining ({remaining_days} days left).")

    return FreshnessCalculateResponse(
        manufacturing_date=mfd_dt.strftime("%Y-%m-%d") if mfd_dt else None,
        expiry_date=exp_dt.strftime("%Y-%m-%d"),
        total_shelf_life_days=(exp_dt - mfd_dt).days if mfd_dt else None,
        remaining_shelf_life_days=remaining_days,
        freshness_percentage=freshness_pct,
        status=status,
        evidence=evidence
    )

def parse_date_string(date_str: str) -> Optional[date]:
    """Helper to parse common Indian grocery date formats."""
    if not date_str:
        return None

    clean_str = date_str.strip()
    formats = [
        "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y",
        "%m/%Y", "%m-%Y", "%d/%m/%y", "%d-%m-%y"
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(clean_str, fmt)
            # If format was MM/YYYY, set day to end of month or 1st
            if fmt in ["%m/%Y", "%m-%Y"]:
                # set to 1st of month
                dt = datetime(dt.year, dt.month, 1)
            return dt.date()
        except ValueError:
            continue

    return None
