from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, UserRole, db
from src.models.news import NewsArticle, NewsCategory, NewsStatus
from datetime import datetime
import re

news_bp = Blueprint('news', __name__)

def generate_slug(title):
    """Generate URL-friendly slug from title"""
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

@news_bp.route('/news', methods=['GET'])
def get_news_articles():
    """Get all published news articles with filtering and pagination"""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'newest')
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        # Base query - only published articles
        query = NewsArticle.query.filter_by(status=NewsStatus.PUBLISHED)
        
        # Apply filters
        if category:
            try:
                category_enum = NewsCategory(category)
                query = query.filter_by(category=category_enum)
            except ValueError:
                return jsonify({'error': 'Invalid category'}), 400
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (NewsArticle.title.ilike(search_term)) |
                (NewsArticle.content.ilike(search_term)) |
                (NewsArticle.excerpt.ilike(search_term))
            )
        
        # Apply sorting
        if sort_by == 'newest':
            query = query.order_by(NewsArticle.published_at.desc())
        elif sort_by == 'oldest':
            query = query.order_by(NewsArticle.published_at.asc())
        elif sort_by == 'most_viewed':
            query = query.order_by(NewsArticle.views.desc())
        else:
            query = query.order_by(NewsArticle.published_at.desc())
        
        # Paginate results
        articles = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'news_articles': [article.to_summary_dict() for article in articles.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': articles.total,
                'pages': articles.pages,
                'has_next': articles.has_next,
                'has_prev': articles.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get news articles error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve news articles'}), 500

@news_bp.route('/news/<int:article_id>', methods=['GET'])
def get_news_article(article_id):
    """Get a specific news article by ID"""
    try:
        article = NewsArticle.query.filter_by(
            id=article_id, 
            status=NewsStatus.PUBLISHED
        ).first()
        
        if not article:
            return jsonify({'error': 'News article not found'}), 404
        
        # Increment view count
        article.views += 1
        db.session.commit()
        
        return jsonify({
            'news_article': article.to_public_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get news article error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve news article'}), 500

@news_bp.route('/news/slug/<slug>', methods=['GET'])
def get_news_article_by_slug(slug):
    """Get a specific news article by slug"""
    try:
        article = NewsArticle.query.filter_by(
            slug=slug, 
            status=NewsStatus.PUBLISHED
        ).first()
        
        if not article:
            return jsonify({'error': 'News article not found'}), 404
        
        # Increment view count
        article.views += 1
        db.session.commit()
        
        return jsonify({
            'news_article': article.to_public_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get news article by slug error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve news article'}), 500

@news_bp.route('/news/featured', methods=['GET'])
def get_featured_news():
    """Get featured news articles (latest 5)"""
    try:
        articles = NewsArticle.query.filter_by(
            status=NewsStatus.PUBLISHED
        ).order_by(NewsArticle.published_at.desc()).limit(5).all()
        
        return jsonify({
            'featured_articles': [article.to_summary_dict() for article in articles]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get featured news error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve featured news'}), 500

# Admin/Editor routes for news management

@news_bp.route('/news', methods=['POST'])
@jwt_required()
def create_news_article():
    """Create a new news article (admin/moderator only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.has_role(UserRole.MODERATOR):
            return jsonify({'error': 'Moderator access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'content', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        title = data['title'].strip()
        content = data['content'].strip()
        category = data['category'].strip()
        
        if len(title) < 5:
            return jsonify({'error': 'Title must be at least 5 characters long'}), 400
        
        if len(content) < 50:
            return jsonify({'error': 'Content must be at least 50 characters long'}), 400
        
        # Validate category
        try:
            category_enum = NewsCategory(category)
        except ValueError:
            return jsonify({'error': 'Invalid category'}), 400
        
        # Generate slug
        base_slug = generate_slug(title)
        slug = base_slug
        counter = 1
        
        # Ensure slug is unique
        while NewsArticle.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Create article
        article = NewsArticle(
            title=title,
            content=content,
            excerpt=data.get('excerpt', '').strip(),
            category=category_enum,
            slug=slug,
            meta_description=data.get('meta_description', '').strip(),
            featured_image=data.get('featured_image', '').strip(),
            featured_image_alt=data.get('featured_image_alt', '').strip(),
            tags=data.get('tags', '').strip(),
            author_id=current_user_id,
            status=NewsStatus.DRAFT
        )
        
        db.session.add(article)
        db.session.commit()
        
        return jsonify({
            'message': 'News article created successfully',
            'news_article': article.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create news article error: {str(e)}")
        return jsonify({'error': 'Failed to create news article'}), 500

@news_bp.route('/news/<int:article_id>', methods=['PUT'])
@jwt_required()
def update_news_article(article_id):
    """Update a news article (admin/moderator only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.has_role(UserRole.MODERATOR):
            return jsonify({'error': 'Moderator access required'}), 403
        
        article = NewsArticle.query.get(article_id)
        if not article:
            return jsonify({'error': 'News article not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'title' in data:
            new_title = data['title'].strip()
            if len(new_title) < 5:
                return jsonify({'error': 'Title must be at least 5 characters long'}), 400
            
            # Update slug if title changed
            if new_title != article.title:
                base_slug = generate_slug(new_title)
                slug = base_slug
                counter = 1
                
                # Ensure slug is unique (excluding current article)
                while NewsArticle.query.filter(
                    NewsArticle.slug == slug,
                    NewsArticle.id != article_id
                ).first():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                article.slug = slug
            
            article.title = new_title
        
        if 'content' in data:
            new_content = data['content'].strip()
            if len(new_content) < 50:
                return jsonify({'error': 'Content must be at least 50 characters long'}), 400
            article.content = new_content
        
        if 'excerpt' in data:
            article.excerpt = data['excerpt'].strip()
        
        if 'category' in data:
            try:
                category_enum = NewsCategory(data['category'])
                article.category = category_enum
            except ValueError:
                return jsonify({'error': 'Invalid category'}), 400
        
        if 'meta_description' in data:
            article.meta_description = data['meta_description'].strip()
        
        if 'featured_image' in data:
            article.featured_image = data['featured_image'].strip()
        
        if 'featured_image_alt' in data:
            article.featured_image_alt = data['featured_image_alt'].strip()
        
        if 'tags' in data:
            article.tags = data['tags'].strip()
        
        article.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'News article updated successfully',
            'news_article': article.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update news article error: {str(e)}")
        return jsonify({'error': 'Failed to update news article'}), 500

@news_bp.route('/news/<int:article_id>/publish', methods=['POST'])
@jwt_required()
def publish_news_article(article_id):
    """Publish a news article (admin/moderator only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.has_role(UserRole.MODERATOR):
            return jsonify({'error': 'Moderator access required'}), 403
        
        article = NewsArticle.query.get(article_id)
        if not article:
            return jsonify({'error': 'News article not found'}), 404
        
        if article.status == NewsStatus.PUBLISHED:
            return jsonify({'error': 'Article is already published'}), 400
        
        article.status = NewsStatus.PUBLISHED
        article.published_at = datetime.utcnow()
        article.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'News article published successfully',
            'news_article': article.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Publish news article error: {str(e)}")
        return jsonify({'error': 'Failed to publish news article'}), 500

@news_bp.route('/news/<int:article_id>/unpublish', methods=['POST'])
@jwt_required()
def unpublish_news_article(article_id):
    """Unpublish a news article (admin/moderator only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.has_role(UserRole.MODERATOR):
            return jsonify({'error': 'Moderator access required'}), 403
        
        article = NewsArticle.query.get(article_id)
        if not article:
            return jsonify({'error': 'News article not found'}), 404
        
        article.status = NewsStatus.DRAFT
        article.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'News article unpublished successfully',
            'news_article': article.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Unpublish news article error: {str(e)}")
        return jsonify({'error': 'Failed to unpublish news article'}), 500

@news_bp.route('/news/drafts', methods=['GET'])
@jwt_required()
def get_draft_articles():
    """Get all draft articles (admin/moderator only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.has_role(UserRole.MODERATOR):
            return jsonify({'error': 'Moderator access required'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)
        
        articles = NewsArticle.query.filter_by(
            status=NewsStatus.DRAFT
        ).order_by(NewsArticle.updated_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'news_articles': [article.to_dict() for article in articles.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': articles.total,
                'pages': articles.pages,
                'has_next': articles.has_next,
                'has_prev': articles.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get draft articles error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve draft articles'}), 500

@news_bp.route('/news/categories', methods=['GET'])
def get_news_categories():
    """Get all available news categories"""
    try:
        categories = [
            {
                'value': category.value,
                'label': category.value.replace('_', ' ').title()
            }
            for category in NewsCategory
        ]
        
        return jsonify({
            'categories': categories
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get news categories error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve categories'}), 500

@news_bp.route('/news/stats', methods=['GET'])
def get_news_stats():
    """Get news statistics"""
    try:
        total_articles = NewsArticle.query.filter_by(status=NewsStatus.PUBLISHED).count()
        draft_articles = NewsArticle.query.filter_by(status=NewsStatus.DRAFT).count()
        total_views = db.session.query(db.func.sum(NewsArticle.views)).scalar() or 0
        
        # Category breakdown
        category_stats = []
        for category in NewsCategory:
            count = NewsArticle.query.filter_by(
                category=category, 
                status=NewsStatus.PUBLISHED
            ).count()
            category_stats.append({
                'category': category.value,
                'count': count
            })
        
        return jsonify({
            'total_articles': total_articles,
            'draft_articles': draft_articles,
            'total_views': total_views,
            'category_breakdown': category_stats
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get news stats error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve news statistics'}), 500

