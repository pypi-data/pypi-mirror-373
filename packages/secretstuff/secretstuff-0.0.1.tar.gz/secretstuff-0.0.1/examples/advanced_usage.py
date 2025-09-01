"""Advanced usage examples for SecretStuff package."""

from secretstuff import SecretStuffPipeline, PIIIdentifier, PIIRedactor, ReverseMapper
import json
import os


def individual_components_example():
    """Example using individual components separately."""
    print("Using individual components:")
    
    text = """
    Legal Notice:
    Mr. Arjun Patel, residing at B-45, Sector 18, Noida - 201301,
    Contact: +91-9876543210, Email: arjun.patel@legal.com
    Aadhaar: 2345 6789 0123, PAN: BCDAP5678B
    Case Number: CS/123/2023, Court: Delhi High Court
    """
    
    # Step 1: Use PIIIdentifier
    print("\nStep 1: Using PIIIdentifier")
    identifier = PIIIdentifier()
    entities = identifier.identify_entities(text)
    entity_mapping = identifier.create_entity_mapping(entities)
    
    print("Identified entities:")
    for label, items in entity_mapping.items():
        print(f"  {label}: {items}")
    
    # Step 2: Use PIIRedactor
    print("\nStep 2: Using PIIRedactor")
    redactor = PIIRedactor()
    replacement_mapping = redactor.create_replacement_mapping(entity_mapping)
    redacted_text = redactor.redact_text(text, replacement_mapping)
    
    print("Redacted text:")
    print(redacted_text)
    
    # Step 3: Use ReverseMapper
    print("\nStep 3: Using ReverseMapper")
    reverse_mapper = ReverseMapper(replacement_mapping)
    
    # Simulate some processing
    processed_text = redacted_text.replace("Legal Notice:", "PROCESSED Legal Notice:")
    
    restored_text, count, details = reverse_mapper.reverse_redaction(processed_text)
    
    print("Restored text:")
    print(restored_text)
    print(f"Replacements made: {count}")


def batch_processing_example():
    """Example of processing multiple documents in batch."""
    print("Batch processing example:")
    
    # Sample documents
    documents = {
        "contract_1.txt": """
        Contract between ABC Corp (CIN: U12345DL2020PLC123456) 
        and John Doe (john.doe@email.com, +91-9876543210).
        Aadhaar: 1234 5678 9012, Address: Delhi
        """,
        
        "invoice_2.txt": """
        Invoice for Jane Smith (jane@company.com, +91-8765432109)
        PAN: ABCDE1234F, GST: 07ABCDE1234F1Z5
        Bank: HDFC Bank, Account: 12345678901234
        """,
        
        "medical_3.txt": """
        Patient: Dr. Raj Kumar (raj.kumar@hospital.com)
        License: MH/MED/67890/2019, Phone: +91-7654321098
        Patient ID: PAT001, Insurance: INS123456789
        """
    }
    
    pipeline = SecretStuffPipeline()
    results = []
    
    # Process each document
    for doc_name, content in documents.items():
        print(f"\nProcessing {doc_name}...")
        
        # Identify and redact
        redacted_text, entities, mapping = pipeline.identify_and_redact(content)
        
        result = {
            "document": doc_name,
            "original_length": len(content),
            "redacted_length": len(redacted_text),
            "entities_found": len(mapping),
            "entity_types": list(entities.keys()),
            "redacted_text": redacted_text,
            "mapping": mapping
        }
        
        results.append(result)
        
        # Show summary
        print(f"  Entities found: {result['entities_found']}")
        print(f"  Entity types: {result['entity_types']}")
    
    # Batch reverse processing
    print("\nBatch reverse processing:")
    for result in results:
        # Simulate cloud processing
        processed_text = f"PROCESSED: {result['redacted_text']}"
        
        # Reverse
        restored_text, count, _ = pipeline.reverse_redaction(
            processed_text, result['mapping']
        )
        
        print(f"\n{result['document']} restored with {count} replacements")
        print(f"Final text: {restored_text[:100]}...")


def memory_efficient_processing():
    """Example of processing large text efficiently."""
    print("Memory efficient processing for large text:")
    
    # Simulate large document
    large_text = """
    Large Document Processing Example:
    This document contains multiple individuals and entities.
    """ + "\n".join([
        f"Person {i}: John Doe {i} (john{i}@email.com, +91-987654{i:04d})"
        for i in range(10)
    ]) + """
    
    Company Information:
    TechCorp India Pvt Ltd (CIN: U72900DL2018PTC123456)
    Address: Sector 62, Noida, Uttar Pradesh
    Contact: info@techcorp.com, +91-1234567890
    """
    
    pipeline = SecretStuffPipeline()
    
    # Process with smaller chunks for memory efficiency
    print(f"Original document size: {len(large_text)} characters")
    
    # Identify with smaller chunk size
    entities = pipeline.identify_pii(large_text, chunk_size=200)
    
    print(f"Found {sum(len(items) for items in entities.values())} total entities")
    print("Entity breakdown:")
    for label, items in entities.items():
        print(f"  {label}: {len(items)} items")
    
    # Redact
    redacted_text = pipeline.redact_pii(large_text, entities)
    print(f"Redacted document size: {len(redacted_text)} characters")
    
    # Show memory usage reduction (simplified)
    unique_entities = set()
    for items in entities.values():
        unique_entities.update(items)
    
    original_entity_chars = sum(len(entity) for entity in unique_entities)
    dummy_chars = len(" ".join(pipeline.get_last_replacement_mapping().values()))
    
    print(f"Character reduction in entities: {original_entity_chars} -> {dummy_chars}")


