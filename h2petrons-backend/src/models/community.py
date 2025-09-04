from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
from src.models.user import db

class ForumCategory(db.Model):
    __tablename__ = 'forum_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Statistics
    topic_count = db.Column(db.Integer, default=0, nullable=False)
    post_count = db.Column(db.Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f'<ForumCategory {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'topic_count': self.topic_count,
            'post_count': self.post_count
        }

class ForumTopic(db.Model):
    __tablename__ = 'forum_topics'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_pinned = db.Column(db.Boolean, default=False, nullable=False)
    is_locked = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_post_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    category_id = db.Column(db.Integer, db.ForeignKey('forum_categories.id'), nullable=False)
    category = db.relationship('ForumCategory', backref=db.backref('topics', lazy=True))
    
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('forum_topics', lazy=True))
    
    # Statistics
    views = db.Column(db.Integer, default=0, nullable=False)
    reply_count = db.Column(db.Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f'<ForumTopic {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'is_pinned': self.is_pinned,
            'is_locked': self.is_locked,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_post_at': self.last_post_at.isoformat() if self.last_post_at else None,
            'category': self.category.to_dict() if self.category else None,
            'author': {
                'id': self.author.id,
                'username': self.author.username
            } if self.author else None,
            'views': self.views,
            'reply_count': self.reply_count
        }

class ForumPost(db.Model):
    __tablename__ = 'forum_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    topic_id = db.Column(db.Integer, db.ForeignKey('forum_topics.id'), nullable=False)
    topic = db.relationship('ForumTopic', backref=db.backref('posts', lazy=True))
    
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('forum_posts', lazy=True))
    
    def __repr__(self):
        return f'<ForumPost {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'topic_id': self.topic_id,
            'author': {
                'id': self.author.id,
                'username': self.author.username
            } if self.author else None
        }

class InterestGroup(db.Model):
    __tablename__ = 'interest_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(500), nullable=True)
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', backref=db.backref('created_groups', lazy=True))
    
    # Statistics
    member_count = db.Column(db.Integer, default=0, nullable=False)
    discussion_count = db.Column(db.Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f'<InterestGroup {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'avatar': self.avatar,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'creator': {
                'id': self.creator.id,
                'username': self.creator.username
            } if self.creator else None,
            'member_count': self.member_count,
            'discussion_count': self.discussion_count
        }

# Association table for group memberships
group_memberships = db.Table('group_memberships',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('interest_groups.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow, nullable=False)
)

class EventType(Enum):
    WATCH_PARTY = "watch_party"
    PRESENTATION = "presentation"
    QA_SESSION = "qa_session"
    DISCUSSION = "discussion"
    MEETUP = "meetup"

class CommunityEvent(db.Model):
    __tablename__ = 'community_events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_type = db.Column(db.Enum(EventType), nullable=False)
    
    # Event details
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    timezone = db.Column(db.String(50), default='UTC', nullable=False)
    location = db.Column(db.String(255), nullable=True)  # Virtual link or physical location
    max_attendees = db.Column(db.Integer, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    organizer = db.relationship('User', backref=db.backref('organized_events', lazy=True))
    
    # Statistics
    attendee_count = db.Column(db.Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f'<CommunityEvent {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_type': self.event_type.value if self.event_type else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'timezone': self.timezone,
            'location': self.location,
            'max_attendees': self.max_attendees,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'organizer': {
                'id': self.organizer.id,
                'username': self.organizer.username
            } if self.organizer else None,
            'attendee_count': self.attendee_count
        }

# Association table for event attendees
event_attendees = db.Table('event_attendees',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('community_events.id'), primary_key=True),
    db.Column('registered_at', db.DateTime, default=datetime.utcnow, nullable=False)
)

