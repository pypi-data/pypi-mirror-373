import json
import re
import random
from typing import Dict, List, Any, Optional, Union
from ..config.dummy_values import DEFAULT_DUMMY_VALUES


class PIIRedactor:
    """
    Redacts personally identifiable information (PII) by replacing identified entities
    with dummy values while maintaining document structure and readability.
    """
    
    def __init__(self, dummy_values: Optional[Dict[str, Union[str, List[str]]]] = None):
        """
        Initialize the PII redactor.
        
        Args:
            dummy_values: Dictionary mapping PII labels to dummy replacement values.
                         If None, uses DEFAULT_DUMMY_VALUES
        """
        self.dummy_values = dummy_values or DEFAULT_DUMMY_VALUES.copy()
        self.replacement_mapping = {}
    
    def create_replacement_mapping(self, identified_entities: Dict[str, List[str]]) -> Dict[str, str]:
        """
        Create a mapping from original entities to their dummy replacements.
        
        Args:
            identified_entities: Dictionary mapping labels to lists of entity texts
            
        Returns:
            Dictionary mapping original entity texts to dummy values
        """
        replacement_map = {}
        
        for label, entities in identified_entities.items():
            if label in self.dummy_values:
                dummy_data = self.dummy_values[label]
                
                # Check if dummy_data is a list or a single value
                if isinstance(dummy_data, list):
                    # If we have multiple entities, ensure they get different dummy values
                    # Create a shuffled copy to avoid repetition
                    shuffled_dummies = dummy_data.copy()
                    random.shuffle(shuffled_dummies)
                    
                    for i, entity in enumerate(entities):
                        # Use modulo to cycle through dummy values if more entities than dummies
                        dummy_value = shuffled_dummies[i % len(shuffled_dummies)]
                        replacement_map[entity] = dummy_value
                else:
                    # Single value, use it for all entities of this label
                    for entity in entities:
                        replacement_map[entity] = dummy_data
        
        self.replacement_mapping = replacement_map
        return replacement_map
    
    def redact_text(self, text: str, replacement_mapping: Optional[Dict[str, str]] = None) -> str:
        """
        Redact PII entities in the given text using replacement mapping.
        
        Args:
            text: Original text to redact
            replacement_mapping: Mapping of original entities to dummy values.
                               If None, uses self.replacement_mapping
            
        Returns:
            Redacted text with PII replaced by dummy values
        """
        if replacement_mapping is None:
            replacement_mapping = self.replacement_mapping
        
        if not replacement_mapping:
            raise ValueError("No replacement mapping provided. Run create_replacement_mapping first.")
        
        # Sort entities by length (longest first) to avoid partial replacements
        sorted_entities = sorted(replacement_mapping.keys(), key=len, reverse=True)
        
        # Replace entities in text
        redacted_text = text
        for entity in sorted_entities:
            # Use case-insensitive replacement and handle special characters properly
            escaped_entity = re.escape(entity)
            
            # Use case-insensitive flag and replace all occurrences
            redacted_text = re.sub(escaped_entity, replacement_mapping[entity], 
                                 redacted_text, flags=re.IGNORECASE)
        
        return redacted_text
    
    def redact_from_identified_entities(self, text: str, identified_entities: Dict[str, List[str]]) -> str:
        """
        Redact text using identified entities dictionary.
        
        Args:
            text: Original text to redact
            identified_entities: Dictionary mapping labels to lists of entity texts
            
        Returns:
            Redacted text with PII replaced by dummy values
        """
        replacement_mapping = self.create_replacement_mapping(identified_entities)
        return self.redact_text(text, replacement_mapping)
    
    def redact_from_file(self, input_file: str, identified_entities_file: str, 
                        output_file: str = "redacted.txt", 
                        mapping_file: str = "replacement_mapping.json") -> str:
        """
        Redact text from file using identified entities from JSON file.
        
        Args:
            input_file: Path to input text file
            identified_entities_file: Path to JSON file with identified entities
            output_file: Path to save redacted text
            mapping_file: Path to save replacement mapping JSON
            
        Returns:
            Redacted text
        """
        # Read original text
        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # Read identified entities
        with open(identified_entities_file, 'r', encoding='utf-8') as file:
            identified_entities = json.load(file)
        
        # Redact text
        redacted_text = self.redact_from_identified_entities(text, identified_entities)
        
        # Save redacted text
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(redacted_text)
        
        # Save replacement mapping
        with open(mapping_file, 'w', encoding='utf-8') as file:
            json.dump(self.replacement_mapping, file, ensure_ascii=False, indent=4)
        
        return redacted_text
    
    def get_replacement_mapping(self) -> Dict[str, str]:
        """
        Get the current replacement mapping.
        
        Returns:
            Dictionary mapping original entities to dummy values
        """
        return self.replacement_mapping.copy()
    
    def save_replacement_mapping(self, output_file: str = "replacement_mapping.json") -> None:
        """
        Save the replacement mapping to a JSON file.
        
        Args:
            output_file: Path to save the replacement mapping
        """
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(self.replacement_mapping, file, ensure_ascii=False, indent=4)
    
    def load_replacement_mapping(self, mapping_file: str) -> None:
        """
        Load replacement mapping from a JSON file.
        
        Args:
            mapping_file: Path to the replacement mapping JSON file
        """
        with open(mapping_file, 'r', encoding='utf-8') as file:
            self.replacement_mapping = json.load(file)
    
    def set_dummy_values(self, dummy_values: Dict[str, Union[str, List[str]]]) -> None:
        """
        Set custom dummy values for PII replacement.
        
        Args:
            dummy_values: Dictionary mapping PII labels to dummy replacement values
        """
        self.dummy_values = dummy_values.copy()
    
    def add_dummy_values(self, additional_dummy_values: Dict[str, Union[str, List[str]]]) -> None:
        """
        Add additional dummy values to the existing set.
        
        Args:
            additional_dummy_values: Additional dummy values to include
        """
        self.dummy_values.update(additional_dummy_values)
    
    def get_dummy_values(self) -> Dict[str, Union[str, List[str]]]:
        """
        Get the current dummy values dictionary.
        
        Returns:
            Current dummy values mapping
        """
        return self.dummy_values.copy()
