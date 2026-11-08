import re

def extract(row: str):
    pattern = (
        r'(?P<month>\w{3})\s+'
        r'(?P<day>\d{1,2})\s+'
        r'(?P<time>\d{2}:\d{2}:\d{2})\s+'
        r'(?P<hostname>\w+)\s+'
        r'(?P<process>\w+)\[(?P<pid>\d+)\]:\s+'
        r'(?P<message>.*)'
    )

    match = re.search(pattern, row)

    if match:
        return match.groupdict()

    return None
def extract_auth(message: str):
    pattern = (
        r'(?P<status>Accepted|Failed) password for '
        r'(?:(?P<invalid>invalid user) )?'
        r'(?P<user>\S+) from '
        r'(?P<ip>\d{1,3}(?:\.\d{1,3}){3})'
    )

    match = re.search(pattern, message)

    if match:
        return match.groupdict()

    return None