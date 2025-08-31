def extract_imports(path,strings=None):
    strings = make_list(strings or ['from','import'])
    funcs = []
    lines = read_from_file(path).splitlines()
    return [line for line in lines if [string for string in strings if string and eatAll(line,[' ','\n','\t']) and eatAll(line,[' ','\n','\t']).startswith(string)]]

def extract_froms(path: str):
    funcs = []
    for line in read_from_file(path).splitlines():
        m = re.match(r"^from\s+([A-Za-z_]\w*)\s*", line)
        if m:
            funcs.append(m.group(1))
    return funcs
def extract_selfs(path: str):
    funcs = []
    for line in read_from_file(path).splitlines():
        m = re.match(r"^def\s+([A-Za-z_]\w*)\s*\(self", line)
        if m:
            funcs.append(m.group(1))
    return funcs
def extract_funcs(path: str):
    funcs = []
    for line in read_from_file(path).splitlines():
        m = re.match(r"^def\s+([A-Za-z_]\w*)\s*\(", line)
        if m:
            funcs.append(m.group(1))
    return funcs
def extract_class(path: str):
    funcs = []
    for line in read_from_file(path).splitlines():
        m = re.match(r"^class\s+([A-Za-z_]\w*)\s*\(", line) or re.match(r"^class\s+([A-Za-z_]\w*)\s*\:", line)
        if m:
            funcs.append(m.group(1))
    return funcs
