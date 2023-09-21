def remove_all_commas_except_last(s):
    last_comma_index = s.rfind(',')

    if last_comma_index == -1:
        return s

    before_last_comma = s[:last_comma_index]
    after_last_comma = s[last_comma_index:]

    before_last_comma = before_last_comma.replace(',', '')

    result = before_last_comma + after_last_comma
    return result


with open('res3.txt', 'r') as f:
    lines = f.readlines()

fixed_lines = [remove_all_commas_except_last(line) for line in lines]
fixed_lines = [line.strip() for line in fixed_lines]

with open("res.txt", "w") as f:
    f.write("\n".join(fixed_lines))
