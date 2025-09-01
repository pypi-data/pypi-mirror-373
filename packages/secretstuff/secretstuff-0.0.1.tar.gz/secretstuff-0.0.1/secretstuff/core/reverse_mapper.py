import json
import re
from typing import Dict, Optional, Tuple


class ReverseMapper:
    """
    Reverses PII redaction by replacing dummy values back to original entities
    using the replacement mapping created during redaction.
    """
    
    def __init__(self, replacement_mapping: Optional[Dict[str, str]] = None):
        """
        Initialize the reverse mapper.
        
        Args:
            replacement_mapping: Dictionary mapping original entities to dummy values.
                               If provided, creates reverse mapping automatically.
        """
        self.replacement_mapping = replacement_mapping or {}
        self.reverse_mapping = {}
        if replacement_mapping:
            self._create_reverse_mapping()
    
    def _create_reverse_mapping(self) -> Dict[str, str]:
        """
        Create reverse mapping (dummy value -> original value).
        
        Returns:
            Dictionary mapping dummy values to original entities
        """
        self.reverse_mapping = {}
        for original, dummy in self.replacement_mapping.items():
            self.reverse_mapping[dummy] = original
        return self.reverse_mapping
    
    def load_replacement_mapping(self, mapping_file: str) -> None:
        """
        Load replacement mapping from JSON file and create reverse mapping.
        
        Args:
            mapping_file: Path to the replacement mapping JSON file
        """
        with open(mapping_file, 'r', encoding='utf-8') as file:
            self.replacement_mapping = json.load(file)
        self._create_reverse_mapping()
    
    def reverse_redaction(self, redacted_text: str) -> Tuple[str, int, Dict[str, int]]:
        """
        Reverse the redaction process to restore original PII entities.
        
        Args:
            redacted_text: Text with dummy values to reverse
            
        Returns:
            Tuple containing:
            - Restored text with original PII
            - Total number of replacements made
            - Dictionary mapping dummy values to replacement counts
        """
        if not self.reverse_mapping:
            raise ValueError("No reverse mapping available. Load replacement mapping first.")
        
        # Sort dummy values by length (longest first) to avoid partial replacements
        sorted_dummies = sorted(self.reverse_mapping.keys(), key=len, reverse=True)
        
        # Replace dummy values back to original values
        final_text = redacted_text
        total_replaced = 0
        replacement_counts = {}
        
        for dummy_value in sorted_dummies:
            original_value = self.reverse_mapping[dummy_value]
            
            # Escape special regex characters in the dummy value
            escaped_dummy = re.escape(dummy_value)
            
            # Count occurrences before replacement
            occurrences = len(re.findall(escaped_dummy, final_text, flags=re.IGNORECASE))
            
            if occurrences > 0:
                # Replace with case-insensitive matching
                final_text = re.sub(escaped_dummy, original_value, final_text, flags=re.IGNORECASE)
                total_replaced += occurrences
                replacement_counts[dummy_value] = occurrences
        
        return final_text, total_replaced, replacement_counts
    
    def reverse_from_file(self, redacted_file: str, mapping_file: str, 
                         output_file: str = "restored.txt") -> Tuple[str, int, Dict[str, int]]:
        """
        Reverse redaction from files.
        
        Args:
            redacted_file: Path to redacted text file
            mapping_file: Path to replacement mapping JSON file
            output_file: Path to save restored text
            
        Returns:
            Tuple containing:
            - Restored text with original PII
            - Total number of replacements made
            - Dictionary mapping dummy values to replacement counts
        """
        # Read the redacted text
        with open(redacted_file, 'r', encoding='utf-8') as file:
            redacted_text = file.read()
        
        # Load replacement mapping
        self.load_replacement_mapping(mapping_file)
        
        # Reverse the redaction
        restored_text, total_replaced, replacement_counts = self.reverse_redaction(redacted_text)
        
        # Save restored text
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(restored_text)
        
        return restored_text, total_replaced, replacement_counts
    
    def get_reverse_mapping(self) -> Dict[str, str]:
        """
        Get the current reverse mapping.
        
        Returns:
            Dictionary mapping dummy values to original entities
        """
        return self.reverse_mapping.copy()
    
    def get_replacement_mapping(self) -> Dict[str, str]:
        """
        Get the original replacement mapping.
        
        Returns:
            Dictionary mapping original entities to dummy values
        """
        return self.replacement_mapping.copy()
    
    def set_replacement_mapping(self, replacement_mapping: Dict[str, str]) -> None:
        """
        Set the replacement mapping and create reverse mapping.
        
        Args:
            replacement_mapping: Dictionary mapping original entities to dummy values
        """
        self.replacement_mapping = replacement_mapping.copy()
        self._create_reverse_mapping()
    
    def validate_mapping(self) -> bool:
        """
        Validate that the reverse mapping is consistent with replacement mapping.
        
        Returns:
            True if mappings are consistent, False otherwise
        """
        if not self.replacement_mapping or not self.reverse_mapping:
            return False
        
        for original, dummy in self.replacement_mapping.items():
            if dummy not in self.reverse_mapping:
                return False
            if self.reverse_mapping[dummy] != original:
                return False
        
        return True
    
    def get_mapping_statistics(self) -> Dict[str, int]:
        """
        Get statistics about the current mappings.
        
        Returns:
            Dictionary with mapping statistics
        """
        return {
            "total_original_entities": len(self.replacement_mapping),
            "total_dummy_values": len(self.reverse_mapping),
            "unique_dummy_values": len(set(self.replacement_mapping.values())),
            "mapping_consistent": self.validate_mapping()
        }
