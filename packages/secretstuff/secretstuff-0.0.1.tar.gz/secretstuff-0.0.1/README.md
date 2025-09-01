# SecretStuff

A comprehensive, production-ready Python library for identifying, redacting, and reversing personally identifiable information (PII) in text documents using advanced NLP models.

## Features

- **PII Identification**: Uses GLiNER model to identify 150+ types of PII including names, addresses, phone numbers, government IDs, and more
- **Flexible Redaction**: Replace identified PII with configurable dummy values while preserving document structure
- **Reverse Mapping**: Restore original PII from redacted text using secure mapping files
- **Modular Architecture**: Use components independently or through unified pipeline
- **Extensive Coverage**: Comprehensive support for Indian and international PII types
- **Production Ready**: Type hints, comprehensive tests, and robust error handling

## Installation

```bash
pip install secretstuff
```

## Quick Start

### Simple Pipeline Usage

```python
from secretstuff import SecretStuffPipeline

# Initialize pipeline
pipeline = SecretStuffPipeline()

# Your sensitive text
text = """
Mr. John Doe lives at 123 Main Street, New York.
His phone number is +1-555-123-4567 and email is john.doe@email.com.
His Aadhaar number is 1234 5678 9012 and PAN is ABCDE1234F.
"""

# Identify and redact PII in one step
redacted_text, entities, mapping = pipeline.identify_and_redact(text)

print("Redacted:", redacted_text)
print("Found entities:", entities)
```

### Step-by-Step Process

```python
from secretstuff import SecretStuffPipeline

pipeline = SecretStuffPipeline()

# Step 1: Identify PII
entities = pipeline.identify_pii(text)
print("Identified PII:", entities)

# Step 2: Redact PII
redacted_text = pipeline.redact_pii(text)
print("Redacted text:", redacted_text)

# Step 3: After cloud LLM processing, reverse the redaction
restored_text, count, details = pipeline.reverse_redaction(processed_text)
print("Restored text:", restored_text)
```

### File Processing

```python
# Process files
result = pipeline.process_text_file(
    input_file="document.txt",
    output_redacted="redacted_document.txt",
    output_identified="identified_entities.json",
    output_mapping="replacement_mapping.json"
)

# Later, reverse the redaction
reverse_result = pipeline.reverse_from_files(
    redacted_file="processed_document.txt",  # After LLM processing
    mapping_file="replacement_mapping.json",
    output_file="final_document.txt"
)
```

## Component Usage

### Individual Components

```python
from secretstuff import PIIIdentifier, PIIRedactor, ReverseMapper

# Use components individually
identifier = PIIIdentifier()
redactor = PIIRedactor()
reverse_mapper = ReverseMapper()

# Identify PII
entities = identifier.identify_entities(text)

# Redact PII
redacted = redactor.redact_from_identified_entities(text, entities)

# Reverse redaction
reverse_mapper.set_replacement_mapping(redactor.get_replacement_mapping())
restored, count, details = reverse_mapper.reverse_redaction(redacted)
```

### Custom Configuration

```python
from secretstuff import SecretStuffPipeline

# Custom labels and dummy values
custom_labels = ["person", "email", "phone number", "custom_entity"]
custom_dummy_values = {
    "person": ["[PERSON_A]", "[PERSON_B]", "[PERSON_C]"],
    "email": "[EMAIL_REDACTED]",
    "custom_entity": "[CUSTOM_REDACTED]"
}

pipeline = SecretStuffPipeline(
    labels=custom_labels,
    dummy_values=custom_dummy_values
)

# Or configure after initialization
pipeline.configure_labels(custom_labels)
pipeline.configure_dummy_values(custom_dummy_values)
```

## Supported PII Types

SecretStuff identifies 150+ types of PII including:

### Personal Information
- Names, addresses, phone numbers, email addresses
- Dates of birth, ages, places of birth
- Family relationships (father's name, mother's name, etc.)

### Government IDs (India)
- Aadhaar numbers, PAN numbers, Voter IDs
- Passport numbers, driving licenses
- Various state and central government IDs

### Financial Information
- Bank account numbers, IFSC codes, UPI IDs
- Credit/debit card numbers, cheque numbers
- GST numbers, tax identification numbers

### Legal & Court Documents
- Case numbers, FIR numbers, court order numbers
- CNR numbers, filing numbers, petition numbers

### Corporate Information
- CIN numbers, trade license numbers
- Professional registration numbers

### Technical Identifiers
- IP addresses, MAC addresses, device serial numbers
- IMEI numbers, device identifiers

[and more....]

## API Reference

### SecretStuffPipeline

