# Enum class to define the kinds of primary links we care about once obtained
import enum

class LinkType(enum.Enum):
    REPO = "repo"
    DIRECTORY = "dir"
    FILE = "file"
    # CSV = enum.auto()
    # ERROR = enum.auto()
    OTHER = "other"



if __name__ == "__main__" :
    print (LinkType("dir"))