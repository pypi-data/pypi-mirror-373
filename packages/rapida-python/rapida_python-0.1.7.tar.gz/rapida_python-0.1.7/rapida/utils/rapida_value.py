from google.protobuf.any_pb2 import Any
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.duration_pb2 import Duration
from google.protobuf.field_mask_pb2 import FieldMask
from google.protobuf.struct_pb2 import Struct, ListValue, Value
from google.protobuf.wrappers_pb2 import (
    StringValue,
    Int32Value,
    UInt32Value,
    Int64Value,
    UInt64Value,
    FloatValue,
    DoubleValue,
    BoolValue,
    BytesValue,
)


# Helper: pack into Any
def pack(message, type_url_prefix="type.googleapis.com"):
    any_value = Any()
    any_value.Pack(message, type_url_prefix)
    return any_value


# -------- Conversion helpers -------- #


def string_to_any(value: str) -> Any:
    sv = StringValue(value=value)
    return pack(sv)


def any_to_string(any_value: Any) -> str:
    sv = StringValue()
    any_value.Unpack(sv)
    return sv.value


def float_to_any(value: float) -> Any:
    dv = DoubleValue(value=value)
    return pack(dv)


def any_to_float(any_value: Any) -> float:
    dv = DoubleValue()
    any_value.Unpack(dv)
    return dv.value


def int32_to_any(value: int) -> Any:
    iv = Int32Value(value=value)
    return pack(iv)


def any_to_int32(any_value: Any) -> int:
    iv = Int32Value()
    any_value.Unpack(iv)
    return iv.value


def bool_to_any(value: bool) -> Any:
    bv = BoolValue(value=value)
    return pack(bv)


def any_to_bool(any_value: Any) -> bool:
    bv = BoolValue()
    any_value.Unpack(bv)
    return bv.value


def bytes_to_any(value: bytes) -> Any:
    bv = BytesValue(value=value)
    return pack(bv)


def json_to_any(obj: dict) -> Any:
    import json

    sv = StringValue(value=json.dumps(obj))
    return pack(sv)


def any_to_json(any_value: Any) -> dict:
    import json

    sv = StringValue()
    any_value.Unpack(sv)
    return json.loads(sv.value)


# -------- Map / Struct helpers -------- #


def map_to_object(proto_map) -> dict:
    result = {}
    if not proto_map:
        return result

    try:
        for key, value in proto_map.items():
            result[key] = safe_convert_value(value)
    except Exception as e:
        print("map_to_object conversion error:", e)

    return result


def safe_convert_value(value):
    if value is None:
        return None

    try:
        if isinstance(value, Any):
            return convert_any_value(value)

        if isinstance(value, (str, int, float, bool)):
            return value

        if isinstance(value, Struct):
            return convert_struct(value)

        if isinstance(value, Value):
            return convert_value(value)

        if isinstance(value, list):
            return [safe_convert_value(v) for v in value]

        if isinstance(value, dict):
            return {k: safe_convert_value(v) for k, v in value.items()}

        return value
    except Exception as e:
        print("value conversion error:", e)
        return None


def convert_any_value(any_value: Any):
    try:
        type_url = any_value.type_url
        type_name = type_url.split("/")[-1]

        if type_name == "google.protobuf.StringValue":
            sv = StringValue()
            any_value.Unpack(sv)
            return sv.value

        if type_name == "google.protobuf.Int32Value":
            iv = Int32Value()
            any_value.Unpack(iv)
            return iv.value

        if type_name == "google.protobuf.UInt32Value":
            uv = UInt32Value()
            any_value.Unpack(uv)
            return uv.value

        if type_name == "google.protobuf.Int64Value":
            iv = Int64Value()
            any_value.Unpack(iv)
            return str(iv.value)

        if type_name == "google.protobuf.UInt64Value":
            uv = UInt64Value()
            any_value.Unpack(uv)
            return str(uv.value)

        if type_name == "google.protobuf.FloatValue":
            fv = FloatValue()
            any_value.Unpack(fv)
            return fv.value

        if type_name == "google.protobuf.DoubleValue":
            dv = DoubleValue()
            any_value.Unpack(dv)
            return dv.value

        if type_name == "google.protobuf.BoolValue":
            bv = BoolValue()
            any_value.Unpack(bv)
            return bv.value

        if type_name == "google.protobuf.BytesValue":
            bv = BytesValue()
            any_value.Unpack(bv)
            return bytes(bv.value)

        if type_name == "google.protobuf.Timestamp":
            ts = Timestamp()
            any_value.Unpack(ts)
            return ts.ToDatetime()

        if type_name == "google.protobuf.Struct":
            st = Struct()
            any_value.Unpack(st)
            return convert_struct(st)

        if type_name == "google.protobuf.Value":
            v = Value()
            any_value.Unpack(v)
            return convert_value(v)

        if type_name == "google.protobuf.Any":
            nested = Any()
            any_value.Unpack(nested)
            return convert_any_value(nested)

        return {"$type": type_url, "$data": any_value.value}
    except Exception as e:
        print(f"failed to convert Any type {any_value.type_url}:", e)
        return None


def convert_struct(struct: Struct) -> dict:
    result = {}
    try:
        for key, val in struct.fields.items():
            result[key] = convert_value(val)
    except Exception as e:
        print("struct conversion error:", e)
    return result


def convert_value(value: Value):
    try:
        kind = value.WhichOneof("kind")
        if kind == "null_value":
            return None
        elif kind == "number_value":
            return value.number_value
        elif kind == "string_value":
            return value.string_value
        elif kind == "bool_value":
            return value.bool_value
        elif kind == "struct_value":
            return convert_struct(value.struct_value)
        elif kind == "list_value":
            return [convert_value(v) for v in value.list_value.values]
        else:
            return None
    except Exception as e:
        print("value conversion error:", e)
        return None
