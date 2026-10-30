from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.system import System
from app.models.version import Version
from app.models.version_change import VersionChange
from app.services.version_service import VersionService
from app.services.audit_service import AuditService

versions_bp = Blueprint('versions', __name__, url_prefix='/versions')


@versions_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    system_id = request.args.get('system_id', type=int) or request.form.get('system_id', type=int)
    systems = System.query.filter(System.status != 'Archived').order_by(System.name).all()

    current_version = None
    suggested_version = None
    if system_id:
        system = System.query.get(system_id)
        if system:
            current_version = system.current_version
            if current_version:
                suggested_version = VersionService.suggest_next_version(
                    current_version.version_number, 'Minor'
                )

    if request.method == 'POST':
        system_id = request.form.get('system_id', type=int)
        version_number = request.form.get('version_number', '').strip()
        version_type = request.form.get('version_type', '').strip()
        release_date_str = request.form.get('release_date', '').strip()
        status = request.form.get('status', 'Draft')
        description = request.form.get('description', '').strip()
        notes = request.form.get('notes', '').strip()
        responsible_person = request.form.get('responsible_person', '').strip()

        release_date = None
        if release_date_str:
            try:
                release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        changes_data = []
        change_types = request.form.getlist('change_type[]')
        change_titles = request.form.getlist('change_title[]')
        change_descriptions = request.form.getlist('change_description[]')

        for i in range(len(change_titles)):
            if change_titles[i].strip():
                ct = change_types[i] if i < len(change_types) else 'New Feature'
                cd = change_descriptions[i] if i < len(change_descriptions) else ''
                changes_data.append({
                    'change_type': ct,
                    'title': change_titles[i].strip(),
                    'description': cd.strip(),
                    'priority': 'Medium'
                })

        if not system_id:
            flash('يرجى اختيار نظام.', 'danger')
            return render_template('versions/create.html',
                                   systems=systems, current_version=current_version,
                                   suggested_version=suggested_version,
                                   change_types=VersionService.CHANGE_TYPES,
                                   version_types=VersionService.VERSION_TYPES)

        if not version_number:
            flash('رقم الإصدار مطلوب.', 'danger')
            return render_template('versions/create.html',
                                   systems=systems, current_version=current_version,
                                   suggested_version=suggested_version,
                                   change_types=VersionService.CHANGE_TYPES,
                                   version_types=VersionService.VERSION_TYPES)

        try:
            version = VersionService.create_version(
                system_id=system_id,
                version_number=version_number,
                version_type=version_type,
                status=status,
                release_date=release_date,
                description=description,
                notes=notes,
                responsible_person=responsible_person,
                created_by=current_user.id,
                changes_data=changes_data
            )

            action = 'create'
            if status == 'Released':
                action = 'release'

            AuditService.log(
                user_id=current_user.id,
                action=action,
                entity_type='Version',
                entity_id=version.id,
                description=f'Version {version.version_number} created for system',
                ip_address=request.remote_addr
            )

            flash(f'تم إنشاء الإصدار {version.version_number} بنجاح.', 'success')
            return redirect(url_for('versions.details', version_id=version.id))

        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('versions/create.html',
                                   systems=systems, current_version=current_version,
                                   suggested_version=suggested_version,
                                   system_id=system_id,
                                   change_types=VersionService.CHANGE_TYPES,
                                   version_types=VersionService.VERSION_TYPES)

    return render_template('versions/create.html',
                           systems=systems,
                           current_version=current_version,
                           suggested_version=suggested_version,
                           system_id=system_id,
                           change_types=VersionService.CHANGE_TYPES,
                           version_types=VersionService.VERSION_TYPES)


@versions_bp.route('/<int:version_id>')
@login_required
def details(version_id):
    version = Version.query.get_or_404(version_id)
    system = System.query.get(version.system_id)
    changes_grouped = VersionService.get_changes_grouped(version_id)
    return render_template('versions/details.html',
                           version=version,
                           system=system,
                           changes_grouped=changes_grouped)


