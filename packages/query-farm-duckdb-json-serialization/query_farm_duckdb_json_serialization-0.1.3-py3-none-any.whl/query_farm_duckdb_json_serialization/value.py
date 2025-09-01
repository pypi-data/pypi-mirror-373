import base64
import math
import uuid
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Discriminator, Tag, field_validator


class ValueBase(BaseModel):
    is_null: bool


class ValueValue_128bits(BaseModel):
    """
    Represent a 128-bit value with an upper and lower half.
    """

    lower: int
    upper: int


def decode_base64(cls: Any, value: Any) -> bytes:
    """
    Decode a Base64 encoded value.
    """
    try:
        return base64.b64decode(value)
    except Exception as e:
        raise ValueError(f"Invalid Base64 encoded value: {e}") from e


class ValueValue_base64(BaseModel):
    """
    Store and decode a base64 value
    """

    base64: bytes
    # Do the decoding of the value here for the user.
    _validate_base64 = field_validator("base64", mode="before")(decode_base64)


class ValueTypeInfo_list(BaseModel):
    alias: str
    child_type: "AnyValueType"
    type: Literal["LIST_TYPE_INFO"] = "LIST_TYPE_INFO"


class ValueType_list(BaseModel):
    id: Literal["LIST"] = "LIST"
    type_info: ValueTypeInfo_list

    def sql(self) -> str:
        return f"{self.type_info.child_type.sql()}[]"


class ValueValue_list(BaseModel):
    children: list["Value"]


class Value_list(ValueBase):
    type: ValueType_list
    value: ValueValue_list

    def sql(self) -> str:
        return "[" + ", ".join([child.sql() for child in self.value.children]) + "]"


class ValueType_bigint(BaseModel):
    id: Literal["BIGINT"] = "BIGINT"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_bigint(ValueBase):
    type: ValueType_bigint
    value: int | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        return str(self.value)


class ValueType_bit(BaseModel):
    id: Literal["BIT"] = "BIT"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_bit(ValueBase):
    type: ValueType_bit
    value: bytes | ValueValue_base64 | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        data = (
            self.value.base64
            if isinstance(self.value, ValueValue_base64)
            else self.value
        )

        if not data or len(data) < 2:
            return ""

        padding_bits = data[0]
        bit_data = data[1:]

        # Convert all bytes to bits
        bits = "".join(f"{byte:08b}" for byte in bit_data)

        # Remove the padding bits from the end
        if padding_bits:
            bits = bits[padding_bits:]

        return f"'{bits}'"


class ValueType_blob(BaseModel):
    id: Literal["BLOB"] = "BLOB"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_blob(ValueBase):
    type: ValueType_blob
    value: str | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        return "'" + self.value.replace("'", "''") + "'"


class ValueType_boolean(BaseModel):
    id: Literal["BOOLEAN"] = "BOOLEAN"
    type_info: None

    def sql(self) -> str:
        return self.id


class ValueType_any(BaseModel):
    id: Literal["ANY"] = "ANY"
    type_info: None

    def sql(self) -> str:
        raise NotImplementedError("ValueType_any.sql() is not implemented.")


class Value_boolean(ValueBase):
    type: ValueType_boolean
    value: bool | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"

        return str("true" if self.value else "false")


class ValueType_date(BaseModel):
    id: Literal["DATE"] = "DATE"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_date(ValueBase):
    type: ValueType_date
    value: int | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        if self.value == -2147483647:
            return "'-infinity'"
        elif self.value == 2147483647:
            return "'infinity'"
        formatted_date = (date(1970, 1, 1) + timedelta(days=self.value)).isoformat()
        return f"'{formatted_date}'"


class ValueTypeInfo_decimal(BaseModel):
    width: int
    scale: int


class ValueType_decimal(BaseModel):
    id: Literal["DECIMAL"] = "DECIMAL"
    type_info: ValueTypeInfo_decimal

    def sql(self) -> str:
        return f"DECIMAL({self.type_info.width}, {self.type_info.scale})"


