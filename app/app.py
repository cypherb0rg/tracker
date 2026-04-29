import os
from datetime import date, timedelta
import math
from flask import Flask, render_template, jsonify, request, redirect, url_for as flask_url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, Phase, Week, DayBlock, ChecklistItem, PhaseMastery, CourseMeta
from dotenv import load_dotenv


# ── Dynamic date computation ─────────────────────────────────────────────────
# Offset tables: same structure as reset_dates.py but used at render time
# so dates always reflect today as the start.

PHASE_OFFSETS = {
    1: (0,  13),
    2: (14, 34),
    3: (35, 55),
    4: (56, 76),
    5: (77, 103),
}

WEEK_OFFSETS = {
    1:  (0,   6),   2:  (7,  13),  3:  (14, 20),  4:  (21, 27),
    5:  (28, 34),   6:  (35, 41),  7:  (42, 48),  8:  (49, 55),
    9:  (56, 62),  10:  (63, 69), 11:  (70, 76), 12:  (77, 83),
    13: (84, 90),  14:  (91, 103),
}

BLOCK_OFFSETS = {
    (1, 0): (0, 0),    (1, 1): (0, 1),    (1, 2): (2, 3),
    (1, 3): (4, 5),    (1, 4): (6, 6),
    (2, 1): (7, 8),    (2, 2): (9, 10),   (2, 3): (11, 13),
    (3, 1): (14, 15),  (3, 2): (16, 17),  (3, 3): (18, 20),
    (4, 1): (21, 23),  (4, 2): (24, 25),  (4, 3): (26, 27),
    (5, 1): (28, 30),  (5, 2): (31, 32),  (5, 3): (33, 34),
    (6, 1): (35, 36),  (6, 2): (37, 38),  (6, 3): (39, 41),
    (7, 1): (42, 44),  (7, 2): (45, 46),  (7, 3): (47, 48),
    (8, 1): (49, 51),  (8, 2): (52, 55),
    (9, 1): (56, 58),  (9, 2): (59, 60),  (9, 3): (61, 62),
    (10, 1): (63, 65), (10, 2): (66, 67), (10, 3): (68, 69),
    (11, 1): (70, 71), (11, 2): (72, 73), (11, 3): (74, 76),
    (12, 1): (77, 78), (12, 2): (79, 80), (12, 3): (81, 83),
    (13, 1): (84, 85), (13, 2): (86, 87), (13, 3): (88, 90),
    (14, 1): (91, 93), (14, 2): (94, 95), (14, 3): (96, 103),
}


def _fmt_date(d):
    return d.strftime("%b %-d")


def _fmt_range(start, end):
    if start == end:
        return _fmt_date(start)
    if start.month == end.month:
        return f"{start.strftime('%b')} {start.day}-{end.day}"
    return f"{_fmt_date(start)} - {_fmt_date(end)}"


def dynamic_date_range(today, phase_number=None, week_number=None, block_key=None):
    """Compute a date range string relative to today as the course start."""
    if phase_number and phase_number in PHASE_OFFSETS:
        s, e = PHASE_OFFSETS[phase_number]
    elif week_number and week_number in WEEK_OFFSETS:
        s, e = WEEK_OFFSETS[week_number]
    elif block_key and block_key in BLOCK_OFFSETS:
        s, e = BLOCK_OFFSETS[block_key]
    else:
        return None
    return _fmt_range(today + timedelta(days=s), today + timedelta(days=e))

load_dotenv()

