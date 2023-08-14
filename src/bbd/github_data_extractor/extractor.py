from __future__ import annotations

from collections.abc import Iterable

import requests
from bs4 import BeautifulSoup
from bbd.github_data_extractor.threadpool import ThreadPool
import enum

# Enum class to define the kinds of primary links we care about once obtained
class PrimaryLink(enum.Enum):
    CSV = enum.auto()
    DIRECTORY = enum.auto()
    OTHER = enum.auto()

# A class to encapsulate and label primary links (directories and files in a repository) once obtained
class LinkNode():
    def __init__(self, url: str, depth: int, parent: LinkNode):
        self.url = url
        self.url_text = url.split("/")[-1]
        if "." not in self.url_text:
            self.type_ = PrimaryLink.DIRECTORY
        elif ".csv" in self.url_text:
            self.type_ = PrimaryLink.CSV
        else:
            self.type_ = PrimaryLink.OTHER
        self.parent = parent
        self.depth = depth

    def __repr__(self):
        return f"LinkNode(url_text: {self.url_text}, type_: {self.type_}, depth: {self.depth})"

class Extraction():
    def __init__(self, repositories_tab_url: str):
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
        # Find all individual repository links, taking all from each results page
        all_repository_links = []
        for url in results_pages_urls:
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')
            repositories = soup.find_all("a", itemprop="name codeRepository")
            repository_links = [repository.get_attribute_list("href")[0] for repository in repositories]
            all_repository_links += repository_links
        # Save these to property
        self.all_repository_links = [LinkNode(url=item, depth=0, parent=None) for item in all_repository_links]

    def get_children(self, link_node: LinkNode) -> list[LinkNode]:
        print(f'{link_node!r}')
        page_url = link_node.url
        try:
            page = requests.get(self.base_url + page_url)
            soup = BeautifulSoup(page.text, 'html.parser')
            primaries = soup.find_all("a", class_="Link--primary")
            primary_links = [primary.get_attribute_list("href")[0] for primary in primaries]
            primary_links = [LinkNode(url=item, depth=link_node.depth + 1, parent=link_node) for item in primary_links]
            return (primary_links)
        except requests.ConnectionError as e:
            print(e)
            return []

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
                        #all_leaves.append(child)
                        yield child
                    else:
                        continue
        #return all_leaves


def main():
    testObject = Extraction(repositories_tab_url="https://github.com/orgs/openelections/repositories")
    one_repository_link = testObject.all_repository_links[0]
    # testObject.get_children(one_repository_link)
    leaves = testObject.get_csvs(link_node_list=testObject.all_repository_links)
    with open("csv_urls.txt", "w") as csv_cache:
        for leaf in leaves:
            csv_cache.write(str(leaf.url))
            csv_cache.write("\n")



if __name__ == '__main__':
    main()
