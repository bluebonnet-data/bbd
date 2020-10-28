import re
def is_valid_email(email):
    """
    return True if email is a valid email and
    False if email is not a valid email.

    email - (str) an email to be validated
    """
    regex = "^[a-zA-Z0-9]+[\._]?[a-zA-Z0-9]+[@]\w+[.]\w{2,3}$"
    if (re.search(regex,email)):
        return True
    else:
        return False