The main interface for all operations:

```python
class SecretStuffPipeline:
    def identify_pii(text: str, chunk_size: int = 384) -> Dict[str, List[str]]
    def redact_pii(text: str, entities: Optional[Dict] = None) -> str
    def identify_and_redact(text: str) -> Tuple[str, Dict, Dict]
    def reverse_redaction(redacted_text: str, mapping: Optional[Dict] = None) -> Tuple[str, int, Dict]
    def process_text_file(input_file: str, **kwargs) -> Dict
    def reverse_from_files(redacted_file: str, mapping_file: str, output_file: str) -> Dict
```

### PIIIdentifier

```python
class PIIIdentifier:
    def identify_entities(text: str, chunk_size: int = 384) -> List[Dict]
    def create_entity_mapping(entities: List[Dict]) -> Dict[str, List[str]]
    def add_custom_labels(labels: List[str]) -> None
    def set_labels(labels: List[str]) -> None
```

### PIIRedactor

```python
class PIIRedactor:
    def create_replacement_mapping(entities: Dict[str, List[str]]) -> Dict[str, str]
    def redact_text(text: str, mapping: Dict[str, str]) -> str
    def redact_from_identified_entities(text: str, entities: Dict) -> str
    def set_dummy_values(dummy_values: Dict) -> None
```

### ReverseMapper

```python
class ReverseMapper:
    def reverse_redaction(redacted_text: str) -> Tuple[str, int, Dict]
    def load_replacement_mapping(mapping_file: str) -> None
    def validate_mapping() -> bool
    def get_mapping_statistics() -> Dict
```

## Advanced Usage

### Custom Model

```python
pipeline = SecretStuffPipeline(
    model_name="your-custom-gliner-model"
)
```

### Batch Processing

```python
# Process multiple files
files = ["doc1.txt", "doc2.txt", "doc3.txt"]
results = []

for file in files:
    result = pipeline.process_text_file(file)
    results.append(result)
```

## Use Cases

### 1. Cloud LLM Data Protection

```python
# Before sending to cloud LLM
original_text = "Patient John Doe (DOB: 1985-03-15) visited on..."
redacted_text, entities, mapping = pipeline.identify_and_redact(original_text)

# Send redacted_text to cloud LLM
llm_response = call_cloud_llm(redacted_text)

# Restore original PII in response
final_response, _, _ = pipeline.reverse_redaction(llm_response, mapping)
```

### 2. Document Anonymization

```python
# Remove PII from documents permanently
entities = pipeline.identify_pii(document_text)
anonymized = pipeline.redact_pii(document_text, entities)
# Don't save the mapping for permanent anonymization
```

### 3. Data Processing Pipeline

```python
# Part of larger data processing workflow
def process_sensitive_documents(input_dir, output_dir):
    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f"redacted_{filename}")
        
        pipeline.process_text_file(
            input_file=input_path,
            output_redacted=output_path
        )
```

## Configuration

### Environment Variables

```bash
export SECRETSTUFF_MODEL_NAME="urchade/gliner_multi_pii-v1"
export SECRETSTUFF_CHUNK_SIZE="384"
export SECRETSTUFF_CACHE_DIR="/path/to/cache"
```

### Custom Configuration File

```python
# config.py
CUSTOM_LABELS = ["person", "email", "phone", "custom_field"]
CUSTOM_DUMMY_VALUES = {
    "custom_field": "[CUSTOM_REDACTED]"
}

# main.py
from config import CUSTOM_LABELS, CUSTOM_DUMMY_VALUES
pipeline = SecretStuffPipeline(
    labels=CUSTOM_LABELS,
    dummy_values=CUSTOM_DUMMY_VALUES
)
```

## Performance Considerations

- **Model Caching**: GLiNER model is cached after first load
- **Batch Processing**: Process multiple documents in batches for efficiency

## Error Handling

```python
from secretstuff import SecretStuffPipeline
from secretstuff.exceptions import SecretStuffError

try:
    pipeline = SecretStuffPipeline()
    result = pipeline.identify_and_redact(text)
except SecretStuffError as e:
    print(f"SecretStuff error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Testing

Run the test suite:

```bash
# Install dev dependencies
pip install secretstuff[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=secretstuff --cov-report=html
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: https://github.com/adw777/secretStuff/blob/main/README.md
- Issues: https://github.com/adw777/secretStuff/issues
- Email: amandogra2016@gmail.com

## Changelog

### v0.0.1
- Initial release
- PII identification with GLiNER
- Flexible redaction system
- Reverse mapping functionality
- Comprehensive test suite
- Production-ready API