class Value_decimal(ValueBase):
    type: ValueType_decimal
    value: int | ValueValue_128bits | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        scale = self.type.type_info.scale

        if isinstance(self.value, ValueValue_128bits):
            # Reconstruct full integer (assuming 64-bit halves)
            combined = (self.value.upper << 64) | self.value.lower

            # Convert from unsigned to signed (two's complement if necessary)
            if self.value.upper & (1 << 63):
                combined -= 1 << 128

            decimal_value = Decimal(combined)
        elif isinstance(self.value, int):
            # Assume it's a simple int (64-bit)
            decimal_value = Decimal(self.value)
        else:
            raise NotImplementedError("Invalid Decimal value storage")

        return str(decimal_value / Decimal(10) ** scale)


class ValueType_double(BaseModel):
    id: Literal["DOUBLE"] = "DOUBLE"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_double(ValueBase):
    type: ValueType_double
    value: float | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        if math.isinf(self.value):
            if self.value > 0:
                return "'infinity'"
            return "'-infinity'"
        elif math.isnan(self.value):
            return "'nan'"
        return str(self.value)


class ValueType_float(BaseModel):
    id: Literal["FLOAT"] = "FLOAT"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_float(ValueBase):
    type: ValueType_float
    value: float | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        if math.isinf(self.value):
            if self.value > 0:
                return "'infinity'"
            return "'-infinity'"
        elif math.isnan(self.value):
            return "'nan'"
        return str(self.value)


class ValueType_hugeint(BaseModel):
    id: Literal["HUGEINT"] = "HUGEINT"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_hugeint(ValueBase):
    type: ValueType_hugeint
    value: ValueValue_128bits | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        upper = self.value.upper
        lower = self.value.lower
        result = (upper << 64) | lower

        # If the highest bit (bit 127) is set, interpret as negative
        if upper & (1 << 63):
            result -= 1 << 128

        return str(result)


class ValueType_integer(BaseModel):
    id: Literal["INTEGER"] = "INTEGER"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_integer(ValueBase):
    type: ValueType_integer
    value: int | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"

        return str(self.value)


class ValueType_interval(BaseModel):
    id: Literal["INTERVAL"] = "INTERVAL"
    type_info: None

    def sql(self) -> str:
        return self.id


class ValueValue_interval(BaseModel):
    months: int
    days: int
    micros: int


class Value_interval(ValueBase):
    type: ValueType_interval
    value: ValueValue_interval | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        return (
            "INTERVAL '"
            + f"{self.value.months} months {self.value.days} days {self.value.micros} us"
            + "'"
        )


class ValueType_null(BaseModel):
    id: Literal["NULL"] = "NULL"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_null(ValueBase):
    type: ValueType_null
    value: None

    def sql(self) -> str:
        return "null"


class ValueType_smallint(BaseModel):
    id: Literal["SMALLINT"] = "SMALLINT"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_smallint(ValueBase):
    type: ValueType_smallint
    value: int | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"

        return str(self.value)


class ValueType_time(BaseModel):
    id: Literal["TIME"] = "TIME"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_time(ValueBase):
    type: ValueType_time
    value: int | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        t = timedelta(microseconds=self.value)
        hours, remainder = divmod(t.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return (
            "TIME '"
            + time(hours, minutes, seconds, microsecond=t.microseconds).strftime(
                "%H:%M:%S.%f"
            )
            + "'"
        )


class ValueType_time_with_time_zone(BaseModel):
    id: Literal["TIME WITH TIME ZONE"] = "TIME WITH TIME ZONE"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_time_with_time_zone(ValueBase):
    type: ValueType_time_with_time_zone
    value: int | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        t = timedelta(microseconds=self.value)
        hours, remainder = divmod(t.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return (
            "TIMETZ '"
            + time(hours, minutes, seconds, microsecond=t.microseconds).strftime(
                "%H:%M:%S.%f"
            )
            + "'"
        )


class ValueType_timestamp_with_time_zone(BaseModel):
    id: Literal["TIMESTAMP WITH TIME ZONE"] = "TIMESTAMP WITH TIME ZONE"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_timestamp_with_time_zone(ValueBase):
    type: ValueType_timestamp_with_time_zone
    value: int | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        return (
            "TIMESTAMPTZ '"
            + datetime.fromtimestamp(int(self.value) / 1_000_000, tz=UTC).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )
            + "'"
        )


class ValueType_timestamp(BaseModel):
    id: Literal["TIMESTAMP"] = "TIMESTAMP"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_timestamp(ValueBase):
    type: ValueType_timestamp
    value: int | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        return (
            "TIMESTAMP '"
            + datetime.fromtimestamp(int(self.value) / 1_000_000, tz=UTC).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )
            + "'"
        )


