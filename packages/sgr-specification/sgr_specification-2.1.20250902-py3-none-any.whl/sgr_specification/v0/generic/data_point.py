from dataclasses import dataclass, field
from typing import Optional
from sgr_specification.v0.generic.base_types import (
    AlternativeNames,
    DataDirectionProduct,
    DataTypeProduct,
    DynamicParameterDescriptionList,
    GenericAttributeListProduct,
    LegibleDescription,
    Units,
)

__NAMESPACE__ = "http://www.smartgridready.com/ns/V0/"


@dataclass
class DataPointDescription:
    """
    Generic data point properties.

    :ivar data_point_name: Name of the data point (unique on functional
        profile)
    :ivar data_direction:
    :ivar data_type:
    :ivar value:
    :ivar unit:
    :ivar array_length: Optional, if present the data point is an array
        of specified length
    :ivar minimum_value:
    :ivar maximum_value:
    :ivar unit_conversion_multiplicator:
    :ivar parameter_list: The dynamic parameter descriptions list
        describes the additional parameters that must be provided to
        execute a read/write operation from/to that DataPoint.
    :ivar alternative_names:
    :ivar legible_description: Published and printable information
        related to this data point
    :ivar programmer_hints: additional device-specific implementation
        hints for this data point
    """
    data_point_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "dataPointName",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    data_direction: Optional[DataDirectionProduct] = field(
        default=None,
        metadata={
            "name": "dataDirection",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    data_type: Optional[DataTypeProduct] = field(
        default=None,
        metadata={
            "name": "dataType",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    value: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    unit: Optional[Units] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    array_length: Optional[int] = field(
        default=None,
        metadata={
            "name": "arrayLength",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    minimum_value: Optional[float] = field(
        default=None,
        metadata={
            "name": "minimumValue",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    maximum_value: Optional[float] = field(
        default=None,
        metadata={
            "name": "maximumValue",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    unit_conversion_multiplicator: Optional[float] = field(
        default=None,
        metadata={
            "name": "unitConversionMultiplicator",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    parameter_list: Optional[DynamicParameterDescriptionList] = field(
        default=None,
        metadata={
            "name": "parameterList",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    alternative_names: Optional[AlternativeNames] = field(
        default=None,
        metadata={
            "name": "alternativeNames",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    legible_description: list[LegibleDescription] = field(
        default_factory=list,
        metadata={
            "name": "legibleDescription",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "max_occurs": 4,
        }
    )
    programmer_hints: list[LegibleDescription] = field(
        default_factory=list,
        metadata={
            "name": "programmerHints",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
@dataclass
class DataPointBase:
    """
    Data point element.
    """
    data_point: Optional[DataPointDescription] = field(
        default=None,
        metadata={
            "name": "dataPoint",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    generic_attribute_list: Optional[GenericAttributeListProduct] = field(
        default=None,
        metadata={
            "name": "genericAttributeList",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )