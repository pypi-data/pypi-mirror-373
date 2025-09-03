#!/usr/bin/env python3
"""
pdf_brand_checker.py

Usage:
  python pdf_brand_checker.py /path/to/file.pdf \
      --brands /path/to/brands.json \
      [--password YOUR_PDF_PASSWORD]

What it does:
1) Detects the brand using the provided get_company_name() from pdf_name_extractor.py.
2) Extracts PDF metadata / internals using pdforensic:
   - extract_pdf_metadata
   - recover_pdf_versions
   - count_pdf_eof_markers
   - check_no_of_versions
3) Loads the brand "ground-truth" from brands.json and compares against
   the extracted values. Outputs a per-field match report and an overall
   percentage score.

Notes:
- Only non-empty expected fields in brands.json are scored.
- String comparisons are case-insensitive and trimmed.
- Numeric fields are compared as integers when possible.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Tuple

# Ensure we can import the user's pdf_name_extractor.py sitting next to this script
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

try:
    from pdf_name_extractor import get_company_name  # provided by user
except Exception as e:
    raise SystemExit(f"Failed to import get_company_name from pdf_name_extractor.py: {e}")

# pdforensic imports (must be installed in the environment where you run this script)
try:
    from pdforensic import (
        extract_pdf_metadata,
        recover_pdf_versions,
        count_pdf_eof_markers,
        check_no_of_versions
    )
except Exception as e:
    raise SystemExit(
        "Failed to import pdforensic. Please install it in your environment "
        "where this script runs.\n"
        f"Import error: {e}"
    )


# ---------- Helpers ----------

def normalize_key(s: str) -> str:
    """Normalize metadata keys for robust matching."""
    return s.strip().lower().replace(" ", "_")

def normalize_val(v: Any) -> str:
    """Normalize values for string-based comparison."""
    if v is None:
        return ""
    return str(v).strip().lower()

def coerce_int(val: Any) -> Tuple[bool, int]:
    """Try to coerce a value to int. Returns (ok, value_if_ok_or_0)."""
    try:
        return True, int(str(val).strip())
    except Exception:
        return False, 0

def pick_first_nonempty(*vals: Any) -> Any:
    for v in vals:
        if v not in (None, "", []):
            return v
    return ""

def extract_all(pdf_path: str, password: str = "") -> Dict[str, Any]:
    """Extract everything we need from pdforensic into a single dict."""
    meta = extract_pdf_metadata(pdf_path)  
    # meta is expected to be a dict-like; we normalize keys for lookups
    meta_norm = {normalize_key(k): v for k, v in (meta or {}).items()}

    # Versions / EOFs
    versions_detail = recover_pdf_versions(pdf_path)  
    eof_count = count_pdf_eof_markers(pdf_path)
    no_of_versions = check_no_of_versions(pdf_path)

    # Build a standardized view
    standardized = {
        # Common PD fields (best-effort fallbacks)
        "pdf_version": pick_first_nonempty(meta_norm.get("pdf_version"), meta_norm.get("version"), meta_norm.get("pdfversion")),
        "author": meta_norm.get("author", ""),
        "subject": meta_norm.get("subject", ""),
        "keywords": meta_norm.get("keywords", ""),
        "creator": meta_norm.get("creator", ""),
        "producer": meta_norm.get("producer", ""),
        "creationdate": pick_first_nonempty(meta_norm.get("creationdate"), meta_norm.get("created"), meta_norm.get("creation_date")),
        "moddate": pick_first_nonempty(meta_norm.get("moddate"), meta_norm.get("modified"), meta_norm.get("mod_date")),
        "trapped": meta_norm.get("trapped", ""),
        # Low-level
        "eof_markers": eof_count,
        "pdf_versions": no_of_versions,
        # Raw passthrough for reference
        "_raw_meta": meta,
        "_versions_detail": versions_detail,
    }
    return standardized

def load_brands(brands_json_path: str) -> Dict[str, List[Dict[str, Any]]]:
    with open(brands_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def best_brand_entry(brand_block: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    If multiple templates exist for a brand, choose the first non-empty
    or the one with the most filled fields. Simple heuristic.
    """
    if not brand_block:
        return {}
    # pick the dict with more non-empty values
    def filled_count(d):
        return sum(1 for k, v in d.items() if v not in (None, "", []))
    brand_block_sorted = sorted(brand_block, key=filled_count, reverse=True)
    return brand_block_sorted[0]

