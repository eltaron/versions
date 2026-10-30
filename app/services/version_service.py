from datetime import datetime, timezone
from app import db
from app.models.version import Version
from app.models.version_change import VersionChange
from app.models.audit_log import AuditLog


class VersionService:

    CHANGE_TYPES = [
        'New Feature', 'Bug Fix', 'Improvement', 'Security',
        'Breaking Change', 'Deprecation', 'Known Issue'
    ]

    VERSION_TYPES = ['Major', 'Minor', 'Patch']

    @staticmethod
    def suggest_next_version(current_version_number, version_type):
        if not current_version_number:
            return '1.0.0'

        parts = current_version_number.replace('v', '').split('.')
        try:
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
        except (ValueError, IndexError):
            return '1.0.0'

        if version_type == 'Major':
            return f'{major + 1}.0.0'
        elif version_type == 'Minor':
            return f'{major}.{minor + 1}.0'
        else:
            return f'{major}.{minor}.{patch + 1}'

    @staticmethod
    def parse_version(version_number):
        clean = version_number.replace('v', '').strip()
        parts = clean.split('.')
        try:
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
        except (ValueError, IndexError):
            major, minor, patch = 0, 0, 0
        return major, minor, patch

    @staticmethod
    def create_version(system_id, version_number, version_type, status,
                       release_date, description, notes, responsible_person,
                       created_by, changes_data=None):
        from app.models.system import System

        existing = Version.query.filter_by(
            system_id=system_id, version_number=version_number
        ).first()
        if existing:
            raise ValueError(f'الإصدار {version_number} موجود بالفعل لهذا النظام.')

        major, minor, patch = VersionService.parse_version(version_number)

        version = Version(
            system_id=system_id,
            version_number=version_number,
            major=major,
            minor=minor,
            patch=patch,
            version_type=version_type,
            status=status,
            release_date=release_date,
            description=description,
            notes=notes,
            responsible_person=responsible_person,
            created_by=created_by
        )
        db.session.add(version)
        db.session.flush()

        if changes_data:
            for change in changes_data:
                vc = VersionChange(
                    version_id=version.id,
                    change_type=change.get('change_type', ''),
                    title=change.get('title', ''),
                    description=change.get('description', ''),
                    priority=change.get('priority', 'Medium'),
                    created_by=created_by
                )
                db.session.add(vc)

        db.session.commit()
        return version

    @staticmethod
    def release_version(version):
        if version.status == 'Released':
            return version

        from app.models.system import System
        system = System.query.get(version.system_id)
        if system:
            old_current = system.current_version
            if old_current and old_current.id != version.id:
                pass

        version.status = 'Released'
        if not version.release_date:
            version.release_date = datetime.now(timezone.utc).date()

        db.session.commit()
        return version

    @staticmethod
    def archive_version(version):
        version.status = 'Archived'
        db.session.commit()
        return version

    @staticmethod
    def get_changes_grouped(version_id):
        changes = VersionChange.query.filter_by(version_id=version_id).all()
        grouped = {}
        for change in changes:
            ct = change.change_type
            if ct not in grouped:
                grouped[ct] = []
            grouped[ct].append(change)
        return grouped

    @staticmethod
    def compare_versions(version_a_id, version_b_id):
        changes_a = VersionChange.query.filter_by(version_id=version_a_id).all()
        changes_b = VersionChange.query.filter_by(version_id=version_b_id).all()

        ids_a = {c.id for c in changes_a}
        ids_b = {c.id for c in changes_b}

        added_ids = ids_b - ids_a
        removed_ids = ids_a - ids_b

        added = [c for c in changes_b if c.id in added_ids]
        removed = [c for c in changes_a if c.id in removed_ids]

        added_grouped = {}
        for c in added:
            ct = c.change_type
            if ct not in added_grouped:
                added_grouped[ct] = []
            added_grouped[ct].append(c)

        return {
            'added': added_grouped,
            'removed': removed,
            'version_a': Version.query.get(version_a_id),
            'version_b': Version.query.get(version_b_id),
        }
