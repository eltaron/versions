from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.services.audit_service import AuditService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and user.is_active and user.check_password(password):
            login_user(user)
            AuditService.log(
                user_id=user.id,
                action='login',
                entity_type='User',
                entity_id=user.id,
                description=f'{user.username} logged in',
                ip_address=request.remote_addr
            )
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))

        flash('البريد الإلكتروني أو كلمة المرور غير صحيحة.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    AuditService.log(
        user_id=current_user.id,
        action='logout',
        entity_type='User',
        entity_id=current_user.id,
        description=f'{current_user.username} logged out',
        ip_address=request.remote_addr
    )
    logout_user()
    flash('تم تسجيل الخروج بنجاح.', 'info')
    return redirect(url_for('auth.login'))
