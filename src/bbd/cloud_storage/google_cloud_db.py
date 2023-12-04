from google.cloud import storage
from bbd.github_data_extractor import extractor
from bbd.github_data_extractor.utils.helper import url_to_local_csv
import pandas as pd
from urllib.parse import urlparse

class GoogleCloudDB:
    def __init__(self, root_bucket = "bluebonnet-data-public"):
        self.root_bucket = root_bucket
        self.client = storage.Client(self.root_bucket)
        self.export_bucket = self.client.get_bucket(self.root_bucket)

    def upload_file(self, uploaded_file_name_path, path_to_local_file: str):
        with open(path_to_local_file, "r") as f:
            self.export_bucket.blob(uploaded_file_name_path).upload_from_file(file_obj=f)
            print("Upload complete, check bucket in browser to confirm.")



if __name__ == "__main__":


    # client = storage.Client("bluebonnet-data-public")
    # export_bucket = client.get_bucket("bluebonnet-data-public")
    #
    # def parse_line(line: str) -> str:
    #     url = line.strip('\n')
    #     path = url.split("/openelections/")[-1]
    #     state = path.split("/")[0][-2:]
    #     file_name = path.split("/")[-1]
    #     new_path = path.split("/master/")[-1]
    #
    #     return (file_name, path, state, new_path, url)
    #
    #
    # def fix_entry(entry):
    #     if isinstance(entry, str):
    #         entry = entry.encode('utf-8')
    #         entry = entry.decode('utf-8')
    #         return entry
    #     else:
    #         return entry
    # def insert_one(line: str):
    #     info = parse_line(line)
    #     file_name = info[0]
    #     original_path = info[1]
    #     state = info[2]
    #     new_path = info[3]
    #     url = info[4]
    #     url_to_local_csv(url=url, file_name="one_file.csv")
    #     df = pd.read_csv("one_file.csv", encoding="utf-8")
    #     # df = df.applymap(lambda x: fix_entry(x))
    #     outfile = df.to_csv("one_file.csv", encoding="utf-8")
    #     with open("one_file.csv", "r", encoding="utf-8") as f:
    #         export_bucket.blob(f"elections/openelections/{state}/{new_path}").upload_from_file(file_obj=f)
    #         print(f"File Inserted: state = {state}, path = {new_path}")
    #
    # failures = []
    # with open("data_urls.txt", "r") as f:
    #     for line in f.readlines():
    #        try:
    #            insert_one(line)
    #        except:
    #            print(line)
    #            failures.append(line)
    # print(failures)
    # test_file = 'https://raw.githubusercontent.com/openelections/openelections-data-wv/master/1950/19500223__wv__general__house.csv'

