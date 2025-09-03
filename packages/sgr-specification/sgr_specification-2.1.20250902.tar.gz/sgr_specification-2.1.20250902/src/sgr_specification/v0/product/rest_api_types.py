from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from sgr_specification.v0.generic.base_types import ResponseQuery

__NAMESPACE__ = "http://www.smartgridready.com/ns/V0/"


@dataclass
class HeaderEntry:
    header_name: Optional[str] = field(
        default=None,
        metadata={
            "name": "headerName",
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
            "required": True,
        }
    )
class HttpMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'
@dataclass
class ParameterEntry:
    name: Optional[str] = field(
        default=None,
        metadata={
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
            "required": True,
        }
    )
class RestApiAuthenticationMethod(Enum):
    NO_SECURITY_SCHEME = 'NoSecurityScheme'
    BEARER_SECURITY_SCHEME = 'BearerSecurityScheme'
    API_KEY_SECURITY_SCHEME = 'ApiKeySecurityScheme'
    BASIC_SECURITY_SCHEME = 'BasicSecurityScheme'
    DIGEST_SECURITY_SCHEME = 'DigestSecurityScheme'
    PSK_SECURITY_SCHEME = 'PskSecurityScheme'
    OAUTH2_SECURITY_SCHEME = 'OAuth2SecurityScheme'
    HAWK_SECURITY_SCHEME = 'HawkSecurityScheme'
    AWS_SIGNATURE_SECURITY_SCHEME = 'AwsSignatureSecurityScheme'
@dataclass
class RestApiBasic:
    rest_basic_username: Optional[str] = field(
        default=None,
        metadata={
            "name": "restBasicUsername",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    rest_basic_password: Optional[str] = field(
        default=None,
        metadata={
            "name": "restBasicPassword",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
class RestApiDataType(Enum):
    """
    Rest api specific data types.
    """
    NULL = 'null'
    JSON_NUMBER = 'JSON_number'
    JSON_STRING = 'JSON_string'
    JSON_BOOLEAN = 'JSON_boolean'
    JSON_OBJECT = 'JSON_object'
    JSON_ARRAY = 'JSON_array'
class RestApiInterfaceSelection(Enum):
    """
    Type of Rest Api interface.
    """
    TCPV4 = 'TCPV4'
    TCPV6 = 'TCPV6'
    URI = 'URI'
@dataclass
class ValueMapping:
    """
    Maps one value to another value.
    """
    generic_value: Optional[str] = field(
        default=None,
        metadata={
            "name": "genericValue",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    device_value: Optional[str] = field(
        default=None,
        metadata={
            "name": "deviceValue",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
@dataclass
class HeaderList:
    header: list[HeaderEntry] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
@dataclass
class ParameterList:
    parameter: list[ParameterEntry] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "min_occurs": 1,
        }
    )
@dataclass
class RestApiValueMapping:
    """
    Maps from generic interface to device specific values.
    """
    mapping: list[ValueMapping] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "min_occurs": 1,
        }
    )
@dataclass
class RestApiServiceCall:
    request_header: Optional[HeaderList] = field(
        default=None,
        metadata={
            "name": "requestHeader",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    request_method: Optional[HttpMethod] = field(
        default=None,
        metadata={
            "name": "requestMethod",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    request_path: Optional[str] = field(
        default=None,
        metadata={
            "name": "requestPath",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    request_query: Optional[ParameterList] = field(
        default=None,
        metadata={
            "name": "requestQuery",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    request_form: Optional[ParameterList] = field(
        default=None,
        metadata={
            "name": "requestForm",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    request_body: Optional[str] = field(
        default=None,
        metadata={
            "name": "requestBody",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    response_query: Optional[ResponseQuery] = field(
        default=None,
        metadata={
            "name": "responseQuery",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    value_mapping: Optional[RestApiValueMapping] = field(
        default=None,
        metadata={
            "name": "valueMapping",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
@dataclass
class RestApiBearer:
    rest_api_service_call: Optional[RestApiServiceCall] = field(
        default=None,
        metadata={
            "name": "restApiServiceCall",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
@dataclass
class RestApiDataPointConfiguration:
    """
    Detailed configuration for Rest api data point.
    """
    data_type: Optional[RestApiDataType] = field(
        default=None,
        metadata={
            "name": "dataType",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    rest_api_service_call: Optional[RestApiServiceCall] = field(
        default=None,
        metadata={
            "name": "restApiServiceCall",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    rest_api_write_service_call: list[RestApiServiceCall] = field(
        default_factory=list,
        metadata={
            "name": "restApiWriteServiceCall",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "min_occurs": 1,
            "max_occurs": 2,
            "sequence": 1,
        }
    )
    rest_api_read_service_call: list[RestApiServiceCall] = field(
        default_factory=list,
        metadata={
            "name": "restApiReadServiceCall",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "min_occurs": 1,
            "max_occurs": 2,
            "sequence": 1,
        }
    )
@dataclass
class RestApiInterfaceDescription:
    """
    Rest Api interface properties.
    """
    rest_api_interface_selection: Optional[RestApiInterfaceSelection] = field(
        default=None,
        metadata={
            "name": "restApiInterfaceSelection",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    rest_api_uri: Optional[str] = field(
        default=None,
        metadata={
            "name": "restApiUri",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    rest_api_authentication_method: Optional[RestApiAuthenticationMethod] = field(
        default=None,
        metadata={
            "name": "restApiAuthenticationMethod",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    rest_api_bearer: Optional[RestApiBearer] = field(
        default=None,
        metadata={
            "name": "restApiBearer",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    rest_api_basic: Optional[RestApiBasic] = field(
        default=None,
        metadata={
            "name": "restApiBasic",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    rest_api_verify_certificate: Optional[str] = field(
        default=None,
        metadata={
            "name": "restApiVerifyCertificate",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "pattern": r'\{\{.+\}\}|true|false',
        }
    )