from typing import (
    Any,
    Dict,
    List,
)
import re
from collections.abc import KeysView


def check_templates_for_valid_placeholders(
    source: Dict[str, Any],
    properties_using_templates: List[str],
    availables_keys: KeysView
) -> Dict[str, Any]:
    invalid_placeholders = []
    for template in properties_using_templates:
        subject = source.get(template)
        if subject:
            placeholders = re.findall(r'{(.*?)}', subject)
            missing_fields = [field for field in placeholders
                              if field not in availables_keys]
            if missing_fields:
                invalid_placeholders.append(
                    f"[{template}: {','.join(missing_fields)}]"
                )
    if len(invalid_placeholders) > 0:
        raise ValueError(
            'Invalid placeholders in templates. '
            f'Allowed: [{", ".join(availables_keys)}], '
            f'Invalid received: {", ".join(invalid_placeholders)}'
        )
    return source
