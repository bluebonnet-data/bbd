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