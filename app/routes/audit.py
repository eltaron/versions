from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models.audit_log import AuditLog

audit_bp = Blueprint('audit', __name__, url_prefix='/audit')


@audit_bp.route('/')
@login_required
def index():
    if not current_user.is_admin:
        from flask import redirect, url_for, flash
        flash('تم رفض الوصول.', 'danger')
        return redirect(url_for('dashboard.index'))

    entity_type = request.args.get('entity_type', '').strip()
    action = request.args.get('action', '').strip()

    query = AuditLog.query

    if entity_type:
        query = query.filter_by(entity_type=entity_type)
    if action:
        query = query.filter_by(action=action)

    logs = query.order_by(AuditLog.created_at.desc()).limit(500).all()

    return render_template('audit/index.html', logs=logs,
                           selected_entity_type=entity_type,
                           selected_action=action)
