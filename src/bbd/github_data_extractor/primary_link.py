# Enum class to define the kinds of primary links we care about once obtained
class PrimaryLink(enum.Enum):
    CSV = enum.auto()
    DIRECTORY = enum.auto()
    ERROR = enum.auto()
    OTHER = enum.auto()
