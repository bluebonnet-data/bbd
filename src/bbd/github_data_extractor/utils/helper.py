from bbd.github_data_extractor.utils.link_node import LinkNode
from typing import Optional
import os
import requests


def leaf_to_local_csv(leaf: LinkNode, directory_name: Optional[str] = "cached_csvs", file_name: Optional[str] = None):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    if file_name is None:
        file_name = leaf.parent.name.replace("/", "") + leaf.name
    if file_name not in os.listdir(directory_name):
        result = requests.get(leaf.url)
        with open(f"{directory_name}/{file_name}", 'wb') as f:
            f.write(result.content)
    else:
        print(f"File already exists, skipping: {leaf.name}")
