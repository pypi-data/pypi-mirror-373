def read_line_by_line(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
        return lines


def write(lines, outfile, append=False):
    mode = 'a' if append else 'w'
    with open(outfile, mode, encoding='utf-8') as f:
        for line in lines:
            f.write(line)
            f.write('\n')
