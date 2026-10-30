from datetime import datetime, timezone
from app import db


class VersionChange(db.Model):
    __tablename__ = 'version_changes'

    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey('versions.id'), nullable=False, index=True)
    change_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), nullable=True, default='Medium')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    author = db.relationship('User', backref='changes')

    def __repr__(self):
        return f'<VersionChange {self.title} ({self.change_type})>'
