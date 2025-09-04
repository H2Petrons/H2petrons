from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, UserRole, db
from src.models.community import (
    ForumCategory, ForumTopic, ForumPost, InterestGroup, CommunityEvent, 
    EventType, group_memberships, event_attendees
)
from datetime import datetime

community_bp = Blueprint('community', __name__)

# Forum routes

@community_bp.route('/forum/categories', methods=['GET'])
def get_forum_categories():
    """Get all forum categories"""
    try:
        categories = ForumCategory.query.order_by(ForumCategory.name).all()
        
        return jsonify({
            'forum_categories': [category.to_dict() for category in categories]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get forum categories error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve forum categories'}), 500

@community_bp.route('/forum/categories', methods=['POST'])
@jwt_required()
def create_forum_category():
    """Create a new forum category (admin/moderator only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.has_role(UserRole.MODERATOR):
            return jsonify({'error': 'Moderator access required'}), 403
        
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        icon = data.get('icon', '').strip()
        
        if not name:
            return jsonify({'error': 'Category name is required'}), 400
        
        if len(name) < 3:
            return jsonify({'error': 'Category name must be at least 3 characters long'}), 400
        
        # Check if category already exists
        if ForumCategory.query.filter_by(name=name).first():
            return jsonify({'error': 'Category already exists'}), 409
        
        category = ForumCategory(
            name=name,
            description=description,
            icon=icon
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Forum category created successfully',
            'forum_category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create forum category error: {str(e)}")
        return jsonify({'error': 'Failed to create forum category'}), 500

@community_bp.route('/forum/topics', methods=['GET'])
def get_forum_topics():
    """Get forum topics with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category_id = request.args.get('category_id', type=int)
        search = request.args.get('search', '')
        
        per_page = min(per_page, 100)
        
        query = ForumTopic.query
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(ForumTopic.title.ilike(search_term))
        
        # Order by pinned first, then by last post date
        query = query.order_by(
            ForumTopic.is_pinned.desc(),
            ForumTopic.last_post_at.desc()
        )
        
        topics = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'forum_topics': [topic.to_dict() for topic in topics.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': topics.total,
                'pages': topics.pages,
                'has_next': topics.has_next,
                'has_prev': topics.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get forum topics error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve forum topics'}), 500

@community_bp.route('/forum/topics', methods=['POST'])
@jwt_required()
def create_forum_topic():
    """Create a new forum topic"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        category_id = data.get('category_id')
        
        if not all([title, content, category_id]):
            return jsonify({'error': 'Title, content, and category are required'}), 400
        
        if len(title) < 5:
            return jsonify({'error': 'Title must be at least 5 characters long'}), 400
        
        if len(content) < 10:
            return jsonify({'error': 'Content must be at least 10 characters long'}), 400
        
        # Verify category exists
        category = ForumCategory.query.get(category_id)
        if not category:
            return jsonify({'error': 'Invalid category'}), 400
        
        topic = ForumTopic(
            title=title,
            content=content,
            category_id=category_id,
            author_id=current_user_id
        )
        
        db.session.add(topic)
        
        # Update category stats
        category.topic_count += 1
        category.post_count += 1
        
        # Update user stats
        user.forum_posts_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Forum topic created successfully',
            'forum_topic': topic.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create forum topic error: {str(e)}")
        return jsonify({'error': 'Failed to create forum topic'}), 500

@community_bp.route('/forum/topics/<int:topic_id>', methods=['GET'])
def get_forum_topic(topic_id):
    """Get a specific forum topic with its posts"""
    try:
        topic = ForumTopic.query.get(topic_id)
        if not topic:
            return jsonify({'error': 'Forum topic not found'}), 404
        
        # Increment view count
        topic.views += 1
        db.session.commit()
        
        # Get posts with pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)
        
        posts = ForumPost.query.filter_by(topic_id=topic_id).order_by(
            ForumPost.created_at.asc()
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'forum_topic': topic.to_dict(),
            'posts': [post.to_dict() for post in posts.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': posts.total,
                'pages': posts.pages,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get forum topic error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve forum topic'}), 500

@community_bp.route('/forum/topics/<int:topic_id>/posts', methods=['POST'])
@jwt_required()
def create_forum_post(topic_id):
    """Create a new post in a forum topic"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        topic = ForumTopic.query.get(topic_id)
        if not topic:
            return jsonify({'error': 'Forum topic not found'}), 404
        
        if topic.is_locked:
            return jsonify({'error': 'Topic is locked'}), 403
        
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'error': 'Post content is required'}), 400
        
        if len(content) < 5:
            return jsonify({'error': 'Post content must be at least 5 characters long'}), 400
        
        post = ForumPost(
            content=content,
            topic_id=topic_id,
            author_id=current_user_id
        )
        
        db.session.add(post)
        
        # Update topic stats
        topic.reply_count += 1
        topic.last_post_at = datetime.utcnow()
        
        # Update category stats
        topic.category.post_count += 1
        
        # Update user stats
        user.forum_posts_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Forum post created successfully',
            'forum_post': post.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create forum post error: {str(e)}")
        return jsonify({'error': 'Failed to create forum post'}), 500

# Interest Groups routes

@community_bp.route('/groups', methods=['GET'])
def get_interest_groups():
    """Get all public interest groups"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        per_page = min(per_page, 100)
        
        query = InterestGroup.query.filter_by(is_public=True)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(InterestGroup.name.ilike(search_term))
        
        query = query.order_by(InterestGroup.member_count.desc())
        
        groups = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'interest_groups': [group.to_dict() for group in groups.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': groups.total,
                'pages': groups.pages,
                'has_next': groups.has_next,
                'has_prev': groups.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get interest groups error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve interest groups'}), 500

@community_bp.route('/groups', methods=['POST'])
@jwt_required()
def create_interest_group():
    """Create a new interest group"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        avatar = data.get('avatar', '').strip()
        is_public = data.get('is_public', True)
        
        if not name:
            return jsonify({'error': 'Group name is required'}), 400
        
        if len(name) < 3:
            return jsonify({'error': 'Group name must be at least 3 characters long'}), 400
        
        # Check if group already exists
        if InterestGroup.query.filter_by(name=name).first():
            return jsonify({'error': 'Group name already exists'}), 409
        
        group = InterestGroup(
            name=name,
            description=description,
            avatar=avatar,
            is_public=is_public,
            creator_id=current_user_id,
            member_count=1  # Creator is automatically a member
        )
        
        db.session.add(group)
        db.session.flush()  # Get the group ID
        
        # Add creator as member
        membership = group_memberships.insert().values(
            user_id=current_user_id,
            group_id=group.id
        )
        db.session.execute(membership)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Interest group created successfully',
            'interest_group': group.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create interest group error: {str(e)}")
        return jsonify({'error': 'Failed to create interest group'}), 500

# Community Events routes

@community_bp.route('/events', methods=['GET'])
def get_community_events():
    """Get upcoming community events"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        event_type = request.args.get('type', '')
        
        per_page = min(per_page, 100)
        
        # Only show future events
        query = CommunityEvent.query.filter(
            CommunityEvent.start_time >= datetime.utcnow()
        )
        
        if event_type:
            try:
                type_enum = EventType(event_type)
                query = query.filter_by(event_type=type_enum)
            except ValueError:
                return jsonify({'error': 'Invalid event type'}), 400
        
        query = query.order_by(CommunityEvent.start_time.asc())
        
        events = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'community_events': [event.to_dict() for event in events.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': events.total,
                'pages': events.pages,
                'has_next': events.has_next,
                'has_prev': events.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get community events error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve community events'}), 500

@community_bp.route('/events', methods=['POST'])
@jwt_required()
def create_community_event():
    """Create a new community event"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        event_type = data.get('event_type', '').strip()
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        location = data.get('location', '').strip()
        max_attendees = data.get('max_attendees')
        
        if not all([title, description, event_type, start_time]):
            return jsonify({'error': 'Title, description, event type, and start time are required'}), 400
        
        if len(title) < 5:
            return jsonify({'error': 'Title must be at least 5 characters long'}), 400
        
        # Validate event type
        try:
            type_enum = EventType(event_type)
        except ValueError:
            return jsonify({'error': 'Invalid event type'}), 400
        
        # Parse datetime
        try:
            start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_datetime = None
            if end_time:
                end_datetime = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid datetime format'}), 400
        
        # Validate start time is in the future
        if start_datetime <= datetime.utcnow():
            return jsonify({'error': 'Event start time must be in the future'}), 400
        
        event = CommunityEvent(
            title=title,
            description=description,
            event_type=type_enum,
            start_time=start_datetime,
            end_time=end_datetime,
            location=location,
            max_attendees=max_attendees,
            organizer_id=current_user_id
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'message': 'Community event created successfully',
            'community_event': event.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create community event error: {str(e)}")
        return jsonify({'error': 'Failed to create community event'}), 500

@community_bp.route('/events/<int:event_id>/attend', methods=['POST'])
@jwt_required()
def attend_event(event_id):
    """Register to attend an event"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        event = CommunityEvent.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Check if event is full
        if event.max_attendees and event.attendee_count >= event.max_attendees:
            return jsonify({'error': 'Event is full'}), 400
        
        # Check if user is already attending
        existing_attendance = db.session.execute(
            event_attendees.select().where(
                (event_attendees.c.user_id == current_user_id) &
                (event_attendees.c.event_id == event_id)
            )
        ).first()
        
        if existing_attendance:
            return jsonify({'error': 'Already registered for this event'}), 409
        
        # Add attendance
        attendance = event_attendees.insert().values(
            user_id=current_user_id,
            event_id=event_id
        )
        db.session.execute(attendance)
        
        # Update attendee count
        event.attendee_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Successfully registered for event'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Attend event error: {str(e)}")
        return jsonify({'error': 'Failed to register for event'}), 500

@community_bp.route('/community/stats', methods=['GET'])
def get_community_stats():
    """Get community statistics"""
    try:
        total_topics = ForumTopic.query.count()
        total_posts = ForumPost.query.count()
        total_groups = InterestGroup.query.filter_by(is_public=True).count()
        upcoming_events = CommunityEvent.query.filter(
            CommunityEvent.start_time >= datetime.utcnow()
        ).count()
        
        return jsonify({
            'total_topics': total_topics,
            'total_posts': total_posts,
            'total_groups': total_groups,
            'upcoming_events': upcoming_events
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get community stats error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve community statistics'}), 500

