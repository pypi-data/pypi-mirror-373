import json
import logging
import re

logger = logging.getLogger(__name__)


def parse_json_data(json_string: str) -> dict | None:
    try:
        # Check for empty string
        if not json_string or not json_string.strip():
            logger.warning("Empty JSON string provided")
            return {}

        # First try to extract JSON from Markdown code blocks
        match = re.search(r'```(?:json)?\s*\n(.*?)\n```', json_string, re.DOTALL)
        if match:
            json_string = match.group(1).strip()

        # In case of extra content before or after the JSON object (like YAML frontmatter)
        # we try to extract the JSON object itself.
        start_index = json_string.find('{')
        end_index = json_string.rfind('}')

        if start_index != -1 and end_index > start_index:
            json_string = json_string[start_index:end_index + 1]
        else:
            # If no JSON object is found, we can check for other formats/prefixes
            # as a fallback from the original implementation.
            stripped = json_string.strip()
            if stripped.startswith('<json>'):
                json_string = stripped[6:].strip()
            elif stripped.startswith('json'):
                json_string = stripped[4:].strip()

        # Parse the JSON data
        data = json.loads(json_string)
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON data: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error while parsing JSON data: {e}")
        return {}

