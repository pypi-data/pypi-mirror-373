#!/usr/bin/env python3
# Copyright 2023 LoxiLB
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Type handling utilities for Octavia LoxiLB driver.
"""

import logging

LOG = logging.getLogger(__name__)


def get_attribute(obj, attr_name, default=None):
    """Get an attribute from an object or dictionary.
    
    Handles both dictionary and object types, with special handling for
    property-based attributes in Octavia models.
    
    Args:
        obj: Object or dictionary to get attribute from
        attr_name: Name of the attribute to get
        default: Default value if attribute is not found
        
    Returns:
        The attribute value or default if not found
    """
    if obj is None:
        return default
        
    if isinstance(obj, dict):
        return obj.get(attr_name, default)
    
    # Direct attribute access
    if hasattr(obj, attr_name):
        try:
            value = getattr(obj, attr_name)
            if value is not None:
                return value
        except Exception:
            pass
    
    # Try property access for Octavia models
    if hasattr(obj.__class__, attr_name) and isinstance(getattr(obj.__class__, attr_name), property):
        try:
            value = getattr(obj, attr_name)
            if value is not None:
                return value
        except Exception:
            pass
            
    return default


def get_id(obj, id_attr="id", fallback_attrs=None):
    """Get ID from an object or dictionary.
    
    Tries multiple approaches to get the ID from an object or dictionary.
    
    Args:
        obj: Object or dictionary to get ID from
        id_attr: Primary attribute name for ID
        fallback_attrs: List of fallback attribute names to try
        
    Returns:
        The ID value or None if not found
    """
    if fallback_attrs is None:
        fallback_attrs = []
    
    # Try primary attribute first
    id_value = get_attribute(obj, id_attr)
    if id_value:
        return id_value
        
    # Try fallback attributes
    for attr in fallback_attrs:
        id_value = get_attribute(obj, attr)
        if id_value:
            return id_value
            
    return None


def to_dict(obj):
    """Convert an object to a dictionary.
    
    If the object is already a dictionary, returns it unchanged.
    If it's an object with a to_dict method, calls that method.
    Otherwise, creates a dictionary from the object's attributes.
    
    Args:
        obj: Object to convert to dictionary
        
    Returns:
        Dictionary representation of the object
    """
    if obj is None:
        return {}
        
    if isinstance(obj, dict):
        return obj
        
    # If object has a to_dict method, use it
    if hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
        try:
            return obj.to_dict()
        except Exception as e:
            LOG.warning("Failed to convert object to dict using to_dict method: %s", e)
    
    # Create dictionary from object attributes
    result = {}
    for attr in dir(obj):
        if not attr.startswith('_') and not callable(getattr(obj, attr)):
            try:
                result[attr] = getattr(obj, attr)
            except Exception:
                pass
                
    return result
