"""Tests for PIIRedactor class."""

import pytest
import json
import tempfile
import os
from secretstuff.core.redactor import PIIRedactor
from secretstuff.config.dummy_values import DEFAULT_DUMMY_VALUES


class TestPIIRedactor:
    """Test cases for PIIRedactor functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.redactor = PIIRedactor()
        self.sample_entities = {
            "person": ["John Doe", "Jane Smith"],
            "email": ["john@email.com"],
            "phone number": ["+1-555-123-4567"]
        }
        self.sample_text = "John Doe's email is john@email.com and phone is +1-555-123-4567."
    
    def test_initialization(self):
        """Test PIIRedactor initialization."""
        assert self.redactor.dummy_values == DEFAULT_DUMMY_VALUES
        assert self.redactor.replacement_mapping == {}
    
    def test_custom_initialization(self):
        """Test PIIRedactor with custom dummy values."""
        custom_dummy_values = {
            "person": ["PERSON_1", "PERSON_2"],
            "email": "EMAIL_REDACTED"
        }
        redactor = PIIRedactor(custom_dummy_values)
        assert redactor.dummy_values == custom_dummy_values
    
    def test_create_replacement_mapping_single_values(self):
        """Test replacement mapping with single dummy values."""
        entities = {"email": ["john@email.com", "jane@email.com"]}
        dummy_values = {"email": "REDACTED_EMAIL"}
        
        redactor = PIIRedactor(dummy_values)
        mapping = redactor.create_replacement_mapping(entities)
        
        assert mapping["john@email.com"] == "REDACTED_EMAIL"
        assert mapping["jane@email.com"] == "REDACTED_EMAIL"
    
    def test_create_replacement_mapping_list_values(self):
        """Test replacement mapping with list dummy values."""
        entities = {"person": ["John Doe", "Jane Smith", "Bob Wilson"]}
        dummy_values = {"person": ["PERSON_1", "PERSON_2"]}
        
        redactor = PIIRedactor(dummy_values)
        mapping = redactor.create_replacement_mapping(entities)
        
        # Should cycle through dummy values
        assert len(mapping) == 3
        assert all(val in ["PERSON_1", "PERSON_2"] for val in mapping.values())
    
    def test_redact_text(self):
        """Test text redaction functionality."""
        replacement_mapping = {
            "John Doe": "PERSON_1",
            "john@email.com": "EMAIL_REDACTED",
            "+1-555-123-4567": "PHONE_REDACTED"
        }
        
        redacted = self.redactor.redact_text(self.sample_text, replacement_mapping)
        
        assert "John Doe" not in redacted
        assert "john@email.com" not in redacted
        assert "+1-555-123-4567" not in redacted
        assert "PERSON_1" in redacted
        assert "EMAIL_REDACTED" in redacted
        assert "PHONE_REDACTED" in redacted
    
    def test_redact_text_case_insensitive(self):
        """Test case-insensitive redaction."""
        replacement_mapping = {"John Doe": "PERSON_1"}
        text = "john doe and JOHN DOE and John Doe"
        
        redacted = self.redactor.redact_text(text, replacement_mapping)
        
        # All variations should be replaced
        assert "john doe" not in redacted.lower()
        assert redacted.count("PERSON_1") == 3
    
    def test_redact_text_special_characters(self):
        """Test redaction with special regex characters."""
        replacement_mapping = {"user@domain.com": "EMAIL_REDACTED"}
        text = "Contact user@domain.com for info"
        
        redacted = self.redactor.redact_text(text, replacement_mapping)
        
        assert "user@domain.com" not in redacted
        assert "EMAIL_REDACTED" in redacted
    
    def test_redact_from_identified_entities(self):
        """Test redaction from identified entities."""
        redacted = self.redactor.redact_from_identified_entities(
            self.sample_text, self.sample_entities
        )
        
        # Check that original entities are not present
        assert "John Doe" not in redacted
        assert "john@email.com" not in redacted
        assert "+1-555-123-4567" not in redacted
        
        # Check that replacement mapping was created
        assert len(self.redactor.replacement_mapping) > 0
    
    def test_redact_from_file(self):
        """Test redacting from files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = os.path.join(temp_dir, "input.txt")
            entities_file = os.path.join(temp_dir, "entities.json")
            output_file = os.path.join(temp_dir, "redacted.txt")
            mapping_file = os.path.join(temp_dir, "mapping.json")
            
            # Create input files
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(self.sample_text)
            
            with open(entities_file, 'w', encoding='utf-8') as f:
                json.dump(self.sample_entities, f)
            
            # Redact from file
            redacted_text = self.redactor.redact_from_file(
                input_file, entities_file, output_file, mapping_file
            )
            
            # Check output file exists and contains redacted text
            assert os.path.exists(output_file)
            with open(output_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
            assert file_content == redacted_text
            
            # Check mapping file exists and is valid JSON
            assert os.path.exists(mapping_file)
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
            assert isinstance(mapping, dict)
            assert len(mapping) > 0
    
    def test_get_replacement_mapping(self):
        """Test getting replacement mapping."""
        self.redactor.create_replacement_mapping(self.sample_entities)
        mapping = self.redactor.get_replacement_mapping()
        
        assert isinstance(mapping, dict)
        assert mapping is not self.redactor.replacement_mapping  # Should be a copy
    
    def test_save_and_load_replacement_mapping(self):
        """Test saving and loading replacement mapping."""
        self.redactor.create_replacement_mapping(self.sample_entities)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            mapping_file = os.path.join(temp_dir, "mapping.json")
            
            # Save mapping
            self.redactor.save_replacement_mapping(mapping_file)
            assert os.path.exists(mapping_file)
            
            # Create new redactor and load mapping
            new_redactor = PIIRedactor()
            new_redactor.load_replacement_mapping(mapping_file)
            
            assert new_redactor.replacement_mapping == self.redactor.replacement_mapping
    
    def test_set_dummy_values(self):
        """Test setting custom dummy values."""
        custom_values = {"person": "REDACTED_PERSON"}
        self.redactor.set_dummy_values(custom_values)
        
        assert self.redactor.dummy_values == custom_values
    
    def test_add_dummy_values(self):
        """Test adding additional dummy values."""
        additional_values = {"custom_label": "CUSTOM_VALUE"}
        original_count = len(self.redactor.dummy_values)
        
        self.redactor.add_dummy_values(additional_values)
        
        assert len(self.redactor.dummy_values) == original_count + 1
        assert self.redactor.dummy_values["custom_label"] == "CUSTOM_VALUE"
    
    def test_get_dummy_values(self):
        """Test getting dummy values."""
        values = self.redactor.get_dummy_values()
        
        assert values == DEFAULT_DUMMY_VALUES
        assert values is not self.redactor.dummy_values  # Should be a copy
    
    def test_redact_text_without_mapping_raises_error(self):
        """Test that redacting without mapping raises error."""
        with pytest.raises(ValueError, match="No replacement mapping provided"):
            self.redactor.redact_text(self.sample_text)
