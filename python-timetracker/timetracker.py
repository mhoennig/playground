#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add/refresh a 'Duration' column for every Markdown table that has a 'Time' column.
Also writes a 'Total duration: H:MM' line below each processed table.
- Skips code fences ```...```.
- Reads from file given as first arg, or stdin if "-" or no arg.
- Writes result to stdout.
"""
import sys, re

def split_row(line: str):
    return [c.strip() for c in line.strip().strip('|').split('|')]

def format_row(cells, widths):
    padded = [cells[j].ljust(widths[j]) for j in range(len(widths))]
    return '| ' + ' | '.join(padded) + ' |'

def is_sep_line(line: str) -> bool:
    s = line.strip()
    if not s.startswith('|'):
        return False
    core = s.replace('|', '').replace(' ', '')
    return bool(core) and '-' in core and set(core) <= set(':-')

TIME_RE = re.compile(r'\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*')

def compute_minutes(span: str):
    m = TIME_RE.fullmatch(span)
    if not m:
        return None
    h1, m1, h2, m2 = map(int, m.groups())
    start = h1 * 60 + m1
    end = h2 * 60 + m2
    if end < start:
        end += 24 * 60  # cross midnight
    return end - start

def hmm(minutes: int):
    h = minutes // 60
    m = minutes % 60
    return f"{h}:{m:02d}"

def process_table(lines, i, n):
    """
    Assumes lines[i] is header row (starts with '|') and lines[i+1] is a separator line.
    Returns (new_lines_for_table_plus_total, next_index_after_original_table_block, processed_bool)
    """
    header = split_row(lines[i])
    # Only process tables that have a 'Time' column:
    try:
        time_idx_in_header = next(idx for idx, c in enumerate(header) if c.strip().lower() == 'time')
    except StopIteration:
        # Not a time-tracking table; return original block unchanged
        j = i + 2
        while j < n and lines[j].lstrip().startswith('|'):
            j += 1
        return lines[i:j], j, False

    # Find table end
    j = i + 2
    while j < n and lines[j].lstrip().startswith('|'):
        j += 1

    # If there is an immediate "Total duration:" line below, skip it (we'll re-create)
    k = j
    if k < n and lines[k].strip().lower().startswith('total duration:'):
        k += 1  # drop existing total line
        # also drop one optional following blank line (cosmetics)
        if k < n and lines[k].strip() == '':
            k += 1
    end_after_drop = k

    # Build rows (remove existing Duration column if present)
    try:
        old_dur_idx = next(idx for idx, c in enumerate(header) if c.strip().lower() == 'duration')
    except StopIteration:
        old_dur_idx = None

    new_header = [c for idx, c in enumerate(header) if idx != old_dur_idx] + ['Duration']

    # Recompute time index in the (potentially) shifted header
    try:
        time_idx = next(idx for idx, c in enumerate(new_header) if c.strip().lower() == 'time')
    except StopIteration:
        # Should not happen, but be defensive
        time_idx = 0

    data_lines = lines[i+2:j]
    rows = []
    total_minutes = 0

    for line in data_lines:
        # ignore separator-like lines that accidentally appear in body
        if is_sep_line(line):
            continue
        cells = split_row(line)
        if old_dur_idx is not None and old_dur_idx < len(cells):
            cells = [c for idx, c in enumerate(cells) if idx != old_dur_idx]
        # pad to header-1 (without new Duration)
        while len(cells) < len(new_header) - 1:
            cells.append('')
        minutes = compute_minutes(cells[time_idx]) if time_idx < len(cells) else None
        dur = hmm(minutes) if minutes is not None else ''
        if minutes is not None:
            total_minutes += minutes
        rows.append(cells + [dur])

    # Column widths
    widths = [len(h) for h in new_header]
    for r in rows:
        for col, val in enumerate(r):
            if len(val) > widths[col]:
                widths[col] = len(val)

    # Rebuild table
    sep = '| ' + ' | '.join('-' * max(3, w) for w in widths) + ' |'
    out = []
    out.append(format_row(new_header, widths))
    out.append(sep)
    for r in rows:
        out.append(format_row(r, widths))

    # Add total line
    out.append('')
    out.append(f"Total duration: {hmm(total_minutes)}")
    out.append('')

    return out, end_after_drop, True

def process_document(text: str):
    lines = text.splitlines()
    n = len(lines)
    i = 0
    out = []
    in_code = False

    while i < n:
        line = lines[i]

        # Toggle code fence blocks (``` ... ```)
        if re.match(r'^\s*```', line):
            in_code = not in_code
            out.append(line)
            i += 1
            continue

        # Detect table start (header row + separator row) outside code
        if not in_code and line.lstrip().startswith('|') and i + 1 < n and is_sep_line(lines[i+1]):
            new_block, next_i, processed = process_table(lines, i, n)
            out.extend(new_block)
            i = next_i
            continue

        # Default: passthrough
        out.append(line)
        i += 1

    return '\n'.join(out)

def main():
    if len(sys.argv) > 1 and sys.argv[1] != '-':
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    sys.stdout.write(process_document(text))

if __name__ == '__main__':
    main()
