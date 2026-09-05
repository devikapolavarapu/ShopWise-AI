from typing import Dict, Any, Tuple, List

class CVProductMatcher:
    def match_product(
        self,
        extracted_text: str,
        detected_brand: str = None,
        target_product_name: str = "Amul Milk"
    ) -> Tuple[str, float, List[str]]:
        """
        Evaluates visual/textual product match against target product.
        Returns:
            match_status: "Likely Match", "Uncertain", or "Mismatch"
            confidence: float (0.0 to 1.0)
            evidence: List of matching observations
        """
        evidence = []
        if not extracted_text:
            return "Uncertain", 0.30, ["Insufficient text extracted from image to verify product identity."]

        text_lower = extracted_text.lower()
        target_lower = target_product_name.lower()
        target_tokens = set(target_lower.split())

        # 1. Brand match check
        brand_matched = False
        if detected_brand and detected_brand.lower() in text_lower:
            brand_matched = True
            evidence.append(f"Brand match verified: '{detected_brand}' found on product packaging.")
        else:
            for token in target_tokens:
                if len(token) > 3 and token in text_lower:
                    evidence.append(f"Keyword match: '{token}' identified on packaging.")
                    brand_matched = True

        # 2. Token overlap score
        found_tokens = [t for t in target_tokens if t in text_lower]
        overlap_ratio = len(found_tokens) / max(1, len(target_tokens))

        if brand_matched and overlap_ratio >= 0.5:
            confidence = round(min(0.98, 0.70 + 0.28 * overlap_ratio), 2)
            match_status = "Likely Match"
            evidence.append(f"Product text matches requested item '{target_product_name}'.")
        elif brand_matched or overlap_ratio >= 0.3:
            confidence = 0.65
            match_status = "Uncertain"
            evidence.append(f"Partial text match found for '{target_product_name}'. Please verify label manually.")
        else:
            confidence = 0.20
            match_status = "Mismatch"
            evidence.append(f"Packaging text does not match target product '{target_product_name}'.")

        return match_status, confidence, evidence

cv_matcher = CVProductMatcher()
