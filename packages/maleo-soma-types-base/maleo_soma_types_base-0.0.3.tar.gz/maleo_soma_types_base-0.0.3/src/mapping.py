from typing import Any, List, Mapping, Optional, Sequence, TypeVar
from .string import ListOfStrings, SequenceOfStrings


KeyT = TypeVar("KeyT")
ValueT = TypeVar("ValueT")


# Generic
OptionalMapping = Optional[Mapping[KeyT, ValueT]]
ListOfMappings = List[Mapping[KeyT, ValueT]]
OptionalListOfMappings = Optional[ListOfMappings[KeyT, ValueT]]
SequenceOfMappings = Sequence[Mapping[KeyT, ValueT]]
OptionalSequenceOfMappings = Optional[SequenceOfMappings[KeyT, ValueT]]


# String key
# Any value
StringToAnyMapping = Mapping[str, Any]
OptionalStringToAnyMapping = Optional[StringToAnyMapping]
ListOfStringToAnyMapping = List[StringToAnyMapping]
OptionalListOfStringToAnyMapping = Optional[ListOfStringToAnyMapping]
SequenceOfStringToAnyMapping = Sequence[StringToAnyMapping]
OptionalSequenceOfStringToAnyMapping = Optional[SequenceOfStringToAnyMapping]

# Object value
StringToObjectMapping = Mapping[str, object]
OptionalStringToObjectMapping = Optional[StringToObjectMapping]
ListOfStringToObjectMapping = List[StringToObjectMapping]
OptionalListOfStringToObjectMapping = Optional[ListOfStringToObjectMapping]
SequenceOfStringToObjectMapping = Sequence[StringToObjectMapping]
OptionalSequenceOfStringToObjectMapping = Optional[SequenceOfStringToObjectMapping]

# String value
StringToStringMapping = Mapping[str, str]
OptionalStringToStringMapping = Optional[StringToStringMapping]
ListOfStringToStringMapping = List[StringToStringMapping]
OptionalListOfStringToStringMapping = Optional[ListOfStringToStringMapping]
SequenceOfStringToStringMapping = Sequence[StringToStringMapping]
OptionalSequenceOfStringToStringMapping = Optional[SequenceOfStringToStringMapping]

# Multi-String value
StringToListOfStringsMapping = Mapping[str, ListOfStrings]
OptionalStringToListOfStringsMapping = Optional[StringToListOfStringsMapping]
StringToSequenceOfStringsMapping = Mapping[str, SequenceOfStrings]
OptionalStringToSequenceOfStringsMapping = Optional[StringToSequenceOfStringsMapping]

# Integer key
# Any value
IntToAnyMapping = Mapping[int, Any]
OptionalIntToAnyMapping = Optional[IntToAnyMapping]
ListOfIntToAnyMapping = List[IntToAnyMapping]
OptionalListOfIntToAnyMapping = Optional[ListOfIntToAnyMapping]
SequenceOfIntToAnyMapping = Sequence[IntToAnyMapping]
OptionalSequenceOfIntToAnyMapping = Optional[SequenceOfIntToAnyMapping]

# String value
IntToStringMapping = Mapping[int, str]
OptionalIntToStringMapping = Optional[IntToStringMapping]
ListOfIntToStringMapping = List[IntToStringMapping]
OptionalListOfIntToStringMapping = Optional[ListOfIntToStringMapping]
SequenceOfIntToStringMapping = Sequence[IntToStringMapping]
OptionalSequenceOfIntToStringMapping = Optional[SequenceOfIntToStringMapping]
