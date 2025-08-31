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
Data models for Open Data Product Specification (ODPS) v4.0 components.

This module contains all the dataclass models that represent the various components
of an ODPS v4.0 document. Each model follows the official specification and includes
comprehensive validation support.

The models are organized into the following categories:

Core Models:
    - ProductDetails: Core product information (required)
    - UseCase: Product use case information

Optional Component Models:
    - DataContract: Data contract specifications
    - SLA: Service Level Agreement definitions
    - DataQuality: Data quality metrics and profiles
    - PricingPlans: Pricing information and plans
    - License: License terms and conditions
    - DataAccess: Data access methods and endpoints
    - DataHolder: Data provider/holder information
    - PaymentGateways: Payment processing configuration

Supporting Models:
    - DataAccessMethod: Individual data access method
    - PricingPlan: Individual pricing plan
    - PaymentGateway: Individual payment gateway
    - SLADimension, SLAProfile: SLA component models
    - DataQualityDimension, DataQualityProfile: Data quality component models
    - SpecificationExtensions: Custom extension fields (x- prefixed)

All models support:
    - Full ODPS v4.0 specification compliance
    - Optional and required field validation
    - International standards compliance (ISO, RFC, ITU-T)
    - Automatic snake_case to camelCase conversion for JSON output
    - Type safety with comprehensive type hints

Example:
    Creating a complete ODPS document with multiple components:

    >>> from odps.models import *
    >>>
    >>> # Core product details
    >>> details = ProductDetails(
    ...     name="Sales Analytics Dataset",
    ...     product_id="sales-analytics-v2",
    ...     visibility="organization",
    ...     status="production",
    ...     type="dataset",
    ...     description="Monthly sales data with customer segments",
    ...     categories=["analytics", "sales"],
    ...     tags=["monthly", "b2b", "revenue"]
    ... )
    >>>
    >>> # Data holder information
    >>> holder = DataHolder(
    ...     name="Acme Corp Data Team",
    ...     email="data-team@acme.com",
    ...     url="https://acme.com/data"
    ... )
    >>>
    >>> # License terms
    >>> license = License(
    ...     scope_of_use="internal",
    ...     geographical_area=["US"],
    ...     permanent=True,
    ...     exclusive=False
    ... )

Note:
    All models are implemented as dataclasses for optimal performance and
    automatic generation of __init__, __repr__, and other methods.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any


@dataclass
class UseCase:
    """Use case information - part of ProductDetails optional attributes"""

    title: str
    description: str
    url: Optional[str] = None


@dataclass
class ProductDetails:
    """Product information and metadata"""

    name: str
    product_id: str
    visibility: str  # private, invitation, organisation, dataspace, public
    status: str  # draft, development, production, deprecated
    type: str  # dataset, algorithm, ml-model, etc.

    # Core optional attributes
    value_proposition: Optional[str] = None
    description: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    brand: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)
    geography: Optional[str] = None
    language: List[str] = field(default_factory=list)
    homepage: Optional[str] = None
    logo_url: Optional[str] = None
    created: Optional[str] = None  # ISO 8601 date
    updated: Optional[str] = None  # ISO 8601 date
    product_series: Optional[str] = None
    standards: List[str] = field(default_factory=list)
    product_version: Optional[str] = None
    version_notes: Optional[str] = None
    issues: Optional[str] = None  # URL to issue tracker
    content_sample: Optional[str] = None  # URL to sample content
    brand_slogan: Optional[str] = None
    use_cases: List[UseCase] = field(default_factory=list)
    recommended_data_products: List[str] = field(default_factory=list)  # URLs
    output_file_formats: List[str] = field(default_factory=list)


@dataclass
class DataContract:
    """Data contract specifications"""

    # Optional attributes
    id: Optional[str] = None  # Unique identifier
    type: Optional[str] = None  # ODCS or DCS
    contract_version: Optional[str] = None
    contract_url: Optional[str] = None  # URL to contract
    spec: Optional[Dict[str, Any]] = None  # Inline YAML specification
    ref: Optional[str] = None  # URI reference


@dataclass
class SLADimension:
    """SLA dimension with objectives and units"""

    name: str
    objective: Union[str, int, float]
    unit: Optional[str] = None


@dataclass
class SLAProfile:
    """Named SLA profile (e.g., default, premium)"""

    dimensions: List[SLADimension] = field(default_factory=list)
    monitoring_specification: Optional[Dict[str, Any]] = None  # Executable monitoring
    support_contact: Optional[str] = None  # Contact details
    support_phone: Optional[str] = None
    support_email: Optional[str] = None
    service_hours: Optional[str] = None  # Phone/email service hours
    documentation_url: Optional[str] = None


@dataclass
class SLA:
    """Service Level Agreement with multiple named profiles"""

    profiles: Dict[str, SLAProfile] = field(default_factory=dict)


@dataclass
class DataQualityDimension:
    """Data quality dimension with objectives and units"""

    name: str
    objective: Union[str, int, float]
    unit: Optional[str] = None
    display_title: Optional[str] = None
    description: Optional[str] = None


@dataclass
class DataQualityProfile:
    """Named data quality profile"""

    dimensions: List[DataQualityDimension] = field(default_factory=list)
    quality_checks: Optional[Dict[str, Any]] = None  # Executable quality checks


