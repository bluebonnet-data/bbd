from __future__ import annotations

from typing import Optional
from collections.abc import Iterable
from datetime import timedelta, datetime
from time import sleep
import requests
import pandas as pd
import os
import ssl
import threading
from bbd.github_data_extractor.threadpool import ThreadPool
from bbd.github_data_extractor.utils.link_node import LinkNode
from bbd.github_data_extractor.utils.link_type import LinkType

# Allow for extraction of csvs even if certificate verification fails
ssl._create_default_https_context = ssl._create_unverified_context

class Extractor:
    def __init__(self, org: str, rate_limit: timedelta, username_token: tuple(str, str)):
        # github authentication variables
        self.username_token = username_token
        # Get a list of all repos for org
        page = 1
        more_pages = True
        repos = []
        while more_pages:
            url = f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}"
            result = requests.get(url, auth=self.username_token).json()
            for item in result:
                name = item["name"]
                url = f"https://api.github.com/repos/{org}/{name}/contents/"
                repos.append(LinkNode(name=name, url=url, type_=LinkType.REPO, depth=0))
            page += 1
            if len(result) == 0:
                more_pages = False
        self.repos = repos

        # Rate Limit Varaibles
        self.last_request = datetime.now()
        self.rate_limit = rate_limit
        self.rate_limit_lock = threading.Lock()

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
        children = []
        try:
            top_url = link_node.url
            result = self.rate_limited_request(top_url, auth=self.username_token).json()
            for item in result:
                name = item["name"]
                type_ = LinkType(item["type"])
                if type_ == LinkType.FILE:
                    url = item["download_url"]
                elif type_ == LinkType.DIRECTORY:
                    url = item["url"]
                children.append(LinkNode(name=name,
                                     url=url,
                                     type_=type_,
                                     depth=link_node.depth + 1,
                                     parent=link_node))

            return children

        except requests.ConnectionError as e:
            return [LinkNode(url=link_node.url, depth=link_node.depth, parent=link_node.parent, error=e)]

    def get_files(self, link_node_list: list[LinkNode]) -> Iterable[LinkNode]:
        with ThreadPool(10) as queue:
            for node in link_node_list:
                queue.add_item(self.get_children, node)
            #all_leaves = []

            for children in queue:
                for child in children:
                    if child.type_ == LinkType.DIRECTORY:
                        queue.add_item(self.get_children, child)
                    elif child.type_ == LinkType.FILE:
                        yield child
                    elif child.type_ == LinkType.ERROR:
                        print(f" \n \n {child.error} \n")
                        assert False
                    else:
                        continue
        print(f'{queue=}')
        assert queue.input_count == 0
        assert queue.processing_count_count == 0
        assert queue.output_count == 0


# creates a new folder in current working directory
#     def leaf_to_local_csv(self, leaf, directory_name ="cached_csvs"):
#         base = "https://raw.githubusercontent.com"
#         extension = leaf.url.replace("/blob", "")
#         full_url = base + extension
#         df = pd.read_csv(full_url)
#         if not os.path.exists(directory_name):
#             os.makedirs(directory_name)
#         df.to_csv(f"{directory_name}/{leaf.url_id}")
#

def main():
    testObject = Extractor(org="openelections", rate_limit=timedelta(milliseconds=200))
    leaves = testObject.get_files(link_node_list=testObject.repos)

    for leaf in leaves:
        print(leaf.url)



if __name__ == '__main__':
    main()
