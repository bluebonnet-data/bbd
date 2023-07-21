import enum

class DataSet(enum.Enum):
    """Datasets available in the census API"""

    ACS5 = "acs/acs5"
    ACS5_SUBJECT = "acs/acs5/subject"
    ACS5_PROFILE = "acs/acs5/profile"
    ACS5_CPROFILE = "acs/acs5/cprofile"
    ACS1 = "acs/acs1"