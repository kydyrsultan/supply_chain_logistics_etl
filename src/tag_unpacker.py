# get_base_and_suffix (tag)
# walks in reverse through tag string
# stops at first digit from right
# returns base (everything before digit and inculding last digit), returns suffix (letters after last digit)
def get_base_and_suffix(tag):
    i = len(tag) - 1
    while i >= 0:
        if tag[i].isdigit():
            break
        i -= 1
    base = tag[:i+1]
    suffix = tag[i+1:]
    return base, suffix

# unpack_letter_suffix(base, suffix)
# handles two casese:
# '/' case - letters are explicit, just split and combine with base
# '-' case - letters are in range, generate all letters between start and end
# S is handled automatically in '/' case - no special logic needed
def unpack_letter_suffix(base, suffix, qty):
    tags = []

    suffix = suffix.strip()
    if '/' in suffix:
        suffix_list = suffix.split('/')
        for x in suffix_list:
            tags.append(base + x)

    elif '-' in suffix:
        start_letter = suffix[0]
        if suffix.endswith('S'):
            end_letter = chr(ord(start_letter) + int(qty) - 2)
            for i in range(ord(start_letter), ord(end_letter)+1):
                tags.append(base + chr(i))
            tags.append(base + 'S')
        else:
            end_letter = suffix[2]
            for i in range(ord(start_letter),ord(end_letter) + 1):
                tags.append(base + chr(i))

    else:
        tags.append(base + suffix)
    
    return tags


def unpack_tilde_range(tag):
    tags = []
    parts = tag.split('~')
    first_part = parts[0]
    
    if parts[1].isalpha(): # if part[1] is letter then,
        base = first_part[:-1] # slices and saves in base 17-51L01
        left = first_part[-1] # in left saves A
        right = parts[1] # in right saves C
    else: # if not letter than other logic related if find number
        i = len(first_part) - 1
        while i >= 0:
            if first_part[i].isalpha():
                break
            i -= 1
        
        base = first_part[:i+1]
        left = first_part[i+1:]
        
        if parts[1].isdigit():
            right = parts[1]
        else:
            j = len(parts[1]) -1
            while j >= 0:
                if parts[1][j].isdigit():
                    break
                j -= 1
            right = parts[1][j:]

    if left.isalpha():
        for j in range(ord(left),ord(right)+1):
            tags.append(base + chr(j))
    else:
        for j in range(int(left), int(right)+1):
            tags.append(base + str(j))
    return tags

SKIP_Patterns = ['PIP'] # i find out several tags coming as ..-..PIP..., i skip it temporarly



def unpack_multiline(raw_tag):
    # should be this - Handles multi-line patterns and returns a list of individual tags
    # but we decided to handle it manually. and + it will all unpacked tags.
    pass

def unpack_tag(raw_tag,qty):
    for pattern in SKIP_Patterns:
        if pattern in raw_tag:
            return None
            
    if '~' in raw_tag:
        return unpack_tilde_range(raw_tag)
    elif '\n' in raw_tag:
        pass
    else:
        base, suffix = get_base_and_suffix(raw_tag)
        if suffix == '':
            return [raw_tag]
        else:
            return unpack_letter_suffix(base,suffix, qty)

# in the end i uploaded all tags unpacked auto and manually 

# === TICKET 11 — REPORT MATCHING PIPELINE ===

# normalize(tag)
# Prepares a tag string for matching by making it consistent
# Rule 1: uppercase everything
# Rule 2: remove all spaces
# Rule 3: remove dashes that sit between a digit and a letter (or letter and digit)
#          keep dashes between two digits (e.g. 17-51) and suffix dashes (e.g. A-B)
def normalize(tag):
    tag = tag.upper()
    tag = tag.replace(' ', '')
    clean = ''
    for i in range(len(tag)):
        if tag[i] == '-':
            if i == 0 or i == len(tag) - 1:
                clean += tag[i]
            elif tag[i-1].isdigit() and tag[i+1].isalpha():
                pass
            elif tag[i-1].isalpha() and tag[i+1].isdigit():
                pass
            else:
                clean += tag[i]
        else:
            clean += tag[i]
    return clean

# === split cell function ===
def split_cell(raw_cell):
    # splits a multi-tag cell into individual candidate strings
    # currently handles: newline separator
    # returns a list of stripped non-empty strings
    candidates = str(raw_cell).split('\n')
    candidates = [c.strip() for c in candidates if c.strip() != '']
    return candidates


# new function for tag in reports, hundles tags in PSR, ESR, SSR

def unpack_report_tag(raw_candidate):
    try:
        if '~' in raw_candidate:
            return unpack_tilde_range(raw_candidate)
        else:
            base, suffix = get_base_and_suffix(raw_candidate)
            if suffix != '':
                return unpack_letter_suffix(base, suffix, qty=1)
            else:
                return [raw_candidate]
    except Exception:
        return [raw_candidate]

#=== demo execution/ test casing ===
if __name__ == "__main__":
    test_tags = [
        ("7G02-PMP-001A/B", 2),
        ("17-51L01A~C", 3),
        ("PMP 16-750A-C", 3)
    ]

    print("--- TAG UNPACKER & NORMALIZER DEMO ---")
    for raw_tag, qty in test_tags:
        unpacked = unpack_tag(raw_tag, qty)
        print(f"Raw Tag: '{raw_tag}' (Qty: {qty})")
        print(f"Unpacked: {unpacked}")
        if unpacked:
            normalized = [normalize(t) for t in unpacked]
            print(f"Normalized: {normalized}")
        print("-" * 40)