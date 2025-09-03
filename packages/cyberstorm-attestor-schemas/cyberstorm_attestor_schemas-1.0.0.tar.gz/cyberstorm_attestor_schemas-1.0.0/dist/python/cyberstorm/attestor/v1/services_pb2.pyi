from google.api import annotations_pb2 as _annotations_pb2
from cyberstorm.attestor.v1 import messages_pb2 as _messages_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateAttestationRequest(_message.Message):
    __slots__ = ("schema_type", "data", "recipient", "revocable", "expiration_time")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AttestationValue
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AttestationValue, _Mapping]] = ...) -> None: ...
    SCHEMA_TYPE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    REVOCABLE_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_TIME_FIELD_NUMBER: _ClassVar[int]
    schema_type: str
    data: _containers.MessageMap[str, AttestationValue]
    recipient: str
    revocable: bool
    expiration_time: int
    def __init__(self, schema_type: _Optional[str] = ..., data: _Optional[_Mapping[str, AttestationValue]] = ..., recipient: _Optional[str] = ..., revocable: _Optional[bool] = ..., expiration_time: _Optional[int] = ...) -> None: ...

class StringArray(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, values: _Optional[_Iterable[str]] = ...) -> None: ...

class BytesArray(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, values: _Optional[_Iterable[bytes]] = ...) -> None: ...

class AttestationValue(_message.Message):
    __slots__ = ("string_value", "bytes_value", "address_value", "uint64_value", "bool_value", "string_array", "bytes_array")
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    BYTES_VALUE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_VALUE_FIELD_NUMBER: _ClassVar[int]
    UINT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRING_ARRAY_FIELD_NUMBER: _ClassVar[int]
    BYTES_ARRAY_FIELD_NUMBER: _ClassVar[int]
    string_value: str
    bytes_value: bytes
    address_value: str
    uint64_value: int
    bool_value: bool
    string_array: StringArray
    bytes_array: BytesArray
    def __init__(self, string_value: _Optional[str] = ..., bytes_value: _Optional[bytes] = ..., address_value: _Optional[str] = ..., uint64_value: _Optional[int] = ..., bool_value: _Optional[bool] = ..., string_array: _Optional[_Union[StringArray, _Mapping]] = ..., bytes_array: _Optional[_Union[BytesArray, _Mapping]] = ...) -> None: ...

class CreateAttestationResponse(_message.Message):
    __slots__ = ("attestation_uid", "transaction_hash", "attester")
    ATTESTATION_UID_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_HASH_FIELD_NUMBER: _ClassVar[int]
    ATTESTER_FIELD_NUMBER: _ClassVar[int]
    attestation_uid: str
    transaction_hash: str
    attester: str
    def __init__(self, attestation_uid: _Optional[str] = ..., transaction_hash: _Optional[str] = ..., attester: _Optional[str] = ...) -> None: ...

class GetSchemasResponse(_message.Message):
    __slots__ = ("schemas", "deployments")
    class SchemasEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: SchemaDefinition
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[SchemaDefinition, _Mapping]] = ...) -> None: ...
    SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENTS_FIELD_NUMBER: _ClassVar[int]
    schemas: _containers.MessageMap[str, SchemaDefinition]
    deployments: _containers.RepeatedCompositeFieldContainer[SchemaDeployment]
    def __init__(self, schemas: _Optional[_Mapping[str, SchemaDefinition]] = ..., deployments: _Optional[_Iterable[_Union[SchemaDeployment, _Mapping]]] = ...) -> None: ...

