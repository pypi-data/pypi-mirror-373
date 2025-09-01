import json
from typing import List, Dict, Any, Optional
from gliner import GLiNER
from ..config.labels import DEFAULT_LABELS


class PIIIdentifier:
    """
    Identifies personally identifiable information (PII) in text using GLiNER model.
    
    This class provides functionality to detect and extract various types of PII
    from text documents using a pre-trained GLiNER model.
    """
    
    def __init__(self, model_name: str = "urchade/gliner_multi_pii-v1", labels: Optional[List[str]] = None):
        """
        Initialize the PII identifier.
        
        Args:
            model_name: Name of the GLiNER model to use
            labels: List of PII labels to identify. If None, uses DEFAULT_LABELS
        """
        self.model_name = model_name
        self.labels = labels or DEFAULT_LABELS.copy()
        self._model = None
        
    def _load_model(self) -> None:
        """Load the GLiNER model if not already loaded."""
        if self._model is None:
            self._model = GLiNER.from_pretrained(self.model_name)
    
    def chunk_text(self, text: str, chunk_size: int = 384) -> List[str]:
        """
        Split text into chunks of specified size.
        
        Args:
            text: Input text to chunk
            chunk_size: Size of each chunk in characters
            
        Returns:
            List of text chunks
        """
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i+chunk_size])
        return chunks
    
    def identify_entities(self, text: str, chunk_size: int = 384) -> List[Dict[str, Any]]:
        """
        Identify PII entities in the given text.
        
        Args:
            text: Input text to analyze
            chunk_size: Size of chunks for processing
            
        Returns:
            List of identified entities with text, label, start, and end positions
        """
        self._load_model()
        
        chunks = self.chunk_text(text, chunk_size)
        all_entities = []
        
        for i, chunk in enumerate(chunks):
            entities = self._model.predict_entities(chunk, self.labels)
            # Adjust entity positions to account for chunking
            chunk_start = i * chunk_size
            for entity in entities:
                entity['start'] += chunk_start
                entity['end'] += chunk_start
            all_entities.extend(entities)
        
        return self._remove_duplicates(all_entities)
    
    def _remove_duplicates(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate entities while preserving order.
        
        Args:
            entities: List of entities to deduplicate
            
        Returns:
            List of unique entities
        """
        seen = set()
        unique_entities = []
        for entity in entities:
            entity_key = (entity["text"], entity["label"])
            if entity_key not in seen:
                seen.add(entity_key)
                unique_entities.append(entity)
        return unique_entities
    
    def create_entity_mapping(self, entities: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Create a mapping of entity labels to their text values.
        
        Args:
            entities: List of identified entities
            
        Returns:
            Dictionary mapping labels to lists of entity texts
        """
        entity_mapping = {}
        for entity in entities:
            entity_text = entity["text"]
            entity_label = entity["label"]
            
            if entity_label not in entity_mapping:
                entity_mapping[entity_label] = []
            
            if entity_text not in entity_mapping[entity_label]:
                entity_mapping[entity_label].append(entity_text)
        
        return entity_mapping
    
    def identify_and_save(self, text: str, output_file: str = "identified.json", 
                         chunk_size: int = 384) -> Dict[str, List[str]]:
        """
        Identify PII entities and save results to JSON file.
        
        Args:
            text: Input text to analyze
            output_file: Path to save the identified entities JSON
            chunk_size: Size of chunks for processing
            
        Returns:
            Dictionary mapping labels to lists of entity texts
        """
        entities = self.identify_entities(text, chunk_size)
        entity_mapping = self.create_entity_mapping(entities)
        
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(entity_mapping, json_file, indent=2, ensure_ascii=False)
        
        return entity_mapping
    
    def add_custom_labels(self, custom_labels: List[str]) -> None:
        """
        Add custom labels to the existing label set.
        
        Args:
            custom_labels: List of additional labels to include
        """
        self.labels.extend(custom_labels)
    
    def set_labels(self, labels: List[str]) -> None:
        """
        Set the labels to use for PII identification.
        
        Args:
            labels: List of labels to use
        """
        self.labels = labels.copy()
    
    def get_labels(self) -> List[str]:
        """
        Get the current list of labels.
        
        Returns:
            Current list of PII labels
        """
        return self.labels.copy()
