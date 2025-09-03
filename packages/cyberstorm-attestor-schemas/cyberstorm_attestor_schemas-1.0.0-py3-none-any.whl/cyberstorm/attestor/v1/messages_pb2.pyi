from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ContributionEventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONTRIBUTION_EVENT_TYPE_UNSPECIFIED: _ClassVar[ContributionEventType]
    CONTRIBUTION_EVENT_TYPE_ISSUE_OPENED: _ClassVar[ContributionEventType]
    CONTRIBUTION_EVENT_TYPE_ISSUE_CLOSED: _ClassVar[ContributionEventType]
    CONTRIBUTION_EVENT_TYPE_PULL_REQUEST_OPENED: _ClassVar[ContributionEventType]
    CONTRIBUTION_EVENT_TYPE_PULL_REQUEST_CLOSED: _ClassVar[ContributionEventType]
    CONTRIBUTION_EVENT_TYPE_PULL_REQUEST_MERGED: _ClassVar[ContributionEventType]
    CONTRIBUTION_EVENT_TYPE_REVIEW_CHANGES_REQUESTED: _ClassVar[ContributionEventType]
    CONTRIBUTION_EVENT_TYPE_REVIEW_APPROVED: _ClassVar[ContributionEventType]
    CONTRIBUTION_EVENT_TYPE_RELEASE_RELEASED: _ClassVar[ContributionEventType]
    CONTRIBUTION_EVENT_TYPE_RELEASE_PUBLISHED: _ClassVar[ContributionEventType]
CONTRIBUTION_EVENT_TYPE_UNSPECIFIED: ContributionEventType
CONTRIBUTION_EVENT_TYPE_ISSUE_OPENED: ContributionEventType
CONTRIBUTION_EVENT_TYPE_ISSUE_CLOSED: ContributionEventType
CONTRIBUTION_EVENT_TYPE_PULL_REQUEST_OPENED: ContributionEventType
CONTRIBUTION_EVENT_TYPE_PULL_REQUEST_CLOSED: ContributionEventType
CONTRIBUTION_EVENT_TYPE_PULL_REQUEST_MERGED: ContributionEventType
CONTRIBUTION_EVENT_TYPE_REVIEW_CHANGES_REQUESTED: ContributionEventType
CONTRIBUTION_EVENT_TYPE_REVIEW_APPROVED: ContributionEventType
CONTRIBUTION_EVENT_TYPE_RELEASE_RELEASED: ContributionEventType
CONTRIBUTION_EVENT_TYPE_RELEASE_PUBLISHED: ContributionEventType

class Identity(_message.Message):
    __slots__ = ("domain", "identifier", "registrant", "proof_url", "attestor", "registrant_signature", "attestor_signature")
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_FIELD_NUMBER: _ClassVar[int]
    PROOF_URL_FIELD_NUMBER: _ClassVar[int]
    ATTESTOR_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    ATTESTOR_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    domain: str
    identifier: str
    registrant: str
    proof_url: str
    attestor: str
    registrant_signature: bytes
    attestor_signature: bytes
    def __init__(self, domain: _Optional[str] = ..., identifier: _Optional[str] = ..., registrant: _Optional[str] = ..., proof_url: _Optional[str] = ..., attestor: _Optional[str] = ..., registrant_signature: _Optional[bytes] = ..., attestor_signature: _Optional[bytes] = ...) -> None: ...

class Repository(_message.Message):
    __slots__ = ("repository", "registrant", "proof_url", "attestor", "registrant_signature", "attestor_signature")
    REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_FIELD_NUMBER: _ClassVar[int]
    PROOF_URL_FIELD_NUMBER: _ClassVar[int]
    ATTESTOR_FIELD_NUMBER: _ClassVar[int]
    REGISTRANT_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    ATTESTOR_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    repository: Repository
    registrant: Identity
    proof_url: str
    attestor: str
    registrant_signature: bytes
    attestor_signature: bytes
    def __init__(self, repository: _Optional[_Union[Repository, _Mapping]] = ..., registrant: _Optional[_Union[Identity, _Mapping]] = ..., proof_url: _Optional[str] = ..., attestor: _Optional[str] = ..., registrant_signature: _Optional[bytes] = ..., attestor_signature: _Optional[bytes] = ...) -> None: ...

class Contribution(_message.Message):
    __slots__ = ("identity", "repository", "event_type", "linked_contributions", "url", "identity_uid", "repository_uid", "linked_contribution_uids")
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    LINKED_CONTRIBUTIONS_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_UID_FIELD_NUMBER: _ClassVar[int]
    REPOSITORY_UID_FIELD_NUMBER: _ClassVar[int]
    LINKED_CONTRIBUTION_UIDS_FIELD_NUMBER: _ClassVar[int]
    identity: Identity
    repository: Repository
    event_type: ContributionEventType
    linked_contributions: _containers.RepeatedCompositeFieldContainer[Contribution]
    url: str
    identity_uid: bytes
    repository_uid: bytes
    linked_contribution_uids: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, identity: _Optional[_Union[Identity, _Mapping]] = ..., repository: _Optional[_Union[Repository, _Mapping]] = ..., event_type: _Optional[_Union[ContributionEventType, str]] = ..., linked_contributions: _Optional[_Iterable[_Union[Contribution, _Mapping]]] = ..., url: _Optional[str] = ..., identity_uid: _Optional[bytes] = ..., repository_uid: _Optional[bytes] = ..., linked_contribution_uids: _Optional[_Iterable[bytes]] = ...) -> None: ...

class WebhookEvent(_message.Message):
    __slots__ = ("repository", "event_type", "raw_payload")
    REPOSITORY_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    RAW_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    repository: Repository
    event_type: ContributionEventType
    raw_payload: str
    def __init__(self, repository: _Optional[_Union[Repository, _Mapping]] = ..., event_type: _Optional[_Union[ContributionEventType, str]] = ..., raw_payload: _Optional[str] = ...) -> None: ...