class ValueType_timestamp_ms(BaseModel):
    id: Literal["TIMESTAMP_MS"] = "TIMESTAMP_MS"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_timestamp_ms(ValueBase):
    type: ValueType_timestamp_ms
    value: int | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        dt = datetime.fromtimestamp(self.value / 1000, tz=UTC)
        return "TIMESTAMP_MS '" + dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "'"


class ValueType_timestamp_ns(BaseModel):
    id: Literal["TIMESTAMP_NS"] = "TIMESTAMP_NS"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_timestamp_ns(ValueBase):
    type: ValueType_timestamp_ns
    value: int | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value
        ns_since_epoch = self.value
        seconds, nanoseconds = divmod(ns_since_epoch, 10**9)

        dt = datetime.fromtimestamp(seconds, tz=UTC)
        formatted = dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{nanoseconds:09d}"
        return f"TIMESTAMP_NS '{formatted}'"


class ValueType_timestamp_s(BaseModel):
    id: Literal["TIMESTAMP_S"] = "TIMESTAMP_S"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_timestamp_s(ValueBase):
    type: ValueType_timestamp_s
    value: int | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        dt = datetime.fromtimestamp(self.value, tz=UTC)
        return "TIMESTAMP_S '" + dt.strftime("%Y-%m-%d %H:%M:%S") + "'"


class ValueType_tinyint(BaseModel):
    id: Literal["TINYINT"] = "TINYINT"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_tinyint(ValueBase):
    type: ValueType_tinyint
    value: int | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"

        return str(self.value)


class ValueType_ubigint(BaseModel):
    id: Literal["UBIGINT"] = "UBIGINT"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_ubigint(ValueBase):
    type: ValueType_ubigint
    value: int | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"

        return str(self.value)


class ValueType_uhugeint(BaseModel):
    id: Literal["UHUGEINT"] = "UHUGEINT"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_uhugeint(ValueBase):
    type: ValueType_uhugeint
    value: ValueValue_128bits | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        upper = self.value.upper
        lower = self.value.lower
        return str((upper << 64) | lower)


class ValueType_uinteger(BaseModel):
    id: Literal["UINTEGER"] = "UINTEGER"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_uinteger(ValueBase):
    type: ValueType_uinteger
    value: int | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value
        return str(self.value)


class ValueType_usmallint(BaseModel):
    id: Literal["USMALLINT"] = "USMALLINT"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_usmallint(ValueBase):
    type: ValueType_usmallint
    value: int | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value
        return str(self.value)


class ValueType_utinyint(BaseModel):
    id: Literal["UTINYINT"] = "UTINYINT"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_utinyint(ValueBase):
    type: ValueType_utinyint
    value: int | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value
        return str(self.value)


class ValueType_uuid(BaseModel):
    id: Literal["UUID"] = "UUID"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_uuid(ValueBase):
    type: ValueType_uuid
    value: ValueValue_128bits | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value
        upper = self.value.upper & ((1 << 64) - 1)  # Convert to unsigned if needed
        lower = self.value.lower

        # Combine into 128-bit integer
        combined = (upper << 64) | lower

        # Convert to 16 bytes (big-endian)
        bytes_ = combined.to_bytes(16, byteorder="big")

        # Create UUID from bytes
        u = uuid.UUID(bytes=bytes_)

        return str(u)


class ValueType_varchar(BaseModel):
    id: Literal["VARCHAR"] = "VARCHAR"
    type_info: None

    def sql(self) -> str:
        return self.id


class Value_varchar(ValueBase):
    type: ValueType_varchar
    value: str | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        return "'" + self.value.replace("'", "''") + "'"