class SchemaDefinition(_message.Message):
    __slots__ = ("name", "definition", "description")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    definition: str
    description: str
    def __init__(self, name: _Optional[str] = ..., definition: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class SchemaDeployment(_message.Message):
    __slots__ = ("contract_name", "contract_address")
    CONTRACT_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    contract_name: str
    contract_address: str
    def __init__(self, contract_name: _Optional[str] = ..., contract_address: _Optional[str] = ...) -> None: ...

class GetSchemaRequest(_message.Message):
    __slots__ = ("schema_type",)
    SCHEMA_TYPE_FIELD_NUMBER: _ClassVar[int]
    schema_type: str
    def __init__(self, schema_type: _Optional[str] = ...) -> None: ...

class GetSchemaResponse(_message.Message):
    __slots__ = ("schema", "deployment")
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    schema: SchemaDefinition
    deployment: SchemaDeployment
    def __init__(self, schema: _Optional[_Union[SchemaDefinition, _Mapping]] = ..., deployment: _Optional[_Union[SchemaDeployment, _Mapping]] = ...) -> None: ...

class ServerSignAttestationRequest(_message.Message):
    __slots__ = ("schema_type", "data", "recipient", "revocable", "expiration_time")
    class DataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: AttestationValue
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[AttestationValue, _Mapping]] = ...) -> None: ...
    SCHEMA_TYPE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    REVOCABLE_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_TIME_FIELD_NUMBER: _ClassVar[int]
    schema_type: str
    data: _containers.MessageMap[str, AttestationValue]
    recipient: str
    revocable: bool
    expiration_time: int
    def __init__(self, schema_type: _Optional[str] = ..., data: _Optional[_Mapping[str, AttestationValue]] = ..., recipient: _Optional[str] = ..., revocable: _Optional[bool] = ..., expiration_time: _Optional[int] = ...) -> None: ...

class ServerSignAttestationResponse(_message.Message):
    __slots__ = ("attestation_uid", "transaction_hash", "attester")
    ATTESTATION_UID_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_HASH_FIELD_NUMBER: _ClassVar[int]
    ATTESTER_FIELD_NUMBER: _ClassVar[int]
    attestation_uid: str
    transaction_hash: str
    attester: str
    def __init__(self, attestation_uid: _Optional[str] = ..., transaction_hash: _Optional[str] = ..., attester: _Optional[str] = ...) -> None: ...

