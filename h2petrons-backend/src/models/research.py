from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
from src.models.user import db

class ResearchStatus(Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISIONS_REQUIRED = "revisions_required"

class ResearchCategory(Enum):
    TECHNICAL = "technical"
    STRATEGY = "strategy"
    HISTORICAL = "historical"
    AERODYNAMICS = "aerodynamics"
    DATA_ANALYSIS = "data_analysis"
    PERFORMANCE = "performance"

class ResearchPaper(db.Model):
    __tablename__ = 'research_papers'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.String(500), nullable=True)
    category = db.Column(db.Enum(ResearchCategory), nullable=False)
    status = db.Column(db.Enum(ResearchStatus), default=ResearchStatus.PENDING, nullable=False)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', foreign_keys=[author_id], backref=db.backref('research_papers', lazy=True))
    
    # Statistics
    views = db.Column(db.Integer, default=0, nullable=False)
    downloads = db.Column(db.Integer, default=0, nullable=False)
    likes = db.Column(db.Integer, default=0, nullable=False)
    
    # Review information
    reviewer_comments = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<ResearchPaper {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'abstract': self.abstract,
            'keywords': self.keywords,
            'category': self.category.value if self.category else None,
            'status': self.status.value if self.status else None,
            'filename': self.filename,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'email': self.author.email
            } if self.author else None,
            'views': self.views,
            'downloads': self.downloads,
            'likes': self.likes,
            'reviewer_comments': self.reviewer_comments,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None
        }
    
    def to_public_dict(self):
        """Returns a public version without sensitive information"""
        return {
            'id': self.id,
            'title': self.title,
            'abstract': self.abstract,
            'keywords': self.keywords,
            'category': self.category.value if self.category else None,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'author': {
                'username': self.author.username
            } if self.author else None,
            'views': self.views,
            'downloads': self.downloads,
            'likes': self.likes
        }

