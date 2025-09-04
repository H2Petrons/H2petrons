from flask import Blueprint, jsonify, request, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from src.models.user import User, UserRole, db
from src.models.research import ResearchPaper, ResearchStatus, ResearchCategory
from datetime import datetime
import os
import uuid

research_bp = Blueprint('research', __name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    """Generate a unique filename to prevent conflicts"""
    ext = original_filename.rsplit('.', 1)[1].lower()
    unique_id = str(uuid.uuid4())
    return f"{unique_id}.{ext}"

@research_bp.route('/research', methods=['GET'])
def get_research_papers():
    """Get all published research papers with filtering and pagination"""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'newest')
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        # Base query - only published papers
        query = ResearchPaper.query.filter_by(status=ResearchStatus.APPROVED)
        
        # Apply filters
        if category:
            try:
                category_enum = ResearchCategory(category)
                query = query.filter_by(category=category_enum)
            except ValueError:
                return jsonify({'error': 'Invalid category'}), 400
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (ResearchPaper.title.ilike(search_term)) |
                (ResearchPaper.abstract.ilike(search_term)) |
                (ResearchPaper.keywords.ilike(search_term))
            )
        
        # Apply sorting
        if sort_by == 'newest':
            query = query.order_by(ResearchPaper.published_at.desc())
        elif sort_by == 'oldest':
            query = query.order_by(ResearchPaper.published_at.asc())
        elif sort_by == 'most_viewed':
            query = query.order_by(ResearchPaper.views.desc())
        elif sort_by == 'most_liked':
            query = query.order_by(ResearchPaper.likes.desc())
        else:
            query = query.order_by(ResearchPaper.published_at.desc())
        
        # Paginate results
        papers = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'research_papers': [paper.to_public_dict() for paper in papers.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': papers.total,
                'pages': papers.pages,
                'has_next': papers.has_next,
                'has_prev': papers.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get research papers error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve research papers'}), 500

@research_bp.route('/research/<int:paper_id>', methods=['GET'])
def get_research_paper(paper_id):
    """Get a specific research paper by ID"""
    try:
        paper = ResearchPaper.query.filter_by(
            id=paper_id, 
            status=ResearchStatus.APPROVED
        ).first()
        
        if not paper:
            return jsonify({'error': 'Research paper not found'}), 404
        
        # Increment view count
        paper.views += 1
        db.session.commit()
        
        return jsonify({
            'research_paper': paper.to_public_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get research paper error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve research paper'}), 500

@research_bp.route('/research', methods=['POST'])
@jwt_required()
def submit_research_paper():
    """Submit a new research paper"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user has researcher role or higher
        if not user.has_role(UserRole.RESEARCHER):
            return jsonify({'error': 'Researcher role required to submit papers'}), 403
        
        # Validate form data
        title = request.form.get('title', '').strip()
        abstract = request.form.get('abstract', '').strip()
        keywords = request.form.get('keywords', '').strip()
        category = request.form.get('category', '').strip()
        
        if not all([title, abstract, category]):
            return jsonify({'error': 'Title, abstract, and category are required'}), 400
        
        if len(title) < 10:
            return jsonify({'error': 'Title must be at least 10 characters long'}), 400
        
        if len(abstract) < 50:
            return jsonify({'error': 'Abstract must be at least 50 characters long'}), 400
        
        # Validate category
        try:
            category_enum = ResearchCategory(category)
        except ValueError:
            return jsonify({'error': 'Invalid category'}), 400
        
        # Handle file upload
        if 'file' not in request.files:
            return jsonify({'error': 'Research paper file is required'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Generate unique filename and save file
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Create research paper record
        paper = ResearchPaper(
            title=title,
            abstract=abstract,
            keywords=keywords,
            category=category_enum,
            filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            author_id=current_user_id,
            status=ResearchStatus.PENDING
        )
        
        db.session.add(paper)
        
        # Update user research count
        user.research_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Research paper submitted successfully',
            'research_paper': paper.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Submit research paper error: {str(e)}")
        return jsonify({'error': 'Failed to submit research paper'}), 500

@research_bp.route('/research/<int:paper_id>/download', methods=['GET'])
def download_research_paper(paper_id):
    """Download a research paper file"""
    try:
        paper = ResearchPaper.query.filter_by(
            id=paper_id, 
            status=ResearchStatus.APPROVED
        ).first()
        
        if not paper:
            return jsonify({'error': 'Research paper not found'}), 404
        
        if not os.path.exists(paper.file_path):
            return jsonify({'error': 'File not found on server'}), 404
        
        # Increment download count
        paper.downloads += 1
        db.session.commit()
        
        return send_file(
            paper.file_path,
            as_attachment=True,
            download_name=paper.filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        current_app.logger.error(f"Download research paper error: {str(e)}")
        return jsonify({'error': 'Failed to download research paper'}), 500

@research_bp.route('/research/<int:paper_id>/like', methods=['POST'])
@jwt_required()
def like_research_paper(paper_id):
    """Like/unlike a research paper"""
    try:
        paper = ResearchPaper.query.filter_by(
            id=paper_id, 
            status=ResearchStatus.APPROVED
        ).first()
        
        if not paper:
            return jsonify({'error': 'Research paper not found'}), 404
        
        # For simplicity, just increment likes
        # In a full implementation, you'd track individual user likes
        paper.likes += 1
        db.session.commit()
        
        return jsonify({
            'message': 'Research paper liked successfully',
            'likes': paper.likes
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Like research paper error: {str(e)}")
        return jsonify({'error': 'Failed to like research paper'}), 500

# Admin/Moderator routes for research management

@research_bp.route('/research/pending', methods=['GET'])
@jwt_required()
def get_pending_research():
    """Get all pending research papers (moderator/admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.has_role(UserRole.MODERATOR):
            return jsonify({'error': 'Moderator access required'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)
        
        papers = ResearchPaper.query.filter_by(
            status=ResearchStatus.PENDING
        ).order_by(ResearchPaper.created_at.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'research_papers': [paper.to_dict() for paper in papers.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': papers.total,
                'pages': papers.pages,
                'has_next': papers.has_next,
                'has_prev': papers.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get pending research error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve pending research'}), 500

@research_bp.route('/research/<int:paper_id>/review', methods=['POST'])
@jwt_required()
def review_research_paper(paper_id):
    """Approve or reject a research paper (moderator/admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.has_role(UserRole.MODERATOR):
            return jsonify({'error': 'Moderator access required'}), 403
        
        paper = ResearchPaper.query.get(paper_id)
        if not paper:
            return jsonify({'error': 'Research paper not found'}), 404
        
        data = request.get_json()
        action = data.get('action')  # 'approve', 'reject', 'request_revisions'
        comments = data.get('comments', '').strip()
        
        if action not in ['approve', 'reject', 'request_revisions']:
            return jsonify({'error': 'Invalid action'}), 400
        
        # Update paper status
        if action == 'approve':
            paper.status = ResearchStatus.APPROVED
            paper.published_at = datetime.utcnow()
        elif action == 'reject':
            paper.status = ResearchStatus.REJECTED
        elif action == 'request_revisions':
            paper.status = ResearchStatus.REVISIONS_REQUIRED
        
        paper.reviewer_comments = comments
        paper.reviewed_by = current_user_id
        paper.reviewed_at = datetime.utcnow()
        paper.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': f'Research paper {action}d successfully',
            'research_paper': paper.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Review research paper error: {str(e)}")
        return jsonify({'error': 'Failed to review research paper'}), 500

@research_bp.route('/research/my-papers', methods=['GET'])
@jwt_required()
def get_my_research_papers():
    """Get current user's research papers"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)
        
        papers = ResearchPaper.query.filter_by(
            author_id=current_user_id
        ).order_by(ResearchPaper.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'research_papers': [paper.to_dict() for paper in papers.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': papers.total,
                'pages': papers.pages,
                'has_next': papers.has_next,
                'has_prev': papers.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get my research papers error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve your research papers'}), 500

@research_bp.route('/research/categories', methods=['GET'])
def get_research_categories():
    """Get all available research categories"""
    try:
        categories = [
            {
                'value': category.value,
                'label': category.value.replace('_', ' ').title()
            }
            for category in ResearchCategory
        ]
        
        return jsonify({
            'categories': categories
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get research categories error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve categories'}), 500

@research_bp.route('/research/stats', methods=['GET'])
def get_research_stats():
    """Get research statistics"""
    try:
        total_papers = ResearchPaper.query.filter_by(status=ResearchStatus.APPROVED).count()
        pending_papers = ResearchPaper.query.filter_by(status=ResearchStatus.PENDING).count()
        total_downloads = db.session.query(db.func.sum(ResearchPaper.downloads)).scalar() or 0
        total_views = db.session.query(db.func.sum(ResearchPaper.views)).scalar() or 0
        
        # Category breakdown
        category_stats = []
        for category in ResearchCategory:
            count = ResearchPaper.query.filter_by(
                category=category, 
                status=ResearchStatus.APPROVED
            ).count()
            category_stats.append({
                'category': category.value,
                'count': count
            })
        
        return jsonify({
            'total_papers': total_papers,
            'pending_papers': pending_papers,
            'total_downloads': total_downloads,
            'total_views': total_views,
            'category_breakdown': category_stats
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get research stats error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve research statistics'}), 500

