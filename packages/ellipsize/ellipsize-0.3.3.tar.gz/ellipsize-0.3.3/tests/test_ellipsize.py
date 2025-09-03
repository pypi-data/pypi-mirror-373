from ellipsize.ellipsize import Dots, ellipsize, format_ellipsized, print_ellipsized


def test_ellipsize():
    a = [1, 2, 3]
    assert ellipsize(a, max_items_to_show=10) == a
    assert str(ellipsize(a, max_items_to_show=2)) == "[1, 2, ..]"
    assert str(ellipsize(a, max_items_to_show=3)) == str(a)
    assert ellipsize({"a": "12345", "b": a}, max_item_length=4, max_items_to_show=2) == {
        "a": "1234..",
        "b": [1, 2, Dots()],
    }
    result = ellipsize(
        {"a": "12345", "b": a, "c": {"d": a}}, max_item_length=4, max_items_to_show=2
    )
    assert len(result) == 3  # 2 items + ".."
    assert result["a"] == "1234.."
    assert result["b"] == [1, 2, Dots()]
    assert ".." in result
    result2 = ellipsize(
        {"a": "12345", "b": a, "c": [{"d": a}, {}, {}]}, max_item_length=4, max_items_to_show=2
    )
    assert len(result2) == 3  # 2 items + ".."
    assert result2["a"] == "1234.."
    assert result2["b"] == [1, 2, Dots()]
    assert ".." in result2


def test_format_ellipsized():
    a = [1, 2, 3]
    assert format_ellipsized(a, max_items_to_show=2) == "[1, 2, ..]"


def test_dict_ellipsize():
    large_dict = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
    result = ellipsize(large_dict, max_items_to_show=3)
    assert len(result) == 4  # 3 items + ".."
    assert ".." in result
    assert isinstance(result[".."], Dots)
    assert result["a"] == 1
    assert result["b"] == 2
    assert result["c"] == 3

    # Test empty dict
    assert ellipsize({}) == {}

    # Test nested dict truncation
    nested = {"x": {"a": 1, "b": 2, "c": 3}, "y": 2}
    result = ellipsize(nested, max_items_to_show=2)
    assert len(result["x"]) == 3  # 2 items + ".."
    assert ".." in result["x"]
    assert isinstance(result["x"][".."], Dots)


def test_tuple_ellipsize():
    large_tuple = (1, 2, 3, 4, 5)
    result = ellipsize(large_tuple, max_items_to_show=3)
    assert result == (1, 2, 3, Dots())
    assert isinstance(result, tuple)

    # Test empty tuple
    assert ellipsize(()) == ()

    # Test nested tuple
    nested = ([1, 2, 3], (4, 5, 6, 7))
    result = ellipsize(nested, max_items_to_show=2)
    assert result == ([1, 2, Dots()], (4, 5, Dots()))


def test_print_ellipsized(capsys):
    a = [1, 2, 3]
    print_ellipsized(a, max_items_to_show=2)
    assert capsys.readouterr().out == "[1, 2, ..]\n"

    print_ellipsized(a, "2nd", max_items_to_show=2, end="", sep="?")
    assert capsys.readouterr().out == "[1, 2, ..]?'2nd'"
