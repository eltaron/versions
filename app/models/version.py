from datetime import datetime, timezone
from app import db


class Version(db.Model):
    __tablename__ = 'versions'

    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('systems.id'), nullable=False, index=True)
    version_number = db.Column(db.String(50), nullable=False)
    major = db.Column(db.Integer, nullable=False, default=0)
    minor = db.Column(db.Integer, nullable=False, default=0)
    patch = db.Column(db.Integer, nullable=False, default=0)
    version_type = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Draft')
    release_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    responsible_person = db.Column(db.String(150), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    changes = db.relationship('VersionChange', backref='version', lazy='dynamic',
                              order_by='VersionChange.id')
    attachments = db.relationship('Attachment', backref='version', lazy='dynamic')
    creator = db.relationship('User', backref='created_versions', foreign_keys=[created_by])

    __table_args__ = (
        db.UniqueConstraint('system_id', 'version_number', name='uq_system_version'),
    )

    @property
    def is_current(self):
        if self.status != 'Released':
            return False
        from app.models.system import System
        system = System.query.get(self.system_id)
        if not system:
            return False
        cv = system.current_version
        return cv is not None and cv.id == self.id

    def __repr__(self):
        return f'<Version {self.version_number} for System {self.system_id}>'
