from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
from src.models.user import db

class NewsCategory(Enum):
    RACE_PREVIEW = "race_preview"
    TECHNICAL = "technical"
    INTERVIEW = "interview"
    ANALYSIS = "analysis"
    COMMUNITY = "community"
    TEAM_NEWS = "team_news"
    GENERAL = "general"

class NewsStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class NewsArticle(db.Model):
    __tablename__ = 'news_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text, nullable=True)
    category = db.Column(db.Enum(NewsCategory), nullable=False)
    status = db.Column(db.Enum(NewsStatus), default=NewsStatus.DRAFT, nullable=False)
    
    # SEO and metadata
    slug = db.Column(db.String(255), unique=True, nullable=True)
    meta_description = db.Column(db.String(160), nullable=True)
    
    # Featured image
    featured_image = db.Column(db.String(500), nullable=True)
    featured_image_alt = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('news_articles', lazy=True))
    
    # Statistics
    views = db.Column(db.Integer, default=0, nullable=False)
    
    # Tags (simple string for now, could be normalized later)
    tags = db.Column(db.String(500), nullable=True)
    
    def __repr__(self):
        return f'<NewsArticle {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'excerpt': self.excerpt,
            'category': self.category.value if self.category else None,
            'status': self.status.value if self.status else None,
            'slug': self.slug,
            'meta_description': self.meta_description,
            'featured_image': self.featured_image,
            'featured_image_alt': self.featured_image_alt,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'email': self.author.email
            } if self.author else None,
            'views': self.views,
            'tags': self.tags.split(',') if self.tags else []
        }
    
    def to_public_dict(self):
        """Returns a public version for display"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'excerpt': self.excerpt,
            'category': self.category.value if self.category else None,
            'slug': self.slug,
            'featured_image': self.featured_image,
            'featured_image_alt': self.featured_image_alt,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'author': {
                'username': self.author.username
            } if self.author else None,
            'views': self.views,
            'tags': self.tags.split(',') if self.tags else []
        }
    
    def to_summary_dict(self):
        """Returns a summary version for lists"""
        return {
            'id': self.id,
            'title': self.title,
            'excerpt': self.excerpt,
            'category': self.category.value if self.category else None,
            'slug': self.slug,
            'featured_image': self.featured_image,
            'featured_image_alt': self.featured_image_alt,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'author': {
                'username': self.author.username
            } if self.author else None,
            'views': self.views,
            'tags': self.tags.split(',') if self.tags else []
        }

