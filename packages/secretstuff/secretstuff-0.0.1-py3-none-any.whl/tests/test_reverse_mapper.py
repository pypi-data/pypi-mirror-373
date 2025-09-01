"""Tests for ReverseMapper class."""

import pytest
import json
import tempfile
import os
from secretstuff.core.reverse_mapper import ReverseMapper


class TestReverseMapper:
    """Test cases for ReverseMapper functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.replacement_mapping = {
            "John Doe": "PERSON_1",
            "jane@email.com": "EMAIL_REDACTED",
            "+1-555-123-4567": "PHONE_REDACTED"
        }
        self.reverse_mapper = ReverseMapper(self.replacement_mapping)
        self.redacted_text = "PERSON_1's email is EMAIL_REDACTED and phone is PHONE_REDACTED."
    
    def test_initialization_empty(self):
        """Test ReverseMapper initialization without mapping."""
        mapper = ReverseMapper()
        assert mapper.replacement_mapping == {}
        assert mapper.reverse_mapping == {}
    
    def test_initialization_with_mapping(self):
        """Test ReverseMapper initialization with mapping."""
        assert self.reverse_mapper.replacement_mapping == self.replacement_mapping
        assert len(self.reverse_mapper.reverse_mapping) == 3
        assert self.reverse_mapper.reverse_mapping["PERSON_1"] == "John Doe"
        assert self.reverse_mapper.reverse_mapping["EMAIL_REDACTED"] == "jane@email.com"
        assert self.reverse_mapper.reverse_mapping["PHONE_REDACTED"] == "+1-555-123-4567"
    
    def test_create_reverse_mapping(self):
        """Test reverse mapping creation."""
        mapper = ReverseMapper()
        mapper.replacement_mapping = self.replacement_mapping
        reverse_mapping = mapper._create_reverse_mapping()
        
        assert len(reverse_mapping) == 3
        assert reverse_mapping["PERSON_1"] == "John Doe"
        assert reverse_mapping["EMAIL_REDACTED"] == "jane@email.com"
        assert reverse_mapping["PHONE_REDACTED"] == "+1-555-123-4567"
    
    def test_load_replacement_mapping(self):
        """Test loading replacement mapping from file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mapping_file = os.path.join(temp_dir, "mapping.json")
            
            # Create mapping file
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.replacement_mapping, f)
            
            # Load mapping
            mapper = ReverseMapper()
            mapper.load_replacement_mapping(mapping_file)
            
            assert mapper.replacement_mapping == self.replacement_mapping
            assert len(mapper.reverse_mapping) == 3
    
    def test_reverse_redaction(self):
        """Test reversing redaction."""
        restored_text, total_replaced, replacement_counts = self.reverse_mapper.reverse_redaction(
            self.redacted_text
        )
        
        # Check that original entities are restored
        assert "John Doe" in restored_text
        assert "jane@email.com" in restored_text
        assert "+1-555-123-4567" in restored_text
        
        # Check that dummy values are gone
        assert "PERSON_1" not in restored_text
        assert "EMAIL_REDACTED" not in restored_text
        assert "PHONE_REDACTED" not in restored_text
        
        # Check replacement statistics
        assert total_replaced == 3
        assert replacement_counts["PERSON_1"] == 1
        assert replacement_counts["EMAIL_REDACTED"] == 1
        assert replacement_counts["PHONE_REDACTED"] == 1
    
    def test_reverse_redaction_case_insensitive(self):
        """Test case-insensitive reverse redaction."""
        redacted_text = "person_1 and PERSON_1 and Person_1"
        replacement_mapping = {"Original Name": "PERSON_1"}
        
        mapper = ReverseMapper(replacement_mapping)
        restored_text, total_replaced, _ = mapper.reverse_redaction(redacted_text)
        
        # All variations should be replaced
        assert "person_1" not in restored_text.lower()
        assert restored_text.count("Original Name") == 3
        assert total_replaced == 3
    
    def test_reverse_redaction_multiple_occurrences(self):
        """Test reversing with multiple occurrences of same dummy value."""
        redacted_text = "PERSON_1 called PERSON_1 and then PERSON_1 left."
        
        restored_text, total_replaced, replacement_counts = self.reverse_mapper.reverse_redaction(
            redacted_text
        )
        
        assert total_replaced == 3
        assert replacement_counts["PERSON_1"] == 3
        assert restored_text.count("John Doe") == 3
    
    def test_reverse_redaction_longest_first(self):
        """Test that longest dummy values are replaced first to avoid partial replacements."""
        replacement_mapping = {
            "AB": "X",
            "ABC": "XY"
        }
        redacted_text = "XY and X"
        
        mapper = ReverseMapper(replacement_mapping)
        restored_text, _, _ = mapper.reverse_redaction(redacted_text)
        
        # Should restore to "ABC and AB", not "ABY and AB"
        assert "ABC" in restored_text
        assert "AB" in restored_text
        assert "XY" not in restored_text
        assert "X" not in restored_text
    
    def test_reverse_from_file(self):
        """Test reversing from files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            redacted_file = os.path.join(temp_dir, "redacted.txt")
            mapping_file = os.path.join(temp_dir, "mapping.json")
            output_file = os.path.join(temp_dir, "restored.txt")
            
            # Create input files
            with open(redacted_file, 'w', encoding='utf-8') as f:
                f.write(self.redacted_text)
            
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.replacement_mapping, f)
            
            # Reverse from file
            mapper = ReverseMapper()
            restored_text, total_replaced, replacement_counts = mapper.reverse_from_file(
                redacted_file, mapping_file, output_file
            )
            
            # Check output file exists and contains restored text
            assert os.path.exists(output_file)
            with open(output_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
            assert file_content == restored_text
            
            # Check restoration results
            assert "John Doe" in restored_text
            assert total_replaced == 3
    
    def test_get_reverse_mapping(self):
        """Test getting reverse mapping."""
        mapping = self.reverse_mapper.get_reverse_mapping()
        
        assert isinstance(mapping, dict)
        assert mapping is not self.reverse_mapper.reverse_mapping  # Should be a copy
        assert len(mapping) == 3
    
    def test_get_replacement_mapping(self):
        """Test getting replacement mapping."""
        mapping = self.reverse_mapper.get_replacement_mapping()
        
        assert isinstance(mapping, dict)
        assert mapping is not self.reverse_mapper.replacement_mapping  # Should be a copy
        assert mapping == self.replacement_mapping
    
    def test_set_replacement_mapping(self):
        """Test setting replacement mapping."""
        new_mapping = {"New Entity": "NEW_DUMMY"}
        
        self.reverse_mapper.set_replacement_mapping(new_mapping)
        
        assert self.reverse_mapper.replacement_mapping == new_mapping
        assert self.reverse_mapper.reverse_mapping["NEW_DUMMY"] == "New Entity"
    
    def test_validate_mapping_consistent(self):
        """Test mapping validation with consistent mappings."""
        assert self.reverse_mapper.validate_mapping() is True
    
    def test_validate_mapping_inconsistent(self):
        """Test mapping validation with inconsistent mappings."""
        # Corrupt the reverse mapping
        self.reverse_mapper.reverse_mapping["WRONG_DUMMY"] = "Wrong Entity"
        
        assert self.reverse_mapper.validate_mapping() is False
    
    def test_validate_mapping_empty(self):
        """Test mapping validation with empty mappings."""
        mapper = ReverseMapper()
        assert mapper.validate_mapping() is False
    
    def test_get_mapping_statistics(self):
        """Test getting mapping statistics."""
        stats = self.reverse_mapper.get_mapping_statistics()
        
        assert stats["total_original_entities"] == 3
        assert stats["total_dummy_values"] == 3
        assert stats["unique_dummy_values"] == 3
        assert stats["mapping_consistent"] is True
    
    def test_get_mapping_statistics_with_duplicates(self):
        """Test mapping statistics with duplicate dummy values."""
        replacement_mapping = {
            "Entity 1": "DUMMY_1",
            "Entity 2": "DUMMY_1",  # Same dummy value
            "Entity 3": "DUMMY_2"
        }
        
        mapper = ReverseMapper(replacement_mapping)
        stats = mapper.get_mapping_statistics()
        
        assert stats["total_original_entities"] == 3
        assert stats["total_dummy_values"] == 2  # Only 2 unique reverse mappings
        assert stats["unique_dummy_values"] == 2
    
    def test_reverse_redaction_without_mapping_raises_error(self):
        """Test that reversing without mapping raises error."""
        mapper = ReverseMapper()
        
        with pytest.raises(ValueError, match="No reverse mapping available"):
            mapper.reverse_redaction(self.redacted_text)
