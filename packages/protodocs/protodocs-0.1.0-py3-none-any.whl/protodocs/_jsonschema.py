from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import cast

from ._specification import (
    DescriptionInfo,
    Field,
    FieldLocation,
    Method,
    ProtoEnum,
    Specification,
    Struct,
)
from ._types import JSON
from ._typesignature import (
    IterableTypeSignature,
    MapTypeSignature,
    TypeSignature,
    TypeSignatureType,
)


@dataclass(frozen=True, kw_only=True, slots=True)
class AdditionalPropertiesSchema:
    field: "JsonSchemaField"

    def to_json(self) -> JSON:
        return self.field.to_json()


@dataclass(frozen=True, kw_only=True, slots=True)
class AdditionalPropertiesBool:
    value: bool

    def to_json(self) -> JSON:
        return self.value


@dataclass(frozen=True, kw_only=True, slots=True)
class JsonSchemaField:
    description: str
    ref: str = ""
    type: str = ""
    enum: Sequence[str] = ()
    properties: Mapping[str, "JsonSchemaField"] | None = None
    additional_properties: (
        AdditionalPropertiesSchema | AdditionalPropertiesBool | None
    ) = None
    items: "JsonSchemaField | None" = None

    def to_json(self) -> JSON:
        res: dict[str, JSON] = {"description": self.description}
        if self.ref:
            res["$ref"] = self.ref
        if self.type:
            res["type"] = self.type
        if self.enum:
            res["enum"] = list(self.enum)
        if self.properties:
            res["properties"] = {k: v.to_json() for k, v in self.properties.items()}
        if self.additional_properties:
            res["additionalProperties"] = self.additional_properties.to_json()
        if self.items:
            res["items"] = self.items.to_json()
        return res


@dataclass(frozen=True, kw_only=True, slots=True)
class JsonSchema:
    id: str
    title: str
    description: str
    properties: Mapping[str, JsonSchemaField]
    additional_properties: bool
    type: str

    def to_json(self) -> JSON:
        return {
            "$id": self.id,
            "title": self.title,
            "description": self.description,
            "properties": {k: v.to_json() for k, v in self.properties.items()},
            "additionalProperties": self.additional_properties,
            "type": self.type,
        }


def generate_json_schema(spec: Specification) -> list[JsonSchema]:
    type_name_to_enum: dict[str, ProtoEnum] = {enum.name: enum for enum in spec.enums}
    type_name_to_struct: dict[str, Struct] = {
        struct.name: struct for struct in spec.structs
    }
    generator = Generator(type_name_to_enum, type_name_to_struct)
    return generator.generate(spec)


