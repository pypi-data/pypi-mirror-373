import re


def extract_dsid_from_file(file_name):
    match = re.search(r"user\.[^.]+\.(\d{6})(?!\d)", file_name)

    if match:
        dsid = int(match.group(1))
    else:
        dsid = None

    return dsid


def extract_campaign_from_file(file_name):
    match = re.search(r"MC\d{2}[a-zA-Z]", file_name)

    if match:
        campaign = match.group(0)
    else:
        campaign = None

    return campaign


def extract_year_from_file(file_name):
    match = re.search(r"Data_\d{2}", file_name)

    if match:
        year = int(match.group(0)[-2:])
    else:
        year = None

    return year


def extract_user_from_file(file_name):
    match = re.search(r"user\.([^.]+)\.", file_name)

    if match:
        user = match.group(1)
    else:
        user = None

    return user