@versions_bp.route('/<int:version_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(version_id):
    version = Version.query.get_or_404(version_id)
    system = System.query.get(version.system_id)
    existing_changes = VersionChange.query.filter_by(version_id=version_id).all()

    if request.method == 'POST':
        version.version_number = request.form.get('version_number', version.version_number).strip()
        version.version_type = request.form.get('version_type', version.version_type)
        version.description = request.form.get('description', '').strip()
        version.notes = request.form.get('notes', '').strip()
        version.responsible_person = request.form.get('responsible_person', '').strip()

        major, minor, patch = VersionService.parse_version(version.version_number)
        version.major = major
        version.minor = minor
        version.patch = patch

        release_date_str = request.form.get('release_date', '').strip()
        if release_date_str:
            try:
                version.release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        existing_change_ids = [int(cid) for cid in request.form.getlist('existing_change_ids[]') if cid]
        delete_change_ids = [int(cid) for cid in request.form.getlist('delete_change_ids[]') if cid]

        VersionChange.query.filter(
            VersionChange.id.in_(delete_change_ids),
            VersionChange.version_id == version_id
        ).delete(synchronize_session='fetch')

        change_titles = request.form.getlist('change_title[]')
        change_descriptions = request.form.getlist('change_description[]')
        change_types = request.form.getlist('change_type[]')
        change_ids = request.form.getlist('change_id[]')

        for i in range(len(change_titles)):
            if change_titles[i].strip():
                cid = change_ids[i] if i < len(change_ids) and change_ids[i] else None
                ct = change_types[i] if i < len(change_types) else 'New Feature'
                cd = change_descriptions[i] if i < len(change_descriptions) else ''

                if cid and int(cid) in existing_change_ids and int(cid) not in delete_change_ids:
                    vc = VersionChange.query.get(int(cid))
                    if vc:
                        vc.change_type = ct
                        vc.title = change_titles[i].strip()
                        vc.description = cd.strip()
                else:
                    vc = VersionChange(
                        version_id=version_id,
                        change_type=ct,
                        title=change_titles[i].strip(),
                        description=cd.strip(),
                        priority='Medium',
                        created_by=current_user.id
                    )
                    db.session.add(vc)

        db.session.commit()

        AuditService.log(
            user_id=current_user.id,
            action='update',
            entity_type='Version',
            entity_id=version.id,
            description=f'Version {version.version_number} updated',
            ip_address=request.remote_addr
        )

        flash(f'تم تحديث الإصدار {version.version_number} بنجاح.', 'success')
        return redirect(url_for('versions.details', version_id=version.id))

    return render_template('versions/edit.html',
                           version=version,
                           system=system,
                           existing_changes=existing_changes,
                           change_types=VersionService.CHANGE_TYPES,
                           version_types=VersionService.VERSION_TYPES)


@versions_bp.route('/<int:version_id>/release', methods=['POST'])
@login_required
def release(version_id):
    version = Version.query.get_or_404(version_id)

    if version.status == 'Released':
        flash('هذا الإصدار صدر بالفعل.', 'info')
        return redirect(url_for('versions.details', version_id=version.id))

    VersionService.release_version(version)

    AuditService.log(
        user_id=current_user.id,
        action='release',
        entity_type='Version',
        entity_id=version.id,
        description=f'Version {version.version_number} released',
        ip_address=request.remote_addr
    )

    flash(f'الإصدار {version.version_number} أصبح الإصدار الحالي!', 'success')
    return redirect(url_for('versions.details', version_id=version.id))


@versions_bp.route('/<int:version_id>/archive', methods=['POST'])
@login_required
def archive(version_id):
    version = Version.query.get_or_404(version_id)

    if version.is_current:
        flash('لا يمكن أرشفة الإصدار الحالي.', 'danger')
        return redirect(url_for('versions.details', version_id=version.id))

    VersionService.archive_version(version)

    AuditService.log(
        user_id=current_user.id,
        action='archive',
        entity_type='Version',
        entity_id=version.id,
        description=f'Version {version.version_number} archived',
        ip_address=request.remote_addr
    )

    flash(f'تم أرشفة الإصدار {version.version_number}.', 'info')
    return redirect(url_for('versions.details', version_id=version.id))


@versions_bp.route('/compare', methods=['GET', 'POST'])
@login_required
def compare():
    systems = System.query.order_by(System.name).all()
    comparison = None
    system_id = request.args.get('system_id', type=int) or request.form.get('system_id', type=int)
    version_a_id = request.args.get('version_a_id', type=int) or request.form.get('version_a_id', type=int)
    version_b_id = request.args.get('version_b_id', type=int) or request.form.get('version_b_id', type=int)

    versions_a = []
    versions_b = []
    if system_id:
        versions_a = Version.query.filter_by(system_id=system_id).order_by(Version.release_date.desc().nullslast()).all()
        versions_b = versions_a

    if request.method == 'POST' and version_a_id and version_b_id:
        comparison = VersionService.compare_versions(version_a_id, version_b_id)

    return render_template('versions/compare.html',
                           systems=systems,
                           selected_system_id=system_id,
                           versions_a=versions_a,
                           versions_b=versions_b,
                           comparison=comparison,
                           version_a_id=version_a_id,
                           version_b_id=version_b_id)


@versions_bp.route('/api/versions/<int:system_id>')
@login_required
def api_versions(system_id):
    versions = Version.query.filter_by(system_id=system_id).order_by(
        Version.release_date.desc().nullslast()
    ).all()
    return jsonify([{
        'id': v.id,
        'version_number': v.version_number,
        'status': v.status,
        'release_date': v.release_date.isoformat() if v.release_date else None
    } for v in versions])


@versions_bp.route('/api/suggest-version')
@login_required
def api_suggest_version():
    system_id = request.args.get('system_id', type=int)
    version_type = request.args.get('version_type', 'Minor')

    if not system_id:
        return jsonify({'suggested': '1.0.0'})

    system = System.query.get(system_id)
    if not system or not system.current_version:
        return jsonify({'suggested': '1.0.0'})

    suggested = VersionService.suggest_next_version(
        system.current_version.version_number, version_type
    )
    return jsonify({'suggested': suggested})
