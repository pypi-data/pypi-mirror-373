def extract_before_marker_line(source, marker):
    lines_out = []
    for line in source.splitlines(keepends=True):
        if marker in line:
            break
        lines_out.append(line)
    return "".join(lines_out)


def extract_between_marker_lines(source, marker):
    if marker not in source:
        return ""

    in_between = False
    lines_out = []
    for line in source.splitlines(keepends=True):
        if marker in line:
            in_between = not in_between
            continue
        if in_between:
            lines_out.append(line)
    return "".join(lines_out)


def extract_sections(source, markers, patch_name='INITIAL SCRIPT'):
    extraction = {}
    for marker in markers:
        content = extract_between_marker_lines(source, marker)
        if content:
            clean_patch_name = patch_name.replace('\n', '').replace('\r', '')
            extraction[marker] = {
                'content': content,
                'patch': clean_patch_name[:100],
            }
    return extraction


def extract_between_fence(s):
    start = "```python\n"
    end = "```"
    if s.startswith(start) and s.endswith(end):
        return s[len(start):-len(end)]
    return ''