def custom_model_example():
    """Example with custom model configuration."""
    print("Custom model configuration:")
    
    # You could use a custom GLiNER model
    custom_labels = [
        "person", "organization", "location", 
        "email", "phone", "date", "money"
    ]
    
    # Initialize with custom labels
    pipeline = SecretStuffPipeline(
        model_name="urchade/gliner_multi_pii-v1",  # Default model
        labels=custom_labels
    )
    
    text = """
    Meeting scheduled for March 15, 2024 at TechHub, Bangalore.
    Attendees: Sarah Johnson (sarah@techfirm.com), Mark Wilson (+1-555-0199)
    Budget allocated: $50,000 for the project.
    Location: 123 Innovation Street, Bangalore 560001
    """
    
    print("Custom model processing:")
    entities = pipeline.identify_pii(text)
    
    print("Entities found with custom labels:")
    for label, items in entities.items():
        print(f"  {label}: {items}")
    
    # Add custom dummy values
    custom_dummies = {
        "money": "[AMOUNT_REDACTED]",
        "date": "[DATE_REDACTED]", 
        "location": "[LOCATION_REDACTED]"
    }
    
    pipeline.add_custom_dummy_values(custom_dummies)
    
    redacted_text = pipeline.redact_pii(text, entities)
    print(f"\nRedacted with custom dummies:\n{redacted_text}")


def error_handling_example():
    """Example of proper error handling."""
    print("Error handling example:")
    
    pipeline = SecretStuffPipeline()
    
    # Example 1: Empty text
    try:
        result = pipeline.identify_pii("")
        print("Empty text processed successfully")
    except Exception as e:
        print(f"Empty text error: {e}")
    
    # Example 2: Redaction without identification
    try:
        pipeline.reset_pipeline()  # Clear any previous state
        result = pipeline.redact_pii("Some text")
    except ValueError as e:
        print(f"Expected error - redaction without identification: {e}")
    
    # Example 3: Reverse without mapping
    try:
        new_pipeline = SecretStuffPipeline()
        result = new_pipeline.reverse_redaction("Some redacted text")
    except ValueError as e:
        print(f"Expected error - reverse without mapping: {e}")
    
    # Example 4: Proper error handling workflow
    try:
        text = "Valid text with John Doe and john@email.com"
        
        # Safe processing with error handling
        entities = pipeline.identify_pii(text)
        if entities:
            redacted = pipeline.redact_pii(text, entities)
            print("Safe processing completed successfully")
        else:
            print("No entities found to redact")
            
    except Exception as e:
        print(f"Unexpected error in safe processing: {e}")


def configuration_management_example():
    """Example of configuration management."""
    print("Configuration management example:")
    
    # Save configuration to file
    config = {
        "labels": ["person", "email", "phone number", "company"],
        "dummy_values": {
            "person": ["[NAME_1]", "[NAME_2]", "[NAME_3]"],
            "email": "[EMAIL_HIDDEN]",
            "phone number": "[PHONE_HIDDEN]",
            "company": "[COMPANY_HIDDEN]"
        },
        "chunk_size": 512,
        "model_name": "urchade/gliner_multi_pii-v1"
    }
    
    # Save configuration
    with open("secretstuff_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Load and use configuration
    with open("secretstuff_config.json", "r") as f:
        loaded_config = json.load(f)
    
    pipeline = SecretStuffPipeline(
        model_name=loaded_config["model_name"],
        labels=loaded_config["labels"],
        dummy_values=loaded_config["dummy_values"]
    )
    
    text = "Test with John Smith (john@test.com) from ABC Corp"
    redacted, entities, mapping = pipeline.identify_and_redact(text)
    
    print("Configuration-based processing:")
    print(f"Original: {text}")
    print(f"Redacted: {redacted}")
    
    # Clean up
    if os.path.exists("secretstuff_config.json"):
        os.remove("secretstuff_config.json")


if __name__ == "__main__":
    print("SecretStuff - Advanced Usage Examples")
    print("=" * 50)
    
    examples = [
        ("Individual Components", individual_components_example),
        ("Batch Processing", batch_processing_example),
        ("Memory Efficient Processing", memory_efficient_processing),
        ("Custom Model Configuration", custom_model_example),
        ("Error Handling", error_handling_example),
        ("Configuration Management", configuration_management_example)
    ]
    
    for title, example_func in examples:
        print(f"\n{title}:")
        print("-" * len(title))
        try:
            example_func()
            print("✓ Example completed successfully")
        except Exception as e:
            print(f"✗ Example failed: {e}")
        print()
    
    print("All advanced examples completed!")
