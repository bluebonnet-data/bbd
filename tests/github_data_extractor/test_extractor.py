from bbd.github_data_extractor.extractor import Extractor
from datetime import timedelta
from config import GITHUB_USERNAME, GITHUB_KEY


def test_initialize_authenticate_get_repos():
    org = "openelections"
    rate_limit = timedelta(milliseconds=200)
    username_token = (GITHUB_USERNAME, GITHUB_KEY)
    extractor = Extractor(org=org, rate_limit=rate_limit, username_token=username_token)
    print(extractor.repos)
    print(len(extractor.repos))
    assert extractor is not None
    assert len(extractor.repos) == 133


def test_get_children():
    org = "openelections"
    rate_limit = timedelta(milliseconds=200)
    username_token = (GITHUB_USERNAME, GITHUB_KEY)
    extractor = Extractor(org=org, rate_limit=rate_limit, username_token=username_token)
    child = extractor.repos[5] # grab one repo with a non-trivial number of children
    print(child.url)
    assert child.url == "https://api.github.com/repos/openelections/fec_results/contents/"
    children = extractor.get_children(child)
    print(children)
    assert len(children) == 14


def test_get_files_by_extension():
    org = "openelections"
    rate_limit = timedelta(milliseconds=200)
    username_token = (GITHUB_USERNAME, GITHUB_KEY)
    extractor = Extractor(org=org, rate_limit=rate_limit, username_token=username_token)
    leaves = extractor.get_files_by_extension(link_node_list=extractor.repos, extension=".csv", thread_count=1)
    for leaf in leaves:
        print(leaf)