class Generator:
    def __init__(
        self,
        type_name_to_enum: dict[str, ProtoEnum],
        type_name_to_struct: dict[str, Struct],
    ) -> None:
        self._type_name_to_enum = type_name_to_enum
        self._type_name_to_struct = type_name_to_struct

    def generate(self, spec: Specification) -> list[JsonSchema]:
        schemas: list[JsonSchema] = []
        for service in spec.services:
            schemas.extend(
                self._generate_method_schema(method) for method in service.methods
            )
        return schemas

    def _generate_method_schema(self, method: Method) -> JsonSchema:
        method_fields: Sequence[Field] = ()
        visited: dict[str, str] = {}
        current_path = "#"

        addtional_properties = False

        if method.use_parameter_as_root:
            sig = method.parameters[0].type_signature
            if struct := self._type_name_to_struct.get(sig.signature()):
                method_fields = struct.fields
            else:
                # Couldnt resolve parameter, allow any parameters.
                addtional_properties = True
            visited[sig.signature()] = current_path

        return JsonSchema(
            id=method.id,
            title=method.name,
            description=method.description_info.doc_string,
            additional_properties=addtional_properties,
            type="object",
            properties=self._generate_properties(method_fields, visited, current_path),
        )

    def _generate_field(
        self, field: Field, visited: dict[str, str], path: str
    ) -> JsonSchemaField:
        if ref := visited.get(field.type_signature.signature()):
            return JsonSchemaField(
                description=field.description_info.doc_string, ref=ref
            )

        schema_type = get_schema_type(field.type_signature)
        enum_values: Sequence[str] = ()
        if field.type_signature.get_type() == TypeSignatureType.ENUM:
            enum_values = self._get_enum_type(field.type_signature)

        current_path = path
        if field.name:
            current_path = f"{path}/{field.name}"

        # We can only have references to struct types, not primitives
        match schema_type:
            case "array" | "object":
                visited[field.type_signature.signature()] = current_path

        properties: Mapping[str, JsonSchemaField] | None = None
        additional_properties: (
            AdditionalPropertiesSchema | AdditionalPropertiesBool | None
        ) = None
        items: JsonSchemaField | None = None
        if field.type_signature.get_type() == TypeSignatureType.MAP:
            aprops = self._generate_map_additional_properties(
                field, visited, current_path
            )
            additional_properties = AdditionalPropertiesSchema(field=aprops)
        elif field.type_signature.get_type() == TypeSignatureType.ITERABLE:
            items = self._generate_array_items(field, visited, current_path)
        elif schema_type == "object":
            props, found = self._generate_struct_properties(
                field, visited, current_path
            )
            if found:
                additional_properties = AdditionalPropertiesBool(value=False)
                properties = props
            else:
                # When we have a struct but the definition cannot not be found, we go ahead
                # and allow all additional properties since it may still be more useful than
                # being completely unusable.
                additional_properties = AdditionalPropertiesBool(value=True)

        return JsonSchemaField(
            description=field.description_info.doc_string,
            type=schema_type,
            enum=enum_values,
            properties=properties,
            additional_properties=additional_properties,
            items=items,
        )

    def _generate_properties(
        self, fields: Sequence[Field], visited: dict[str, str], path: str
    ) -> dict[str, JsonSchemaField]:
        properties: dict[str, JsonSchemaField] = {}
        for field in fields:
            match field.location:
                case FieldLocation.BODY | FieldLocation.UNSPECIFIED:
                    properties[field.name] = self._generate_field(
                        field, visited, f"{path}/properties"
                    )
        return properties

    def _generate_map_additional_properties(
        self, field: Field, visited: dict[str, str], path: str
    ) -> JsonSchemaField:
        value_type = cast("MapTypeSignature", field.type_signature).value_type
        # Create a virtual field for generation
        item_field = Field(
            location=FieldLocation.BODY,
            type_signature=value_type,
            # Other attributes not used for JSON schema
            name="",
            requirement="",
            description_info=DescriptionInfo(doc_string="", markup=""),
        )
        return self._generate_field(item_field, visited, f"{path}/additionalProperties")

    def _generate_array_items(
        self, field: Field, visited: dict[str, str], path: str
    ) -> JsonSchemaField:
        item_type = cast("IterableTypeSignature", field.type_signature).item_type
        # Create a virtual field for generation
        item_field = Field(
            location=FieldLocation.BODY,
            type_signature=item_type,
            # Other attributes not used for JSON schema
            name="",
            requirement="",
            description_info=DescriptionInfo(doc_string="", markup=""),
        )
        return self._generate_field(item_field, visited, f"{path}/items")

    def _generate_struct_properties(
        self, field: Field, visited: dict[str, str], path: str
    ) -> tuple[dict[str, JsonSchemaField], bool]:
        if struct := self._type_name_to_struct.get(field.type_signature.signature()):
            return self._generate_properties(struct.fields, visited, path), True
        return {}, False

    def _get_enum_type(self, t: TypeSignature) -> Sequence[str]:
        if enum := self._type_name_to_enum.get(t.signature()):
            return [v.name for v in enum.values]
        return ()


def get_schema_type(t: TypeSignature) -> str:
    match t.get_type():
        case TypeSignatureType.ENUM:
            return "string"
        case TypeSignatureType.ITERABLE:
            return "array"
        case TypeSignatureType.MAP:
            return "object"
        case TypeSignatureType.BASE:
            return get_base_type(t.signature())
        case _:
            return "object"


def get_base_type(sig: str) -> str:
    match sig:
        case "bool" | "boolean":
            return "boolean"
        case "short" | "number" | "float" | "double":
            return "number"
        case (
            "i"
            | "i8"
            | "i16"
            | "i32"
            | "i64"
            | "integer"
            | "int"
            | "l32"
            | "l64"
            | "long"
            | "long32"
            | "long64"
            | "int32"
            | "int64"
            | "uint32"
            | "uint64"
            | "sint32"
            | "sint64"
            | "fixed32"
            | "fixed64"
            | "sfixed32"
            | "sfixed64"
        ):
            return "integer"
        case "binary" | "byte" | "bytes" | "string":
            return "string"
        case _:
            return "object"
