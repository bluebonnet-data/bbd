import urllib
from urllib.parse import urlparse


def parse_line(line: str) -> str:
    url = line.strip('\n')
    path = url.split("/openelections/")[-1]
    state = path.split("/")[0][-2:]
    file_name = path.split("/")[-1]
    new_path = path.split("/master/")[-1]

    return (file_name, path, state, new_path, url)

class ParsedUrl:
    def __init__(self,
                 url: str):
        self.url = url
        self.path = urlparse(url).path
        self.directories = [item for item in self.path.split("/") if len(item) > 0]
        self.indicies_to_directories = dict()
        for i in range(len(self.directories)):
            self.indicies_to_directories[i] = self.directories[i]



if __name__ == "__main__":
    test_url = 'https://raw.githubusercontent.com/openelections/openelections-data-wv/master/1950/19500223__wv__general__house.csv'
    parsed = ParsedUrl(test_url)
    path = parsed.path
    directories = parsed.indicies_to_directories
    print(path)
    print(directories)