import csv
import io
from datetime import datetime
from flask import Blueprint, render_template, request, Response
from flask_login import login_required
from app.models.system import System
from app.models.version import Version
from app.services.report_service import ReportService
from app.services.version_service import VersionService

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/')
@login_required
def index():
    return render_template('reports/index.html')


@reports_bp.route('/current-versions')
@login_required
def current_versions():
    data = ReportService.current_versions_report()
    return render_template('reports/current_versions.html', data=data)


@reports_bp.route('/current-versions/export')
@login_required
def current_versions_export():
    data = ReportService.current_versions_report()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['System Name', 'Code', 'Type', 'Current Version', 'Release Date', 'Status'])
    for item in data:
        writer.writerow([
            item['system'].name,
            item['system'].code,
            item['system'].system_type,
            item['current_version'].version_number if item['current_version'] else 'N/A',
            item['current_version'].release_date.strftime('%Y-%m-%d') if item['current_version'] and item['current_version'].release_date else 'N/A',
            item['system'].status,
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=current_versions.csv'}
    )


@reports_bp.route('/version-history', methods=['GET', 'POST'])
@login_required
def version_history():
    systems = System.query.order_by(System.name).all()
    data = None
    selected_system_id = None

    if request.method == 'POST':
        selected_system_id = request.form.get('system_id', type=int)
    else:
        selected_system_id = request.args.get('system_id', type=int)

    if selected_system_id:
        data = ReportService.version_history_report(selected_system_id)

    return render_template('reports/version_history.html',
                           systems=systems,
                           data=data,
                           selected_system_id=selected_system_id)


@reports_bp.route('/releases', methods=['GET', 'POST'])
@login_required
def releases():
    versions = []
    start_date = None
    end_date = None

    if request.method == 'POST':
        start_str = request.form.get('start_date', '').strip()
        end_str = request.form.get('end_date', '').strip()

        if start_str:
            try:
                start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        if end_str:
            try:
                end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        if start_date and end_date:
            versions = ReportService.releases_report(start_date, end_date)

    return render_template('reports/releases.html',
                           versions=versions,
                           start_date=start_date,
                           end_date=end_date)


@reports_bp.route('/changes', methods=['GET', 'POST'])
@login_required
def changes():
    systems = System.query.order_by(System.name).all()
    results = []
    filters = {}

    if request.method == 'POST':
        change_type = request.form.get('change_type', '').strip()
        system_id = request.form.get('system_id', type=int)
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()

        start_date = None
        end_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                pass
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                pass

        results = ReportService.changes_report(
            change_type=change_type or None,
            system_id=system_id,
            start_date=start_date,
            end_date=end_date
        )

        filters = {
            'change_type': change_type,
            'system_id': system_id,
            'start_date': start_date_str,
            'end_date': end_date_str,
        }

    return render_template('reports/changes.html',
                           systems=systems,
                           results=results,
                           filters=filters,
                           change_types=VersionService.CHANGE_TYPES)


@reports_bp.route('/changes/export')
@login_required
def changes_export():
    change_type = request.args.get('change_type', '').strip()
    system_id = request.args.get('system_id', type=int)

    results = ReportService.changes_report(
        change_type=change_type or None,
        system_id=system_id
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['System', 'Version', 'Change Type', 'Title', 'Description', 'Date'])

    for change in results:
        version = change.version
        system = version.system if version else None
        writer.writerow([
            system.name if system else 'N/A',
            version.version_number if version else 'N/A',
            change.change_type,
            change.title,
            change.description or '',
            change.created_at.strftime('%Y-%m-%d') if change.created_at else 'N/A',
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=changes_report.csv'}
    )
