"""Tests for SecretStuffPipeline class."""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch
from secretstuff.api.pipeline import SecretStuffPipeline
from secretstuff.config.labels import DEFAULT_LABELS
from secretstuff.config.dummy_values import DEFAULT_DUMMY_VALUES


class TestSecretStuffPipeline:
    """Test cases for SecretStuffPipeline functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.pipeline = SecretStuffPipeline()
        self.sample_text = """
        Mr. John Doe lives at 123 Main Street, New York.
        His phone number is +1-555-123-4567 and email is john.doe@email.com.
        """
        self.sample_entities = {
            "person": ["John Doe"],
            "email": ["john.doe@email.com"],
            "phone number": ["+1-555-123-4567"]
        }
        self.sample_replacement_mapping = {
            "John Doe": "PERSON_1",
            "john.doe@email.com": "EMAIL_REDACTED",
            "+1-555-123-4567": "PHONE_REDACTED"
        }
    
    def test_initialization(self):
        """Test SecretStuffPipeline initialization."""
        assert self.pipeline.identifier.model_name == "urchade/gliner_multi_pii-v1"
        assert self.pipeline.identifier.labels == DEFAULT_LABELS
        assert self.pipeline.redactor.dummy_values == DEFAULT_DUMMY_VALUES
        assert isinstance(self.pipeline.reverse_mapper, type(self.pipeline.reverse_mapper))
    
    def test_custom_initialization(self):
        """Test SecretStuffPipeline with custom parameters."""
        custom_labels = ["person", "email"]
        custom_dummy_values = {"person": "REDACTED_PERSON"}
        
        pipeline = SecretStuffPipeline(
            model_name="custom-model",
            labels=custom_labels,
            dummy_values=custom_dummy_values
        )
        
        assert pipeline.identifier.model_name == "custom-model"
        assert pipeline.identifier.labels == custom_labels
        assert pipeline.redactor.dummy_values == custom_dummy_values
    
    @patch('secretstuff.core.identifier.PIIIdentifier.identify_and_save')
    def test_identify_pii(self, mock_identify):
        """Test PII identification."""
        mock_identify.return_value = self.sample_entities
        
        result = self.pipeline.identify_pii(self.sample_text)
        
        assert result == self.sample_entities
        assert self.pipeline._last_identified_entities == self.sample_entities
        mock_identify.assert_called_once_with(self.sample_text, "identified_entities.json", 384)
    
    def test_redact_pii_with_entities(self):
        """Test PII redaction with provided entities."""
        with patch.object(self.pipeline.redactor, 'redact_from_identified_entities') as mock_redact:
            mock_redact.return_value = "redacted text"
            
            result = self.pipeline.redact_pii(self.sample_text, self.sample_entities)
            
            assert result == "redacted text"
            mock_redact.assert_called_once_with(self.sample_text, self.sample_entities)
    
    def test_redact_pii_with_last_entities(self):
        """Test PII redaction using last identified entities."""
        self.pipeline._last_identified_entities = self.sample_entities
        
        with patch.object(self.pipeline.redactor, 'redact_from_identified_entities') as mock_redact:
            mock_redact.return_value = "redacted text"
            
            result = self.pipeline.redact_pii(self.sample_text)
            
            assert result == "redacted text"
            mock_redact.assert_called_once_with(self.sample_text, self.sample_entities)
    
    def test_redact_pii_without_entities_raises_error(self):
        """Test that redacting without entities raises error."""
        with pytest.raises(ValueError, match="No identified entities available"):
            self.pipeline.redact_pii(self.sample_text)
    
    @patch('secretstuff.api.pipeline.SecretStuffPipeline.identify_pii')
    @patch('secretstuff.api.pipeline.SecretStuffPipeline.redact_pii')
    def test_identify_and_redact(self, mock_redact, mock_identify):
        """Test combined identify and redact operation."""
        mock_identify.return_value = self.sample_entities
        mock_redact.return_value = "redacted text"
        self.pipeline._last_replacement_mapping = self.sample_replacement_mapping
        
        redacted_text, entities, mapping = self.pipeline.identify_and_redact(self.sample_text)
        
        assert redacted_text == "redacted text"
        assert entities == self.sample_entities
        assert mapping == self.sample_replacement_mapping
        mock_identify.assert_called_once_with(self.sample_text, 384)
        mock_redact.assert_called_once_with(self.sample_text, self.sample_entities)
    
    def test_reverse_redaction_with_mapping(self):
        """Test reverse redaction with provided mapping."""
        redacted_text = "PERSON_1's email is EMAIL_REDACTED"
        
        with patch.object(self.pipeline.reverse_mapper, 'reverse_redaction') as mock_reverse:
            mock_reverse.return_value = ("restored text", 2, {"PERSON_1": 1, "EMAIL_REDACTED": 1})
            
            result = self.pipeline.reverse_redaction(redacted_text, self.sample_replacement_mapping)
            
            assert result == ("restored text", 2, {"PERSON_1": 1, "EMAIL_REDACTED": 1})
            mock_reverse.assert_called_once_with(redacted_text)
    
    def test_reverse_redaction_with_last_mapping(self):
        """Test reverse redaction using last replacement mapping."""
        self.pipeline._last_replacement_mapping = self.sample_replacement_mapping
        redacted_text = "PERSON_1's email is EMAIL_REDACTED"
        
        with patch.object(self.pipeline.reverse_mapper, 'reverse_redaction') as mock_reverse:
            mock_reverse.return_value = ("restored text", 2, {})
            
            result = self.pipeline.reverse_redaction(redacted_text)
            
            assert result == ("restored text", 2, {})
            mock_reverse.assert_called_once_with(redacted_text)
    
    def test_reverse_redaction_without_mapping_raises_error(self):
        """Test that reversing without mapping raises error."""
        with pytest.raises(ValueError, match="No replacement mapping available"):
            self.pipeline.reverse_redaction("redacted text")
    
    def test_process_text_file(self):
        """Test processing a complete text file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = os.path.join(temp_dir, "input.txt")
            
            # Create input file
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(self.sample_text)
            
            # Mock the components
            with patch.object(self.pipeline.identifier, 'identify_and_save') as mock_identify, \
                 patch.object(self.pipeline.redactor, 'redact_from_file') as mock_redact:
                
                mock_identify.return_value = self.sample_entities
                mock_redact.return_value = "redacted text"
                self.pipeline.redactor.replacement_mapping = self.sample_replacement_mapping
                
                result = self.pipeline.process_text_file(input_file)
                
                assert result["input_file"] == input_file
                assert result["entities_count"] == len(self.sample_replacement_mapping)
                assert result["labels_found"] == list(self.sample_entities.keys())
    
    def test_reverse_from_files(self):
        """Test reversing redaction from files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            redacted_file = os.path.join(temp_dir, "redacted.txt")
            mapping_file = os.path.join(temp_dir, "mapping.json")
            
            with patch.object(self.pipeline.reverse_mapper, 'reverse_from_file') as mock_reverse:
                mock_reverse.return_value = ("restored text", 3, {"DUMMY": 3})
                
                result = self.pipeline.reverse_from_files(redacted_file, mapping_file)
                
                assert result["redacted_file"] == redacted_file
                assert result["mapping_file"] == mapping_file
                assert result["total_replacements"] == 3
                assert result["replacement_details"] == {"DUMMY": 3}
    
    def test_get_last_identified_entities(self):
        """Test getting last identified entities."""
        self.pipeline._last_identified_entities = self.sample_entities
        
        entities = self.pipeline.get_last_identified_entities()
        
        assert entities == self.sample_entities
        assert entities is not self.pipeline._last_identified_entities  # Should be a copy
    
    def test_get_last_replacement_mapping(self):
        """Test getting last replacement mapping."""
        self.pipeline._last_replacement_mapping = self.sample_replacement_mapping
        
        mapping = self.pipeline.get_last_replacement_mapping()
        
        assert mapping == self.sample_replacement_mapping
        assert mapping is not self.pipeline._last_replacement_mapping  # Should be a copy
    
    def test_configure_labels(self):
        """Test configuring PII labels."""
        new_labels = ["person", "email"]
        
        self.pipeline.configure_labels(new_labels)
        
        assert self.pipeline.identifier.labels == new_labels
    
    def test_add_custom_labels(self):
        """Test adding custom labels."""
        custom_labels = ["custom_label1", "custom_label2"]
        original_count = len(self.pipeline.identifier.labels)
        
        self.pipeline.add_custom_labels(custom_labels)
        
        assert len(self.pipeline.identifier.labels) == original_count + 2
        assert "custom_label1" in self.pipeline.identifier.labels
    
    def test_configure_dummy_values(self):
        """Test configuring dummy values."""
        new_dummy_values = {"person": "REDACTED_PERSON"}
        
        self.pipeline.configure_dummy_values(new_dummy_values)
        
        assert self.pipeline.redactor.dummy_values == new_dummy_values
    
    def test_add_custom_dummy_values(self):
        """Test adding custom dummy values."""
        additional_values = {"custom_label": "CUSTOM_VALUE"}
        original_count = len(self.pipeline.redactor.dummy_values)
        
        self.pipeline.add_custom_dummy_values(additional_values)
        
        assert len(self.pipeline.redactor.dummy_values) == original_count + 1
        assert self.pipeline.redactor.dummy_values["custom_label"] == "CUSTOM_VALUE"
    
    def test_get_available_labels(self):
        """Test getting available labels."""
        labels = self.pipeline.get_available_labels()
        
        assert labels == DEFAULT_LABELS
        assert labels is not self.pipeline.identifier.labels  # Should be a copy
    
    def test_get_dummy_values(self):
        """Test getting dummy values."""
        values = self.pipeline.get_dummy_values()
        
        assert values == DEFAULT_DUMMY_VALUES
        assert values is not self.pipeline.redactor.dummy_values  # Should be a copy
    
    def test_reset_pipeline(self):
        """Test resetting pipeline state."""
        # Set some state
        self.pipeline._last_identified_entities = self.sample_entities
        self.pipeline._last_replacement_mapping = self.sample_replacement_mapping
        self.pipeline.redactor.replacement_mapping = self.sample_replacement_mapping
        
        # Reset
        self.pipeline.reset_pipeline()
        
        # Check that state is cleared
        assert self.pipeline._last_identified_entities == {}
        assert self.pipeline._last_replacement_mapping == {}
        assert self.pipeline.redactor.replacement_mapping == {}
        assert self.pipeline.reverse_mapper.replacement_mapping == {}
        assert self.pipeline.reverse_mapper.reverse_mapping == {}
