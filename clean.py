def remove_all_commas_except_last(s):
    last_comma_index = s.rfind(',')

    if last_comma_index == -1:
        return s

    before_last_comma = s[:last_comma_index]
    after_last_comma = s[last_comma_index:]

    before_last_comma = before_last_comma.replace(',', '')

    result = before_last_comma + after_last_comma
    return result


with open('res_5c7e.txt', 'r') as f:
    lines = f.readlines()

fixed_lines = [line.strip() for line in lines]
fixed_lines = [remove_all_commas_except_last(line) for line in fixed_lines]
# french_lines = [line for line in fixed_lines if any(ord(i) > 128 for i in line)]
# fixed_lines = [line for line in fixed_lines if not any(ord(i) > 128 for i in line)]

with open("res2.csv", "w") as f:
    f.write("\n".join(fixed_lines))

'''with open("french_lines", "w") as f:
    french_lines = [line.split(",")[0] for line in french_lines]
    f.write("\n".join(french_lines))
'''