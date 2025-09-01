from collections.abc import Iterable, Mapping

from google.protobuf import descriptor_pool, message_factory
from google.protobuf.descriptor import (
    Descriptor,
    EnumDescriptor,
    EnumValueDescriptor,
    FieldDescriptor,
    MethodDescriptor,
    ServiceDescriptor,
)
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from google.protobuf.json_format import MessageToJson
from google.protobuf.message import Message

from ._proto_docstrings import extract_docstrings
from ._prototypes import ProtoTypeSignature
from ._specification import (
    DescriptionInfo,
    Endpoint,
    Field,
    FieldLocation,
    Method,
    ProtoEnum,
    Service,
    Specification,
    Struct,
    Value,
)
from ._typesignature import (
    DescriptiveTypeSignature,
    IterableTypeSignature,
    MapTypeSignature,
    TypeSignature,
    TypeSignatureType,
)


def generate_proto_specification(
    services: Iterable[str],
    serialized_descriptors: bytes | None,
    example_requests: Mapping[str, Iterable[Message]] | None = None,
) -> Specification:
    pool: descriptor_pool.DescriptorPool = descriptor_pool.Default()

    service_descriptors: list[ServiceDescriptor] = [
        pool.FindServiceByName(name) for name in services
    ]

    docstrings: dict[str, str] = {}
    if serialized_descriptors:
        descriptors = FileDescriptorSet()
        descriptors.ParseFromString(serialized_descriptors)
        for file in descriptors.file:
            extract_docstrings(file, docstrings)

    messages: dict[str, Descriptor] = {}
    enums: dict[str, EnumDescriptor] = {}

    # First find what we need to generate for.
    for svc in service_descriptors:
        find_service_messages_and_enums(svc, messages, enums)

    # Then generate.
    structs = [convert_message(msg, docstrings) for msg in messages.values()]
    structs.sort(key=lambda s: s.name)

    proto_enums = [convert_enum(enum, docstrings) for enum in enums.values()]
    proto_enums.sort(key=lambda e: e.name)

    services_spec = [
        convert_service(svc, docstrings, example_requests)
        for svc in service_descriptors
    ]
    services_spec.sort(key=lambda s: s.name)

    return Specification(
        services=services_spec,
        enums=proto_enums,
        structs=structs,
        exceptions=[],
        example_headers=[],
    )


def find_service_messages_and_enums(
    svc: ServiceDescriptor,
    messages: dict[str, Descriptor],
    enums: dict[str, EnumDescriptor],
) -> None:
    method: MethodDescriptor
    for method in svc.methods:
        find_message_dependencies(method.input_type, messages, enums)
        find_message_dependencies(method.output_type, messages, enums)


def find_message_dependencies(
    msg: Descriptor, messages: dict[str, Descriptor], enums: dict[str, EnumDescriptor]
) -> None:
    if msg.full_name in messages or msg.GetOptions().map_entry:
        return

    messages[msg.full_name] = msg
    field: FieldDescriptor
    message_type: Descriptor
    enum_type: EnumDescriptor
    for field in msg.fields:
        if field.message_type:
            message_type = field.message_type
            find_message_dependencies(message_type, messages, enums)
        elif field.enum_type:
            enum_type = field.enum_type
            enum_name = enum_type.full_name
            if enum_name not in enums:
                enums[enum_name] = enum_type

    for enum_type in msg.enum_types:
        enum_name = enum_type.full_name
        if enum_name not in enums:
            enums[enum_name] = enum_type

    for message_type in msg.nested_types:
        find_message_dependencies(message_type, messages, enums)


def convert_message(msg: Descriptor, docstrings: dict[str, str]) -> Struct:
    fields = [convert_field(msg, field, docstrings) for field in msg.fields]
    doc = docstrings.get(msg.full_name, "")
    return Struct(
        name=msg.full_name,
        alias="",
        fields=fields,
        description_info=DescriptionInfo(doc_string=doc, markup="NONE"),
    )


def convert_field(
    msg: Descriptor, field: FieldDescriptor, docstrings: dict[str, str]
) -> Field:
    requirement = "REQUIRED" if field.is_required else "OPTIONAL"  # pyright: ignore[reportAttributeAccessIssue]
    doc = docstrings.get(f"{msg.full_name}/{field.name}", "")
    type_sig = field_type_signature(field)
    return Field(
        name=field.name,
        location=FieldLocation.UNSPECIFIED,
        requirement=requirement,
        type_signature=type_sig,
        description_info=DescriptionInfo(doc_string=doc, markup="NONE"),
    )


