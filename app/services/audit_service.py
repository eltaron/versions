from datetime import datetime, timezone
from app import db
from app.models.audit_log import AuditLog


class AuditService:

    @staticmethod
    def log(user_id, action, entity_type, entity_id=None, description=None, ip_address=None):
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=ip_address
        )
        db.session.add(entry)
        db.session.commit()
        return entry
