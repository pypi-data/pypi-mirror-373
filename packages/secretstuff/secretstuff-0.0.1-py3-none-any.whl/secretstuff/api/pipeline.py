import json
from typing import Dict, List, Optional, Union, Tuple, Any
from ..core.identifier import PIIIdentifier
from ..core.redactor import PIIRedactor
from ..core.reverse_mapper import ReverseMapper
from ..config.labels import DEFAULT_LABELS
from ..config.dummy_values import DEFAULT_DUMMY_VALUES


class SecretStuffPipeline:
    """
    High-level pipeline for PII identification, redaction, and reverse mapping operations.
    
    This class provides a simple, unified interface for all SecretStuff operations,
    allowing users to perform complex PII workflows with minimal code.
    """
    
    def __init__(self, 
                 model_name: str = "urchade/gliner_multi_pii-v1",
                 labels: Optional[List[str]] = None,
                 dummy_values: Optional[Dict[str, Union[str, List[str]]]] = None):
        """
        Initialize the SecretStuff pipeline.
        
        Args:
            model_name: Name of the GLiNER model to use for PII identification
            labels: List of PII labels to identify. If None, uses DEFAULT_LABELS
            dummy_values: Dictionary mapping PII labels to dummy replacement values.
                         If None, uses DEFAULT_DUMMY_VALUES
        """
        self.identifier = PIIIdentifier(model_name, labels)
        self.redactor = PIIRedactor(dummy_values)
        self.reverse_mapper = ReverseMapper()
        
        self._last_identified_entities = {}
        self._last_replacement_mapping = {}
    
    def identify_pii(self, text: str, chunk_size: int = 384) -> Dict[str, List[str]]:
        """
        Identify PII entities in the given text.
        
        Args:
            text: Input text to analyze for PII
            chunk_size: Size of chunks for processing large texts
            
        Returns:
            Dictionary mapping PII labels to lists of identified entity texts
        """
        self._last_identified_entities = self.identifier.identify_and_save(
            text, "identified_entities.json", chunk_size
        )
        return self._last_identified_entities
    
    def redact_pii(self, text: str, identified_entities: Optional[Dict[str, List[str]]] = None) -> str:
        """
        Redact PII entities in the given text.
        
        Args:
            text: Original text to redact
            identified_entities: Previously identified entities. If None, uses last identified entities
            
        Returns:
            Redacted text with PII replaced by dummy values
        """
        if identified_entities is None:
            if not self._last_identified_entities:
                raise ValueError("No identified entities available. Run identify_pii first or provide identified_entities.")
            identified_entities = self._last_identified_entities
        
        redacted_text = self.redactor.redact_from_identified_entities(text, identified_entities)
        self._last_replacement_mapping = self.redactor.get_replacement_mapping()
        
        return redacted_text
    
    def identify_and_redact(self, text: str, chunk_size: int = 384) -> Tuple[str, Dict[str, List[str]], Dict[str, str]]:
        """
        Identify PII and redact text in a single operation.
        
        Args:
            text: Input text to process
            chunk_size: Size of chunks for processing large texts
            
        Returns:
            Tuple containing:
            - Redacted text
            - Dictionary of identified entities
            - Dictionary of replacement mappings
        """
        identified_entities = self.identify_pii(text, chunk_size)
        redacted_text = self.redact_pii(text, identified_entities)
        
        return redacted_text, identified_entities, self._last_replacement_mapping
    
    def reverse_redaction(self, redacted_text: str, 
                         replacement_mapping: Optional[Dict[str, str]] = None) -> Tuple[str, int, Dict[str, int]]:
        """
        Reverse redaction to restore original PII entities.
        
        Args:
            redacted_text: Text with dummy values to reverse
            replacement_mapping: Mapping of original entities to dummy values.
                               If None, uses last replacement mapping
            
        Returns:
            Tuple containing:
            - Restored text with original PII
            - Total number of replacements made
            - Dictionary mapping dummy values to replacement counts
        """
        if replacement_mapping is None:
            if not self._last_replacement_mapping:
                raise ValueError("No replacement mapping available. Provide replacement_mapping or run redact_pii first.")
            replacement_mapping = self._last_replacement_mapping
        
        self.reverse_mapper.set_replacement_mapping(replacement_mapping)
        return self.reverse_mapper.reverse_redaction(redacted_text)
    
    def process_text_file(self, input_file: str, 
                         output_redacted: str = "redacted.txt",
                         output_identified: str = "identified_entities.json",
                         output_mapping: str = "replacement_mapping.json",
                         chunk_size: int = 384) -> Dict[str, Any]:
        """
        Process a text file through the complete PII pipeline.
        
        Args:
            input_file: Path to input text file
            output_redacted: Path to save redacted text
            output_identified: Path to save identified entities JSON
            output_mapping: Path to save replacement mapping JSON
            chunk_size: Size of chunks for processing
            
        Returns:
            Dictionary containing processing results and file paths
        """
        # Read input text
        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # Identify PII
        identified_entities = self.identifier.identify_and_save(text, output_identified, chunk_size)
        
        # Redact text
        redacted_text = self.redactor.redact_from_file(
            input_file, output_identified, output_redacted, output_mapping
        )
        
        # Update internal state
        self._last_identified_entities = identified_entities
        self._last_replacement_mapping = self.redactor.get_replacement_mapping()
        
        return {
            "input_file": input_file,
            "redacted_file": output_redacted,
            "identified_file": output_identified,
            "mapping_file": output_mapping,
            "entities_count": len(self._last_replacement_mapping),
            "labels_found": list(identified_entities.keys())
        }
    
    def reverse_from_files(self, redacted_file: str, mapping_file: str, 
                          output_file: str = "restored.txt") -> Dict[str, Any]:
        """
        Reverse redaction using files.
        
        Args:
            redacted_file: Path to redacted text file
            mapping_file: Path to replacement mapping JSON file
            output_file: Path to save restored text
            
        Returns:
            Dictionary containing reversal results
        """
        restored_text, total_replaced, replacement_counts = self.reverse_mapper.reverse_from_file(
            redacted_file, mapping_file, output_file
        )
        
        return {
            "redacted_file": redacted_file,
            "mapping_file": mapping_file,
            "restored_file": output_file,
            "total_replacements": total_replaced,
            "replacement_details": replacement_counts
        }
    
    def get_last_identified_entities(self) -> Dict[str, List[str]]:
        """
        Get the last identified entities.
        
        Returns:
            Dictionary of last identified entities
        """
        return self._last_identified_entities.copy()
    
    def get_last_replacement_mapping(self) -> Dict[str, str]:
        """
        Get the last replacement mapping.
        
        Returns:
            Dictionary of last replacement mapping
        """
        return self._last_replacement_mapping.copy()
    
    def configure_labels(self, labels: List[str]) -> None:
        """
        Configure the PII labels to identify.
        
        Args:
            labels: List of PII labels to use
        """
        self.identifier.set_labels(labels)
    
    def add_custom_labels(self, custom_labels: List[str]) -> None:
        """
        Add custom labels to the existing label set.
        
        Args:
            custom_labels: List of additional labels to include
        """
        self.identifier.add_custom_labels(custom_labels)
    
    def configure_dummy_values(self, dummy_values: Dict[str, Union[str, List[str]]]) -> None:
        """
        Configure the dummy values for PII replacement.
        
        Args:
            dummy_values: Dictionary mapping PII labels to dummy replacement values
        """
        self.redactor.set_dummy_values(dummy_values)
    
    def add_custom_dummy_values(self, additional_dummy_values: Dict[str, Union[str, List[str]]]) -> None:
        """
        Add additional dummy values to the existing set.
        
        Args:
            additional_dummy_values: Additional dummy values to include
        """
        self.redactor.add_dummy_values(additional_dummy_values)
    
    def get_available_labels(self) -> List[str]:
        """
        Get the current list of available PII labels.
        
        Returns:
            List of currently configured PII labels
        """
        return self.identifier.get_labels()
    
    def get_dummy_values(self) -> Dict[str, Union[str, List[str]]]:
        """
        Get the current dummy values configuration.
        
        Returns:
            Dictionary of current dummy values
        """
        return self.redactor.get_dummy_values()
    
    def reset_pipeline(self) -> None:
        """
        Reset the pipeline state, clearing cached entities and mappings.
        """
        self._last_identified_entities = {}
        self._last_replacement_mapping = {}
        self.redactor.replacement_mapping = {}
        self.reverse_mapper.replacement_mapping = {}
        self.reverse_mapper.reverse_mapping = {}