def compare_fields(extracted: Dict[str, Any], expected: Dict[str, Any]) -> Tuple[List[Tuple[str, Any, Any, bool]], float]:
    """
    Compare standardized extracted values against expected template fields.
    Only score non-empty expected fields.
    Returns:
      - list of tuples: (field_name, expected, actual, match_bool)
      - percentage score (0..100)
    """
    # Map some aliases from expected->extracted standardized keys
    key_map = {
        "pdf version": "pdf_version",
        "versions": "pdf_versions",
        "eof_markers": "eof_markers",
        "author": "author",
        "subject": "subject",
        "keywords": "keywords",
        "creator": "creator",
        "producer": "producer",
        "creationdate": "creationdate",
        "moddate": "moddate",
        "trapped": "trapped",
        # allow underscores too
        "pdf_version": "pdf_version",
        "creation_date": "creationdate",
        "mod_date": "moddate",
    }

    results: List[Tuple[str, Any, Any, bool]] = []
    considered = 0
    matched = 0

    for k, v in expected.items():
        if k == "brand":
            # we don't score the brand name here
            continue
        if v in (None, "", []):
            # skip empty expected
            continue
            
        # Skip creationdate and moddate as we'll handle them specially
        k_norm = normalize_key(k)
        if k_norm in ("creationdate", "creation_date", "moddate", "mod_date"):
            continue

        target_key = key_map.get(k_norm, k_norm)
        actual = extracted.get(target_key, "")

        # Numeric comparisons for Versions / eof markers
        if target_key in ("pdf_versions", "eof_markers"):
            ok1, v_int = coerce_int(v)
            ok2, a_int = coerce_int(actual)
            is_match = ok1 and ok2 and (v_int == a_int)
        else:
            # String compare (case-insensitive)
            is_match = normalize_val(v) == normalize_val(actual)

        considered += 1
        matched += 1 if is_match else 0
        results.append((target_key, v, actual, is_match))
    
    # Special check for creation date equals modification date
    creation_date = extracted.get("creationdate", "")
    mod_date = extracted.get("moddate", "")
    dates_equal = normalize_val(creation_date) == normalize_val(mod_date)
    
    # Add this to results with a special field name
    considered += 1
    matched += 1 if dates_equal else 0
    results.append(("dates_equal_check", "True" if dates_equal else "False", 
                   f"creationdate({creation_date}) == moddate({mod_date})", dates_equal))

    pct = (matched / considered * 100.0) if considered else 0.0
    return results, pct

def main():
    ap = argparse.ArgumentParser(description="Check PDF brand and compare metadata against brands.json template.")
    ap.add_argument("pdf", help="Path to the PDF to check")
    ap.add_argument("--brands", default=os.path.join(THIS_DIR, "brands.json"), help="Path to brands.json")
    ap.add_argument("--password", default="", help="PDF password if any")
    args = ap.parse_args()

    pdf_path = os.path.abspath(args.pdf)
    brands_json_path = os.path.abspath(args.brands)

    if not os.path.exists(pdf_path):
        raise SystemExit(f"PDF not found: {pdf_path}")
    if not os.path.exists(brands_json_path):
        raise SystemExit(f"brands.json not found: {brands_json_path}")

    # 1) Detect brand
    detected_brand = get_company_name(pdf_path, password=args.password)

    # 2) Extract metadata & internals
    extracted = extract_all(pdf_path)  # Removed password parameter

    # 3) Load expected templates
    brands = load_brands(brands_json_path)
    brand_key = normalize_val(detected_brand)
    # brands.json keys look like 'vodacom', 'absa_cbs', etc; use detected key directly
    expected_block = brands.get(brand_key, [])

    # If detection failed, try fallback: pick nothing to compare
    if not expected_block:
        print(f"[!] Brand '{detected_brand}' not found in brands.json. Scoring skipped.\n")
        print("Extracted summary (for reference):")
        for k in ("pdf_version", "author", "subject", "keywords", "creator", "producer", "creationdate", "moddate", "trapped", "eof_markers", "pdf_versions"):
            print(f"  {k}: {extracted.get(k, '')}")
        sys.exit(2)

    expected = best_brand_entry(expected_block)

    # 4) Compare
    results, pct = compare_fields(extracted, expected)

    # 5) Report
    print("=" * 72)
    print(f"PDF: {pdf_path}")
    print(f"Detected brand: {detected_brand}")
    print(f"Template in use: {brand_key}")
    print("-" * 72)
    print("Field Comparison (expected vs. actual):")
    for field, exp, act, ok in results:
        status = "✓" if ok else "✗"
        print(f"  [{status}] {field:15s}  expected={exp!r}  actual={act!r}")
    print("-" * 72)
    print(f"Score: {pct:.1f}% match")
    print("=" * 72)

    # Optional: exit code thresholding if needed
    # sys.exit(0 if pct >= 80 else 1)


