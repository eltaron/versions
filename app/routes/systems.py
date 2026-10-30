from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.system import System
from app.services.audit_service import AuditService

systems_bp = Blueprint('systems', __name__, url_prefix='/systems')


@systems_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '').strip()
    system_type = request.args.get('type', '').strip()
    status = request.args.get('status', '').strip()

    query = System.query

    if search:
        query = query.filter(
            db.or_(
                System.name.ilike(f'%{search}%'),
                System.code.ilike(f'%{search}%'),
                System.description.ilike(f'%{search}%'),
                System.owner.ilike(f'%{search}%'),
            )
        )

    if system_type:
        query = query.filter_by(system_type=system_type)

    if status:
        query = query.filter_by(status=status)

    systems = query.order_by(System.name).all()

    system_data = []
    for system in systems:
        current = system.current_version
        system_data.append({
            'system': system,
            'current_version': current,
        })

    return render_template('systems/index.html',
                           system_data=system_data,
                           search=search,
                           selected_type=system_type,
                           selected_status=status)


@systems_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip()
        system_type = request.form.get('system_type', '').strip()
        description = request.form.get('description', '').strip()
        owner = request.form.get('owner', '').strip()
        department = request.form.get('department', '').strip()
        technology = request.form.get('technology', '').strip()
        platform = request.form.get('platform', '').strip()
        repository_url = request.form.get('repository_url', '').strip()
        documentation_url = request.form.get('documentation_url', '').strip()
        status = request.form.get('status', 'Active')

        if not name or not code or not system_type:
            flash('الاسم والكود والنوع مطلوبة.', 'danger')
            return render_template('systems/create.html')

        existing = System.query.filter_by(code=code).first()
        if existing:
            flash(f'يوجد نظام بالفعل بالكود "{code}".', 'danger')
            return render_template('systems/create.html')

        system = System(
            name=name,
            code=code,
            system_type=system_type,
            description=description,
            owner=owner,
            department=department,
            technology=technology,
            platform=platform,
            repository_url=repository_url,
            documentation_url=documentation_url,
            status=status
        )
        db.session.add(system)
        db.session.commit()

        AuditService.log(
            user_id=current_user.id,
            action='create',
            entity_type='System',
            entity_id=system.id,
            description=f'System "{system.name}" created',
            ip_address=request.remote_addr
        )

        flash(f'تم إنشاء النظام "{system.name}" بنجاح.', 'success')
        return redirect(url_for('systems.details', system_id=system.id))

    return render_template('systems/create.html')


@systems_bp.route('/<int:system_id>')
@login_required
def details(system_id):
    system = System.query.get_or_404(system_id)
    current = system.current_version
    versions = system.versions.all()

    return render_template('systems/details.html',
                           system=system,
                           current_version=current,
                           versions=versions)


@systems_bp.route('/<int:system_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(system_id):
    system = System.query.get_or_404(system_id)

    if request.method == 'POST':
        system.name = request.form.get('name', system.name).strip()
        system.code = request.form.get('code', system.code).strip()
        system.system_type = request.form.get('system_type', system.system_type).strip()
        system.description = request.form.get('description', '').strip()
        system.owner = request.form.get('owner', '').strip()
        system.department = request.form.get('department', '').strip()
        system.technology = request.form.get('technology', '').strip()
        system.platform = request.form.get('platform', '').strip()
        system.repository_url = request.form.get('repository_url', '').strip()
        system.documentation_url = request.form.get('documentation_url', '').strip()
        system.status = request.form.get('status', system.status)

        db.session.commit()

        AuditService.log(
            user_id=current_user.id,
            action='update',
            entity_type='System',
            entity_id=system.id,
            description=f'System "{system.name}" updated',
            ip_address=request.remote_addr
        )

        flash(f'تم تحديث النظام "{system.name}" بنجاح.', 'success')
        return redirect(url_for('systems.details', system_id=system.id))

    return render_template('systems/edit.html', system=system)


@systems_bp.route('/<int:system_id>/archive', methods=['POST'])
@login_required
def archive(system_id):
    system = System.query.get_or_404(system_id)
    system.status = 'Archived'
    db.session.commit()

    AuditService.log(
        user_id=current_user.id,
        action='archive',
        entity_type='System',
        entity_id=system.id,
        description=f'System "{system.name}" archived',
        ip_address=request.remote_addr
    )

    flash(f'تم أرشفة النظام "{system.name}".', 'info')
    return redirect(url_for('systems.index'))
