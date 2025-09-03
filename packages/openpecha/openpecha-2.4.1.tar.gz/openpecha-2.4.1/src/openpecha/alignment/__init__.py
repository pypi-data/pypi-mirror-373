from typing import Dict, List

class TranslationAlignmentMapping:

    def map_annotation_layer_to_layer(self, target_annotation: dict, source_annotation: dict) -> dict:
        '''
        This function takes the target annotation and the source annotation and compare
        both of them layer to layer. Both the annotation within the same pecha.
        And produce a dictionary which gives the output as
        {
            1: [1],
            2: [1, 2]
        }
        which says the target layer index 1 is mapped with source layer index 2 and 
        target layer index 2 is mapped with source layer index 1 and 2.
        The target annotation should be a segmentation annotation.
        The source annotation can be a alignment annotation.
        '''

        if target_annotation is None or source_annotation is None:
            return {}

        mapping: Dict[int, List[int]] = {}

        for source_annotation in source_annotation['alignment']:
            source_index = source_annotation["index"]
            source_start = source_annotation["span"]["start"]
            source_end = source_annotation["span"]["end"]

            overlapping_segments = []

            for segment_item in target_annotation['segmentation']:
                target_index = segment_item["index"]
                target_start = segment_item["span"]["start"]
                target_end = segment_item["span"]["end"]

                # Check for overlap
                if source_start <= target_end and source_end >= target_start:
                    overlapping_segments.append(target_index)

            mapping[source_index] = overlapping_segments
            
        return mapping





        