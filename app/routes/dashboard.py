from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models.system import System
from app.services.report_service import ReportService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    stats = ReportService.dashboard_stats()
    systems = System.query.filter(
        System.status.in_(['Active', 'Maintenance'])
    ).order_by(System.name).all()

    system_data = []
    for system in systems:
        current = system.current_version
        system_data.append({
            'system': system,
            'current_version': current,
        })

    return render_template('dashboard/index.html',
                           stats=stats,
                           system_data=system_data)
