# Statement Verification

A Python package for verifying PDF statements from financial institutions. Extracts metadata, detects the issuing institution, and provides verification scores.

## Installation

```bash
# From PyPI (recommended)
pip install sverification

# Or from source
git clone https://github.com/Tausi-Africa/statement-verification.git
cd statement-verification
pip install -e .
```

## Usage

### Command Line

```bash
# Verify a PDF statement
verify-statement path/to/statement.pdf --brands statements_metadata.json
```

### Python API

```python
import sverification

# Simple verification
result = sverification.verify_statement_verbose("statement.pdf")
print(f"Brand: {result['detected_brand']}")
print(f"Score: {result['verification_score']:.1f}%")

# Print detailed report
sverification.print_verification_report(result)
```

### Step-by-Step Analysis

```python
import sverification

# Extract metadata
metadata = sverification.extract_all("statement.pdf")

# Detect company
company = sverification.get_company_name("statement.pdf")

# Compare with templates
brands = sverification.load_brands("statements_metadata.json")
expected = brands.get(company.lower(), [{}])[0]
results, score = sverification.compare_fields(metadata, expected)

print(f"Verification Score: {score:.1f}%")
```

## Supported Institutions

Banks: ABSA, CRDB, DTB, Exim, NMB, NBC, TCB, UBA  
Mobile Money: Airtel, Tigo, Vodacom, Halotel, Selcom  
Others: Azam Pesa, PayMaart, and more...

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=sverification
```

## License

Proprietary software licensed under Black Swan AI Global. See [LICENSE](LICENSE) for details.
