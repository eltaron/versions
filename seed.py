import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.user import User
from app.models.system import System
from app.models.version import Version
from app.models.version_change import VersionChange


def seed():
    app = create_app('development')
    with app.app_context():
        db.create_all()

        if User.query.first():
            print('Database already seeded.')
            return

        print('Seeding database...')

        admin = User(username='admin', email='admin@company.com', full_name='Administrator', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

        user1 = User(username='ahmed', email='ahmed@company.com', full_name='Ahmed Hassan', role='user')
        user1.set_password('user123')
        db.session.add(user1)

        user2 = User(username='mohamed', email='mohamed@company.com', full_name='Mohamed Ali', role='user')
        user2.set_password('user123')
        db.session.add(user2)

        user3 = User(username='sara', email='sara@company.com', full_name='Sara Ahmed', role='user')
        user3.set_password('user123')
        db.session.add(user3)

        db.session.flush()

        systems_data = [
            {
                'name': 'HR Management System',
                'code': 'HR-SYS',
                'system_type': 'Desktop Application',
                'description': 'Comprehensive human resources management system for employee records, payroll, leave management, and performance tracking.',
                'owner': 'Ahmed Hassan',
                'department': 'Human Resources',
                'technology': 'C#, WPF, SQL Server',
                'platform': 'Windows',
                'status': 'Active',
            },
            {
                'name': 'Accounting System',
                'code': 'ACC-SYS',
                'system_type': 'Desktop Application',
                'description': 'Full-featured accounting system managing general ledger, accounts payable/receivable, financial reporting, and tax compliance.',
                'owner': 'Mohamed Ali',
                'department': 'Finance',
                'technology': 'C#, WinForms, SQL Server',
                'platform': 'Windows',
                'status': 'Active',
            },
            {
                'name': 'Inventory System',
                'code': 'INV-SYS',
                'system_type': 'Desktop Application',
                'description': 'Inventory management system tracking stock levels, warehouse operations, purchase orders, and supplier management.',
                'owner': 'Sara Ahmed',
                'department': 'Operations',
                'technology': 'Java, Swing, MySQL',
                'platform': 'Cross-Platform',
                'status': 'Active',
            },
            {
                'name': 'Company Website',
                'code': 'WEB-CORP',
                'system_type': 'Web Application',
                'description': 'Corporate website serving as the main online presence including marketing pages, career portal, and contact forms.',
                'owner': 'Ahmed Hassan',
                'department': 'Marketing',
                'technology': 'React, Node.js, MongoDB',
                'platform': 'Cloud (AWS)',
                'status': 'Active',
            },
            {
                'name': 'Employee Portal',
                'code': 'EMP-PORT',
                'system_type': 'Web Application',
                'description': 'Internal web portal for employees to view payslips, submit requests, access documents, and manage personal information.',
                'owner': 'Mohamed Ali',
                'department': 'IT',
                'technology': 'Python, Flask, PostgreSQL',
                'platform': 'Cloud (AWS)',
                'status': 'Active',
            },
        ]

        systems = []
        for sd in systems_data:
            system = System(**sd)
            db.session.add(system)
            systems.append(system)

        db.session.flush()

        # HR Management System versions
        hr = systems[0]
        hr_versions_data = [
            {'version_number': '1.0.0', 'major': 1, 'minor': 0, 'patch': 0, 'release_date': date(2025, 1, 15), 'status': 'Released', 'description': 'Initial release of HR Management System with basic employee management.', 'notes': 'First production release.', 'responsible_person': 'Ahmed Hassan'},
            {'version_number': '1.1.0', 'major': 1, 'minor': 1, 'patch': 0, 'release_date': date(2025, 3, 10), 'status': 'Released', 'description': 'Added payroll management module.', 'responsible_person': 'Ahmed Hassan'},
            {'version_number': '1.2.0', 'major': 1, 'minor': 2, 'patch': 0, 'release_date': date(2025, 5, 20), 'status': 'Released', 'description': 'Added leave management features.', 'responsible_person': 'Ahmed Hassan'},
            {'version_number': '1.2.1', 'major': 1, 'minor': 2, 'patch': 1, 'release_date': date(2025, 6, 5), 'status': 'Released', 'description': 'Bug fixes for leave calculation.', 'responsible_person': 'Mohamed Ali'},
            {'version_number': '2.0.0', 'major': 2, 'minor': 0, 'patch': 0, 'release_date': date(2025, 8, 1), 'status': 'Released', 'description': 'Major update with performance tracking module and new UI.', 'notes': 'Breaking: Updated database schema. Migration required.', 'responsible_person': 'Ahmed Hassan'},
            {'version_number': '2.1.0', 'major': 2, 'minor': 1, 'patch': 0, 'release_date': date(2025, 10, 15), 'status': 'Released', 'description': 'Added document management and reporting.', 'responsible_person': 'Sara Ahmed'},
            {'version_number': '2.2.0', 'major': 2, 'minor': 2, 'patch': 0, 'release_date': date(2025, 12, 1), 'status': 'Released', 'description': 'Holiday calendar and attendance tracking.', 'responsible_person': 'Ahmed Hassan'},
            {'version_number': '2.3.0', 'major': 2, 'minor': 3, 'patch': 0, 'release_date': date(2026, 2, 20), 'status': 'Released', 'description': 'Recruitment module and onboarding workflows.', 'responsible_person': 'Mohamed Ali'},
            {'version_number': '2.3.1', 'major': 2, 'minor': 3, 'patch': 1, 'release_date': date(2026, 3, 10), 'status': 'Released', 'description': 'Bug fixes and performance improvements.', 'responsible_person': 'Ahmed Hassan'},
            {'version_number': '2.3.2', 'major': 2, 'minor': 3, 'patch': 2, 'release_date': date(2026, 4, 5), 'status': 'Released', 'description': 'Security patches for authentication module.', 'responsible_person': 'Ahmed Hassan'},
            {'version_number': '2.4.0', 'major': 2, 'minor': 4, 'patch': 0, 'release_date': date(2026, 6, 1), 'status': 'Released', 'description': 'Employee self-service portal integration.', 'responsible_person': 'Mohamed Ali'},
            {'version_number': '2.4.1', 'major': 2, 'minor': 4, 'patch': 1, 'release_date': date(2026, 8, 15), 'status': 'Released', 'description': 'Employee management improvements and bug fixes.', 'responsible_person': 'Ahmed Hassan'},
        ]

        for i, vd in enumerate(hr_versions_data):
            v = Version(system_id=hr.id, created_by=admin.id, **vd)
            db.session.add(v)
            db.session.flush()

        db.session.flush()

        # Add changes for HR v2.4.1
        hr_v241 = Version.query.filter_by(system_id=hr.id, version_number='2.4.1').first()
        changes_v241 = [
            ('New Feature', 'Employee Search', 'Added advanced employee search with filters for department, position, and status.'),
            ('New Feature', 'Excel Export', 'Users can export employee data to Excel format.'),
            ('Bug Fix', 'Login Error', 'Fixed login failure for users with special characters in password.'),
            ('Bug Fix', 'Report Calculation', 'Fixed incorrect salary calculation in monthly reports.'),
            ('Improvement', 'Performance', 'Improved database query performance by 40%.'),
            ('Improvement', 'UI Updates', 'Modernized the employee profile interface.'),
            ('Security', 'Authentication', 'Updated authentication mechanism to support MFA.'),
            ('Known Issue', 'Export Limit', 'Export may be slow for datasets exceeding 10,000 records.'),
        ]
        for ct, title, desc in changes_v241:
            db.session.add(VersionChange(version_id=hr_v241.id, change_type=ct, title=title, description=desc, priority='Medium', created_by=admin.id))

        # Add changes for HR v2.4.0
        hr_v240 = Version.query.filter_by(system_id=hr.id, version_number='2.4.0').first()
        changes_v240 = [
            ('New Feature', 'Self-Service Portal', 'Employees can now update their personal information.'),
            ('New Feature', 'Leave Request Online', 'Online leave request submission and approval workflow.'),
            ('Improvement', 'Dashboard', 'Redesigned dashboard with key HR metrics.'),
        ]
        for ct, title, desc in changes_v240:
            db.session.add(VersionChange(version_id=hr_v240.id, change_type=ct, title=title, description=desc, priority='Medium', created_by=admin.id))

        # Accounting System versions
        acc = systems[1]
        acc_versions_data = [
            {'version_number': '1.0.0', 'major': 1, 'minor': 0, 'patch': 0, 'release_date': date(2024, 6, 1), 'status': 'Released', 'description': 'Initial release with general ledger.', 'responsible_person': 'Mohamed Ali'},
            {'version_number': '2.0.0', 'major': 2, 'minor': 0, 'patch': 0, 'release_date': date(2025, 1, 15), 'status': 'Released', 'description': 'Added accounts payable/receivable.', 'responsible_person': 'Mohamed Ali'},
            {'version_number': '3.0.0', 'major': 3, 'minor': 0, 'patch': 0, 'release_date': date(2025, 9, 1), 'status': 'Released', 'description': 'Financial reporting and tax module.', 'responsible_person': 'Mohamed Ali'},
            {'version_number': '3.1.0', 'major': 3, 'minor': 1, 'patch': 0, 'release_date': date(2026, 8, 10), 'status': 'Released', 'description': 'Multi-currency support and bank reconciliation.', 'responsible_person': 'Mohamed Ali'},
        ]

        for vd in acc_versions_data:
            db.session.add(Version(system_id=acc.id, created_by=admin.id, **vd))
        db.session.flush()

        acc_v310 = Version.query.filter_by(system_id=acc.id, version_number='3.1.0').first()
        for ct, title, desc in [
            ('New Feature', 'Multi-Currency', 'Support for transactions in multiple currencies with automatic conversion.'),
            ('New Feature', 'Bank Reconciliation', 'Automated bank reconciliation matching.'),
            ('Improvement', 'Reporting', 'Enhanced financial report generation speed.'),
        ]:
            db.session.add(VersionChange(version_id=acc_v310.id, change_type=ct, title=title, description=desc, priority='Medium', created_by=admin.id))

        # Inventory System versions
        inv = systems[2]
        inv_versions_data = [
            {'version_number': '1.0.0', 'major': 1, 'minor': 0, 'patch': 0, 'release_date': date(2025, 3, 1), 'status': 'Released', 'description': 'Initial inventory tracking system.', 'responsible_person': 'Sara Ahmed'},
            {'version_number': '1.5.0', 'major': 1, 'minor': 5, 'patch': 0, 'release_date': date(2025, 8, 15), 'status': 'Released', 'description': 'Added purchase order management.', 'responsible_person': 'Sara Ahmed'},
            {'version_number': '1.8.0', 'major': 1, 'minor': 8, 'patch': 0, 'release_date': date(2026, 4, 1), 'status': 'Released', 'description': 'Warehouse management and barcode scanning.', 'responsible_person': 'Sara Ahmed'},
            {'version_number': '1.8.2', 'major': 1, 'minor': 8, 'patch': 2, 'release_date': date(2026, 7, 20), 'status': 'Released', 'description': 'Bug fixes and stock alert improvements.', 'responsible_person': 'Sara Ahmed'},
        ]

        for vd in inv_versions_data:
            db.session.add(Version(system_id=inv.id, created_by=admin.id, **vd))
        db.session.flush()

        inv_v182 = Version.query.filter_by(system_id=inv.id, version_number='1.8.2').first()
        for ct, title, desc in [
            ('Bug Fix', 'Stock Alert', 'Fixed stock alert not triggering for low inventory items.'),
            ('Bug Fix', 'Barcode Reader', 'Fixed barcode scanner compatibility with USB devices.'),
            ('Improvement', 'Alert System', 'Improved alert notification system with email support.'),
        ]:
            db.session.add(VersionChange(version_id=inv_v182.id, change_type=ct, title=title, description=desc, priority='Medium', created_by=admin.id))

        # Company Website versions
        web = systems[3]
        web_versions_data = [
            {'version_number': '1.0.0', 'major': 1, 'minor': 0, 'patch': 0, 'release_date': date(2025, 1, 1), 'status': 'Released', 'description': 'Initial corporate website launch.', 'responsible_person': 'Ahmed Hassan'},
            {'version_number': '2.0.0', 'major': 2, 'minor': 0, 'patch': 0, 'release_date': date(2025, 6, 15), 'status': 'Released', 'description': 'Complete redesign with React framework.', 'responsible_person': 'Ahmed Hassan'},
            {'version_number': '2.5.0', 'major': 2, 'minor': 5, 'patch': 0, 'release_date': date(2026, 1, 10), 'status': 'Released', 'description': 'Career portal and job application system.', 'responsible_person': 'Ahmed Hassan'},
            {'version_number': '2.7.3', 'major': 2, 'minor': 7, 'patch': 3, 'release_date': date(2026, 8, 12), 'status': 'Released', 'description': 'SEO improvements and performance optimization.', 'responsible_person': 'Ahmed Hassan'},
        ]

        for vd in web_versions_data:
            db.session.add(Version(system_id=web.id, created_by=admin.id, **vd))
        db.session.flush()

        web_v273 = Version.query.filter_by(system_id=web.id, version_number='2.7.3').first()
        for ct, title, desc in [
            ('Improvement', 'SEO Optimization', 'Improved meta tags, structured data, and sitemap generation.'),
            ('Improvement', 'Page Speed', 'Reduced page load time by 60% with lazy loading and caching.'),
            ('Bug Fix', 'Mobile Navigation', 'Fixed hamburger menu not closing on link click.'),
            ('Security', 'Headers', 'Added security headers (CSP, HSTS, X-Frame-Options).'),
        ]:
            db.session.add(VersionChange(version_id=web_v273.id, change_type=ct, title=title, description=desc, priority='Medium', created_by=admin.id))

        # Employee Portal versions
        emp = systems[4]
        emp_versions_data = [
            {'version_number': '1.0.0', 'major': 1, 'minor': 0, 'patch': 0, 'release_date': date(2025, 9, 1), 'status': 'Released', 'description': 'Initial employee portal with payslip viewing.', 'responsible_person': 'Mohamed Ali'},
            {'version_number': '1.3.0', 'major': 1, 'minor': 3, 'patch': 0, 'release_date': date(2026, 3, 15), 'status': 'Released', 'description': 'Added document access and request submission.', 'responsible_person': 'Mohamed Ali'},
            {'version_number': '1.5.0', 'major': 1, 'minor': 5, 'patch': 0, 'release_date': date(2026, 8, 1), 'status': 'Released', 'description': 'Personal info management and notification system.', 'responsible_person': 'Mohamed Ali'},
        ]

        for vd in emp_versions_data:
            db.session.add(Version(system_id=emp.id, created_by=admin.id, **vd))
        db.session.flush()

        emp_v150 = Version.query.filter_by(system_id=emp.id, version_number='1.5.0').first()
        for ct, title, desc in [
            ('New Feature', 'Profile Management', 'Employees can update their personal details and emergency contacts.'),
            ('New Feature', 'Notifications', 'In-app notification system for leave approvals and announcements.'),
            ('Improvement', 'UI Refresh', 'Updated interface with consistent design language.'),
        ]:
            db.session.add(VersionChange(version_id=emp_v150.id, change_type=ct, title=title, description=desc, priority='Medium', created_by=admin.id))

        db.session.commit()
        print('Database seeded successfully!')
        print('Users: admin/admin123, ahmed/user123, mohamed/user123, sara/user123')


if __name__ == '__main__':
    seed()
