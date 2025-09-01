"""Basic usage examples for SecretStuff package."""

from secretstuff import SecretStuffPipeline

def basic_example():
    """Basic PII identification and redaction example."""
    # Initialize pipeline
    pipeline = SecretStuffPipeline()
    
    # Sample text with PII
    text = """
    Mr. Rajesh Kumar lives at H-25, Lajpat Nagar-II, New Delhi - 110024.
    His phone number is +91-9876543210 and email is rajesh.kumar@email.com.
    His Aadhaar number is 4578 1234 9087 and PAN is ABCPK2345L.
    The company TechNova Solutions Pvt. Ltd. has CIN: U74999DL2018PTC123456.
    """
    
    print("Original text:")
    print(text)
    print("\n" + "="*50 + "\n")
    
    # Identify PII
    print("Step 1: Identifying PII...")
    entities = pipeline.identify_pii(text)
    print("Identified entities:")
    for label, items in entities.items():
        print(f"  {label}: {items}")
    
    print("\n" + "="*50 + "\n")
    
    # Redact PII
    print("Step 2: Redacting PII...")
    redacted_text = pipeline.redact_pii(text)
    print("Redacted text:")
    print(redacted_text)
    
    print("\n" + "="*50 + "\n")
    
    # Get replacement mapping
    mapping = pipeline.get_last_replacement_mapping()
    print("Replacement mapping:")
    for original, dummy in mapping.items():
        print(f"  '{original}' -> '{dummy}'")
    
    print("\n" + "="*50 + "\n")
    
    # Simulate cloud LLM processing (just return the same text for demo)
    processed_text = redacted_text  # In real scenario, this would be LLM output
    
    # Reverse redaction
    print("Step 3: Reversing redaction...")
    restored_text, total_replaced, replacement_details = pipeline.reverse_redaction(processed_text)
    print("Restored text:")
    print(restored_text)
    print(f"\nTotal replacements made: {total_replaced}")
    print("Replacement details:")
    for dummy, count in replacement_details.items():
        print(f"  '{dummy}' replaced {count} times")


def file_processing_example():
    """Example of processing files."""
    import tempfile
    import os
    
    # Create sample input file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""
        Patient Information:
        Name: Dr. Priya Sharma
        Address: Flat 302, Sunrise Apartments, Bandra West, Mumbai - 400050
        Phone: +91-9123456789
        Email: priya.sharma@hospital.com
        Aadhaar: 1234 5678 9012
        PAN: ABCPS1234A
        Medical License: MH/MED/12345/2020
        """)
        input_file = f.name
    
    try:
        pipeline = SecretStuffPipeline()
        
        print(f"Processing file: {input_file}")
        
        # Process the file
        result = pipeline.process_text_file(
            input_file=input_file,
            output_redacted="redacted_patient.txt",
            output_identified="identified_entities.json",
            output_mapping="replacement_mapping.json"
        )
        
        print("Processing complete!")
        print(f"Results: {result}")
        
        # Read and display redacted content
        with open("redacted_patient.txt", 'r') as f:
            redacted_content = f.read()
        print("\nRedacted content:")
        print(redacted_content)
        
        # Simulate processing and reverse
        # In real scenario, you'd send redacted_content to LLM and get response
        processed_content = redacted_content  # For demo
        
        # Reverse redaction
        reverse_result = pipeline.reverse_from_files(
            redacted_file="redacted_patient.txt",
            mapping_file="replacement_mapping.json",
            output_file="final_patient.txt"
        )
        
        print(f"\nReverse processing complete: {reverse_result}")
        
        # Read and display final content
        with open("final_patient.txt", 'r') as f:
            final_content = f.read()
        print("\nFinal restored content:")
        print(final_content)
        
    finally:
        # Clean up
        for file in [input_file, "redacted_patient.txt", "identified_entities.json", 
                    "replacement_mapping.json", "final_patient.txt"]:
            if os.path.exists(file):
                os.remove(file)


def custom_configuration_example():
    """Example with custom labels and dummy values."""
    
    # Custom labels - focus only on specific PII types
    custom_labels = [
        "person",
        "email", 
        "phone number",
        "company",
        "custom_id"  # Your custom entity type
    ]
    
    # Custom dummy values
    custom_dummy_values = {
        "person": ["[PERSON_A]", "[PERSON_B]", "[PERSON_C]"],
        "email": "[EMAIL_MASKED]",
        "phone number": "[PHONE_MASKED]", 
        "company": ["[COMPANY_X]", "[COMPANY_Y]"],
        "custom_id": "[CUSTOM_ID_MASKED]"
    }
    
    # Initialize with custom configuration
    pipeline = SecretStuffPipeline(
        labels=custom_labels,
        dummy_values=custom_dummy_values
    )
    
    text = """
    Contact John Smith at john.smith@company.com or +1-555-0123.
    He works at Acme Corporation.
    His employee ID is EMP001 (custom_id).
    """
    
    print("Custom configuration example:")
    print(f"Using labels: {custom_labels}")
    print(f"Original text: {text}")
    
    # Process with custom configuration
    redacted_text, entities, mapping = pipeline.identify_and_redact(text)
    
    print(f"\nRedacted text: {redacted_text}")
    print(f"Entities found: {entities}")
    print(f"Mapping used: {mapping}")


if __name__ == "__main__":
    print("SecretStuff - Basic Usage Examples")
    print("=" * 50)
    
    print("\n1. Basic Example:")
    basic_example()
    
    print("\n\n2. File Processing Example:")
    file_processing_example()
    
    print("\n\n3. Custom Configuration Example:")
    custom_configuration_example()
    
    print("\nAll examples completed successfully!")
