# H2PETRONS Website - Deployment Guide

## 🚀 Live Demo
**Deployed Website**: https://vgh0i1c11z6d.manus.space

## 📦 Package Contents

This zip file contains the complete H2PETRONS website with the following components:

### Backend (Flask Application)
- **Location**: `h2petrons-backend/src/`
- **Framework**: Flask with SQLAlchemy
- **Database**: SQLite (included with sample data)
- **Authentication**: JWT-based authentication system
- **API**: RESTful API endpoints for all features

### Frontend (Static Files)
- **Location**: `h2petrons-backend/src/static/`
- **Technology**: HTML5, CSS3, JavaScript (ES6+)
- **Design**: Responsive, mobile-friendly
- **Integration**: Connected to Flask backend APIs

### Documentation
- `testing_results.md` - Comprehensive testing report
- `backend_requirements.md` - Technical specifications
- `design_specifications.md` - Design and UI guidelines
- `website_structure.md` - Site architecture overview

## 🛠️ Local Development Setup

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Git (optional, for version control)

### Installation Steps

1. **Extract the zip file**
   ```bash
   unzip h2petrons-website-final.zip
   cd h2petrons-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python src/main.py
   ```

5. **Access the website**
   - Open your browser and go to: `http://localhost:5000`
   - The website will be fully functional with sample data

## 🌐 Production Deployment

### Option 1: Traditional Web Server
1. Set up a Linux server (Ubuntu/CentOS)
2. Install Python 3.11+ and required dependencies
3. Configure a reverse proxy (Nginx/Apache)
4. Use a WSGI server like Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
   ```

### Option 2: Cloud Platforms
- **Heroku**: Use the included `requirements.txt`
- **AWS/Google Cloud**: Deploy using their Python runtime
- **DigitalOcean**: Use App Platform for easy deployment

### Environment Variables (Production)
```bash
export SECRET_KEY="your-secret-key-here"
export JWT_SECRET_KEY="your-jwt-secret-here"
export DATABASE_URL="your-database-url"  # Optional: Use PostgreSQL in production
```

## 🔧 Configuration

### Database
- **Development**: SQLite database included with sample data
- **Production**: Easily configurable to use PostgreSQL or MySQL
- **Sample Data**: Includes users, research papers, news articles, and community content

### Authentication
- **Default Admin Account**:
  - Username: `admin`
  - Password: `admin123`
- **JWT Tokens**: 24-hour access tokens, 30-day refresh tokens

### File Uploads
- **Research Papers**: Configured for PDF uploads up to 16MB
- **Upload Directory**: `src/uploads/` (automatically created)

## 🎯 Features Overview

### ✅ Fully Functional Features

#### User Management
- User registration and login
- Role-based access control (User, Researcher, Moderator, Admin)
- Profile management
- JWT-based authentication

#### Research Platform
- Research paper submission and approval workflow
- Category-based organization (Technical, Strategy, Historical, etc.)
- Search and filtering capabilities
- View, download, and like tracking
- Peer review system

#### Community Features
- Discussion forums with categories
- Interest groups and communities
- Event management and attendance
- User statistics and leaderboards

#### News & Content
- News article publishing system
- Category-based organization
- Featured articles and announcements
- Race schedule and results integration

#### Technical Features
- RESTful API architecture
- CORS enabled for frontend integration
- Responsive design for all devices
- Real-time content loading
- Secure file upload handling

## 🔒 Security Features

- Password hashing with Werkzeug
- JWT token-based authentication
- Input validation and sanitization
- File upload security measures
- CORS configuration for API access
- Role-based access control

## 📊 Sample Data Included

### Users
- Admin user for testing and management
- Sample user profiles with different roles

### Research Papers
- 3 sample research papers with full metadata
- Different categories and approval statuses
- View/download/like statistics

### News Articles
- Platform announcements
- Technical analysis articles
- Community milestone updates

### Community Content
- Forum categories and sample discussions
- Interest groups and events
- Community statistics

## 🐛 Known Issues & Limitations

### Minor Issues
- Authentication state persistence needs improvement in frontend
- Some API error handling could be enhanced

### Future Enhancements
- Real-time notifications
- Advanced search functionality
- File preview capabilities
- Email notification system
- Social media integration

## 📞 Support & Maintenance

### Database Management
- Backup the SQLite database regularly: `src/database/app.db`
- Monitor disk space for file uploads
- Clean up old session tokens periodically

### Performance Optimization
- Consider using Redis for session management in production
- Implement database indexing for large datasets
- Use CDN for static file delivery

### Monitoring
- Monitor API response times
- Track user registration and activity
- Monitor file upload sizes and storage

## 🎨 Customization

### Branding
- Update logo and colors in `src/static/styles/main.css`
- Modify site title and metadata in HTML files
- Replace favicon in `src/static/favicon.ico`

### Content
- Modify sample data in `src/main.py` (create_default_data function)
- Update news articles and research categories
- Customize forum categories and community groups

### Functionality
- Add new API endpoints in `src/routes/`
- Extend database models in `src/models/`
- Enhance frontend features in `src/static/scripts/`

## 📈 Scaling Considerations

### Database
- Migrate to PostgreSQL for production use
- Implement database connection pooling
- Add database indexing for performance

### File Storage
- Use cloud storage (AWS S3, Google Cloud Storage) for file uploads
- Implement CDN for static file delivery
- Add file compression and optimization

### Caching
- Implement Redis for session and data caching
- Add API response caching
- Use browser caching for static assets

## 🏆 Success Metrics

The H2PETRONS platform is designed to support:
- **Research Collaboration**: Enable researchers to share and collaborate on F1 studies
- **Community Building**: Foster discussions and knowledge sharing among F1 enthusiasts
- **Knowledge Management**: Organize and categorize F1 research and analysis
- **User Engagement**: Provide interactive features to keep users engaged

## 📝 License & Credits

This website was created as a comprehensive F1 research and community platform. The codebase is modular and well-documented for easy maintenance and enhancement.

---

**Ready to deploy!** The H2PETRONS website is production-ready and includes all necessary components for a fully functional F1 research and community platform.

