from typing import Any, Dict, List, Optional, Sequence, TypeVar
from .string import ListOfStrings, SequenceOfStrings


KeyT = TypeVar("KeyT")
ValueT = TypeVar("ValueT")


# Generic
OptionalDict = Optional[Dict[KeyT, ValueT]]
ListOfDicts = List[Dict[KeyT, ValueT]]
OptionalListOfDicts = Optional[ListOfDicts[KeyT, ValueT]]
SequenceOfDicts = Sequence[Dict[KeyT, ValueT]]
OptionalSequenceOfDicts = Optional[SequenceOfDicts[KeyT, ValueT]]

# String key
# Any value
StringToAnyDict = Dict[str, Any]
OptionalStringToAnyDict = Optional[StringToAnyDict]
ListOfStringToAnyDict = List[StringToAnyDict]
OptionalListOfStringToAnyDict = Optional[ListOfStringToAnyDict]
SequenceOfStringToAnyDict = Sequence[StringToAnyDict]
OptionalSequenceOfStringToAnyDict = Optional[SequenceOfStringToAnyDict]

# Object value
StringToObjectDict = Dict[str, object]
OptionalStringToObjectDict = Optional[StringToObjectDict]
ListOfStringToObjectDict = List[StringToObjectDict]
OptionalListOfStringToObjectDict = Optional[ListOfStringToObjectDict]
SequenceOfStringToObjectDict = Sequence[StringToObjectDict]
OptionalSequenceOfStringToObjectDict = Optional[SequenceOfStringToObjectDict]

# String value
StringToStringDict = Dict[str, str]
OptionalStringToStringDict = Optional[StringToStringDict]
ListOfStringToStringDict = List[StringToStringDict]
OptionalListOfStringToStringDict = Optional[ListOfStringToStringDict]
SequenceOfStringToStringDict = Sequence[StringToStringDict]
OptionalSequenceOfStringToStringDict = Optional[SequenceOfStringToStringDict]

# Multi-String value
StringToListOfStringsDict = Dict[str, ListOfStrings]
OptionalStringToListOfStringsDict = Optional[StringToListOfStringsDict]
StringToSequenceOfStringsDict = Dict[str, SequenceOfStrings]
OptionalStringToSequenceOfStringsDict = Optional[StringToSequenceOfStringsDict]

# Integer key
# Any value
IntToAnyDict = Dict[int, Any]
OptionalIntToAnyDict = Optional[IntToAnyDict]
ListOfIntToAnyDict = List[IntToAnyDict]
OptionalListOfIntToAnyDict = Optional[ListOfIntToAnyDict]
SequenceOfIntToAnyDict = Sequence[IntToAnyDict]
OptionalSequenceOfIntToAnyDict = Optional[SequenceOfIntToAnyDict]

# String value
IntToStringDict = Dict[int, str]
OptionalIntToStringDict = Optional[IntToStringDict]
ListOfIntToStringDict = List[IntToStringDict]
OptionalListOfIntToStringDict = Optional[ListOfIntToStringDict]
SequenceOfIntToStringDict = Sequence[IntToStringDict]
OptionalSequenceOfIntToStringDict = Optional[SequenceOfIntToStringDict]
