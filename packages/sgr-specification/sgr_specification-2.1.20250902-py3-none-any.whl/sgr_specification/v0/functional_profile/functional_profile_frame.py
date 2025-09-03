from dataclasses import dataclass, field
from typing import Optional
from sgr_specification.v0.generic.base_types import (
    AlternativeNames,
    DataDirectionFunctionalProfile,
    DataTypeFunctionalProfile,
    DynamicParameterDescriptionList,
    FunctionalProfileIdentification,
    GenericAttributeListFunctionalProfile,
    LegibleDescription,
    PresenceLevel,
    ReleaseNotes,
    Units,
)

__NAMESPACE__ = "http://www.smartgridready.com/ns/V0/"


@dataclass
class FunctionalProfileDataPoint:
    """
    Data point element.
    """
    data_point: Optional["FunctionalProfileDataPoint.DataPoint"] = field(
        default=None,
        metadata={
            "name": "dataPoint",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    generic_attribute_list: Optional[GenericAttributeListFunctionalProfile] = field(
        default=None,
        metadata={
            "name": "genericAttributeList",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )

    @dataclass
    class DataPoint:
        """
        Generic data point description.

        :ivar data_point_name: Bezeichnung des Datenpunktes:
            «Schlagwort», welches die Bedeutung identifiziert. Diese
            Bezeichnung gilt neben der Indexnummer als Definition für
            den SmartGridready Namespace für die maschinenlesbaren
            Daten.
        :ivar data_direction:
        :ivar presence_level:
        :ivar data_type:
        :ivar unit:
        :ivar array_length:
        :ivar parameter_list: The dynamic parameter descriptions list
            describes the additional parameters that must be provided to
            execute a read/write operation from/to that DataPoint.
        :ivar alternative_names:
        :ivar legible_description: Published and printable information
            related to this data point
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
        data_direction: Optional[DataDirectionFunctionalProfile] = field(
            default=None,
            metadata={
                "name": "dataDirection",
                "type": "Element",
                "namespace": "http://www.smartgridready.com/ns/V0/",
                "required": True,
            }
        )
        presence_level: Optional[PresenceLevel] = field(
            default=None,
            metadata={
                "name": "presenceLevel",
                "type": "Element",
                "namespace": "http://www.smartgridready.com/ns/V0/",
                "required": True,
            }
        )
        data_type: Optional[DataTypeFunctionalProfile] = field(
            default=None,
            metadata={
                "name": "dataType",
                "type": "Element",
                "namespace": "http://www.smartgridready.com/ns/V0/",
                "required": True,
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
@dataclass
class FunctionalProfileDataPointList:
    """
    List of data points.
    """
    data_point_list_element: list[FunctionalProfileDataPoint] = field(
        default_factory=list,
        metadata={
            "name": "dataPointListElement",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "min_occurs": 1,
        }
    )
@dataclass
class FunctionalProfileFrame:
    """
    Functional profile template.
    """
    class Meta:
        namespace = "http://www.smartgridready.com/ns/V0/"

    release_notes: Optional[ReleaseNotes] = field(
        default=None,
        metadata={
            "name": "releaseNotes",
            "type": "Element",
        }
    )
    functional_profile: Optional["FunctionalProfileFrame.FunctionalProfile"] = field(
        default=None,
        metadata={
            "name": "functionalProfile",
            "type": "Element",
            "required": True,
        }
    )
    generic_attribute_list: Optional[GenericAttributeListFunctionalProfile] = field(
        default=None,
        metadata={
            "name": "genericAttributeList",
            "type": "Element",
        }
    )
    data_point_list: Optional[FunctionalProfileDataPointList] = field(
        default=None,
        metadata={
            "name": "dataPointList",
            "type": "Element",
        }
    )

    @dataclass
    class FunctionalProfile:
        """
        Functional profile element.

        :ivar functional_profile_identification:
        :ivar alternative_names:
        :ivar legible_description: Published and printable information
            related to this functional profile
        """
        functional_profile_identification: Optional[FunctionalProfileIdentification] = field(
            default=None,
            metadata={
                "name": "functionalProfileIdentification",
                "type": "Element",
                "required": True,
            }
        )
        alternative_names: Optional[AlternativeNames] = field(
            default=None,
            metadata={
                "name": "alternativeNames",
                "type": "Element",
            }
        )
        legible_description: list[LegibleDescription] = field(
            default_factory=list,
            metadata={
                "name": "legibleDescription",
                "type": "Element",
                "max_occurs": 4,
            }
        )