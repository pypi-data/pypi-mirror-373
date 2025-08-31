# noqa: INP001
import sys
from typing import Union

from ozi_build.regexploit._char import Character  # noqa: TC001
from ozi_build.regexploit._repeat import Repeat  # noqa: TC001
from ozi_build.regexploit._sre import SreOpParser

if sys.version_info < (3, 11):
    import sre_parse as _parser
else:
    from re import _parser


def from_regex(pattern: str) -> Union[Repeat, Character]:
    (parsed_char,) = _parser.parse(pattern)
    repeat = SreOpParser().parse_op(*parsed_char)
    return repeat


def test_star():
    r = from_regex(r"(abc)*")
    assert r.starriness == 1
    assert r.minimum_length == 0
    assert r.exact_character_class() is None


def test_question():
    r = from_regex(r"(abc)?")
    assert r.starriness == 0
    assert r.minimum_length == 0
    assert r.maximum_repeats == 1
    assert r.exact_character_class() is None


def test_plus():
    r = from_regex(r"(?:abc)+")
    assert r.starriness == 1
    assert r.minimum_length == 3
    assert r.exact_character_class() is None


def test_character_class():
    r = from_regex(r"a{4,}")
    assert r.starriness == 1
    assert r.minimum_length == 4
    assert r.exact_character_class() == from_regex(r"a")


def test_subsequence_character_class():
    r = from_regex(r"(a?b+)*")
    assert r.starriness == 11
    assert r.minimum_length == 0
    assert r.exact_character_class() is None
    assert r.overall_character_class() is None
    inner_repeats = list(r.repeat.matching_repeats())
    assert len(inner_repeats) == 1
    assert inner_repeats[0].overall_character_class() == from_regex(r"b")


def test_negative_lookahead_infinite():
    r = SreOpParser().parse_sre(r"(?!b)[a-d]+")
    assert r == SreOpParser().parse_sre(r"[acd][a-d]*")


def test_negative_lookahead_finite():
    r = SreOpParser().parse_sre(r"(?!b)[a-d]{1,3}")
    assert r == SreOpParser().parse_sre(r"[acd][a-d]{0,2}")


def test_exponential_starriness():
    r = from_regex(r"(?:(?:a{4,})*)+")
    assert r.starriness == 111  # ((1 * 10) * 10) + 1
    assert r.minimum_length == 0
    assert r.exact_character_class() == from_regex(r"a")


def test_exponential_starriness2():
    r = from_regex(r"(?:(?:a{4,}bc+)*)+")
    assert r.starriness == 211  # ((2 * 10) * 10) + 1
    assert r.minimum_length == 0
    assert r.exact_character_class() is None
