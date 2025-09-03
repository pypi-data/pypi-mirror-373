"""
Schema loader utility for IvyBloom CLI tools.

This module provides functionality to load tool schemas from the authenticated API,
ensuring all schema access is properly gated through user authentication.
"""

from typing import Dict, Any, Optional, List

# Tool aliases mapping for UI compatibility
TOOL_ALIASES = {
    'proteinfolding': 'esmfold',
    'moleculardocking': 'diffdock', 
    'denovodesign': 'reinvent',
    'fragmentsearch': 'fragment_library',
    'aianalysis': 'biobert',
    'csp': 'xtalnet_csp',
    'polymorphscreening': 'xtalnet_csp'
}

class SchemaLoader:
    """Schema loader that retrieves tool schemas from authenticated API."""
    
    def __init__(self):
        self._schema_cache: Dict[str, Dict[str, Any]] = {}
    
    def resolve_tool_name(self, tool_name: str) -> str:
        """Resolve tool aliases to actual tool names."""
        return TOOL_ALIASES.get(tool_name.lower(), tool_name)
    
    def get_tool_schema(self, tool_name: str, api_client) -> Optional[Dict[str, Any]]:
        """Get schema information for a tool from the authenticated API.
        
        Args:
            tool_name: Name of the tool to get schema for
            api_client: Authenticated API client instance
            
        Returns:
            Schema data dictionary or None if not found
        """
        # Resolve aliases
        resolved_name = self.resolve_tool_name(tool_name)
        
        # Check cache
        cache_key = f"{resolved_name}"
        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]
        
        try:
            # Load schema from API
            schema_data = api_client.get_tool_schema(resolved_name)
            
            # Cache the result
            if schema_data:
                self._schema_cache[cache_key] = schema_data
            
            return schema_data
            
        except Exception as e:
            print(f"Warning: Could not load schema for {tool_name}: {e}")
            return None
    
    def get_available_tools(self, api_client, verbose: bool = False) -> List[Any]:
        """Get list of all available tools from the authenticated API.
        
        Args:
            api_client: Authenticated API client instance
            
        Returns:
            List of available tool names
        """
        try:
            tools_data = api_client.list_tools(verbose=verbose)
            if isinstance(tools_data, list):
                return tools_data
            elif isinstance(tools_data, dict) and 'tools' in tools_data:
                return tools_data['tools']
            else:
                return []
        except Exception as e:
            print(f"Warning: Could not load available tools: {e}")
            return []
    
    def clear_cache(self):
        """Clear the schema cache."""
        self._schema_cache.clear()

# Global schema loader instance
_schema_loader = SchemaLoader()

def get_tool_schema(tool_name: str, api_client) -> Optional[Dict[str, Any]]:
    """Get schema information for a tool using authenticated API.
    
    Args:
        tool_name: Name of the tool
        api_client: Authenticated API client instance
        
    Returns:
        Schema data dictionary or None if not found
    """
    return _schema_loader.get_tool_schema(tool_name, api_client)

def get_available_tools(api_client) -> List[str]:
    """Get list of available tools using authenticated API.
    
    Args:
        api_client: Authenticated API client instance
        
    Returns:
        List of available tool names
    """
    return _schema_loader.get_available_tools(api_client)

def resolve_tool_name(tool_name: str) -> str:
    """Resolve tool name aliases."""
    return _schema_loader.resolve_tool_name(tool_name)

# -------------------------
# Schema normalization utils
# -------------------------

def normalize_parameters_schema(schema_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize various parameter schema shapes into a standard form.

    Supports:
      - JSON Schema-like: parameters: { properties: {...}, required: [...] }
      - Flat dict form:   parameters: { param: { type, required, ... }, ... }

    Returns a dict with keys:
      - properties: Dict[str, Dict[str, Any]]
      - required: List[str]
    """
    parameters = schema_data.get('parameters') or {}

    if not isinstance(parameters, dict):
        return {"properties": {}, "required": []}

    # JSON Schema-like
    if 'properties' in parameters:
        properties = parameters.get('properties') or {}
        required = parameters.get('required') or []
        if not isinstance(properties, dict):
            properties = {}
        if not isinstance(required, list):
            required = []
        return {"properties": properties, "required": required}

    # Flat dict form -> lift to properties/required
    properties: Dict[str, Any] = {}
    required: List[str] = []
    for name, spec in parameters.items():
        if not isinstance(spec, dict):
            # best-effort wrap
            properties[str(name)] = {"type": "string", "description": str(spec)}
            continue
        properties[str(name)] = spec
        if spec.get('required') is True:
            required.append(str(name))

    return {"properties": properties, "required": required}


def get_parameter_definitions(schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return a list of parameter definitions with normalized fields.

    Each item contains: name, type, required, description, default, enum, schema
    """
    normalized = normalize_parameters_schema(schema_data)
    properties = normalized.get('properties', {})
    required = set(normalized.get('required', []))

    items: List[Dict[str, Any]] = []
    for name, spec in properties.items():
        if not isinstance(spec, dict):
            spec = {}
        items.append({
            'name': name,
            'type': spec.get('type', 'unknown'),
            'required': name in required,
            'description': spec.get('description', ''),
            'default': spec.get('default'),
            'enum': spec.get('enum'),
            'schema': spec,
        })
    return items


def extract_enum_choices(schema_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Collect enum choices recursively for completion helpers.

    Returns a dict mapping parameter paths (e.g., "ligand.input_type") to enum value lists.
    """
    normalized = normalize_parameters_schema(schema_data)
    properties = normalized.get('properties', {})

    results: Dict[str, List[str]] = {}

    def walk(spec: Dict[str, Any], path: str):
        if not isinstance(spec, dict):
            return
        if 'enum' in spec and isinstance(spec['enum'], list) and spec['enum']:
            results[path] = [str(v) for v in spec['enum']]
        if spec.get('type') == 'object' and isinstance(spec.get('properties'), dict):
            for key, child in spec['properties'].items():
                walk(child, f"{path}.{key}" if path else key)
        if spec.get('type') == 'array' and isinstance(spec.get('items'), dict):
            walk(spec['items'], f"{path}[]")

    for key, spec in properties.items():
        walk(spec, key)

    return results


def build_json_schema(schema_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build a JSON Schema document from the normalized tool schema.

    This produces a draft-07-ish schema for validating CLI parameter objects.
    """
    normalized = normalize_parameters_schema(schema_data)
    properties = normalized.get('properties', {})
    required = normalized.get('required', [])

    def convert(spec: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(spec, dict):
            return {}
        out: Dict[str, Any] = {}
        # passthrough basic constraints
        for key in [
            'type', 'enum', 'default', 'min', 'max', 'minLength', 'maxLength',
            'minItems', 'maxItems'
        ]:
            if key in spec:
                out[key] = spec[key]

        t = spec.get('type')
        if t == 'object':
            child_props = spec.get('properties') or {}
            out['type'] = 'object'
            out['properties'] = {k: convert(v or {}) for k, v in child_props.items()}
            if isinstance(spec.get('required'), list):
                out['required'] = spec['required']
        elif t == 'array':
            out['type'] = 'array'
            if isinstance(spec.get('items'), dict):
                out['items'] = convert(spec['items'])
        return out

    json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {k: convert(v or {}) for k, v in properties.items()},
        "required": required,
        "additionalProperties": False,
    }
    return json_schema