def field_type_signature(field: FieldDescriptor) -> TypeSignature:
    message_type: Descriptor = field.message_type
    if message_type and message_type.GetOptions().map_entry:
        key_field: FieldDescriptor = message_type.fields[0]
        value_field: FieldDescriptor = message_type.fields[1]
        return MapTypeSignature(
            key_type=field_type_signature(key_field),
            value_type=field_type_signature(value_field),
        )

    field_type: int = field.type
    match field_type:
        case FieldDescriptor.TYPE_BOOL:
            type_signature = ProtoTypeSignature.BOOL
        case FieldDescriptor.TYPE_BYTES:
            type_signature = ProtoTypeSignature.BYTES
        case FieldDescriptor.TYPE_DOUBLE:
            type_signature = ProtoTypeSignature.DOUBLE
        case FieldDescriptor.TYPE_FIXED32:
            type_signature = ProtoTypeSignature.FIXED32
        case FieldDescriptor.TYPE_FIXED64:
            type_signature = ProtoTypeSignature.FIXED64
        case FieldDescriptor.TYPE_FLOAT:
            type_signature = ProtoTypeSignature.FLOAT
        case FieldDescriptor.TYPE_INT32:
            type_signature = ProtoTypeSignature.INT32
        case FieldDescriptor.TYPE_INT64:
            type_signature = ProtoTypeSignature.INT64
        case FieldDescriptor.TYPE_SFIXED32:
            type_signature = ProtoTypeSignature.SFIXED32
        case FieldDescriptor.TYPE_SFIXED64:
            type_signature = ProtoTypeSignature.SFIXED64
        case FieldDescriptor.TYPE_SINT32:
            type_signature = ProtoTypeSignature.SINT32
        case FieldDescriptor.TYPE_SINT64:
            type_signature = ProtoTypeSignature.SINT64
        case FieldDescriptor.TYPE_STRING:
            type_signature = ProtoTypeSignature.STRING
        case FieldDescriptor.TYPE_UINT32:
            type_signature = ProtoTypeSignature.UINT32
        case FieldDescriptor.TYPE_UINT64:
            type_signature = ProtoTypeSignature.UINT64
        case FieldDescriptor.TYPE_MESSAGE:
            type_signature = DescriptiveTypeSignature(
                sig=message_type.full_name, type=TypeSignatureType.STRUCT
            )
        case FieldDescriptor.TYPE_GROUP:
            # This type has been deprecated since the launch of protocol buffers to open source.
            # There is no real metadata for this in the descriptor, so we just treat as UNKNOWN
            # since it shouldn't happen in practice anyway.
            type_signature = ProtoTypeSignature.UNKNOWN
        case FieldDescriptor.TYPE_ENUM:
            type_signature = DescriptiveTypeSignature(
                sig=field.enum_type.full_name, type=TypeSignatureType.ENUM
            )
        case _:
            type_signature = ProtoTypeSignature.UNKNOWN

    if field.is_repeated:  # pyright: ignore[reportAttributeAccessIssue]
        type_signature = IterableTypeSignature(
            name="repeated", item_type=type_signature
        )

    return type_signature


def convert_service(
    svc: ServiceDescriptor,
    docstrings: dict[str, str],
    example_requests: Mapping[str, Iterable[Message]] | None,
) -> Service:
    methods = [
        convert_method(svc, m, docstrings, example_requests) for m in svc.methods
    ]
    doc = docstrings.get(svc.full_name, "")
    return Service(
        name=svc.full_name,
        methods=methods,
        example_headers=[],
        description_info=DescriptionInfo(doc_string=doc, markup="NONE"),
    )


def convert_method(
    svc: ServiceDescriptor,
    method: MethodDescriptor,
    docstrings: dict[str, str],
    example_requests: Mapping[str, Iterable[Message]] | None,
) -> Method:
    full_name = f"{svc.full_name}/{method.name}"
    endpoint = Endpoint(
        hostname_pattern="*",
        path_mapping=f"/{full_name}",
        default_mime_type="",
        available_mime_types=[
            "application/grpc+json",
            "application/grpc+proto",
            "application/grpc-web+json",
            "application/grpc-web+proto",
            "application/json; charset=utf-8; protocol=gRPC",
            "application/protobuf; protocol=gRPC",
        ],
        regex_path_prefix="",
        fragment="",
    )

    examples: list[str] = []

    if example_requests:
        for n, requests in example_requests.items():
            name = n.removeprefix("/")
            if full_name == name:
                examples.extend(
                    MessageToJson(
                        req,
                        preserving_proto_field_name=True,
                        always_print_fields_with_no_presence=True,
                    )
                    for req in requests
                )

    # TODO: Python does not seem to have a way to serialize JSON fields that
    # were never explicitly populated.
    request_class = message_factory.GetMessageClass(method.input_type)
    prototype_json = MessageToJson(
        request_class(),
        preserving_proto_field_name=True,
        always_print_fields_with_no_presence=True,
    )
    if prototype_json != "{\n}" and prototype_json != "{}":
        examples.append(prototype_json)

    doc = docstrings.get(full_name, "")
    return Method(
        name=method.name,
        id=f"{full_name}/POST",
        endpoints=[endpoint],
        return_type_signature=DescriptiveTypeSignature(
            type=TypeSignatureType.STRUCT, sig=method.output_type.full_name
        ),
        parameters=[
            Field(
                name="request",
                location=FieldLocation.UNSPECIFIED,
                requirement="REQUIRED",
                type_signature=DescriptiveTypeSignature(
                    type=TypeSignatureType.STRUCT, sig=method.input_type.full_name
                ),
                description_info=DescriptionInfo(doc_string="", markup="NONE"),
            )
        ],
        use_parameter_as_root=True,
        exception_type_signatures=[],
        example_headers=[],
        example_requests=examples,
        example_paths=[],
        example_queries=[],
        http_method="POST",
        description_info=DescriptionInfo(doc_string=doc, markup="NONE"),
    )


def convert_enum(enum: EnumDescriptor, docstrings: dict[str, str]) -> ProtoEnum:
    values = [convert_enum_value(enum, v, docstrings) for v in enum.values]
    doc = docstrings.get(enum.full_name, "")
    return ProtoEnum(
        name=enum.full_name,
        values=values,
        description_info=DescriptionInfo(doc_string=doc, markup="NONE"),
    )


def convert_enum_value(
    enum: EnumDescriptor, value: EnumValueDescriptor, docstrings: dict[str, str]
) -> Value:
    doc = docstrings.get(f"{enum.full_name}/{value.name}", "")
    return Value(
        name=value.name,
        int_value=value.number,
        description_info=DescriptionInfo(doc_string=doc, markup="NONE"),
    )
