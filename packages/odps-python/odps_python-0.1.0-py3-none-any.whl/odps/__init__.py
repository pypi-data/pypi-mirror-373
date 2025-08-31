# Copyright 2024 ODPS Python Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Open Data Product Specification (ODPS) Python Library

A comprehensive, high-performance Python library for creating, validating, and manipulating
Open Data Product Specification (ODPS) v4.0 documents with full international standards compliance.

Features:
    - Complete ODPS v4.0 specification support
    - Full validation with detailed error reporting
    - Element support with international standards (ISO, RFC, ITU-T)
    - Validation caching and optimizations
    - Type-safe protocols and comprehensive error handling
    - JSON and YAML serialization/deserialization
    - Modular architecture with pluggable validators

Quick Start:
    >>> from odps import OpenDataProduct, ProductDetails
    >>>
    >>> # Create product details
    >>> details = ProductDetails(
    ...     name="My Dataset",
    ...     product_id="dataset-001",
    ...     visibility="public",
    ...     status="production",
    ...     type="dataset"
    ... )
    >>>
    >>> # Create ODPS document
    >>> product = OpenDataProduct(details)
    >>>
    >>> # Validate and export
    >>> product.validate()  # True
    >>> json_str = product.to_json()
    >>> product.save("my_product.json")

Main Classes:
    OpenDataProduct: Main class for ODPS documents
    ProductDetails: Core product information model
    ODPSValidator: Validation utilities
    ODPSValidationError: Validation error exception

Modules:
    core: Main OpenDataProduct class and functionality
    models: All ODPS component data models
    validation: Validation framework and rules
    validators: Individual validation functions
    protocols: Type protocols for duck typing
    enums: Enumeration classes for constants
    exceptions: Exception hierarchy

For detailed documentation, see: https://github.com/accenture/odps-python
For ODPS specification: https://opendataproducts.org/v4.0/
"""

__version__ = "0.1.0"

from .core import OpenDataProduct
from .models import *
from .validators import ODPSValidator
from .enums import *
from .exceptions import *
from .protocols import *

__all__ = ["OpenDataProduct", "ODPSValidationError", "ODPSValidator"]