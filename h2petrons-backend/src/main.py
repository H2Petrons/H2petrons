import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models.user import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.research import research_bp
from src.routes.news import news_bp
from src.routes.community import community_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string-change-in-production'

# Enable CORS for all routes
CORS(app, origins="*")

# Initialize JWT
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(research_bp, url_prefix='/api')
app.register_blueprint(news_bp, url_prefix='/api')
app.register_blueprint(community_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

# Import all models to ensure they're registered with SQLAlchemy
from src.models.research import ResearchPaper
from src.models.news import NewsArticle
from src.models.community import ForumCategory, ForumTopic, ForumPost, InterestGroup, CommunityEvent

with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


def create_default_data():
    """Create default categories and sample data"""
    
    # Create forum categories
    from src.models.community import ForumCategory
    if not ForumCategory.query.first():
        categories = [
            ForumCategory(name="General Discussion", description="General F1 and research discussions", icon="fas fa-comments"),
            ForumCategory(name="Technical Analysis", description="Technical discussions about F1 cars and performance", icon="fas fa-cogs"),
            ForumCategory(name="Research Collaboration", description="Collaborate on research projects", icon="fas fa-users"),
            ForumCategory(name="News & Updates", description="Latest F1 news and updates", icon="fas fa-newspaper"),
        ]
        
        for category in categories:
            db.session.add(category)
    
    # Create sample admin user
    from src.models.user import User, UserRole
    from werkzeug.security import generate_password_hash
    
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            email='admin@h2petrons.com',
            first_name='Admin',
            last_name='User',
            password_hash=generate_password_hash('admin123'),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.session.add(admin_user)
    
    # Create sample news articles
    from src.models.news import NewsArticle, NewsCategory, NewsStatus
    
    if not NewsArticle.query.first():
        sample_articles = [
            {
                'title': 'H2PETRONS Platform Launch: Revolutionizing F1 Research',
                'content': 'We are excited to announce the launch of H2PETRONS, a comprehensive platform for Formula 1 research and community collaboration. Our platform brings together researchers, analysts, and F1 enthusiasts to share knowledge and advance understanding of the sport.',
                'excerpt': 'H2PETRONS launches as the premier platform for F1 research collaboration.',
                'category': NewsCategory.GENERAL,
                'status': NewsStatus.PUBLISHED,
                'author_id': 1
            },
            {
                'title': '2024 Season Analysis: Aerodynamic Innovations',
                'content': 'The 2024 Formula 1 season has brought significant aerodynamic innovations. Teams have pushed the boundaries of ground effect technology, leading to improved performance and closer racing. Our research community has been analyzing these developments.',
                'excerpt': 'Comprehensive analysis of aerodynamic innovations in the 2024 F1 season.',
                'category': NewsCategory.TECHNICAL,
                'status': NewsStatus.PUBLISHED,
                'author_id': 1
            },
            {
                'title': 'Community Milestone: 1000+ Research Papers Submitted',
                'content': 'We are proud to announce that our community has submitted over 1000 research papers covering various aspects of Formula 1. From aerodynamics to strategy analysis, our researchers continue to contribute valuable insights to the sport.',
                'excerpt': 'H2PETRONS community reaches milestone of 1000+ research papers.',
                'category': NewsCategory.COMMUNITY,
                'status': NewsStatus.PUBLISHED,
                'author_id': 1
            }
        ]
        
        for article_data in sample_articles:
            article = NewsArticle(**article_data)
            db.session.add(article)
    
    # Create sample research papers
    from src.models.research import ResearchPaper, ResearchCategory, ResearchStatus
    
    if not ResearchPaper.query.first():
        sample_papers = [
            {
                'title': 'Aerodynamic Efficiency Analysis of 2024 F1 Cars',
                'abstract': 'This paper presents a comprehensive analysis of aerodynamic efficiency in 2024 Formula 1 cars, focusing on the impact of ground effect regulations on overall performance. Using computational fluid dynamics and wind tunnel data, we examine how teams have optimized their designs.',
                'category': ResearchCategory.AERODYNAMICS,
                'author_id': 1,
                'status': ResearchStatus.APPROVED,
                'filename': 'aerodynamic_analysis_2024.pdf',
                'file_path': '/uploads/aerodynamic_analysis_2024.pdf',
                'views': 1250,
                'downloads': 89,
                'likes': 45
            },
            {
                'title': 'Strategic Analysis of Pit Stop Timing in Modern F1',
                'abstract': 'An in-depth statistical analysis of pit stop strategies and their correlation with race outcomes across multiple seasons. This research identifies optimal timing windows and factors that influence strategic decisions during races.',
                'category': ResearchCategory.STRATEGY,
                'author_id': 1,
                'status': ResearchStatus.APPROVED,
                'filename': 'pit_stop_strategy_analysis.pdf',
                'file_path': '/uploads/pit_stop_strategy_analysis.pdf',
                'views': 980,
                'downloads': 67,
                'likes': 32
            },
            {
                'title': 'Evolution of F1 Safety Measures: A Historical Perspective',
                'abstract': 'A comprehensive review of safety improvements in Formula 1 from 1950 to 2024, highlighting key innovations, regulatory changes, and their impact on driver safety and race outcomes.',
                'category': ResearchCategory.HISTORICAL,
                'author_id': 1,
                'status': ResearchStatus.APPROVED,
                'filename': 'f1_safety_evolution.pdf',
                'file_path': '/uploads/f1_safety_evolution.pdf',
                'views': 1450,
                'downloads': 112,
                'likes': 78
            }
        ]
        
        for paper_data in sample_papers:
            paper = ResearchPaper(**paper_data)
            db.session.add(paper)
    
    try:
        db.session.commit()
        print("Default data created successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating default data: {e}")

# Create default data after database initialization
with app.app_context():
    create_default_data()

