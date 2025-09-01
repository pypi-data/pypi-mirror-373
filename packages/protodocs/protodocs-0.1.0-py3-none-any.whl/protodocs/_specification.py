from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from ._types import JSON
from ._typesignature import TypeSignature


class FieldLocation(Enum):
    UNSPECIFIED = "UNSPECIFIED"
    PATH = "PATH"
    HEADER = "HEADER"
    QUERY = "QUERY"
    BODY = "BODY"


@dataclass(frozen=True, kw_only=True, slots=True)
class DescriptionInfo:
    doc_string: str
    markup: str

    def to_json(self) -> JSON:
        return {"docString": self.doc_string, "markup": self.markup}


@dataclass(frozen=True, kw_only=True, slots=True)
class Endpoint:
    hostname_pattern: str
    path_mapping: str
    default_mime_type: str
    available_mime_types: Sequence[str]
    regex_path_prefix: str
    fragment: str

    def to_json(self) -> JSON:
        res = {
            "hostnamePattern": self.hostname_pattern,
            "pathMapping": self.path_mapping,
            "availableMimeTypes": self.available_mime_types,
        }
        if self.default_mime_type:
            res["defaultMimeType"] = self.default_mime_type
        if self.regex_path_prefix:
            res["regexPathPrefix"] = self.regex_path_prefix
        if self.fragment:
            res["fragment"] = self.fragment
        return res


@dataclass(frozen=True, kw_only=True, slots=True)
class Field:
    name: str
    location: FieldLocation
    requirement: str
    type_signature: TypeSignature
    description_info: DescriptionInfo

    def to_json(self) -> JSON:
        return {
            "name": self.name,
            "location": self.location.value,
            "requirement": self.requirement,
            "typeSignature": self.type_signature.signature(),
            "descriptionInfo": self.description_info.to_json(),
        }


@dataclass(frozen=True, kw_only=True, slots=True)
class Struct:
    name: str
    alias: str
    fields: Sequence[Field]
    description_info: DescriptionInfo

    def to_json(self) -> JSON:
        res = {
            "name": self.name,
            "fields": [f.to_json() for f in self.fields],
            "descriptionInfo": self.description_info.to_json(),
        }
        if self.alias:
            res["alias"] = self.alias
        return res


@dataclass(frozen=True, kw_only=True, slots=True)
class Method:
    name: str
    id: str
    return_type_signature: TypeSignature
    parameters: Sequence[Field]
    exception_type_signatures: Sequence[TypeSignature]
    endpoints: Sequence[Endpoint]
    example_headers: Sequence[dict[str, str]]
    example_requests: Sequence[str]
    example_paths: Sequence[str]
    example_queries: Sequence[str]
    http_method: str
    description_info: DescriptionInfo
    use_parameter_as_root: bool

    def to_json(self) -> JSON:
        return {
            "name": self.name,
            "id": self.id,
            "returnTypeSignature": self.return_type_signature.signature(),
            "parameters": [p.to_json() for p in self.parameters],
            "exceptionTypeSignatures": [
                e.signature() for e in self.exception_type_signatures
            ],
            "endpoints": [ep.to_json() for ep in self.endpoints],
            "exampleHeaders": self.example_headers,
            "exampleRequests": self.example_requests,
            "examplePaths": self.example_paths,
            "exampleQueries": self.example_queries,
            "httpMethod": self.http_method,
            "descriptionInfo": self.description_info.to_json(),
        }


@dataclass(frozen=True, kw_only=True, slots=True)
class Service:
    name: str
    methods: Sequence[Method]
    example_headers: Sequence[dict[str, str]]
    description_info: DescriptionInfo

    def to_json(self) -> JSON:
        return {
            "name": self.name,
            "methods": [m.to_json() for m in self.methods],
            "exampleHeaders": self.example_headers,
            "descriptionInfo": self.description_info.to_json(),
        }


@dataclass(frozen=True, kw_only=True, slots=True)
class Value:
    name: str
    int_value: int | None
    description_info: DescriptionInfo

    def to_json(self) -> JSON:
        res = {"name": self.name, "descriptionInfo": self.description_info.to_json()}
        if self.int_value is not None:
            res["intValue"] = self.int_value
        return res


@dataclass(frozen=True, kw_only=True, slots=True)
class ProtoEnum:
    name: str
    values: Sequence[Value]
    description_info: DescriptionInfo

    def to_json(self) -> JSON:
        return {
            "name": self.name,
            "values": [v.to_json() for v in self.values],
            "descriptionInfo": self.description_info.to_json(),
        }


@dataclass(frozen=True, kw_only=True, slots=True)
class Specification:
    services: Sequence[Service]
    enums: Sequence[ProtoEnum]
    structs: Sequence[Struct]
    exceptions: Sequence[Struct]
    example_headers: Sequence[dict]

    def to_json(self) -> JSON:
        return {
            "services": [s.to_json() for s in self.services],
            "enums": [e.to_json() for e in self.enums],
            "structs": [st.to_json() for st in self.structs],
            "exceptions": [ex.to_json() for ex in self.exceptions],
            "exampleHeaders": self.example_headers,
        }