@dataclass
class DataQuality:
    """Data quality specifications with named profiles"""

    profiles: Dict[str, DataQualityProfile] = field(default_factory=dict)


@dataclass
class PricingPlan:
    """Individual pricing plan with language support"""

    name: Union[str, Dict[str, str]]  # String or multilingual dict
    price_currency: str
    price: Optional[float] = None
    billing_duration: Optional[str] = None
    unit: Optional[str] = None
    max_transactions_per_second: Optional[int] = None
    max_transactions_per_month: Optional[int] = None

    # Additional optional attributes from ODPS v4.0
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    value_added_tax: Optional[float] = None  # VAT percentage
    valid_from: Optional[str] = None  # ISO 8601 date
    valid_to: Optional[str] = None  # ISO 8601 date
    additional_pricing_details: Optional[Dict[str, Any]] = None
    quality_profile_reference: Optional[str] = None  # Reference to quality profile
    sla_profile_reference: Optional[str] = None  # Reference to SLA profile
    access_profile_reference: Optional[str] = None  # Reference to access profile


@dataclass
class PricingPlans:
    """Pricing information with multiple language-specific plans"""

    plans: List[PricingPlan] = field(default_factory=list)
    language_specific_plans: Dict[str, List[PricingPlan]] = field(
        default_factory=dict
    )  # ISO 639-1 keys


@dataclass
class License:
    """Licensing information with comprehensive optional attributes"""

    scope_of_use: str
    geographical_area: List[str] = field(default_factory=list)
    permanent: bool = True
    exclusive: bool = False
    right_to_sublicense: bool = False
    right_to_modify: bool = False
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    license_grant: Optional[str] = None
    license_name: Optional[str] = None
    license_url: Optional[str] = None

    # Additional optional attributes from ODPS v4.0
    scope_details: Optional[str] = None  # Detailed scope description
    termination_conditions: Optional[str] = None
    governance_specifics: Optional[str] = None
    audit_terms: Optional[str] = None
    warranties: Optional[str] = None
    damages: Optional[str] = None  # Liability and damages clauses
    confidentiality_clauses: Optional[str] = None


@dataclass
class DataAccessMethod:
    """Individual data access method (e.g., default, API, agent)"""

    name: Optional[Dict[str, str]] = None  # Multilingual name
    description: Optional[Dict[str, str]] = None  # Multilingual description
    output_port_type: Optional[str] = None  # file, API, etc.
    format: Optional[str] = None  # JSON, CSV, etc.
    access_url: Optional[str] = None
    authentication_method: Optional[str] = None
    specs_url: Optional[str] = None
    documentation_url: Optional[str] = None
    specification: Optional[Dict[str, Any]] = None
    version: Optional[str] = None  # Version of the access method
    reference: Optional[str] = None  # Reference details


@dataclass
class DataAccess:
    """Data access specifications with required default method"""

    default: DataAccessMethod
    additional_methods: Dict[str, DataAccessMethod] = field(default_factory=dict)


@dataclass
class DataHolder:
    """Data holder information with comprehensive optional attributes"""

    name: str
    email: str
    url: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

    # Additional optional attributes from ODPS v4.0
    business_identifiers: List[str] = field(
        default_factory=list
    )  # Business registration numbers
    contact_person: Optional[str] = None  # Primary contact person
    contact_phone: Optional[str] = None  # Alternative contact phone
    contact_email: Optional[str] = None  # Alternative contact email
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country: Optional[str] = None  # ISO 3166-1 alpha-2 country code
    ratings: Optional[Dict[str, Any]] = None  # Various ratings and scores
    organizational_description: Optional[str] = None


@dataclass
class PaymentGateway:
    """Payment gateway information with comprehensive optional attributes"""

    name: Union[str, Dict[str, str]]  # String or multilingual dict
    url: str
    specification: Optional[Dict[str, Any]] = None

    # Additional optional attributes from ODPS v4.0
    description: Optional[Dict[str, str]] = None  # Multilingual descriptions
    version: Optional[str] = None  # Gateway version
    reference: Optional[str] = None  # Reference details
    executable_specifications: Optional[Dict[str, Any]] = None


@dataclass
class PaymentGateways:
    """Payment gateways collection with multiple gateway configurations"""

    gateways: List[PaymentGateway] = field(default_factory=list)
    named_gateways: Dict[str, PaymentGateway] = field(
        default_factory=dict
    )  # Named gateway configs


@dataclass
class SpecificationExtensions:
    """Container for custom specification extensions (x- prefixed fields)"""

    extensions: Dict[str, Any] = field(default_factory=dict)

    def add_extension(self, key: str, value: Any) -> None:
        """Add a custom extension field"""
        if not key.startswith("x-"):
            key = f"x-{key}"
        self.extensions[key] = value

    def get_extension(self, key: str) -> Any:
        """Get a custom extension field"""
        if not key.startswith("x-"):
            key = f"x-{key}"
        return self.extensions.get(key)

    def remove_extension(self, key: str) -> None:
        """Remove a custom extension field"""
        if not key.startswith("x-"):
            key = f"x-{key}"
        self.extensions.pop(key, None)
