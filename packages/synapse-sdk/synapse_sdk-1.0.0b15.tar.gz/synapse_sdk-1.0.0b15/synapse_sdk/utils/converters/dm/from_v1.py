from . import BaseDMConverter


class DMV1ToV2Converter(BaseDMConverter):
    """DM v1 to v2 format converter class."""

    def __init__(self, old_dm_data={}, file_type=None):
        """Initialize the converter.

        Args:
            old_dm_data (dict): DM v1 format data to be converted
            file_type (str, optional): Type of file being converted
        """
        super().__init__(file_type)
        self.old_dm_data = old_dm_data
        self.classification_info = {}
        self.media_data = {}

    def convert(self):
        """Convert DM v1 data to v2 format.

        Returns:
            dict: Converted data in DM v2 format
        """
        # Reset state
        old_dm_data = self.old_dm_data
        self.classification_info = {}
        self.media_data = {}

        # Extract media IDs from annotations key
        media_ids = list(old_dm_data.get('annotations', {}).keys())

        # If file_type is not specified, try to detect from media_ids
        if not self.file_type and media_ids:
            detected_file_type = self._detect_file_type(media_ids[0])
            if detected_file_type:
                self.file_type = detected_file_type
                # Re-setup tool processors with detected file_type
                self.tool_processors = self._setup_tool_processors()

        for media_id in media_ids:
            self._convert_media_item(old_dm_data, media_id)

        # Build final result (put classification at the front)
        result = {'classification': self.classification_info}
        result.update(self.media_data)

        return result

    def _detect_file_type(self, media_id):
        """Detect file type from media ID."""
        if '_' in media_id:
            return media_id.split('_')[0]
        return media_id

    def _convert_media_item(self, old_dm_data, media_id):
        """Process a single media item.

        Args:
            old_dm_data (dict): Original DM v1 data
            media_id (str): ID of the media item to process
        """
        # Extract media type (e.g., "video_1" -> "videos", "image_2" -> "images")
        media_type, media_type_plural = self._extract_media_type_info(media_id)

        # Create list for this media type if it doesn't exist
        if media_type_plural not in self.media_data:
            self.media_data[media_type_plural] = []

        # Create id -> class and tool mappings
        annotations = old_dm_data.get('annotations', {}).get(media_id, [])

        id_to_class = {}
        id_to_tool = {}
        for annotation in annotations:
            id_to_class[annotation['id']] = annotation['classification']['class']
            id_to_tool[annotation['id']] = annotation['tool']

        # Create id -> full classification mapping (including additional attributes)
        id_to_full_classification = {annotation['id']: annotation['classification'] for annotation in annotations}

        # Collect all classifications from annotations (regardless of whether they have data)
        for annotation in annotations:
            tool_type = annotation['tool']
            classification = annotation['classification']['class']

            if tool_type not in self.classification_info:
                self.classification_info[tool_type] = []

            # Add only non-duplicate classifications
            if classification and classification not in self.classification_info[tool_type]:
                self.classification_info[tool_type].append(classification)

        # Initialize current media item
        media_item = {}

        # Process data from annotationsData for this media
        annotations_data = old_dm_data.get('annotationsData', {}).get(media_id, [])

        # Group by annotation tool type
        tools_data = {}

        for item in annotations_data:
            item_id = item.get('id', '')
            # Get tool and classification info from annotations
            tool_type = id_to_tool.get(item_id, '')
            classification = id_to_class.get(item_id, '')

            # Process by each tool type
            self._convert_annotation_item(
                item, item_id, tool_type, classification, id_to_full_classification, tools_data, media_type
            )

        # Add processed tool data to media item
        for tool_type, tool_data in tools_data.items():
            if tool_data:  # Only add if data exists
                media_item[tool_type] = tool_data

        # Add media item to result (only if data exists)
        if media_item:
            self.media_data[media_type_plural].append(media_item)

    def _convert_annotation_item(
        self, item, item_id, tool_type, classification, id_to_full_classification, tools_data, media_type
    ):
        """Process a single annotation item based on its tool type and media type.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            tool_type (str): Type of annotation tool
            classification (str): Classification label
            id_to_full_classification (dict): Mapping of ID to full classification data
            tools_data (dict): Dictionary to store processed tool data
            media_type (str): Type of media (image, video, pcd, text)
        """
        # Check if tool_processors is available and contains the tool_type
        if hasattr(self, 'tool_processors') and self.tool_processors:
            processor = self.tool_processors.get(tool_type)
            if processor:
                processor(item, item_id, classification, tools_data, id_to_full_classification)
            else:
                self._handle_unknown_tool(tool_type, item_id)
        else:
            # Use file_type + tool_type pattern for method names
            method_name = f'_convert_{media_type}_{tool_type}'
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                method(item, item_id, classification, tools_data, id_to_full_classification)
            else:
                self._handle_unknown_tool(tool_type, item_id, media_type)

    def _handle_unknown_tool(self, tool_type, item_id=None, media_type=None):
        """Handle unknown tool types with consistent warning message."""
        warning_msg = f"Warning: Unknown tool type '{tool_type}'"
        if media_type:
            warning_msg += f' for media type {media_type}'
        if item_id:
            warning_msg += f' for item {item_id}'
        print(warning_msg)

    def _extract_media_type_info(self, media_id):
        """Extract media type information from media ID."""
        media_type = media_id.split('_')[0] if '_' in media_id else media_id
        media_type_plural = media_type + 's' if not media_type.endswith('s') else media_type
        return media_type, media_type_plural

    def _singularize_media_type(self, media_type_plural):
        """Convert plural media type to singular."""
        return media_type_plural.rstrip('s')

    def _process_bounding_box_common(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process bounding box annotation - common logic.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'bounding_box' not in tools_data:
            tools_data['bounding_box'] = []

        # Process coordinate or coordinates
        coord_data = None
        if 'coordinate' in item and isinstance(item['coordinate'], dict):
            # Single coordinate structure (dictionary)
            coord_data = item['coordinate']
        elif 'coordinates' in item:
            # Multiple coordinates structure (video etc.)
            coords_data = item['coordinates']
            if coords_data:
                # Use coordinate data from first key
                first_key = list(coords_data.keys())[0]
                coord_data = coords_data[first_key]

        if coord_data and 'width' in coord_data and 'height' in coord_data:
            data = [
                coord_data['x'],
                coord_data['y'],
                coord_data['width'],
                coord_data['height'],
            ]

            tools_data['bounding_box'].append({
                'id': item_id,
                'classification': classification,
                'attrs': [],
                'data': data,
            })

    def _convert_bounding_box(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process bounding box annotation."""
        return self._process_bounding_box_common(item, item_id, classification, tools_data, id_to_full_classification)

    def _convert_named_entity(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process named entity annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'named_entity' not in tools_data:
            tools_data['named_entity'] = []

        # Process named_entity ranges and content
        entity_data = {}
        if 'ranges' in item and isinstance(item['ranges'], list):
            # Store ranges information
            entity_data['ranges'] = item['ranges']

        if 'content' in item:
            # Store selected text content
            entity_data['content'] = item['content']

        tools_data['named_entity'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': entity_data,  # Format: {ranges: [...], content: "..."}
        })

    def _process_polyline_common(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process polyline annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'polyline' not in tools_data:
            tools_data['polyline'] = []

        # Process polyline coordinates
        polyline_data = []
        if 'coordinate' in item and isinstance(item['coordinate'], list):
            # Convert each coordinate point to [x, y] format
            for point in item['coordinate']:
                if 'x' in point and 'y' in point:
                    polyline_data.append([point['x'], point['y']])

        tools_data['polyline'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': polyline_data,  # Format: [[x1, y1], [x2, y2], [x3, y3], ...]
        })

    def _process_keypoint_common(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process keypoint annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'keypoint' not in tools_data:
            tools_data['keypoint'] = []

        # Process keypoint coordinate (single point)
        keypoint_data = []
        if 'coordinate' in item and isinstance(item['coordinate'], dict):
            coord = item['coordinate']
            if 'x' in coord and 'y' in coord:
                keypoint_data = [coord['x'], coord['y']]

        tools_data['keypoint'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': keypoint_data,  # Format: [x, y]
        })

    def _convert_3d_bounding_box(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process 3D bounding box annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if '3d_bounding_box' not in tools_data:
            tools_data['3d_bounding_box'] = []

        # Process 3d_bounding_box psr (position, scale, rotation)
        psr_data = {}
        if 'psr' in item and isinstance(item['psr'], dict):
            psr = item['psr']

            # Extract only x, y, z values from position, scale, rotation
            for component in ['position', 'scale', 'rotation']:
                if component in psr and isinstance(psr[component], dict):
                    psr_data[component] = {
                        'x': psr[component].get('x'),
                        'y': psr[component].get('y'),
                        'z': psr[component].get('z'),
                    }

        tools_data['3d_bounding_box'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': psr_data,  # Format: {position: {x,y,z}, scale: {x,y,z}, rotation: {x,y,z}}
        })

    def _convert_video_segmentation_data(
        self, item, item_id, classification, tools_data, id_to_full_classification=None
    ):
        """Process video segmentation annotation data.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'segmentation' not in tools_data:
            tools_data['segmentation'] = []

        # Process frame section-based segmentation (videos)
        segmentation_data = {}
        if 'section' in item and isinstance(item['section'], dict):
            segmentation_data = item['section']

        tools_data['segmentation'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': segmentation_data,  # Format: {startFrame: x, endFrame: y}
        })

    def _convert_image_segmentation_data(
        self, item, item_id, classification, tools_data, id_to_full_classification=None
    ):
        """Process image segmentation annotation data.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'segmentation' not in tools_data:
            tools_data['segmentation'] = []

        # Process pixel-based segmentation (images)
        segmentation_data = {}
        if 'pixel_indices' in item and isinstance(item['pixel_indices'], list):
            segmentation_data = item['pixel_indices']

        tools_data['segmentation'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': segmentation_data,  # Format: [pixel_indices...]
        })

    def _process_polygon_common(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process polygon annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'polygon' not in tools_data:
            tools_data['polygon'] = []

        # Process polygon coordinates
        polygon_data = []
        if 'coordinate' in item and isinstance(item['coordinate'], list):
            # Convert each coordinate point to [x, y] format
            for point in item['coordinate']:
                if 'x' in point and 'y' in point:
                    polygon_data.append([point['x'], point['y']])

        tools_data['polygon'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': polygon_data,  # Format: [[x1, y1], [x2, y2], [x3, y3], ...]
        })

    def _process_relation_common(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process relation annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'relation' not in tools_data:
            tools_data['relation'] = []

        # Process relation data (needs adjustment based on actual relation data structure)
        relation_data = []
        if 'data' in item:
            relation_data = item['data']

        tools_data['relation'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': relation_data,  # Format: ['from_id', 'to_id']
        })

    def _convert_group(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process group annotation.

        Args:
            item (dict): Annotation item data
            item_id (str): ID of the annotation item
            classification (str): Classification label
            tools_data (dict): Dictionary to store processed tool data
            id_to_full_classification (dict, optional): Full classification mapping
        """
        if 'group' not in tools_data:
            tools_data['group'] = []

        # Process group data (needs adjustment based on actual group data structure)
        group_data = []
        if 'data' in item:
            group_data = item['data']

        tools_data['group'].append({
            'id': item_id,
            'classification': classification,
            'attrs': [],
            'data': group_data,  # Format: ['id1', 'id2', 'id3', ...]
        })

    # Include all the _convert_* methods from previous code...
    def _convert_classification(self, item, item_id, classification, tools_data, id_to_full_classification):
        """Process classification annotation."""
        if 'classification' not in tools_data:
            tools_data['classification'] = []

        # Get full classification info (including additional attributes)
        full_classification = id_to_full_classification.get(item_id, {})

        # Store additional attributes in attrs array
        attrs = []
        classification_data = {}

        for key, value in full_classification.items():
            if key != 'class':  # class is already stored in classification field
                if isinstance(value, list) and len(value) > 0:
                    # Array attributes like multiple
                    attrs.append({'name': key, 'value': value})
                elif isinstance(value, str) and value.strip():
                    # String attributes like text, single_radio, single_dropdown
                    attrs.append({'name': key, 'value': value})

        tools_data['classification'].append({
            'id': item_id,
            'classification': classification,
            'attrs': attrs,
            'data': classification_data,  # Empty object for full text classification
        })

    def _convert_prompt(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process prompt annotation."""
        if 'prompt' not in tools_data:
            tools_data['prompt'] = []

        # Process prompt input data from annotationsData
        prompt_data = {}
        attrs = []

        if 'input' in item and isinstance(item['input'], list):
            # Store complete input structure
            input_items = []
            for input_item in item['input']:
                if isinstance(input_item, dict):
                    input_items.append(input_item)
                    # Extract text value for easy access
                    if input_item.get('type') == 'text' and 'value' in input_item:
                        prompt_data['text'] = input_item['value']
                        attrs.append('text')

            prompt_data['input'] = input_items
            attrs.append('input')

        # Include any additional metadata
        for key in ['model', 'displayName', 'generatedBy', 'timestamp']:
            if key in item:
                prompt_data[key] = item[key]
                attrs.append(key)

        result_item = {
            'id': item_id,
            'classification': classification,
            'attrs': attrs,
            'data': prompt_data,  # Format: {text: "prompt text", input: [...], ...}
        }
        tools_data['prompt'].append(result_item)

    def _convert_answer(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process answer annotation."""
        if 'answer' not in tools_data:
            tools_data['answer'] = []

        # Process answer output data from annotationsData
        answer_data = {}
        attrs = []

        if 'output' in item and isinstance(item['output'], list):
            # Store complete output structure
            output_items = []
            for output_item in item['output']:
                if isinstance(output_item, dict):
                    output_items.append(output_item)
                    # Extract text value for easy access
                    if output_item.get('type') == 'text' and 'value' in output_item:
                        answer_data['text'] = output_item['value']
                        attrs.append('text')

            answer_data['output'] = output_items
            attrs.append('output')

        # Include all additional metadata from annotationsData
        metadata_fields = ['model', 'displayName', 'generatedBy', 'promptAnnotationId', 'timestamp', 'primaryKey']
        for key in metadata_fields:
            if key in item:
                answer_data[key] = item[key]
                attrs.append(key)

        result_item = {
            'id': item_id,
            'classification': classification,
            'attrs': attrs,
            'data': answer_data,  # Format: {text: "answer text", output: [...], model: "...", ...}
        }

        tools_data['answer'].append(result_item)

    def _convert_3d_segmentation(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process 3D segmentation annotation."""
        if '3d_segmentation' not in tools_data:
            tools_data['3d_segmentation'] = []

        # Process 3D segmentation point data from annotationsData
        segmentation_data = {}
        attrs = []

        if 'points' in item and isinstance(item['points'], list):
            segmentation_data['points'] = item['points']
            attrs.append('points')

        # Include any additional metadata
        for key in ['tool']:
            if key in item:
                segmentation_data[key] = item[key]
                attrs.append(key)

        result_item = {
            'id': item_id,
            'classification': classification,
            'attrs': attrs,
            'data': segmentation_data,  # Format: {points: [146534, 146662, ...], ...}
        }
        tools_data['3d_segmentation'].append(result_item)

    def _convert_polygon(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process polygon annotation."""
        return self._process_polygon_common(item, item_id, classification, tools_data, id_to_full_classification)

    def _convert_polyline(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process polyline annotation."""
        return self._process_polyline_common(item, item_id, classification, tools_data, id_to_full_classification)

    def _convert_keypoint(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process keypoint annotation."""
        return self._process_keypoint_common(item, item_id, classification, tools_data, id_to_full_classification)

    # Segmentation methods
    def _convert_image_segmentation(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process segmentation annotation for image."""
        return self._convert_image_segmentation_data(
            item, item_id, classification, tools_data, id_to_full_classification
        )

    def _convert_video_segmentation(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process segmentation annotation for video."""
        return self._convert_video_segmentation_data(
            item, item_id, classification, tools_data, id_to_full_classification
        )

    def _convert_relation(self, item, item_id, classification, tools_data, id_to_full_classification=None):
        """Process relation annotation."""
        return self._process_relation_common(item, item_id, classification, tools_data, id_to_full_classification)
