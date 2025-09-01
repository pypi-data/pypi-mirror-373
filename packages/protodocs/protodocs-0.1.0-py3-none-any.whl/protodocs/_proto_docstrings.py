from collections.abc import Sequence

from google.protobuf.descriptor_pb2 import (
    DescriptorProto,
    EnumDescriptorProto,
    FileDescriptorProto,
    ServiceDescriptorProto,
)


def extract_docstrings(
    file_descriptor: FileDescriptorProto, docstrings: dict[str, str]
) -> None:
    source_code_info = file_descriptor.source_code_info
    for loc in source_code_info.location:
        if not loc.leading_comments:
            continue
        name, ok = get_full_name(file_descriptor, loc.path)
        if ok:
            docstrings[name] = loc.leading_comments


def get_full_name(
    descriptor: FileDescriptorProto, path: Sequence[int]
) -> tuple[str, bool]:
    name: list[str] = [descriptor.package]

    match path[0]:
        case FileDescriptorProto.MESSAGE_TYPE_FIELD_NUMBER:
            message = descriptor.message_type[path[1]]
            if not append_message_to_full_name(message, path, name):
                return "", False
        case FileDescriptorProto.ENUM_TYPE_FIELD_NUMBER:
            enum = descriptor.enum_type[path[1]]
            if not append_enum_to_full_name(enum, path, name):
                return "", False
        case FileDescriptorProto.SERVICE_FIELD_NUMBER:
            service = descriptor.service[path[1]]
            append_name_component(service.name, name)
            if len(path) > 2 and not append_method_to_full_name(service, path, name):
                return "", False
        case _:
            return "", False

    return "".join(name), True


def append_method_to_full_name(
    service: ServiceDescriptorProto, path: Sequence[int], name: list[str]
) -> bool:
    if len(path) == 4 and path[2] == ServiceDescriptorProto.METHOD_FIELD_NUMBER:
        append_field_component(service.method[path[3]].name, name)
        return True
    return False


def append_to_full_name(
    descriptor: DescriptorProto, path: Sequence[int], name: list[str]
) -> bool:
    match path[0]:
        case DescriptorProto.FIELD_FIELD_NUMBER:
            field = descriptor.field[path[1]]
            append_field_component(field.name, name)
            return True
        case DescriptorProto.NESTED_TYPE_FIELD_NUMBER:
            msg = descriptor.nested_type[path[1]]
            return append_message_to_full_name(msg, path, name)
        case DescriptorProto.ENUM_TYPE_FIELD_NUMBER:
            enum = descriptor.enum_type[path[1]]
            return append_enum_to_full_name(enum, path, name)
        case _:
            return False


def append_message_to_full_name(
    message: DescriptorProto, path: Sequence[int], name: list[str]
) -> bool:
    append_name_component(message.name, name)
    if len(path) > 2:
        append_to_full_name(message, path[2:], name)
    return True


def append_enum_to_full_name(
    enum: EnumDescriptorProto, path: Sequence[int], name: list[str]
) -> bool:
    append_name_component(enum.name, name)
    if len(path) <= 2:
        return True
    if path[2] == EnumDescriptorProto.VALUE_FIELD_NUMBER:
        append_field_component(enum.value[path[3]].name, name)
        return True
    return False


def append_name_component(component: str, name: list[str]) -> None:
    name.append(f".{component}")


def append_field_component(component: str, name: list[str]) -> None:
    name.append(f"/{component}")
