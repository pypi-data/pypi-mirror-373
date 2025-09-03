from typing import Dict, Any
from openpecha.pecha.serializers.json import JsonSerializer, AlignedPechaJsonSerializer
from openpecha.config import get_logger
from openpecha.pecha.annotations import AlignedPechaJson, PechaJson

logger = get_logger(__name__)


class SerializerLogicHandler:
    """Handles serialization logic for different types of pecha alignment scenarios."""
    
    def serialize(
        self,
        target: Dict[str, Any],
        source: Dict[str, Any] = None
    ) -> PechaJson | AlignedPechaJson:
        """
        Serialize pecha data based on alignment structure.
        
        Args:
            to: Dictionary containing target pecha and its annotations
                Format: {
                    'pecha': Pecha object,
                    'annotations': [{'id': str, 'type': str}]
                }
            from_: Dictionary containing source pecha and its annotations (optional)
                Format: {
                    'pecha': Pecha object,
                    'annotations': [{'id': str, 'type': str, 'aligned_to': str}]
                }
        
        Returns:
            Serialized data structure
        """
        target_pecha = target['pecha']
        target_annotations = target['annotations']
        
        
        if source == None:
            # Simple serialization of target pecha only
            logger.info(f"Serializing target pecha only for Pecha '{target_pecha.id}'.")
            return JsonSerializer().serialize(target_pecha, target_annotations)
        else:
            # Alignment-based serialization
            source_pecha = source['pecha']
            source_annotations = source['annotations']
            logger.info(f"Serializing aligned target and source pechas for Pecha '{target_pecha.id}' and Pecha '{source_pecha.id}'.")
            return AlignedPechaJsonSerializer(
                target_pecha, target_annotations,
                source_pecha, source_annotations
            ).serialize()
    
    