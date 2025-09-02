import pytest

from arkindex_cli.argtypes import URLArgument


def test_url_valid():
    arg = URLArgument()
    assert arg("http://google.com") == "http://google.com"
    with pytest.raises(ValueError, match="is not a valid URL$"):
        # This causes a ValueError('Invalid IPv6 URL')
        arg("//[")


def test_url_allow_path():
    arg = URLArgument()
    assert arg("http://somewhere/path") == "http://somewhere/path"
    arg = URLArgument(allow_path=False)
    with pytest.raises(ValueError, match="cannot have a path$"):
        arg("http://somewhere/path")


def test_url_allow_query():
    arg = URLArgument()
    assert arg("http://somewhere/?q=4") == "http://somewhere/?q=4"
    arg = URLArgument(allow_query=False)
    with pytest.raises(ValueError, match="cannot have query parameters"):
        arg("http://somewhere/?q=4")


def test_url_allow_fragment():
    arg = URLArgument()
    with pytest.raises(ValueError, match="cannot have a fragment"):
        arg("http://somewhere/#fragment")
    arg = URLArgument(allow_fragment=True)
    assert arg("http://somewhere/#fragment") == "http://somewhere/#fragment"


def test_url_default_scheme():
    arg = URLArgument()
    assert arg("//nowhere") == "https://nowhere"
    # Special case here: without //, `nowhere` is treated as a path instead of a hostname
    assert arg("nowhere") == "https://nowhere"

    arg = URLArgument(default_scheme=None)
    assert arg("nowhere") == "nowhere"

    arg = URLArgument(default_scheme="ftp")
    assert arg("nowhere") == "ftp://nowhere"
