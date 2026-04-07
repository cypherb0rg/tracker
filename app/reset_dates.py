"""
reset_dates.py — Recalculate all phase/week/block date ranges from a new start date.

Usage (run inside the tracker container):
    python reset_dates.py              # starts from today
    python reset_dates.py 2026-06-01   # starts from a specific date

All dates are recomputed relative to the original plan structure.
Checked items, reflections, and all other data are untouched.
"""
import sys
from datetime import date, timedelta
from app import app
from models import db, Phase, Week, DayBlock, CourseMeta


# ── Date formatting helpers ────────────────────────────────────────────────────

def fmt(d):
    """Format a single date: 'Apr 7'"""
    return d.strftime("%b %-d")

def fmt_range(start, end):
    """Format a date range: 'Apr 7', 'Apr 7-9', or 'Apr 29 - May 3'"""
    if start == end:
        return fmt(start)
    if start.month == end.month:
        return f"{start.strftime('%b')} {start.day}-{end.day}"
    return f"{fmt(start)} - {fmt(end)}"


# ── Plan structure: (start_offset, end_offset) from day 0 ─────────────────────
# Offsets are days from the course start date.
# Edit these if you change the course structure.

PHASES = [
    # (phase_number, start_offset, end_offset)
    (1, 0,  13),   # Foundation          — 2 weeks
    (2, 14, 34),   # Core Structures     — 3 weeks
    (3, 35, 55),   # Advanced DS         — 3 weeks
    (4, 56, 76),   # Algorithms          — 3 weeks
    (5, 77, 103),  # Practice & Mastery  — 4 weeks
    # Phases 6 & 7 are Fast Track with no fixed dates — left unchanged
]

WEEKS = [
    # (week_number, start_offset, end_offset)
    (1,  0,   6),
    (2,  7,  13),
    (3,  14, 20),
    (4,  21, 27),
    (5,  28, 34),
    (6,  35, 41),
    (7,  42, 48),
    (8,  49, 55),
    (9,  56, 62),
    (10, 63, 69),
    (11, 70, 76),
    (12, 77, 83),
    (13, 84, 90),
    (14, 91, 103),
]

# Blocks keyed by (week_number, sort_order): (start_offset, end_offset)
BLOCKS = {
    # Week 1
    (1, 0): (0,   0),
    (1, 1): (0,   1),
    (1, 2): (2,   3),
    (1, 3): (4,   5),
    (1, 4): (6,   6),
    # Week 2
    (2, 1): (7,   8),
    (2, 2): (9,  10),
    (2, 3): (11, 13),
    # Week 3
    (3, 1): (14, 15),
    (3, 2): (16, 17),
    (3, 3): (18, 20),
    # Week 4
    (4, 1): (21, 23),
    (4, 2): (24, 25),
    (4, 3): (26, 27),
    # Week 5
    (5, 1): (28, 30),
    (5, 2): (31, 32),
    (5, 3): (33, 34),
    # Week 6
    (6, 1): (35, 36),
    (6, 2): (37, 38),
    (6, 3): (39, 41),
    # Week 7
    (7, 1): (42, 44),
    (7, 2): (45, 46),
    (7, 3): (47, 48),
    # Week 8
    (8, 1): (49, 51),
    (8, 2): (52, 55),
    # Week 9
    (9, 1): (56, 58),
    (9, 2): (59, 60),
    (9, 3): (61, 62),
    # Week 10
    (10, 1): (63, 65),
    (10, 2): (66, 67),
    (10, 3): (68, 69),
    # Week 11
    (11, 1): (70, 71),
    (11, 2): (72, 73),
    (11, 3): (74, 76),
    # Week 12
    (12, 1): (77, 78),
    (12, 2): (79, 80),
    (12, 3): (81, 83),
    # Week 13
    (13, 1): (84, 85),
    (13, 2): (86, 87),
    (13, 3): (88, 90),
    # Week 14
    (14, 1): (91, 93),
    (14, 2): (94, 95),
    (14, 3): (96, 103),
}


def reset_dates(start: date):
    with app.app_context():
        total_days = 104

        # ── CourseMeta ────────────────────────────────────────────────────────
        started = CourseMeta.query.filter_by(key='started_at').first()
        planned = CourseMeta.query.filter_by(key='planned_end').first()
        if started:
            started.value = start.isoformat()
        if planned:
            planned.value = (start + timedelta(days=total_days)).isoformat()

        def d(offset):
            return start + timedelta(days=offset)

        # ── Phases ────────────────────────────────────────────────────────────
        for phase_num, s, e in PHASES:
            phase = Phase.query.filter_by(number=phase_num).first()
            if phase:
                phase.date_range = fmt_range(d(s), d(e))
                print(f"  Phase {phase_num}: {phase.date_range}")

        # ── Weeks ─────────────────────────────────────────────────────────────
        for week_num, s, e in WEEKS:
            week = Week.query.filter_by(number=week_num).first()
            if week:
                week.date_range = fmt_range(d(s), d(e))
                print(f"    Week {week_num}: {week.date_range}")

        # ── Day Blocks ────────────────────────────────────────────────────────
        for (week_num, sort_order), (s, e) in BLOCKS.items():
            week = Week.query.filter_by(number=week_num).first()
            if not week:
                continue
            block = DayBlock.query.filter_by(
                week_id=week.id, sort_order=sort_order
            ).first()
            if block:
                block.date_range = fmt_range(d(s), d(e))
                print(f"      Block (wk{week_num} pos{sort_order}): {block.date_range}")

        db.session.commit()
        print(f"\nDone. Course now runs {fmt(start)} → {fmt(start + timedelta(days=total_days))}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        start = date.fromisoformat(sys.argv[1])
    else:
        start = date.today()
    print(f"Resetting dates to start: {start}")
    reset_dates(start)
