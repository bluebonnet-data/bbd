from __future__ import annotations
from collections.abc import Iterable
from datetime import timedelta, datetime
from time import sleep
from typing import Optional
import requests
import threading
import tests.github_data_extractor.config
import ssl
from bbd.github_data_extractor.threadpool import ThreadPool
from bbd.github_data_extractor.utils.link_node import LinkNode
from bbd.github_data_extractor.utils.link_type import LinkType
from bbd.github_data_extractor.utils.helper import leaf_to_local_csv, cache_url_from_leaf, leaf_to_uploaded_csv
from google.cloud import storage
# Allow for extraction of csvs later even if certificate verification fails
ssl._create_default_https_context = ssl._create_unverified_context


class Extractor:
    def __init__(self, org: str, rate_limit: timedelta, username_token: tuple[str, str]):
        # GitHub's authentication variables
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

        # Rate Limit Variables
        self.last_request = datetime.now()
        self.rate_limit = rate_limit
        self.rate_limit_lock = threading.Lock()

    def rate_limited_request(self, *args, **kwargs):
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
        return requests.get(*args, **kwargs)

    def get_children(self, link_node: LinkNode) -> list[LinkNode]:
        print(f'getting children for node: {link_node!r}')
        children = []
        try:
            top_url = link_node.url
            result = self.rate_limited_request(top_url, auth=self.username_token).json()
            for item in result:
                try:
                    name = item["name"]
                    type_ = LinkType(item["type"])
                    if type_ == LinkType.FILE:
                        url = item["download_url"]

                    else:
                        url = item["url"]
                    children.append(LinkNode(name=name,
                                         url=url,
                                         type_=type_,
                                         depth=link_node.depth + 1,
                                         parent=link_node))

                # If the repository is empty, don't return any children, but modify the repo LinkNode in place
                except TypeError as e:
                    if result["message"] == 'This repository is empty.':
                        link_node.type_ = LinkType.ERROR
                    link_node.error = e
                    continue

            return children

        except requests.ConnectionError as e:
            return [LinkNode(name=link_node.name,
                             type_=link_node.type_,
                             url=link_node.url,
                             depth=link_node.depth,
                             parent=link_node.parent,
                             error=e)]

    def get_files_by_extension(self, link_node_list: Iterable[LinkNode], extension: str, thread_count: int) -> Iterable[LinkNode]:
        with ThreadPool(thread_count) as queue:
            for node in link_node_list:
                queue.add_item(self.get_children, node)
            for children in queue:
                for child in children:
                    if child.type_ == LinkType.DIRECTORY:
                        queue.add_item(self.get_children, child)
                    elif child.type_ == LinkType.FILE and child.name[-4:] == extension:
                        print(child.url)
                        yield child
                    elif child.type_ == LinkType.ERROR:
                        print(f" \n \n {child.error} \n")
                        assert False
                    else:
                        continue
        print(f'{queue=}')
        assert queue.input_count == 0
        assert queue.processing_count == 0
        assert queue.output_count == 0

# creates a new folder in current working directory and deposits csvs



def main():
    GITHUB_KEY = tests.github_data_extractor.config.GITHUB_KEY
    GITHUB_USERNAME = tests.github_data_extractor.config.GITHUB_KEY
    org = "openelections"
    rate_limit = timedelta(milliseconds=200)
    username_token = (GITHUB_USERNAME, GITHUB_KEY)
    extractor = Extractor(org=org, rate_limit=rate_limit, username_token=username_token)
    leaves = extractor.get_files_by_extension(link_node_list=extractor.repos, extension=".csv", thread_count=1)
    client = storage.Client("bluebonnet-data-public")
    export_bucket = client.get_bucket("bluebonnet-data-public")

    for leaf in leaves:
        leaf_to_local_csv(leaf, directory_name="cached_csvs")
        print(f"saving leaf from: {leaf.url}")
        #cache_url_from_leaf(leaf, file_name="cached_urls.txt")

    # with open("cached_urls.txt", "r") as read_file:
    #     with open ("../cloud_storage/data_urls.txt", "a") as write_file:
    #         for line in read_file:
    #             if "-data" in line:
    #                 write_file.write(line)




if __name__ == '__main__':
    main()