class PrefixMiddleware:
    """Strip SCRIPT_NAME prefix so Flask routes match, while keeping prefix in url_for."""
    def __init__(self, app, prefix):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ.get('PATH_INFO', '').startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):] or '/'
            environ['SCRIPT_NAME'] = self.prefix
        return self.app(environ, start_response)


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'sqlite:///tracker.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    # Tables are created by seed.py on startup, not here

    def apply_dynamic_dates(phases=None, weeks=None, day_blocks=None):
        """Override static date_range with dynamically computed dates based on today."""
        today = date.today()
        if phases:
            for p in phases:
                dr = dynamic_date_range(today, phase_number=p.number)
                if dr:
                    p.date_range = dr
        if weeks:
            for w in weeks:
                dr = dynamic_date_range(today, week_number=w.number)
                if dr:
                    w.date_range = dr
        if day_blocks:
            week_num_cache = {}
            for b in day_blocks:
                if b.week_id not in week_num_cache:
                    w = Week.query.get(b.week_id)
                    week_num_cache[b.week_id] = w.number if w else None
                wn = week_num_cache[b.week_id]
                if wn:
                    dr = dynamic_date_range(today, block_key=(wn, b.sort_order))
                    if dr:
                        b.date_range = dr

    def get_all_phases_with_weeks():
        """Helper to get all phases with their weeks"""
        phases = Phase.query.order_by(Phase.number).all()
        for phase in phases:
            phase.weeks = Week.query.filter_by(phase_id=phase.id).order_by(Week.number).all()
        all_weeks = [w for p in phases for w in p.weeks]
        apply_dynamic_dates(phases=phases, weeks=all_weeks)
        return phases

    def get_timeline():
        """Calculate projected finish date and delay based on progress.

        Uses the planned rate (total_items / planned_days) as the baseline.
        Measures how many items you should have done by today vs how many
        you actually did, then shifts the projected end date linearly.
        """
        started_row = CourseMeta.query.filter_by(key='started_at').first()
        planned_row = CourseMeta.query.filter_by(key='planned_end').first()
        if not started_row or not planned_row:
            return None

        today = date.today()
        started_at = today
        planned_end = today + timedelta(days=104)

        total_items = ChecklistItem.query.count()
        checked_items = ChecklistItem.query.filter(
            ChecklistItem.is_checked == True
        ).count()

        planned_days = max((planned_end - started_at).days, 1)
        items_per_day = total_items / planned_days

        if checked_items >= total_items:
            projected_end = today
        elif checked_items == 0:
            projected_end = planned_end
        else:
            remaining = total_items - checked_items
            days_to_finish = math.ceil(remaining / items_per_day)
            projected_end = today + timedelta(days=days_to_finish)

        delay_days = max((projected_end - planned_end).days, 0)

        if delay_days >= 21:
            delay_level = 'red'
        elif delay_days >= 14:
            delay_level = 'yellow'
        else:
            delay_level = 'none'

        return {
            'started_at': started_at,
            'planned_end': planned_end,
            'projected_end': projected_end,
            'total_items': total_items,
            'checked_items': checked_items,
            'delay_days': delay_days,
            'delay_level': delay_level,
        }

    @app.context_processor
    def inject_timeline():
        """Make timeline data available in every template."""
        return {'timeline': get_timeline()}

    # Routes
    @app.route('/')
    def index():
        """Redirect to Phase 1"""
        phase = Phase.query.filter_by(number=1).first()
        if phase:
            return redirect(flask_url_for('phase_view', phase_id=phase.id))
        return redirect(flask_url_for('phase_view', phase_id=1))

    @app.route('/phase/<int:phase_id>')
    def phase_view(phase_id):
        """Phase overview with mastery checklist"""
        phase = Phase.query.get_or_404(phase_id)
        weeks = Week.query.filter_by(phase_id=phase_id).order_by(Week.number).all()
        mastery_items = PhaseMastery.query.filter_by(phase_id=phase_id).order_by(PhaseMastery.sort_order).all()
        phases = get_all_phases_with_weeks()
        apply_dynamic_dates(phases=[phase], weeks=weeks)

        # Calculate progress
        total_items = ChecklistItem.query.join(DayBlock).join(Week).filter(Week.phase_id == phase_id).count()
        checked_items = ChecklistItem.query.join(DayBlock).join(Week).filter(
            Week.phase_id == phase_id,
            ChecklistItem.is_checked == True
        ).count()
        progress = int((checked_items / total_items * 100) if total_items > 0 else 0)

        return render_template(
            'phase.html',
            phase=phase,
            phases=phases,
            week=None,
            weeks=weeks,
            mastery_items=mastery_items,
            progress=progress
        )

    @app.route('/search')
    def search():
        """Search checklist items by label"""
        q = request.args.get('q', '').strip()
        results = []
        if q:
            items = (
                ChecklistItem.query
                .filter(ChecklistItem.label.ilike(f'%{q}%'))
                .join(DayBlock)
                .join(Week)
                .order_by(Week.number, DayBlock.sort_order, ChecklistItem.sort_order)
                .all()
            )
            for item in items:
                block = DayBlock.query.get(item.day_block_id)
                week = Week.query.get(block.week_id)
                phase = Phase.query.get(week.phase_id)
                results.append({'item': item, 'block': block, 'week': week, 'phase': phase})

        phases = get_all_phases_with_weeks()
        total_items = ChecklistItem.query.count()
        checked_items = ChecklistItem.query.filter(ChecklistItem.is_checked == True).count()
        progress = int((checked_items / total_items * 100) if total_items > 0 else 0)

        return render_template(
            'search.html',
            q=q,
            results=results,
            phases=phases,
            phase=phases[0] if phases else None,
            week=None,
            progress=progress
        )

    @app.route('/week/<int:week_id>')
    def week_view(week_id):
        """Week view with all day blocks and checklist items"""
        week = Week.query.get_or_404(week_id)
        phase = Phase.query.get(week.phase_id)
        day_blocks = DayBlock.query.filter_by(week_id=week_id).order_by(DayBlock.sort_order).all()
        phases = get_all_phases_with_weeks()
        apply_dynamic_dates(phases=[phase], weeks=[week], day_blocks=day_blocks)

        # Calculate overall progress
        total_items = ChecklistItem.query.count()
        checked_items = ChecklistItem.query.filter(ChecklistItem.is_checked == True).count()
        progress = int((checked_items / total_items * 100) if total_items > 0 else 0)

        return render_template(
            'week.html',
            week=week,
            phase=phase,
            phases=phases,
            day_blocks=day_blocks,
            progress=progress
        )

    # API Endpoints
    @app.route('/api/item/<int:item_id>', methods=['PATCH'])
    def toggle_item(item_id):
        """Toggle checklist item"""
        item = ChecklistItem.query.get_or_404(item_id)
        item.is_checked = not item.is_checked
        db.session.commit()
        tl = get_timeline()
        return jsonify({
            'id': item.id,
            'is_checked': item.is_checked,
            'timeline': {
                'projected_end': tl['projected_end'].strftime('%b %d, %Y'),
                'started_at_short': tl['started_at'].strftime('%b %d'),
                'delay_days': tl['delay_days'],
                'delay_level': tl['delay_level'],
            } if tl else None
        }), 200

    @app.route('/api/mastery/<int:mastery_id>', methods=['PATCH'])
    def toggle_mastery(mastery_id):
        """Toggle phase mastery item"""
        item = PhaseMastery.query.get_or_404(mastery_id)
        item.is_checked = not item.is_checked
        db.session.commit()
        return jsonify({'id': item.id, 'is_checked': item.is_checked}), 200

    @app.route('/api/block/<int:block_id>/reflection', methods=['PATCH'])
    def save_reflection(block_id):
        """Save day block reflection"""
        block = DayBlock.query.get_or_404(block_id)
        data = request.get_json()
        block.reflection = data.get('reflection', '')
        db.session.commit()
        return jsonify({'id': block.id, 'reflection': block.reflection}), 200

    prefix = os.getenv('APP_PREFIX', '')
    if prefix:
        app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
