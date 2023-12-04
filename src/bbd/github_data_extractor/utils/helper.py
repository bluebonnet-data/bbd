from bbd.github_data_extractor.utils.link_node import LinkNode
from typing import Optional
import os
import requests
import csv
import pandas as pd

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

def leaf_to_uploaded_csv(leaf: LinkNode, client, export_bucket):
    leaf_to_local_csv(leaf, file_name="one_file.csv")
    df = pd.read_csv("one_file.csv")
    outfile = df.to_csv("one_file.csv", encoding="utf-8")
    with open("one_file.csv", "r", encoding="utf-8") as f:
        export_bucket.blob(f"elections/openelections/{state}/{new_path}").upload_from_file(file_obj=f)
        print(f"File Inserted: state = {state}, path = {new_path}")

def url_to_local_csv(url: str, file_name: str):
    headers = {'Content-Type': 'text/text; charset=utf-8'}
    result = requests.get(url, headers = headers)
    with open(file_name, 'wb') as f:
        f.write(result.content)


def cache_url_from_leaf(leaf: LinkNode, file_name: str):
    with open(f"{file_name}", 'a+') as f:
        if file_name not in f:
            f.write(f"{leaf.url}\n")
        else:
            print(f"Skipping duplicate record: {leaf.url}")