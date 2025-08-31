# Copyright © 2025 GlacieTeam. All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not
# distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# SPDX-License-Identifier: MPL-2.0

from bedrock_protocol.nbt._internal.native_library import get_library_handle
from bedrock_protocol.nbt.tag import Tag
from bedrock_protocol.nbt.byte_tag import ByteTag
from bedrock_protocol.nbt.short_tag import ShortTag
from bedrock_protocol.nbt.int_tag import IntTag
from bedrock_protocol.nbt.int64_tag import Int64Tag
from bedrock_protocol.nbt.float_tag import FloatTag
from bedrock_protocol.nbt.double_tag import DoubleTag
from bedrock_protocol.nbt.byte_array_tag import ByteArrayTag
from bedrock_protocol.nbt.string_tag import StringTag
from bedrock_protocol.nbt.list_tag import ListTag
from bedrock_protocol.nbt.int_array_tag import IntArrayTag
from bedrock_protocol.nbt.long_array_tag import LongArrayTag
from bedrock_protocol.nbt.compound_tag_variant import CompoundTagVariant
from bedrock_protocol.nbt.tag_type import TagType
from typing import Any, List, Optional, Union, Dict
import ctypes


class CompoundTag(Tag):
    """CompoundTag

    A Tag contains map of tags
    """

    def __init__(self, tag_map: Optional[Dict[str, Any]] = None):
        """Create a CompoundTag"""
        self._lib_handle = get_library_handle()
        self._tag_handle = self._lib_handle.nbt_compound_tag_create()
        self.set_tag_map(tag_map)

    def __getitem__(self, key: str) -> CompoundTagVariant:
        """Get a tag in the CompoundTag
        Args:
            key: the key of the tag
        Returns:
            None if failed
        """
        if not self.contains(key):
            self.put(key, CompoundTag())
        return CompoundTagVariant(self, self.get(key), key)

    def __setitem__(self, key: str, value: Tag) -> bool:
        """Set a tag in the CompoundTag
        Args:
            key: the key of the tag
            value: new tag to set
        Returns:
            True if succeed
        """
        return self.put(key, value)

    def __delitem__(self, key: str) -> bool:
        """Delete value from the CompoundTag
        Args:
            key: the key of the tag
        Returns:
            True if pop succeed
        """
        return self.pop(key)

    def __contains__(self, key: str) -> bool:
        """check the CompoundTag contains a key-value
        Returns:
            True if contains
        """
        return self.contains(key)

    def size(self) -> int:
        """Get size of the CompoundTag
        Returns:
            size
        """
        return self._lib_handle.nbt_compound_tag_size(self._tag_handle)

    def contains(self, key: str) -> bool:
        """check the CompoundTag contains a key-value
        Returns:
            True if contains
        """
        return self._lib_handle.nbt_compound_tag_has_tag(
            self._tag_handle, key.encode("utf-8")
        )

    def pop(self, key: str) -> bool:
        """Delete value from the CompoundTag
        Args:
            key: the key of the tag
        Returns:
            True if pop succeed
        """
        return self._lib_handle.nbt_compound_tag_remove_tag(
            self._tag_handle, key.encode("utf-8")
        )

    def put(self, key: str, val: Any) -> bool:
        """Set a tag in the CompoundTag
        Args:
            key: the key of the tag
            value: new tag to set
        Returns:
            True if succeed
        """
        if isinstance(val, Tag):
            value = val
        else:
            if isinstance(val, dict):
                value = CompoundTag(val)
            elif isinstance(val, list):
                value = ListTag(val)
            elif isinstance(val, (bool, ctypes.c_uint8)):
                value = ByteTag(val)
            elif isinstance(val, ctypes.c_int16):
                value = ShortTag(val)
            elif isinstance(val, (int, ctypes.c_int32)):
                value = IntTag(val)
            elif isinstance(val, (int, ctypes.c_int64)):
                value = Int64Tag(val)
            elif isinstance(val, (float, ctypes.c_float)):
                value = FloatTag(val)
            elif isinstance(val, ctypes.c_double):
                value = DoubleTag(val)
            elif isinstance(val, str):
                value = StringTag(val)
            elif isinstance(val, (bytes, bytearray)):
                value = ByteArrayTag(val)
            else:
                raise TypeError("Wrong type of argument")
        return self._lib_handle.nbt_compound_tag_set_tag(
            self._tag_handle, key.encode("utf-8"), value._tag_handle
        )

    def get(self, key: str) -> Optional[Tag]:
        """Get a tag in the CompoundTag
        Args:
            key: the key of the tag
        Returns:
            None if failed
        """
        handle = self._lib_handle.nbt_compound_tag_get_tag(
            self._tag_handle, key.encode("utf-8")
        )
        if handle is not None:
            return Tag._Tag__create_tag_by_handle(handle)
        return None

    def set_tag_map(self, tag_map: Dict[str, Any]) -> None:
        """Set the tag map
        Args:
            key: the key of the tag
            value: new tag to set
        Returns:
            True if succeed
        """
        if tag_map is not None:
            for key, val in tag_map.items():
                self.put(key, val)

    def get_tag_map(self) -> Optional[Dict[str, Tag]]:
        """Get the tag map
        Args:
            key: the key of the tag
        Returns:
            None if failed
        """
        result = dict()
        for index in range(self.size()):
            keybuf = self._lib_handle.nbt_compound_tag_get_key_index(
                self._tag_handle, index
            )
            keybytes = bytes(ctypes.string_at(keybuf.data, keybuf.size))
            self._lib_handle.nbtio_buffer_destroy(ctypes.byref(keybuf))
            key = keybytes.decode("utf-8")
            val = Tag._Tag__create_tag_by_handle(
                self._lib_handle.nbt_compound_tag_get_tag_index(self._tag_handle, index)
            )
            result[key] = val
        return result

    def clear(self) -> None:
        """Clear all tags in the CompoundTag"""
        self._lib_handle.nbt_compound_tag_clear(self._tag_handle)

    def merge(self, other: "CompoundTag", merge_list: bool = False) -> None:
        for key, val in other.get_tag_map().items():
            if self.contains(key):
                if (
                    self.get(key).get_type() == TagType.Compound
                    and val.get_type() == TagType.Compound
                ):
                    object: CompoundTag = self.get(key)
                    object.merge(val, merge_list)
                    self.put(key, object)
                    continue
                elif (
                    self.get(key).get_type() == TagType.List
                    and val.get_type() == TagType.List
                    and merge_list
                ):
                    array: ListTag = self.get(key)
                    array.merge(val)
                    self.put(key, array)
                    continue
            self.put(key, val)

    def put_byte(self, key: str, value: int) -> None:
        """Put a ByteTag in this CompoundTag
        Args:
            key: the key of the tag
            value: the byte value
        """
        self.put(key, ByteTag(value))

    def get_byte(self, key: str) -> Optional[int]:
        """Get a ByteTag's value in this CompoundTag
        Args:
            key: the key of the tag
        Returns:
            the byte value
        """
        tag = self.get(key)
        if tag is not None:
            return tag.get()
        return None

    def put_short(self, key: str, value: int) -> None:
        """Put a ShortTag in this CompoundTag
        Args:
            key: the key of the tag
            value: the short value
        """
        self.put(key, ShortTag(value))

    def get_short(self, key: str) -> Optional[int]:
        """Get a ShortTag's value in this CompoundTag
        Args:
            key: the key of the tag
        Returns:
            the short value
        """
        tag = self.get(key)
        if tag is not None:
            return tag.get()
        return None

    def put_int(self, key: str, value: int) -> None:
        """Put a IntTag in this CompoundTag
        Args:
            key: the key of the tag
            value: the int value
        """
        self.put(key, IntTag(value))

    def get_int(self, key: str) -> Optional[int]:
        """Get a IntTag's value in this CompoundTag
        Args:
            key: the key of the tag
        Returns:
            the int value
        """
        tag = self.get(key)
        if tag is not None:
            return tag.get()
        return None

    def put_int64(self, key: str, value: int) -> None:
        """Put a Int64Tag in this CompoundTag
        Args:
            key: the key of the tag
            value: the int64 value
        """
        self.put(key, Int64Tag(value))

    def get_int64(self, key: str) -> Optional[int]:
        """Get a Int64Tag's value in this CompoundTag
        Args:
            key: the key of the tag
        Returns:
            the int64 value
        """
        tag = self.get(key)
        if tag is not None:
            return tag.get()
        return None

    def put_float(self, key: str, value: float) -> None:
        """Put a FloatTag in this CompoundTag
        Args:
            key: the key of the tag
            value: the float value
        """
        self.put(key, FloatTag(value))

    def get_float(self, key: str) -> Optional[float]:
        """Get a FloatTag's value in this CompoundTag
        Args:
            key: the key of the tag
        Returns:
            the float value
        """
        tag = self.get(key)
        if tag is not None:
            return tag.get()
        return None

    def put_double(self, key: str, value: float) -> None:
        """Put a DoubleTag in this CompoundTag
        Args:
            key: the key of the tag
            value: the double value
        """
        self.put(key, DoubleTag(value))

    def get_double(self, key: str) -> Optional[float]:
        """Get a DoubleTag's value in this CompoundTag
        Args:
            key: the key of the tag
        Returns:
            the double value
        """
        tag = self.get(key)
        if tag is not None:
            return tag.get()
        return None

    def put_byte_array(self, key: str, value: Union[bytearray, bytes]) -> None:
        """Put a ByteArrayTag in this CompoundTag
        Args:
            key: the key of the tag
            value: the byte array value
        """
        self.put(key, ByteArrayTag(value))

    def get_byte_array(self, key: str) -> Optional[bytes]:
        """Get a ByteArrayTag's value in this CompoundTag
        Args:
            key: the key of the tag
        Returns:
            the byte array value
        """
        tag = self.get(key)
        if tag is not None:
            return tag.get()
        return None

    def put_string(self, key: str, value: str) -> None:
        """Put a StringTag in this CompoundTag
        Args:
            key: the key of the tag
            value: the string value
        """
        self.put(key, StringTag(value))

    def get_string(self, key: str) -> Optional[str]:
        """Get a StringTag's value in this CompoundTag
        Args:
            key: the key of the tag
        Returns:
            the string value
        """
        tag = self.get(key)
        if tag is not None:
            return tag.get_str()
        return None

    def put_binary_string(self, key: str, value: Union[bytearray, bytes]) -> None:
        """Put a StringTag in this CompoundTag
        Args:
            key: the key of the tag
            value: the binary value
        """
        self.put(key, StringTag(value))

    def get_binary_string(self, key: str) -> Optional[bytes]:
        """Get a StringTag's value in this CompoundTag
        Args:
            key: the key of the tag
        Returns:
            the binary value
        """
        tag = self.get(key)
        if tag is not None:
            return tag.get()
        return None

    def put_compound(self, key: str, value: Dict[str, Tag]) -> None:
        """Put a CompoundTag in this CompoundTag
        Args:
            key: the key of the tag
            value: the CompoundTag
        """
        self.put(key, CompoundTag(value))

    def get_compound(self, key: str) -> Optional[Dict[str, Tag]]:
        """Get a CompoundTag in this CompoundTag
        Args:
            key: the key of the tag
        Returns:
            the CompoundTag
        """
        return self.get(key).get_tag_map()

    def put_list(self, key: str, value: List[Tag]) -> None:
        """Put a ListTag in this CompoundTag
        Args:
            key: the key of the tag
            value: the tag list
        """
        self.put(key, ListTag(value))

    def get_list(self, key: str) -> Optional[List[Tag]]:
        """Get a ListTag's value in this CompoundTag
        Args:
            key: the key of the tag
        Returns:
            the tag list
        """
        tag = self.get(key)
        if tag is not None:
            return tag.get_list()
        return None

    def put_int_array(self, key: str, value: List[int]) -> None:
        """Put a IntArrayTag in this CompoundTag
        Args:
            key: the key of the tag
            value: the int array
        """
        self.put(key, IntArrayTag(value))

    def get_int_array(self, key: str) -> Optional[List[int]]:
        """Get a IntArrayTag's value in this CompoundTag
        Args:
            key: the key of the tag
        Returns:
            the tag int array
        """
        tag = self.get(key)
        if tag is not None:
            return tag.get_list()
        return None

    def put_long_array(self, key: str, value: List[int]) -> None:
        """Put a LongArrayTag in this CompoundTag
        Args:
            key: the key of the tag
            value: the long array
        """
        self.put(key, LongArrayTag(value))

    def get_long_array(self, key: str) -> Optional[List[int]]:
        """Get a LongArrayTag's value in this CompoundTag
        Args:
            key: the key of the tag
        Returns:
            the tag long array
        """
        tag = self.get(key)
        if tag is not None:
            return tag.get_list()
        return None

    def write(self, stream: Any) -> None:
        """Serialize NBT into a BinaryStream in network NBT format
        Args:
            BinaryStream: output stream

        Warning:
            Requires package 'bedrock-protocol-binarystream' to be installed
            stream must be a instance of bedrock_protocol.binarystream.BinaryStream
        """
        stream.write_byte(TagType.Compound)
        stream.write_byte(0)
        self._lib_handle.nbt_any_tag_write(self._tag_handle, stream._stream_handle)

    def read(self, stream: Any) -> None:
        """Deserialize NBT from a ReadOnlyBinaryStream in network NBT format
        Args:
            ReadOnlyBinaryStream: input stream

        Warning:
            Requires package 'bedrock-protocol-binarystream' to be installed
            stream must be a instance of bedrock_protocol.binarystream.ReadOnlyBinaryStream
        """
        stream.ignore_bytes(2)
        self._lib_handle.nbt_any_tag_load(self._tag_handle, stream._stream_handle)

    def to_binary_nbt(self, little_endian: bool = True) -> bytes:
        """Encode the CompoundTag to binary NBT format
        Args:
            little_endian: whether use little-endian bytes order
        Returns:
            serialized bytes
        """
        buffer = self._lib_handle.nbt_compound_tag_to_binary_nbt(
            self._tag_handle, little_endian, False
        )
        result = bytes(ctypes.string_at(buffer.data, buffer.size))
        self._lib_handle.nbtio_buffer_destroy(ctypes.byref(buffer))
        return result

    def to_binary_nbt_with_header(self, little_endian: bool = True) -> bytes:
        """Encode the CompoundTag to binary NBT with header format
        Args:
            little_endian: whether use little-endian bytes order
        Returns:
            serialized bytes
        """
        buffer = self._lib_handle.nbt_compound_tag_to_binary_nbt(
            self._tag_handle, little_endian, True
        )
        result = bytes(ctypes.string_at(buffer.data, buffer.size))
        self._lib_handle.nbtio_buffer_destroy(ctypes.byref(buffer))
        return result

    def to_network_nbt(self) -> bytes:
        """Encode the CompoundTag to network NBT format
        Returns:
            serialized bytes
        """
        buffer = self._lib_handle.nbt_compound_tag_to_network_nbt(self._tag_handle)
        result = bytes(ctypes.string_at(buffer.data, buffer.size))
        self._lib_handle.nbtio_buffer_destroy(ctypes.byref(buffer))
        return result

    @staticmethod
    def from_binary_nbt(
        content: bytes, little_endian: bool = True
    ) -> Optional["CompoundTag"]:
        """Parse binary NBT
        Args:
            little_endian: whether use little-endian bytes order
        Returns:
            CompoundTag
        """
        length = len(content)
        char_ptr = ctypes.c_char_p(content)
        buf = ctypes.cast(char_ptr, ctypes.POINTER(ctypes.c_uint8 * length))
        handle = get_library_handle().nbt_compound_tag_from_binary_nbt(
            ctypes.cast(buf, ctypes.POINTER(ctypes.c_uint8)),
            length,
            little_endian,
            False,
        )
        if handle is not None:
            return Tag._Tag__create_tag_by_handle(handle)
        return None

    @staticmethod
    def from_binary_nbt_with_header(
        content: bytes, little_endian: bool = True
    ) -> Optional["CompoundTag"]:
        """Parse binary NBT with header
        Args:
            little_endian: whether use little-endian bytes order
        Returns:
            CompoundTag
        """
        length = len(content)
        char_ptr = ctypes.c_char_p(content)
        buf = ctypes.cast(char_ptr, ctypes.POINTER(ctypes.c_uint8 * length))
        handle = get_library_handle().nbt_compound_tag_from_binary_nbt(
            ctypes.cast(buf, ctypes.POINTER(ctypes.c_uint8)),
            length,
            little_endian,
            True,
        )
        if handle is not None:
            return Tag._Tag__create_tag_by_handle(handle)
        return None

    @staticmethod
    def from_network_nbt(content: bytes) -> Optional["CompoundTag"]:
        """Parse network NBT
        Returns:
            CompoundTag
        """
        length = len(content)
        char_ptr = ctypes.c_char_p(content)
        buf = ctypes.cast(char_ptr, ctypes.POINTER(ctypes.c_uint8 * length))
        handle = get_library_handle().nbt_compound_tag_from_network_nbt(
            ctypes.cast(buf, ctypes.POINTER(ctypes.c_uint8)), length
        )
        if handle is not None:
            return Tag._Tag__create_tag_by_handle(handle)
        return None

    @staticmethod
    def from_snbt(content: str) -> Optional["CompoundTag"]:
        """Parse SNBT
        Returns:
            CompoundTag or None
        """
        value = content.encode("utf-8")
        length = len(value)
        char_ptr = ctypes.c_char_p(value)
        buf = ctypes.cast(char_ptr, ctypes.POINTER(ctypes.c_uint8 * length))
        handle = get_library_handle().nbt_compound_tag_from_snbt(
            ctypes.cast(buf, ctypes.POINTER(ctypes.c_uint8)), length
        )
        if handle is not None:
            return Tag._Tag__create_tag_by_handle(handle)
        return None
