def b_make_catalog(md_path, prefix='- ', newline=True, print_out=False):
    def del_jing(string):
        index = 0
        for i in range(len(string)):
            if string[i] != '#' and string[i] != ' ':
                index = i
                break
        return string[index:]

    results = []
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('#'):
            string = del_jing(line.strip())
            results.append(string)

    for i in range(len(results)):
        results[i] = f"{prefix}[{results[i]}](#{results[i]})"
        if newline:
            results[i] += '\n'

    if print_out:
        for result in results:
            print(result)

    return results

if __name__ == '__main__':
    md_path = r'E:\byzh_study\byzh_code_note\博客\1.md'
    catalog = b_make_catalog(md_path, print_out=True)