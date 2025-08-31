import re


EMAIL_REGEX: str = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
SORT_COLUMN_REGEX = r"^[a-z_]+\.(asc|desc)$"
SORT_COLUMN_PATTERN = re.compile(SORT_COLUMN_REGEX)
DATE_FILTER_REGEX = r"^[a-z_]+(?:\|from::\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))?(?:\|to::\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))?$"
DATE_FILTER_PATTERN = re.compile(DATE_FILTER_REGEX)