def verify_statement_verbose(pdf_path: str, brands_json_path: str = None, password: str = "") -> Dict[str, Any]:
    """
    Perform complete statement verification and return verbose results.
    
    Args:
        pdf_path: Path to the PDF file to verify
        brands_json_path: Path to brands.json file (defaults to package default)
        password: PDF password if required
    
    Returns:
        Dictionary containing:
        - pdf_path: Path to the PDF file
        - detected_brand: Brand detected from PDF
        - template_used: Template key used for comparison
        - verification_score: Percentage score (0-100)
        - field_results: List of field comparison results
        - extracted_metadata: Raw extracted metadata
        - expected_metadata: Expected metadata template
        - summary: Human-readable summary
    """
    if brands_json_path is None:
        brands_json_path = os.path.join(THIS_DIR, "statements_metadata.json")
    
    pdf_path = os.path.abspath(pdf_path)
    brands_json_path = os.path.abspath(brands_json_path)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if not os.path.exists(brands_json_path):
        raise FileNotFoundError(f"brands.json not found: {brands_json_path}")

    # 1) Detect brand
    detected_brand = get_company_name(pdf_path, password=password)

    # 2) Extract metadata & internals
    extracted = extract_all(pdf_path)

    # 3) Load expected templates
    brands = load_brands(brands_json_path)
    brand_key = normalize_val(detected_brand)
    expected_block = brands.get(brand_key, [])

    # If detection failed, return error info
    if not expected_block:
        return {
            "pdf_path": pdf_path,
            "detected_brand": detected_brand,
            "template_used": None,
            "verification_score": 0.0,
            "field_results": [],
            "extracted_metadata": extracted,
            "expected_metadata": {},
            "summary": f"Brand '{detected_brand}' not found in brands.json. No template available for comparison.",
            "error": f"Brand '{detected_brand}' not found in templates"
        }

    expected = best_brand_entry(expected_block)

    # 4) Compare
    results, pct = compare_fields(extracted, expected)

    # 5) Build field results with detailed info
    field_results = []
    for field, exp, act, ok in results:
        field_results.append({
            "field": field,
            "expected": exp,
            "actual": act,
            "match": ok,
            "status": "✓" if ok else "✗"
        })

    # 6) Create summary
    total_fields = len(field_results)
    matched_fields = sum(1 for r in field_results if r["match"])
    
    summary_lines = [
        f"PDF: {os.path.basename(pdf_path)}",
        f"Detected brand: {detected_brand}",
        f"Template used: {brand_key}",
        f"Fields checked: {total_fields}",
        f"Fields matched: {matched_fields}",
        f"Verification score: {pct:.1f}%"
    ]
    
    return {
        "pdf_path": pdf_path,
        "detected_brand": detected_brand,
        "template_used": brand_key,
        "verification_score": pct,
        "field_results": field_results,
        "extracted_metadata": extracted,
        "expected_metadata": expected,
        "summary": "\n".join(summary_lines),
        "total_fields": total_fields,
        "matched_fields": matched_fields
    }


def print_verification_report(verification_result: Dict[str, Any]) -> None:
    """
    Print a formatted verification report from verification results.
    
    Args:
        verification_result: Result from verify_statement_verbose()
    """
    result = verification_result
    
    print("=" * 72)
    print(result["summary"])
    print("-" * 72)
    print("Field Comparison (expected vs. actual):")
    
    for field_result in result["field_results"]:
        status = field_result["status"]
        field = field_result["field"]
        exp = field_result["expected"]
        act = field_result["actual"]
        print(f"  [{status}] {field:15s}  expected={exp!r}  actual={act!r}")
    
    print("-" * 72)
    print(f"Score: {result['verification_score']:.1f}% match")
    print("=" * 72)


if __name__ == "__main__":
    main()
