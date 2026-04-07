import os
from datetime import date, timedelta
import math
from flask import Flask, render_template, jsonify, request, redirect, url_for as flask_url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, Phase, Week, DayBlock, ChecklistItem, PhaseMastery, CourseMeta
from dotenv import load_dotenv

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

    def get_all_phases_with_weeks():
        """Helper to get all phases with their weeks"""
        phases = Phase.query.order_by(Phase.number).all()
        for phase in phases:
            phase.weeks = Week.query.filter_by(phase_id=phase.id).order_by(Week.number).all()
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

        started_at = date.fromisoformat(started_row.value)
        planned_end = date.fromisoformat(planned_row.value)
        today = date.today()

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
