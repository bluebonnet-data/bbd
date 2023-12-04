# Enum class to define the kinds of primary links we care about once obtained
import enum

class LinkType(enum.Enum):
    REPO = "repo"
    DIRECTORY = "dir"
    FILE = "file"
    # EMPTY = "empty"
    # CSV = enum.auto()
    ERROR = "error"
    OTHER = "other"
    SYMBOLIC_LINK = "symlink"



if __name__ == "__main__" :
    print (LinkType("dir"))