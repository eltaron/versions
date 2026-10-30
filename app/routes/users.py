from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.services.audit_service import AuditService

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/')
@login_required
def index():
    if not current_user.is_admin:
        flash('تم رفض الوصول.', 'danger')
        return redirect(url_for('dashboard.index'))

    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users/index.html', users=users)


@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_admin:
        flash('تم رفض الوصول.', 'danger')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'user')

        if not username or not email or not full_name or not password:
            flash('جميع الحقول مطلوبة.', 'danger')
            return render_template('users/create.html')

        if User.query.filter_by(username=username).first():
            flash('اسم المستخدم موجود بالفعل.', 'danger')
            return render_template('users/create.html')

        if User.query.filter_by(email=email).first():
            flash('البريد الإلكتروني موجود بالفعل.', 'danger')
            return render_template('users/create.html')

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        AuditService.log(
            user_id=current_user.id,
            action='create',
            entity_type='User',
            entity_id=user.id,
            description=f'User "{user.username}" created',
            ip_address=request.remote_addr
        )

        flash(f'تم إنشاء المستخدم "{user.username}" بنجاح.', 'success')
        return redirect(url_for('users.index'))

    return render_template('users/create.html')


@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(user_id):
    if not current_user.is_admin:
        flash('تم رفض الوصول.', 'danger')
        return redirect(url_for('dashboard.index'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.full_name = request.form.get('full_name', user.full_name).strip()
        user.email = request.form.get('email', user.email).strip()
        user.role = request.form.get('role', user.role)
        user.is_active = request.form.get('is_active') in ('on', '1', 'true')

        password = request.form.get('password', '').strip()
        if password:
            user.set_password(password)

        db.session.commit()

        AuditService.log(
            user_id=current_user.id,
            action='update',
            entity_type='User',
            entity_id=user.id,
            description=f'User "{user.username}" updated',
            ip_address=request.remote_addr
        )

        flash(f'تم تحديث المستخدم "{user.username}" بنجاح.', 'success')
        return redirect(url_for('users.index'))

    return render_template('users/edit.html', user=user)


@users_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
def delete(user_id):
    if not current_user.is_admin:
        flash('تم رفض الوصول.', 'danger')
        return redirect(url_for('dashboard.index'))

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('لا يمكن حذف حسابك الخاص.', 'danger')
        return redirect(url_for('users.index'))

    username = user.username
    db.session.delete(user)
    db.session.commit()

    flash(f'تم حذف المستخدم "{username}" بنجاح.', 'success')
    return redirect(url_for('users.index'))


@users_bp.route('/<int:user_id>/toggle-active', methods=['POST'])
@login_required
def toggle_active(user_id):
    if not current_user.is_admin:
        flash('تم رفض الوصول.', 'danger')
        return redirect(url_for('dashboard.index'))

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('لا يمكن تعطيل حسابك الخاص.', 'danger')
        return redirect(url_for('users.index'))

    user.is_active = not user.is_active
    db.session.commit()

    status = 'تم تنشيطه' if user.is_active else 'تم تعطيله'
    flash(f'المستخدم "{user.username}" {status}.', 'info')
    return redirect(url_for('users.index'))
