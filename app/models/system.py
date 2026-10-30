from datetime import datetime, timezone
from app import db


class System(db.Model):
    __tablename__ = 'systems'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    system_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner = db.Column(db.String(150), nullable=True)
    department = db.Column(db.String(150), nullable=True)
    technology = db.Column(db.String(200), nullable=True)
    platform = db.Column(db.String(100), nullable=True)
    repository_url = db.Column(db.String(500), nullable=True)
    documentation_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Active')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    versions = db.relationship('Version', backref='system', lazy='dynamic',
                               order_by='Version.created_at.desc()')

    @property
    def current_version(self):
        from app.models.version import Version
        return self.versions.filter_by(status='Released').order_by(
            Version.release_date.desc(), Version.id.desc()
        ).first()

    @property
    def latest_version(self):
        return self.versions.first()

    def __repr__(self):
        return f'<System {self.name}>'