class ValueType_bignum(BaseModel):
    id: Literal["bignum"] = "bignum"
    type_info: None

    def sql(self) -> str:
        return self.id


def _bignum_get_byte_array(blob: bytes) -> tuple[list[int], bool]:
    if len(blob) < 4:
        raise ValueError("Invalid blob size.")

    # Determine if the number is negative
    is_negative = (blob[0] & 0x80) == 0

    # Extract byte array starting from the 4th byte
    byte_array = [~b & 255 for b in blob[3:]] if is_negative else list(blob[3:])
    return byte_array, is_negative


class Value_bignum(ValueBase):
    type: ValueType_bignum
    value: bytes | ValueValue_base64 | None = None

    def sql(self) -> str:
        if self.is_null:
            return "null"
        assert self.value

        decimal_string = ""
        if isinstance(self.value, ValueValue_base64):
            byte_array, is_negative = _bignum_get_byte_array(self.value.base64)
        else:
            byte_array, is_negative = _bignum_get_byte_array(self.value)

        digits: list[int] = []

        # Constants matching your C++ code (update if needed)
        DIGIT_BYTES = 4  # Assuming 4 bytes per digit (like a uint32_t)
        DIGIT_BITS = 32
        DECIMAL_BASE = 1000000000  # Typically 10^9 for efficient base conversion
        DECIMAL_SHIFT = 9  # Number of decimal digits in DECIMAL_BASE

        # Pad the byte array so we can process in DIGIT_BYTES chunks without conditionals
        padding_size = (-len(byte_array)) & (DIGIT_BYTES - 1)
        byte_array = [0] * padding_size + byte_array

        for i in range(0, len(byte_array), DIGIT_BYTES):
            hi = 0
            for j in range(DIGIT_BYTES):
                hi |= byte_array[i + j] << (8 * (DIGIT_BYTES - j - 1))

            for j in range(len(digits)):
                tmp = (digits[j] << DIGIT_BITS) | hi
                hi = tmp // DECIMAL_BASE
                digits[j] = tmp - DECIMAL_BASE * hi

            while hi:
                digits.append(hi % DECIMAL_BASE)
                hi //= DECIMAL_BASE

        if not digits:
            digits.append(0)

        for i in range(len(digits) - 1):
            remain = digits[i]
            for _ in range(DECIMAL_SHIFT):
                decimal_string += str(remain % 10)
                remain //= 10

        remain = digits[-1]
        while remain != 0:
            decimal_string += str(remain % 10)
            remain //= 10

        if is_negative:
            decimal_string += "-"

        # Reverse the string to get the correct number
        decimal_string = decimal_string[::-1]
        return decimal_string if decimal_string else "0"


def get_discriminator_value(v: Any) -> str:
    return v.get("type").get("id")


class ValueTypeInfoChild_struct(BaseModel):
    first: str
    second: "AnyValueType"


class ValueTypeInfo_struct(BaseModel):
    child_types: list[ValueTypeInfoChild_struct]
    type: Literal["STRUCT_TYPE_INFO"] = "STRUCT_TYPE_INFO"
    alias: str | None = None


class ValueType_struct(BaseModel):
    id: Literal["STRUCT"] = "STRUCT"
    type_info: ValueTypeInfo_struct

    def sql(self) -> str:
        return (
            "STRUCT("
            + ",".join(
                [
                    f'"{child.first}" {child.second.sql()}'
                    for child in self.type_info.child_types
                ]
            )
            + ")"
        )


class ValueValue_struct(BaseModel):
    children: list["Value"]


class Value_struct(ValueBase):
    type: ValueType_struct
    value: ValueValue_struct

    def sql(self) -> str:
        names = [child.first for child in self.type.type_info.child_types]
        values = self.value.children
        return (
            "{"
            + ",".join(
                [
                    f"'{name}':" + value.sql()
                    for name, value in zip(names, values, strict=True)
                ]
            )
            + "}"
        )


class ValueTypeInfo_map(BaseModel):
    child_type: ValueType_struct
    type: Literal["LIST_TYPE_INFO"] = "LIST_TYPE_INFO"
    alias: str | None = None


