from typing import Optional, Union
from .any import ListOfAny, SequenceOfAny
from .dict import StringToAnyDict
from .mapping import StringToAnyMapping


BytesOrString = Union[bytes, str]
OptionalBytesOrString = Optional[BytesOrString]

ListOrStringDictOfAny = Union[ListOfAny, StringToAnyDict]
OptionalListOrStringDictOfAny = Optional[ListOrStringDictOfAny]
SequenceOrStringDictOfAny = Union[SequenceOfAny, StringToAnyDict]
OptionalSequenceOrStringDictOfAny = Optional[Union[SequenceOfAny, StringToAnyDict]]

ListOrStringMappingOfAny = Union[ListOfAny, StringToAnyMapping]
OptionalListOrStringMappingOfAny = Optional[Union[ListOfAny, StringToAnyMapping]]
SequenceOrStringMappingOfAny = Union[SequenceOfAny, StringToAnyMapping]
OptionalSequenceOrStringMappingOfAny = Optional[
    Union[SequenceOfAny, StringToAnyMapping]
]
