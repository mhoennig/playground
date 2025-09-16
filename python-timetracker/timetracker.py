#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- Adds/refreshes a right aligned 'Duration' column for every Markdown table that has a 'Time' column.
- Also adds/updates a 'Total working time' line below each processed table,
    which consists of the date, taken from the title above the table, in the first column,
    the day of week of that date in the second column, 'Total working time' in the third column,
    and the total duration in hours:minutes in the fourth column.
- Skips code fences ```...```.
- Reads from file given as first arg, or stdin if "-" or no arg.
- Writes result to stdout.
"""
import sys, re
from datetime import datetime

def split_row(line: str):
    return [c.strip() for c in line.strip().strip('|').split('|')]

def format_row(cells, widths, right_align_indices=None):
    right = set(right_align_indices or [])
    padded = []
    for j, w in enumerate(widths):
        val = cells[j] if j < len(cells) else ''
        padded.append(val.rjust(w) if j in right else val.ljust(w))
    return '| ' + ' | '.join(padded) + ' |'

def is_sep_line(line: str) -> bool:
    s = line.strip()
    if not s.startswith('|'):
        return False
    core = s.replace('|', '').replace(' ', '')
    return bool(core) and '-' in core and set(core) <= set(':-')

TIME_RE = re.compile(r'\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*')
DATE_RE = re.compile(r'(\d{4}-\d{2}-\d{2})')
DAY_RE = re.compile(r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b', re.I)

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

    # If there is an immediate totals line below, skip it (we'll re-create or update)
    k = j
    # Legacy "Total duration:" single-line summary
    if k < n and lines[k].strip().lower().startswith('total duration:'):
        k += 1
        if k < n and lines[k].strip() == '':
            k += 1
    # Previously generated totals row as a single Markdown row below the table
    if k < n and lines[k].lstrip().startswith('|'):
        existing_cells = split_row(lines[k])
        def norm_cell(s: str) -> str:
            return re.sub(r'^\**|\**$', '', s or '').strip().lower()
        if len(existing_cells) >= 3 and norm_cell(existing_cells[2]) == 'total working time':
            # consume existing totals row below (we'll output an updated one)
            k += 1
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

    # Identify indices (for reference; totals line will be placed below the table)
    dur_idx = len(new_header) - 1  # Duration is appended at the end

    # Copy data lines and drop an in-table totals row if present (update it instead)
    data_lines = lines[i+2:j]
    # If last non-separator row in the table is a "Total working time" row, drop it
    def is_totals_row_line(line: str) -> bool:
        if not line.lstrip().startswith('|'):
            return False
        cells = split_row(line)
        if len(cells) < 3:
            return False
        val = re.sub(r'^\**|\**$', '', cells[2] or '').strip().lower()
        return val == 'total working time'

    while data_lines and (is_sep_line(data_lines[-1]) or data_lines[-1].strip() == ''):
        data_lines.pop()
    if data_lines and is_totals_row_line(data_lines[-1]):
        data_lines.pop()

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

    # Extract date and weekday from the nearest non-empty title line above the table
    title_line = None
    p = i - 1
    while p >= 0:
        s = lines[p].strip()
        if s == '':
            p -= 1
            continue
        if s.startswith('|') or s.startswith('```'):
            break
        title_line = s
        break
    date_str = None
    day_str = None
    if title_line:
        m_date = DATE_RE.search(title_line)
        if m_date:
            date_str = m_date.group(1)

    # Compute weekday strictly from date_str (if available)
    day_str = None
    if date_str:
        try:
            day_str = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
        except ValueError:
            day_str = None

    # Prepare totals "line below table" cells (all values in bold)
    totals_cells = [''] * len(new_header)
    # Column 1: date (bold) if found
    totals_cells[0] = f"**{date_str}**" if date_str else "** **"
    # Column 2: day of week computed from date (bold)
    if len(totals_cells) > 1:
        totals_cells[1] = f"**{day_str}**" if day_str else "** **"
    # Column 3: literal marker (bold)
    if len(totals_cells) > 2:
        totals_cells[2] = "**Total working time**"
    # Last column: total duration (bold)
    totals_cells[dur_idx] = f"**{hmm(total_minutes)}**"

    # Column widths (account for all rows AND totals line to keep alignment consistent)
    widths = [len(h) for h in new_header]
    for r in rows + [totals_cells]:
        for col, val in enumerate(r):
            if len(val) > widths[col]:
                widths[col] = len(val)

    # Build separator with right alignment for Duration column
    sep_cells = []
    for idx, w in enumerate(widths):
        w2 = max(3, w)
        if idx == dur_idx:
            sep_cells.append('-' * (w2 - 1) + ':')
        else:
            sep_cells.append('-' * w2)
    sep = '| ' + ' | '.join(sep_cells) + ' |'

    # Rebuild table (no totals row inside the table)
    out = []
    out.append(format_row(new_header, widths, right_align_indices={dur_idx}))
    out.append(sep)
    for r in rows:
        out.append(format_row(r, widths, right_align_indices={dur_idx}))
    # Append a single totals line BELOW the table, aligned to the same widths
    out.append(format_row(totals_cells, widths, right_align_indices={dur_idx}))

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
