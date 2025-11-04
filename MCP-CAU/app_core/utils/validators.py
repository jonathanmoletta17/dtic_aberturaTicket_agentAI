# -*- coding: utf-8 -*-

def is_powerfx_expression(value) -> bool:
    if isinstance(value, str):
        v = value.strip()
        patterns = [
            (v.startswith('{') and v.endswith('}') and 'Topic.' in v),
            (v.startswith('=') and 'Topic.' in v),
            (v.startswith('@{') and v.endswith('}') and 'Topic.' in v),
        ]
        return any(patterns)
    return False


