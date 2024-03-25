import bibtexparser
import sys
import os
import re
import string

assert len(sys.argv) >= 3, 'invalid number of arguments'
output_filename = sys.argv[1]
input_filenames = sys.argv[2:]


# only allow certain characters in names
def clean_name_segments(s:str)->str:
    new_s = ''
    cand = string.ascii_letters + ' '
    for c in s:
        if c in cand:
            new_s += c

    return new_s

# return a list of authors
# each author name is represented using a list, where name segments are ordered from first name to last name
def process_author_names(s:str)->list:
    s = s.strip()

    braces_match = re.match('\{(.*)\}', s)
    if braces_match:
        return [[clean_name_segments(braces_match.group(1))]]
    
    ret = []

    parts = s.split(' and ')
    for part in parts:
        if ',' in part:
            last, _, first = part.partition(',')
            ret.append(first.split(' ') + [last])
        else:
            ret.append(part.split(' '))

    for item in ret:
        new_item = [clean_name_segments(x.strip()) for x in item]
        new_item = [x for x in new_item if x]
        item.clear()
        item.extend(new_item)

    return ret
    

def get_author_sort_key(e:list):
    return tuple(map(lambda x: x.lower(), reversed(e)))

author_lut = dict()

for fn in input_filenames:
    assert os.path.exists(fn), f'input file "{fn}" does not exist'

    with open(fn) as f:
        bib = bibtexparser.load(f)
    
    for entry in bib.entries:
        entry_name = entry['ID']

        if 'author' not in entry:
            print(f'Entry {entry_name} does not have author field, it is skipped')
            continue
        
        authors = process_author_names(entry['author'].replace('\r', ' ').replace('\n', ' '))

        # sort based on first author
        first_author_key = get_author_sort_key(authors[0])
        if first_author_key not in author_lut:
            author_lut[first_author_key] = []

        author_lut[first_author_key].append(entry_name)

author_sorted = sorted(list(author_lut.keys()))

output_lines = []
author_name_ids = []
for ind, author_name_seg in enumerate(author_sorted):
    author_bib_items = author_lut[author_name_seg]
    author_name_id = (' '.join(author_name_seg)).replace(' ', '-')
    author_name_ids.append(author_name_id)
    output_lines.append(r'\BibAuthorInfo{%s}{%s}' % (author_name_id, ','.join(author_bib_items)))

output_lines.append('\BibAllAuthors{%s}' % ','.join(author_name_ids))

with open(output_filename, 'w') as f:
    f.write('\n'.join(output_lines))





