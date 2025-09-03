from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from sgr_specification.v0.generic.base_types import (
    EmptyType,
    MessageFilter,
    ResponseQuery,
)
from sgr_specification.v0.product.rest_api_types import ValueMapping

__NAMESPACE__ = "http://www.smartgridready.com/ns/V0/"


@dataclass
class MessageBrokerAuthenticationBasic:
    username: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    password: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
@dataclass
class MessageBrokerAuthenticationClientCertificate:
    keystore_path: Optional[str] = field(
        default=None,
        metadata={
            "name": "keystorePath",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    keystore_password: Optional[str] = field(
        default=None,
        metadata={
            "name": "keystorePassword",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    truststore_path: Optional[str] = field(
        default=None,
        metadata={
            "name": "truststorePath",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    truststore_password: Optional[str] = field(
        default=None,
        metadata={
            "name": "truststorePassword",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
@dataclass
class MessageBrokerListElement:
    host: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    port: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    tls: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "pattern": r'\{\{.+\}\}|true|false',
        }
    )
    tls_verify_certificate: Optional[str] = field(
        default=None,
        metadata={
            "name": "tlsVerifyCertificate",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "pattern": r'\{\{.+\}\}|true|false',
        }
    )
class MessagingPlatformType(Enum):
    """
    Type of the messaging platform.
    """
    MQTT5 = 'MQTT5'
    KAFKA = 'Kafka'
@dataclass
class MessageBrokerAuthentication:
    basic_authentication: Optional[MessageBrokerAuthenticationBasic] = field(
        default=None,
        metadata={
            "name": "basicAuthentication",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    client_certificate_authentication: Optional[MessageBrokerAuthenticationClientCertificate] = field(
        default=None,
        metadata={
            "name": "clientCertificateAuthentication",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
@dataclass
class MessageBrokerList:
    message_broker_list_element: list[MessageBrokerListElement] = field(
        default_factory=list,
        metadata={
            "name": "messageBrokerListElement",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "min_occurs": 1,
        }
    )
@dataclass
class MessagingDataType:
    """Messaging API specific data types.

    <xs:ul xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:li>number: message payload is a plain number</xs:li>
    <xs:li>string: message payload us a plain string</xs:li>
    <xs:li>JSON_array: message payload is a JSON array</xs:li>
    <xs:li>JSON_object: message payload is a JSON object</xs:li>
    </xs:ul>
    """
    number: Optional[EmptyType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    string: Optional[EmptyType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    json_array: Optional[EmptyType] = field(
        default=None,
        metadata={
            "name": "JSON_array",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    json_object: Optional[EmptyType] = field(
        default=None,
        metadata={
            "name": "JSON_object",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
@dataclass
class MessagingValueMapping:
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
class InMessage:
    topic: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    filter: Optional[MessageFilter] = field(
        default=None,
        metadata={
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
    value_mapping: Optional[MessagingValueMapping] = field(
        default=None,
        metadata={
            "name": "valueMapping",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
@dataclass
class MessagingInterfaceDescription:
    """
    Messaging interface properties.
    """
    platform: Optional[MessagingPlatformType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    message_broker_list: Optional[MessageBrokerList] = field(
        default=None,
        metadata={
            "name": "messageBrokerList",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    client_id: Optional[str] = field(
        default=None,
        metadata={
            "name": "clientId",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    message_broker_authentication: Optional[MessageBrokerAuthentication] = field(
        default=None,
        metadata={
            "name": "messageBrokerAuthentication",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
@dataclass
class OutMessage:
    topic: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    template: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    value_mapping: Optional[MessagingValueMapping] = field(
        default=None,
        metadata={
            "name": "valueMapping",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
@dataclass
class MessagingDataPointConfiguration:
    messaging_data_type: Optional[MessagingDataType] = field(
        default=None,
        metadata={
            "name": "messagingDataType",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
            "required": True,
        }
    )
    read_cmd_message: Optional[OutMessage] = field(
        default=None,
        metadata={
            "name": "readCmdMessage",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    write_cmd_message: Optional[OutMessage] = field(
        default=None,
        metadata={
            "name": "writeCmdMessage",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )
    in_message: Optional[InMessage] = field(
        default=None,
        metadata={
            "name": "inMessage",
            "type": "Element",
            "namespace": "http://www.smartgridready.com/ns/V0/",
        }
    )