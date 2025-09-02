import pytest
from slate import Span

from zenith.markup import (
    zml,
    zml_get_spans,
    zml_alias,
    zml_macro,
    zml_pre_process,
    GLOBAL_CONTEXT,
)


def test_markup_str_parse():
    @zml_macro
    def upper(text: str) -> str:
        return text.upper()

    assert (
        zml("[bold underline 61]Hello [141 /bold]There")
        == "\x1b[38;5;61;1;4mHello \x1b[22m\x1b[38;5;141mThere\x1b[0m"
    )

    assert zml("[38]Hello [!upper]There") == "\x1b[38;5;38mHello THERE\x1b[0m"

    assert zml(
        "Click [141 underline ~https://google.com]me[61] and me[/~ / bold red] NOW"
    ) == (
        "Click \x1b]8;;https://google.com\x1b\\\x1b[38;5;141;4mme"
        + "\x1b]8;;https://google.com\x1b\\\x1b[38;5;61m and me\x1b[0m"
        + "\x1b]8;;\x1b\\\x1b[38;2;255;0;0;1m NOW\x1b[0m"
    )

    assert zml("The never-ending [~https://google.com]URI") == (
        "The never-ending \x1b]8;;https://google.com\x1b\\URI\x1b]8;;\x1b\\"
    ), repr(zml("The never-ending [~https://google.com]URI"))

    assert zml("[blue][@red]This is hard to parse") == (
        "\x1b[38;2;0;0;255;48;2;255;0;0mThis is hard to parse\x1b[0m"
    )


def test_markup_parse():
    assert list(zml_get_spans("[bold italic]Hello")) == [
        Span("Hello", bold=True, italic=True),
    ]

    assert list(zml_get_spans("[bold italic]Hello[/bold]Not bold")) == [
        Span("Hello", bold=True, italic=True),
        Span("Not bold", italic=True),
    ]


def test_markup_color():
    # 0-7 indexed colors
    assert list(zml_get_spans("[@0 1]Test[@1 0]Other")) == [
        Span("Test", background="40", foreground="31"),
        Span("Other", background="41", foreground="30"),
    ]

    # 8-15 indexed colors
    assert list(zml_get_spans("[@9 15]Test[@14 10]Other")) == [
        Span("Test", background="101", foreground="97"),
        Span("Other", background="106", foreground="92"),
    ]

    # 16-256 indexed colors
    assert list(zml_get_spans("[@141 61]Test[@54 78]Other")) == [
        Span("Test", background="48;5;141", foreground="38;5;61"),
        Span("Other", background="48;5;54", foreground="38;5;78"),
    ]

    # OOB indexed color
    with pytest.raises(ValueError):
        list(zml_get_spans("[@333 231]Please don't parse..."))

    # CSS colors
    assert list(zml_get_spans("[@lavender cadetblue]Pretty colors")) == [
        Span(
            "Pretty colors", foreground="38;2;95;158;160", background="48;2;230;230;250"
        )
    ]

    # HEX colors
    assert list(zml_get_spans("[@#212121 #dedede]Nice contrast")) == [
        Span("Nice contrast", foreground="38;2;222;222;222", background="48;2;33;33;33")
    ]

    # RGB colors
    assert list(zml_get_spans("[@11;22;123 123;22;11]What even are these colors")) == [
        Span(
            "What even are these colors",
            foreground="38;2;123;22;11",
            background="48;2;11;22;123",
        )
    ]


def test_markup_auto_foreground():
    assert list(zml_get_spans("[@#FFFFFF]test")) == [
        Span("test", background="48;2;255;255;255", foreground="38;2;35;35;35")
    ]

    assert list(zml_get_spans("[@0]White[@7]Black[@160]White[@116]Black")) == [
        Span("White", background="40", foreground="38;2;245;245;245"),
        Span("Black", background="47", foreground="38;2;35;35;35"),
        Span("White", background="48;5;160", foreground="38;2;245;245;245"),
        Span("Black", background="48;5;116", foreground="38;2;35;35;35"),
    ]


def test_markup_macros():
    @zml_macro
    def upper(text: str) -> str:
        return text.upper()

    @zml_macro
    def conceal(text: str) -> str:
        return "*" * (len(text) - 1) + text[-1]

    assert (
        zml_pre_process("[!upper 141]Test[/!upper /fg !conceal bold]other test")
        == "[141]TEST[/fg bold]*********t"
    )

    with pytest.raises(ValueError):
        zml_pre_process("[!undefined]Test")

    with pytest.raises(ValueError):
        zml_pre_process("[undefined]Test")

    with pytest.raises(ValueError):
        zml_pre_process("[/!upper]Test")


def test_markup_aliases():
    zml_alias(a="b", test="141 bold")

    assert zml_pre_process("[test italic]What is this?") == (
        "[141 bold italic]What is this?"
    )

    @zml_macro
    def upper(text: str) -> str:
        return text.upper()

    zml_alias(complex_with_macro="!upper lavender")

    assert zml_pre_process("[complex-with-macro]test") == "[lavender]TEST"

    zml_alias(complex_with_hyperlink="~https://google.com underline slategray")

    assert (
        zml_pre_process("[complex-with-hyperlink]test")
        == "[~https://google.com underline slategray]test"
    )


def test_markup_hyperlink():
    assert list(
        zml_get_spans("[~https://google.com]Test [bold]me [/~]no more link")
    ) == [
        Span("Test ", hyperlink="https://google.com"),
        Span("me ", bold=True, hyperlink="https://google.com"),
        Span("no more link", bold=True),
    ]


def test_markup_parse_plain():
    assert list(zml_get_spans("Test")) == [Span("Test")]
