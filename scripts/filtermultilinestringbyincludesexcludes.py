def filter_multiline_string_by_includes_excludes(multiline_string, includes=None, excludes=None,
                                                 mkdwn_line_endings=False):
    """
    Filter Multiline string with include/excludes and optional Markdown line endings.
    Args:
        multiline_string (): String to filter.
        includes (): List of strings for including lines if don't include an excluded word: ['important word', 'important word2']
        excludes (): List of strings for excluding lines with: ['undesired word', 'unimportant word2']
        mkdwn_line_endings (): Optional Markdown line endings with two spaces '  '

    Returns: Filtered string

    """
    if excludes is None:
        excludes = []
    if includes is None:
        includes = []
    filtered_string = ''
    for line in multiline_string.splitlines():
        # print(line)
        if len(includes) > 0:
            if any(x in line for x in includes):
                if not any(x in line for x in excludes):
                    filtered_string = filtered_string + '\n' + line
        elif len(includes) == 0:
            if not any(x in line for x in excludes):
                filtered_string = filtered_string + '\n' + line

    lines = filtered_string.split("\n")
    non_empty_lines = [line for line in lines if line.strip() != ""]
    string_without_empty_lines = ""
    for line in non_empty_lines:
        if mkdwn_line_endings is True:
            string_without_empty_lines += line + "  \n"
        else:
            string_without_empty_lines += line + "\n"

    return string_without_empty_lines


ignored_entries = [
    'Ignore1:',
    "MR's",
    'merge_requests',
    'Ignore3',
    'Release information',
    '==================='
]

tag_name = 'v2.8.6'
alert_words = [tag_name, 'link:', 'sha256sum', 'SourceFile']

release_description = """Release information
Release link https://gitlab.nonexistent/
===================
v2.8.6 Some package Was Here
link: https://gitlab.nonexistent.2.8.6.tar.gz
sha256sum: e3c96ea4df5dc9e991f175c818b4d2e75cbb5d835814721c5fe499a107864a1f
SourceFile: https://gitlab.nonexistent-src.2.8.6.tar.gz
==================="""

installer_information = filter_multiline_string_by_includes_excludes(release_description,
                                                                     alert_words,
                                                                     ignored_entries)
print(installer_information)
