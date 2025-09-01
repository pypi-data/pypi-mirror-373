# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from enum import Enum
from typing import Iterable, Text
from unicodedata import category


class UnicodeCharacterTypes(Enum):
    """Classification of Unicode characters for identifier construction."""
    LETTER_OR_UNDERSCORE = 1
    DECIMAL_DIGIT = 2
    SPACE_OR_CONTROL = 3
    OTHER = 4


def get_unicode_character_type(unicode_character):
    # type: (Text) -> UnicodeCharacterTypes
    """
    Classifies a Unicode character into identifier-friendly types.

    Args:
        unicode_character (Text): The Unicode character to classify.

    Returns:
        UnicodeCharacterTypes: The classification.
    """
    unicode_character_category = category(unicode_character)

    if unicode_character_category.startswith('L') or unicode_character == u'_':
        return UnicodeCharacterTypes.LETTER_OR_UNDERSCORE
    elif unicode_character_category == 'Nd':
        return UnicodeCharacterTypes.DECIMAL_DIGIT
    elif unicode_character_category.startswith('Z') or unicode_character_category == 'Cc':
        return UnicodeCharacterTypes.SPACE_OR_CONTROL
    else:
        return UnicodeCharacterTypes.OTHER


class States(Enum):
    """Finite-state machine states for the text-to-identifier converter.

    Values:
        START: Initial state, before any sub-identifier detected.
        AFTER_SUB_IDENTIFIER: Currently building or after a valid identifier run.
        AFTER_SPACE_CONTROL_SEQUENCE: After a whitespace or control character run.
    """
    START = 1
    AFTER_SUB_IDENTIFIER = 2
    AFTER_SPACE_CONTROL_SEQUENCE = 3


def text_to_unicode_characters_in_identifier(text):
    # type: (Text) -> Iterable[Text]
    """Yield a sequence of Unicode characters that forms a valid Python identifier from input text.

    Implements a state machine that:
    - Prepends an underscore if the identifier must start with a non-letter.
    - Collapses runs of whitespace/control characters to single underscores.
    - Converts illegal identifier characters to underscores, doubling for non-space runs after spaces.

    Args:
        text (Text): The arbitrary text to convert.

    Yields:
        Text: Individual Unicode characters forming a valid identifier.
    """
    state = States.START
    for c in text:
        c_type = get_unicode_character_type(c)
        if state == States.START:
            if c_type == UnicodeCharacterTypes.LETTER_OR_UNDERSCORE:
                yield c
                state = States.AFTER_SUB_IDENTIFIER
            elif c_type == UnicodeCharacterTypes.DECIMAL_DIGIT:
                yield u'_'
                yield c
                state = States.AFTER_SUB_IDENTIFIER
            elif c_type == UnicodeCharacterTypes.SPACE_OR_CONTROL:
                state = States.AFTER_SPACE_CONTROL_SEQUENCE
            else:
                yield u'_'
                state = States.AFTER_SUB_IDENTIFIER
        elif state == States.AFTER_SUB_IDENTIFIER:
            if c_type == UnicodeCharacterTypes.LETTER_OR_UNDERSCORE or c_type == UnicodeCharacterTypes.DECIMAL_DIGIT:
                yield c
                state = States.AFTER_SUB_IDENTIFIER
            elif c_type == UnicodeCharacterTypes.SPACE_OR_CONTROL:
                state = States.AFTER_SPACE_CONTROL_SEQUENCE
            else:
                yield u'_'
                state = States.AFTER_SUB_IDENTIFIER
        else:
            if c_type == UnicodeCharacterTypes.LETTER_OR_UNDERSCORE or c_type == UnicodeCharacterTypes.DECIMAL_DIGIT:
                yield u'_'
                yield c
                state = States.AFTER_SUB_IDENTIFIER
            elif c_type == UnicodeCharacterTypes.SPACE_OR_CONTROL:
                state = States.AFTER_SPACE_CONTROL_SEQUENCE
            else:
                yield u'_'
                yield u'_'
                state = States.AFTER_SUB_IDENTIFIER

    if state != States.AFTER_SUB_IDENTIFIER:
        yield u'_'


def text_to_identifier(text):
    # type: (Text) -> Text
    """Convert arbitrary text to a valid Python identifier.

    Args:
        text (Text): Arbitrary input string.

    Returns:
        Text: A valid Python identifier representing the input.
    """
    return u''.join(text_to_unicode_characters_in_identifier(text))
