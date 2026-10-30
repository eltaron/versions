from datetime import datetime, timezone
from sqlalchemy import func
from app import db
from app.models.system import System
from app.models.version import Version
from app.models.version_change import VersionChange


class ReportService:

    @staticmethod
    def current_versions_report():
        systems = System.query.filter(
            System.status.in_(['Active', 'Maintenance'])
        ).order_by(System.name).all()

        results = []
        for system in systems:
            current = system.current_version
            results.append({
                'system': system,
                'current_version': current,
            })
        return results

    @staticmethod
    def version_history_report(system_id):
        system = System.query.get(system_id)
        if not system:
            return None
        versions = system.versions.order_by(Version.release_date.desc().nullslast(),
                                            Version.created_at.desc()).all()
        return {
            'system': system,
            'versions': versions,
        }

    @staticmethod
    def releases_report(start_date, end_date):
        versions = Version.query.filter(
            Version.status == 'Released',
            Version.release_date >= start_date,
            Version.release_date <= end_date
        ).order_by(Version.release_date.desc()).all()
        return versions

    @staticmethod
    def changes_report(change_type=None, system_id=None, version_id=None,
                       start_date=None, end_date=None, user_id=None):
        query = VersionChange.query

        if change_type:
            query = query.filter(VersionChange.change_type == change_type)
        if user_id:
            query = query.filter(VersionChange.created_by == user_id)
        if version_id:
            query = query.filter(VersionChange.version_id == version_id)
        elif system_id:
            version_ids = db.session.query(Version.id).filter(
                Version.system_id == system_id
            ).subquery()
            query = query.filter(VersionChange.version_id.in_(version_ids))
        if start_date:
            query = query.filter(VersionChange.created_at >= start_date)
        if end_date:
            query = query.filter(VersionChange.created_at <= end_date)

        return query.order_by(VersionChange.created_at.desc()).all()

    @staticmethod
    def dashboard_stats():
        from app.models.user import User

        total_systems = System.query.count()
        active_systems = System.query.filter_by(status='Active').count()
        total_versions = Version.query.count()
        now = datetime.now(timezone.utc)
        first_day_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        versions_this_month = Version.query.filter(
            Version.status == 'Released',
            Version.release_date >= first_day_month.date()
        ).count()
        draft_versions = Version.query.filter_by(status='Draft').count()
        archived_systems = System.query.filter_by(status='Archived').count()

        recent_releases = Version.query.filter_by(status='Released').order_by(
            Version.release_date.desc().nullslast()
        ).limit(5).all()

        return {
            'total_systems': total_systems,
            'active_systems': active_systems,
            'total_versions': total_versions,
            'versions_this_month': versions_this_month,
            'draft_versions': draft_versions,
            'archived_systems': archived_systems,
            'recent_releases': recent_releases,
        }
