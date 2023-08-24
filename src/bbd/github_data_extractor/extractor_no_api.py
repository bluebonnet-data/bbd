from __future__ import annotations

import threading
from collections.abc import Iterable
from datetime import timedelta, datetime
from time import sleep
from typing import Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from bbd.github_data_extractor.threadpool import ThreadPool
import enum
import pandas as pd
import os
import ssl

# Allow for extraction of csvs even if certificate verification fails
ssl._create_default_https_context = ssl._create_unverified_context


# Enum class to define the kinds of primary links we care about once obtained
class PrimaryLink(enum.Enum):
    CSV = enum.auto()
    DIRECTORY = enum.auto()
    ERROR = enum.auto()
    OTHER = enum.auto()


# A class to encapsulate and label primary links (directories and files in a repository) once obtained
class LinkNode:
    def __init__(self, url: str, depth: int, parent: LinkNode, error: Optional[Exception] = None):
        self.url = url
        self.url_text = self.url.split("/")[-1]
        self.url_id = urlparse(self.url).path[1:].replace("/", "_")
        if error is not None:
            self.type_ = PrimaryLink.ERROR
        elif "." not in self.url_text:
            self.type_ = PrimaryLink.DIRECTORY
        elif ".csv" in self.url_text:
            self.type_ = PrimaryLink.CSV
        else:
            self.type_ = PrimaryLink.OTHER
        self.parent = parent
        self.depth = depth
        self.error = error

    def __repr__(self):
        return f"LinkNode(url: {self.url}, type_: {self.type_}, depth: {self.depth})"

class ExtractorNoApi:
    def __init__(self, repositories_tab_url: str, rate_limit: timedelta):
        self.base_url = "https://github.com"
        self.repositories_tab_url = repositories_tab_url
        # Get repository tab
        repository_tab = requests.get(self.repositories_tab_url)
        soup = BeautifulSoup(repository_tab.text, 'html.parser')
        # Find total number of pages
        current_page_of_total = soup.find("em", class_="current")
        total_pages = int(current_page_of_total.get_attribute_list("data-total-pages")[0])
        # Find url for every page of the repository list
        results_pages_urls = [f"{repositories_tab_url}?page={i + 1}&type=all" for i in range(total_pages)]

        self.last_request = datetime.now()
        self.rate_limit = rate_limit
        self.rate_limit_lock = threading.Lock()

        # Find all individual repository links, taking all from each results page
        all_repository_links = []
        for url in results_pages_urls:
            print(f'results_pages_url = {url}')
            page = self.rate_limited_request(url)
            soup = BeautifulSoup(page.text, 'html.parser')
            repositories = soup.find_all("a", itemprop="name codeRepository")
            repository_links = [repository.get_attribute_list("href")[0] for repository in repositories]
            all_repository_links += repository_links
        # Save these to property
        self.all_repository_links = [LinkNode(url=item, depth=0, parent=None) for item in all_repository_links]


    def rate_limited_request(self, *args, **kwags):
        self.rate_limit_lock.acquire()
        next_request = self.last_request + self.rate_limit
        wait_seconds = (next_request - datetime.now()).total_seconds()
        while wait_seconds > 0:
            self.rate_limit_lock.release()
            sleep(wait_seconds)
            self.rate_limit_lock.acquire()
            next_request = self.last_request + self.rate_limit
            wait_seconds = (next_request - datetime.now()).total_seconds()
        self.last_request = datetime.now()
        self.rate_limit_lock.release()
        return requests.get(*args, **kwags)

    def get_children(self, link_node: LinkNode) -> list[LinkNode]:
        print(f'{link_node!r}')
        page_url = link_node.url
        try:
            page = self.rate_limited_request(self.base_url + page_url)
            soup = BeautifulSoup(page.text, 'html.parser')
            primaries = soup.find_all("a", class_="js-navigation-open")
            maybe_csvs = soup.find_all("a", class_="Link--primary")
            csv_links = [maybe_csv.get_attribute_list("href")[0] for maybe_csv in maybe_csvs if '.csv' in maybe_csv.get_attribute_list("href")[0]]
            primary_links = [primary.get_attribute_list("href")[0] for primary in primaries]
            primary_links = [LinkNode(url=item, depth=link_node.depth + 1, parent=link_node) for item in primary_links]
            return primary_links
        except requests.ConnectionError as e:
            return [LinkNode(url = link_node.url, depth = link_node.depth, parent= link_node.parent, error = e)]

    def get_csvs(self, link_node_list: list[LinkNode]) -> Iterable[LinkNode]:
        with ThreadPool(10) as queue:
            for node in link_node_list:
                queue.add_item(self.get_children, node)
            #all_leaves = []

            for children in queue:
                for child in children:
                    if child.type_ == PrimaryLink.DIRECTORY:
                        queue.add_item(self.get_children, child)
                    elif child.type_ == PrimaryLink.CSV:
                        yield child
                    elif child.type_ == PrimaryLink.ERROR:
                        print(f" \n \n {child.error} \n")
                        assert False
                    else:
                        continue
        print(f'{queue=}')
        assert queue.input_count == 0
        assert queue.processing_count_count == 0
        assert queue.output_count == 0


# creates a new folder in current working directory
    def leaf_to_local_csv(self, leaf, directory_name ="cached_csvs"):
        base = "https://raw.githubusercontent.com"
        extension = leaf.url.replace("/blob", "")
        full_url = base + extension
        df = pd.read_csv(full_url)
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
        df.to_csv(f"{directory_name}/{leaf.url_id}")


def main():
    testObject = ExtractorNoApi(repositories_tab_url="https://github.com/orgs/openelections/repositories", rate_limit=timedelta(milliseconds=100))
    leaves = testObject.get_csvs(link_node_list=testObject.all_repository_links)
    for leaf in leaves:
        print(leaf.url)



if __name__ == '__main__':
    main()