class ValueType_map(BaseModel):
    id: Literal["MAP"] = "MAP"
    type_info: ValueTypeInfo_map

    def sql(self) -> str:
        return (
            "MAP("
            + ",".join(
                [
                    f"{child.second.sql()}"
                    for child in self.type_info.child_type.type_info.child_types
                ]
            )
            + ")"
        )


class ValueValue_map(BaseModel):
    children: list["Value"]


class Value_map(ValueBase):
    type: ValueType_map
    value: ValueValue_map

    def sql(self) -> str:
        pairs: list[str] = []
        for child in self.value.children:
            assert isinstance(child.value, ValueValue_struct)
            k, v = child.value.children
            pairs.append(f"{k.sql()}:{v.sql()}")

        return "MAP {" + ",".join(pairs) + "}"


AnyValueType = (
    ValueType_any
    | ValueType_boolean
    | ValueType_bigint
    | ValueType_bit
    | ValueType_blob
    | ValueType_date
    | ValueType_decimal
    | ValueType_double
    | ValueType_float
    | ValueType_hugeint
    | ValueType_integer
    | ValueType_interval
    | ValueType_list
    | ValueType_map
    | ValueType_null
    | ValueType_smallint
    | ValueType_struct
    | ValueType_time
    | ValueType_time_with_time_zone
    | ValueType_timestamp
    | ValueType_timestamp_with_time_zone
    | ValueType_timestamp_ms
    | ValueType_timestamp_ns
    | ValueType_timestamp_s
    | ValueType_tinyint
    | ValueType_ubigint
    | ValueType_uhugeint
    | ValueType_uinteger
    | ValueType_usmallint
    | ValueType_utinyint
    | ValueType_uuid
    | ValueType_varchar
    | ValueType_bignum
)


Value = Annotated[
    Annotated[Value_bigint, Tag("BIGINT")]
    | Annotated[Value_bit, Tag("BIT")]
    | Annotated[Value_blob, Tag("BLOB")]
    | Annotated[Value_boolean, Tag("BOOLEAN")]
    | Annotated[Value_date, Tag("DATE")]
    | Annotated[Value_decimal, Tag("DECIMAL")]
    | Annotated[Value_double, Tag("DOUBLE")]
    | Annotated[Value_float, Tag("FLOAT")]
    | Annotated[Value_hugeint, Tag("HUGEINT")]
    | Annotated[Value_integer, Tag("INTEGER")]
    | Annotated[Value_interval, Tag("INTERVAL")]
    | Annotated[Value_list, Tag("LIST")]
    | Annotated[Value_map, Tag("MAP")]
    | Annotated[Value_null, Tag("NULL")]
    | Annotated[Value_smallint, Tag("SMALLINT")]
    | Annotated[Value_struct, Tag("STRUCT")]
    | Annotated[Value_time, Tag("TIME")]
    | Annotated[Value_time_with_time_zone, Tag("TIME WITH TIME ZONE")]
    | Annotated[Value_timestamp, Tag("TIMESTAMP")]
    | Annotated[Value_timestamp_with_time_zone, Tag("TIMESTAMP WITH TIME ZONE")]
    | Annotated[Value_timestamp_ms, Tag("TIMESTAMP_MS")]
    | Annotated[Value_timestamp_ns, Tag("TIMESTAMP_NS")]
    | Annotated[Value_timestamp_s, Tag("TIMESTAMP_S")]
    | Annotated[Value_tinyint, Tag("TINYINT")]
    | Annotated[Value_ubigint, Tag("UBIGINT")]
    | Annotated[Value_uhugeint, Tag("UHUGEINT")]
    | Annotated[Value_uinteger, Tag("UINTEGER")]
    | Annotated[Value_usmallint, Tag("USMALLINT")]
    | Annotated[Value_utinyint, Tag("UTINYINT")]
    | Annotated[Value_uuid, Tag("UUID")]
    | Annotated[Value_varchar, Tag("VARCHAR")]
    | Annotated[Value_bignum, Tag("bignum")],
    Discriminator(get_discriminator_value),
]
