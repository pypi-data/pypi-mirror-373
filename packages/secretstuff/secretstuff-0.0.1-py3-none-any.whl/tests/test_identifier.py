"""Tests for PIIIdentifier class."""

import pytest
import json
import tempfile
import os
from secretstuff.core.identifier import PIIIdentifier
from secretstuff.config.labels import DEFAULT_LABELS


class TestPIIIdentifier:
    """Test cases for PIIIdentifier functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.identifier = PIIIdentifier()
        self.sample_text = """
        Mr. John Doe lives at 123 Main Street, New York, NY 10001.
        His phone number is +1-555-123-4567 and email is john.doe@email.com.
        His Aadhaar number is 1234 5678 9012 and PAN is ABCDE1234F.
        """
    
    def test_initialization(self):
        """Test PIIIdentifier initialization."""
        assert self.identifier.model_name == "urchade/gliner_multi_pii-v1"
        assert self.identifier.labels == DEFAULT_LABELS
        assert self.identifier._model is None
    
    def test_custom_initialization(self):
        """Test PIIIdentifier with custom parameters."""
        custom_labels = ["person", "email", "phone number"]
        identifier = PIIIdentifier(
            model_name="custom-model",
            labels=custom_labels
        )
        assert identifier.model_name == "custom-model"
        assert identifier.labels == custom_labels
    
    def test_chunk_text(self):
        """Test text chunking functionality."""
        text = "A" * 1000
        chunks = self.identifier.chunk_text(text, chunk_size=384)
        
        assert len(chunks) == 3  # 1000 / 384 = 2.6, so 3 chunks
        assert len(chunks[0]) == 384
        assert len(chunks[1]) == 384
        assert len(chunks[2]) == 232  # 1000 - 384 - 384
    
    def test_remove_duplicates(self):
        """Test duplicate entity removal."""
        entities = [
            {"text": "John Doe", "label": "person", "start": 0, "end": 8},
            {"text": "john doe", "label": "person", "start": 20, "end": 28},  # Different case
            {"text": "John Doe", "label": "person", "start": 40, "end": 48},  # Exact duplicate
            {"text": "Jane Smith", "label": "person", "start": 60, "end": 70},
        ]
        
        unique_entities = self.identifier._remove_duplicates(entities)
        
        assert len(unique_entities) == 3  # Should remove exact duplicate only
        texts = [entity["text"] for entity in unique_entities]
        assert "John Doe" in texts
        assert "john doe" in texts  # Case difference preserved
        assert "Jane Smith" in texts
    
    def test_create_entity_mapping(self):
        """Test entity mapping creation."""
        entities = [
            {"text": "John Doe", "label": "person"},
            {"text": "Jane Smith", "label": "person"},
            {"text": "john@email.com", "label": "email"},
            {"text": "+1-555-123-4567", "label": "phone number"},
        ]
        
        mapping = self.identifier.create_entity_mapping(entities)
        
        assert "person" in mapping
        assert "email" in mapping
        assert "phone number" in mapping
        assert len(mapping["person"]) == 2
        assert "John Doe" in mapping["person"]
        assert "Jane Smith" in mapping["person"]
        assert mapping["email"] == ["john@email.com"]
        assert mapping["phone number"] == ["+1-555-123-4567"]
    
    def test_add_custom_labels(self):
        """Test adding custom labels."""
        initial_count = len(self.identifier.labels)
        custom_labels = ["custom_label1", "custom_label2"]
        
        self.identifier.add_custom_labels(custom_labels)
        
        assert len(self.identifier.labels) == initial_count + 2
        assert "custom_label1" in self.identifier.labels
        assert "custom_label2" in self.identifier.labels
    
    def test_set_labels(self):
        """Test setting labels."""
        new_labels = ["person", "email", "phone number"]
        self.identifier.set_labels(new_labels)
        
        assert self.identifier.labels == new_labels
        assert len(self.identifier.labels) == 3
    
    def test_get_labels(self):
        """Test getting labels."""
        labels = self.identifier.get_labels()
        assert labels == DEFAULT_LABELS
        assert labels is not self.identifier.labels  # Should return a copy
    
    def test_identify_and_save(self):
        """Test identifying entities and saving to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "test_identified.json")
            
            # Mock the identify_entities method for testing
            def mock_identify_entities(text, chunk_size):
                return [
                    {"text": "John Doe", "label": "person", "start": 0, "end": 8},
                    {"text": "john@email.com", "label": "email", "start": 20, "end": 35}
                ]
            
            self.identifier.identify_entities = mock_identify_entities
            
            mapping = self.identifier.identify_and_save(
                self.sample_text, output_file
            )
            
            # Check that file was created
            assert os.path.exists(output_file)
            
            # Check file contents
            with open(output_file, 'r', encoding='utf-8') as f:
                saved_mapping = json.load(f)
            
            assert saved_mapping == mapping
            assert "person" in mapping
            assert "email" in mapping
