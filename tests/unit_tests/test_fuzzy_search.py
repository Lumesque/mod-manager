import pytest

from mod_manager.algorithms import FuzzyFind


@pytest.fixture(params=["BepInEx"])
def search_request(request):
    return request.param


@pytest.fixture(params=["biggerlob", "bepinex"])
def search_request_case_insensitive(request):
    return request.param


@pytest.fixture(params=["DOESNOTEXISTOOH", "WSAWSIEKEWLSP"])
def notreal_search_request(request):
    return request.param


@pytest.fixture
def searcher(full_api):
    # Get list of names, we don't care about unique-keys here we just want to test that it works
    return FuzzyFind(set(full_api._cache_index_by_name.keys()))


def test_search(searcher, search_request):
    out = searcher.search(search_request)
    assert len(out) != 0, f"Expected to find some parameter for {search_request}, found nothing"
    for found in out:
        assert found.count != 0, f"Expected {found} to have a match, got='{found.count}'"
        assert found.match_positions, f"Expected {found} to have a match, got='{found.match_positions}'"


def test_search_case_insensitive(searcher, search_request_case_insensitive):
    out = searcher.search(search_request_case_insensitive, case_insensitive=True)
    assert len(out) != 0, f"Expected to find some parameter for {search_request_case_insensitive}, found nothing"
    for found in out:
        assert found.count != 0, f"Expected {found} to have a match, got='{found.count}'"
        assert found.match_positions, f"Expected {found} to have a match, got='{found.match_positions}'"


def test_search_failures(searcher, notreal_search_request):
    out = searcher.search(notreal_search_request)
    assert len(out) == 0, f"Expected to find nothing for {notreal_search_request}, found {out}"
