from pytest import mark, raises

from seedcase_sprout.internals import _get_nested_attr


class D:
    none: str | None = None
    Number_1: int = 123


d = D()


class C:
    d: D = d


c = C()


class B:
    c: C = c


b = B()


class A:
    b: B = b


a = A()


@mark.parametrize(
    "nested_object,attributes,expected",
    [
        (a, "b.c.d", d),
        (a, "b.c", c),
        (a, "b", b),
        (b, "c.d", d),
        (c, "d", d),
        (d, "Number_1", 123),
        (d, "none", None),
        (a, "a", None),
        (a, "e", None),
        (a, "b.c.d.e", None),
        (a, "b.e.f.g", None),
        (a, "b.c.d.e.f.g.h", None),
    ],
)
def test_gets_nested_attribute(nested_object, attributes, expected):
    """Should resolve an attribute chain and return the correct value."""
    assert _get_nested_attr(nested_object, attributes) == expected


def test_returns_default_if_attribute_not_found():
    """Should return the default value when the attribute chain cannot be resolved."""
    assert _get_nested_attr(a, "e", default="default") == "default"


def test_returns_default_if_attribute_is_none():
    """Should return the default value when the attribute exists and is None."""
    assert _get_nested_attr(d, "none", default="default") == "default"


def test_ignores_default_if_attribute_found():
    """Should ignore the default value when the attribute chain can be resolved."""
    assert _get_nested_attr(d, "Number_1", default=456) == 123


@mark.parametrize(
    "attributes",
    [
        "",
        ".",
        "...",
        ".b",
        "...b",
        "b.",
        "b...",
        ".b.",
        ".b.c.d",
        "b..c",
        ".b.c.d.",
        "b,c,d",
        "$",
        "1",
    ],
)
def test_throws_error_if_attribute_not_identifier(attributes):
    """Should throw `ValueError` if the input doesn't contain valid identifiers."""
    with raises(ValueError):
        _get_nested_attr(a, attributes)