class SignMessageRequest(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class SignMessageResponse(_message.Message):
    __slots__ = ("signature", "signer_address", "message_hash")
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    SIGNER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_HASH_FIELD_NUMBER: _ClassVar[int]
    signature: str
    signer_address: str
    message_hash: str
    def __init__(self, signature: _Optional[str] = ..., signer_address: _Optional[str] = ..., message_hash: _Optional[str] = ...) -> None: ...

class VerifySignatureRequest(_message.Message):
    __slots__ = ("message", "signature", "expected_signer")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_SIGNER_FIELD_NUMBER: _ClassVar[int]
    message: str
    signature: str
    expected_signer: str
    def __init__(self, message: _Optional[str] = ..., signature: _Optional[str] = ..., expected_signer: _Optional[str] = ...) -> None: ...

class VerifySignatureResponse(_message.Message):
    __slots__ = ("valid", "signer_address", "error")
    VALID_FIELD_NUMBER: _ClassVar[int]
    SIGNER_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    signer_address: str
    error: str
    def __init__(self, valid: _Optional[bool] = ..., signer_address: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class GenerateWebhookSecretRequest(_message.Message):
    __slots__ = ("repository", "registrant_signature")
    REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    repository: _messages_pb2.Repository
    registrant_signature: bytes
    def __init__(self, repository: _Optional[_Union[_messages_pb2.Repository, _Mapping]] = ..., registrant_signature: _Optional[bytes] = ...) -> None: ...

class GenerateWebhookSecretResponse(_message.Message):
    __slots__ = ("webhook_secret", "repository", "attestor_address")
    WEBHOOK_SECRET_FIELD_NUMBER: _ClassVar[int]
    REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    ATTESTOR_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    webhook_secret: str
    repository: _messages_pb2.Repository
    attestor_address: str
    def __init__(self, webhook_secret: _Optional[str] = ..., repository: _Optional[_Union[_messages_pb2.Repository, _Mapping]] = ..., attestor_address: _Optional[str] = ...) -> None: ...

class VerifyWebhookSignatureRequest(_message.Message):
    __slots__ = ("payload", "signature", "webhook_secret")
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    WEBHOOK_SECRET_FIELD_NUMBER: _ClassVar[int]
    payload: str
    signature: str
    webhook_secret: str
    def __init__(self, payload: _Optional[str] = ..., signature: _Optional[str] = ..., webhook_secret: _Optional[str] = ...) -> None: ...

class VerifyWebhookSignatureResponse(_message.Message):
    __slots__ = ("valid", "error")
    VALID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    error: str
    def __init__(self, valid: _Optional[bool] = ..., error: _Optional[str] = ...) -> None: ...

class GetServerAddressResponse(_message.Message):
    __slots__ = ("address",)
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    address: str
    def __init__(self, address: _Optional[str] = ...) -> None: ...

class RegisterRepositoryResponse(_message.Message):
    __slots__ = ("attestation_uid", "webhook_secret")
    ATTESTATION_UID_FIELD_NUMBER: _ClassVar[int]
    WEBHOOK_SECRET_FIELD_NUMBER: _ClassVar[int]
    attestation_uid: str
    webhook_secret: str
    def __init__(self, attestation_uid: _Optional[str] = ..., webhook_secret: _Optional[str] = ...) -> None: ...

class WebhookSecretResponse(_message.Message):
    __slots__ = ("webhook_secret", "registered")
    WEBHOOK_SECRET_FIELD_NUMBER: _ClassVar[int]
    REGISTERED_FIELD_NUMBER: _ClassVar[int]
    webhook_secret: str
    registered: bool
    def __init__(self, webhook_secret: _Optional[str] = ..., registered: _Optional[bool] = ...) -> None: ...

class ListRepositoriesResponse(_message.Message):
    __slots__ = ("repositories",)
    REPOSITORIES_FIELD_NUMBER: _ClassVar[int]
    repositories: _containers.RepeatedCompositeFieldContainer[_messages_pb2.Repository]
    def __init__(self, repositories: _Optional[_Iterable[_Union[_messages_pb2.Repository, _Mapping]]] = ...) -> None: ...

class RegisterIdentityResponse(_message.Message):
    __slots__ = ("attestation_uid", "attestation_signature", "attestor")
    ATTESTATION_UID_FIELD_NUMBER: _ClassVar[int]
    ATTESTATION_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    ATTESTOR_FIELD_NUMBER: _ClassVar[int]
    attestation_uid: str
    attestation_signature: str
    attestor: str
    def __init__(self, attestation_uid: _Optional[str] = ..., attestation_signature: _Optional[str] = ..., attestor: _Optional[str] = ...) -> None: ...

class ValidateIdentityRequest(_message.Message):
    __slots__ = ("identifier", "proof_url", "registrant")
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    PROOF_URL_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_FIELD_NUMBER: _ClassVar[int]
    identifier: str
    proof_url: str
    registrant: str
    def __init__(self, identifier: _Optional[str] = ..., proof_url: _Optional[str] = ..., registrant: _Optional[str] = ...) -> None: ...

class ValidateIdentityResponse(_message.Message):
    __slots__ = ("valid", "attestation_signature", "attestor", "error")
    VALID_FIELD_NUMBER: _ClassVar[int]
    ATTESTATION_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    ATTESTOR_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    attestation_signature: str
    attestor: str
    error: str
    def __init__(self, valid: _Optional[bool] = ..., attestation_signature: _Optional[str] = ..., attestor: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class ListIdentitiesResponse(_message.Message):
    __slots__ = ("identities", "total_count")
    IDENTITIES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    identities: _containers.RepeatedCompositeFieldContainer[_messages_pb2.Identity]
    total_count: int
    def __init__(self, identities: _Optional[_Iterable[_Union[_messages_pb2.Identity, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class ProcessWebhookResponse(_message.Message):
    __slots__ = ("processed", "attestation_uid", "error")
    PROCESSED_FIELD_NUMBER: _ClassVar[int]
    ATTESTATION_UID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    processed: bool
    attestation_uid: str
    error: str
    def __init__(self, processed: _Optional[bool] = ..., attestation_uid: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...

class GetContributionsRequest(_message.Message):
    __slots__ = ("repository", "identity", "event_types", "limit", "offset")
    REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPES_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    repository: _messages_pb2.Repository
    identity: _messages_pb2.Identity
    event_types: _containers.RepeatedScalarFieldContainer[_messages_pb2.ContributionEventType]
    limit: int
    offset: int
    def __init__(self, repository: _Optional[_Union[_messages_pb2.Repository, _Mapping]] = ..., identity: _Optional[_Union[_messages_pb2.Identity, _Mapping]] = ..., event_types: _Optional[_Iterable[_Union[_messages_pb2.ContributionEventType, str]]] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetContributionsResponse(_message.Message):
    __slots__ = ("contributions", "total_count")
    CONTRIBUTIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    contributions: _containers.RepeatedCompositeFieldContainer[_messages_pb2.Contribution]
    total_count: int
    def __init__(self, contributions: _Optional[_Iterable[_Union[_messages_pb2.Contribution, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class GetContributionsByUidRequest(_message.Message):
    __slots__ = ("attestation_uid", "limit", "offset")
    ATTESTATION_UID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    attestation_uid: bytes
    limit: int
    offset: int
    def __init__(self, attestation_uid: _Optional[bytes] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetLinkedIssuesRequest(_message.Message):
    __slots__ = ("pr_attestation_uid",)
    PR_ATTESTATION_UID_FIELD_NUMBER: _ClassVar[int]
    pr_attestation_uid: bytes
    def __init__(self, pr_attestation_uid: _Optional[bytes] = ...) -> None: ...

class GetLinkedIssuesResponse(_message.Message):
    __slots__ = ("issues",)
    ISSUES_FIELD_NUMBER: _ClassVar[int]
    issues: _containers.RepeatedCompositeFieldContainer[_messages_pb2.Contribution]
    def __init__(self, issues: _Optional[_Iterable[_Union[_messages_pb2.Contribution, _Mapping]]] = ...) -> None: ...

class GetPullRequestReviewsRequest(_message.Message):
    __slots__ = ("pr_attestation_uid",)
    PR_ATTESTATION_UID_FIELD_NUMBER: _ClassVar[int]
    pr_attestation_uid: bytes
    def __init__(self, pr_attestation_uid: _Optional[bytes] = ...) -> None: ...

class GetPullRequestReviewsResponse(_message.Message):
    __slots__ = ("reviews",)
    REVIEWS_FIELD_NUMBER: _ClassVar[int]
    reviews: _containers.RepeatedCompositeFieldContainer[_messages_pb2.Contribution]
    def __init__(self, reviews: _Optional[_Iterable[_Union[_messages_pb2.Contribution, _Mapping]]] = ...) -> None: ...

class GenerateRepositoryBranchNameRequest(_message.Message):
    __slots__ = ("repository_path", "registrant_signature")
    REPOSITORY_PATH_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    repository_path: str
    registrant_signature: bytes
    def __init__(self, repository_path: _Optional[str] = ..., registrant_signature: _Optional[bytes] = ...) -> None: ...

class GenerateRepositoryBranchNameResponse(_message.Message):
    __slots__ = ("branch_name", "repository_path", "expected_message", "generated_at")
    BRANCH_NAME_FIELD_NUMBER: _ClassVar[int]
    REPOSITORY_PATH_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    GENERATED_AT_FIELD_NUMBER: _ClassVar[int]
    branch_name: str
    repository_path: str
    expected_message: str
    generated_at: int
    def __init__(self, branch_name: _Optional[str] = ..., repository_path: _Optional[str] = ..., expected_message: _Optional[str] = ..., generated_at: _Optional[int] = ...) -> None: ...

class ValidateRepositoryBranchRequest(_message.Message):
    __slots__ = ("repository_path", "registrant_address", "registrant_signature")
    REPOSITORY_PATH_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    repository_path: str
    registrant_address: str
    registrant_signature: bytes
    def __init__(self, repository_path: _Optional[str] = ..., registrant_address: _Optional[str] = ..., registrant_signature: _Optional[bytes] = ...) -> None: ...

class ValidateRepositoryBranchResponse(_message.Message):
    __slots__ = ("valid", "branch_name", "branch_sha", "verified_at", "error")
    VALID_FIELD_NUMBER: _ClassVar[int]
    BRANCH_NAME_FIELD_NUMBER: _ClassVar[int]
    BRANCH_SHA_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_AT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    branch_name: str
    branch_sha: str
    verified_at: int
    error: str
    def __init__(self, valid: _Optional[bool] = ..., branch_name: _Optional[str] = ..., branch_sha: _Optional[str] = ..., verified_at: _Optional[int] = ..., error: _Optional[str] = ...) -> None: ...

class GetSchemasRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetServerAddressRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListRepositoriesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListIdentitiesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RegisterRepositoryRequest(_message.Message):
    __slots__ = ("repository",)
    REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    repository: _messages_pb2.Repository
    def __init__(self, repository: _Optional[_Union[_messages_pb2.Repository, _Mapping]] = ...) -> None: ...

class GetWebhookSecretRequest(_message.Message):
    __slots__ = ("repository",)
    REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    repository: _messages_pb2.Repository
    def __init__(self, repository: _Optional[_Union[_messages_pb2.Repository, _Mapping]] = ...) -> None: ...

class GetWebhookSecretResponse(_message.Message):
    __slots__ = ("response",)
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: WebhookSecretResponse
    def __init__(self, response: _Optional[_Union[WebhookSecretResponse, _Mapping]] = ...) -> None: ...

class RegisterIdentityRequest(_message.Message):
    __slots__ = ("identity",)
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    identity: _messages_pb2.Identity
    def __init__(self, identity: _Optional[_Union[_messages_pb2.Identity, _Mapping]] = ...) -> None: ...

class LookupIdentityRequest(_message.Message):
    __slots__ = ("domain", "identifier")
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    domain: str
    identifier: str
    def __init__(self, domain: _Optional[str] = ..., identifier: _Optional[str] = ...) -> None: ...

class ProcessWebhookRequest(_message.Message):
    __slots__ = ("event",)
    EVENT_FIELD_NUMBER: _ClassVar[int]
    event: _messages_pb2.WebhookEvent
    def __init__(self, event: _Optional[_Union[_messages_pb2.WebhookEvent, _Mapping]] = ...) -> None: ...

class GetContributionsByIdentityRequest(_message.Message):
    __slots__ = ("identity", "event_types", "limit", "offset")
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPES_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    identity: _messages_pb2.Identity
    event_types: _containers.RepeatedScalarFieldContainer[_messages_pb2.ContributionEventType]
    limit: int
    offset: int
    def __init__(self, identity: _Optional[_Union[_messages_pb2.Identity, _Mapping]] = ..., event_types: _Optional[_Iterable[_Union[_messages_pb2.ContributionEventType, str]]] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetContributionsByRepositoryRequest(_message.Message):
    __slots__ = ("repository", "event_types", "limit", "offset")
    REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPES_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    repository: _messages_pb2.Repository
    event_types: _containers.RepeatedScalarFieldContainer[_messages_pb2.ContributionEventType]
    limit: int
    offset: int
    def __init__(self, repository: _Optional[_Union[_messages_pb2.Repository, _Mapping]] = ..., event_types: _Optional[_Iterable[_Union[_messages_pb2.ContributionEventType, str]]] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetContributionsByIdentityResponse(_message.Message):
    __slots__ = ("contributions", "total_count")
    CONTRIBUTIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    contributions: _containers.RepeatedCompositeFieldContainer[_messages_pb2.Contribution]
    total_count: int
    def __init__(self, contributions: _Optional[_Iterable[_Union[_messages_pb2.Contribution, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class GetContributionsByRepositoryResponse(_message.Message):
    __slots__ = ("contributions", "total_count")
    CONTRIBUTIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    contributions: _containers.RepeatedCompositeFieldContainer[_messages_pb2.Contribution]
    total_count: int
    def __init__(self, contributions: _Optional[_Iterable[_Union[_messages_pb2.Contribution, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class GetContributionsByUidResponse(_message.Message):
    __slots__ = ("contributions", "total_count")
    CONTRIBUTIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    contributions: _containers.RepeatedCompositeFieldContainer[_messages_pb2.Contribution]
    total_count: int
    def __init__(self, contributions: _Optional[_Iterable[_Union[_messages_pb2.Contribution, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class LookupIdentityResponse(_message.Message):
    __slots__ = ("identity", "found")
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    FOUND_FIELD_NUMBER: _ClassVar[int]
    identity: _messages_pb2.Identity
    found: bool
    def __init__(self, identity: _Optional[_Union[_messages_pb2.Identity, _Mapping]] = ..., found: _Optional[bool] = ...) -> None: ...
