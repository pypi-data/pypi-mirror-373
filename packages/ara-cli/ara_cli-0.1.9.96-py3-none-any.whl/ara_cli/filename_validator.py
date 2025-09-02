import re

def is_valid_filename(filename):
    return bool(re.match("^[a-zA-Z0-9_äöüÄÖÜß-]+$", filename))
