from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, UserRole, db
from datetime import datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users (public information only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        users = User.query.filter_by(is_active=True).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_public_dict() for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get users error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve users'}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID (public information only)"""
    try:
        user = User.query.filter_by(id=user_id, is_active=True).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_public_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get user error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve user'}), 500

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's full profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get profile error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve profile'}), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name'].strip()
        if 'last_name' in data:
            user.last_name = data['last_name'].strip()
        if 'bio' in data:
            user.bio = data['bio'].strip()
        if 'profile_picture' in data:
            user.profile_picture = data['profile_picture'].strip()
        
        # Update username if provided and not taken
        if 'username' in data:
            new_username = data['username'].strip()
            if new_username != user.username:
                if len(new_username) < 3:
                    return jsonify({'error': 'Username must be at least 3 characters long'}), 400
                
                existing_user = User.query.filter_by(username=new_username).first()
                if existing_user:
                    return jsonify({'error': 'Username already taken'}), 409
                
                user.username = new_username
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update profile error: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500

@user_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
def update_user_role(user_id):
    """Update user role (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.has_role(UserRole.ADMIN):
            return jsonify({'error': 'Admin access required'}), 403
        
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        new_role = data.get('role')
        
        if not new_role:
            return jsonify({'error': 'Role is required'}), 400
        
        try:
            role_enum = UserRole(new_role)
        except ValueError:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Prevent users from promoting themselves to admin
        if current_user_id == user_id and role_enum == UserRole.ADMIN:
            return jsonify({'error': 'Cannot modify your own admin role'}), 403
        
        target_user.role = role_enum
        target_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'User role updated successfully',
            'user': target_user.to_public_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update user role error: {str(e)}")
        return jsonify({'error': 'Failed to update user role'}), 500

@user_bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_user(user_id):
    """Deactivate user account (admin/moderator only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.has_role(UserRole.MODERATOR):
            return jsonify({'error': 'Moderator access required'}), 403
        
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent deactivating admins unless you're an admin
        if target_user.has_role(UserRole.ADMIN) and not current_user.has_role(UserRole.ADMIN):
            return jsonify({'error': 'Cannot deactivate admin users'}), 403
        
        # Prevent self-deactivation
        if current_user_id == user_id:
            return jsonify({'error': 'Cannot deactivate your own account'}), 403
        
        target_user.is_active = False
        target_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'User account deactivated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Deactivate user error: {str(e)}")
        return jsonify({'error': 'Failed to deactivate user'}), 500

@user_bp.route('/users/<int:user_id>/activate', methods=['POST'])
@jwt_required()
def activate_user(user_id):
    """Activate user account (admin/moderator only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.has_role(UserRole.MODERATOR):
            return jsonify({'error': 'Moderator access required'}), 403
        
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': 'User not found'}), 404
        
        target_user.is_active = True
        target_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'User account activated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Activate user error: {str(e)}")
        return jsonify({'error': 'Failed to activate user'}), 500

@user_bp.route('/users/search', methods=['GET'])
def search_users():
    """Search users by username"""
    try:
        query = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if not query or len(query) < 2:
            return jsonify({'error': 'Search query must be at least 2 characters'}), 400
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 50)
        
        users = User.query.filter(
            User.username.contains(query),
            User.is_active == True
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [user.to_public_dict() for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Search users error: {str(e)}")
        return jsonify({'error': 'Failed to search users'}), 500
