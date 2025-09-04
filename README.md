# H2PETRONS - Formula 1 Research Hub

A comprehensive website for Formula 1 research, community engagement, and news updates. Built with modern web technologies and designed with a sleek, professional aesthetic inspired by Mercedes-AMG F1 Team.

## Features

### 🏎️ Core Functionality
- **Research Library**: Browse and submit F1 research papers with peer review system
- **Community Hub**: Discussion forums, interest groups, and events
- **News & Schedule**: Latest F1 news, race schedule, and results
- **User Approval System**: Owner-moderated research submissions
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices

### 🎨 Design Elements
- **Color Scheme**: Black, red, silver, and teal accent colors
- **Typography**: Inter font family for modern, clean appearance
- **Interactive Elements**: Hover effects, smooth transitions, and animations
- **Professional Layout**: Grid-based design with consistent spacing

### 📱 Pages Included
1. **Homepage** (`index.html`) - Hero section, featured research, community highlights
2. **Research** (`research.html`) - Research library with filtering and submission form
3. **Community** (`community.html`) - Forums, groups, events, and guidelines
4. **News & Schedule** (`news.html`) - F1 news, race calendar, and standings
5. **About** (`about.html`) - Mission, team, values, and contact information

## File Structure

```
h2petrons-website/
├── index.html              # Homepage
├── research.html           # Research library page
├── community.html          # Community hub page
├── news.html              # News and schedule page
├── about.html             # About page
├── styles/
│   └── main.css           # Main stylesheet
├── scripts/
│   └── main.js            # JavaScript functionality
├── images/                # Image assets directory
└── README.md              # This file
```

## Setup Instructions

### 1. Basic Setup
1. Extract the zip file to your web server directory
2. Ensure all files maintain their directory structure
3. Open `index.html` in a web browser to view the site

### 2. Web Server Deployment
For optimal performance, serve the files through a web server:

**Apache/Nginx:**
- Copy files to your web root directory (e.g., `/var/www/html/`)
- Ensure proper file permissions (644 for files, 755 for directories)

**Local Development:**
- Use Python: `python -m http.server 8000`
- Use Node.js: `npx serve .`
- Use PHP: `php -S localhost:8000`

### 3. Customization

#### Colors
Edit the CSS variables in `styles/main.css`:
```css
:root {
    --primary-black: #000000;
    --racing-red: #DC143C;
    --silver: #C0C0C0;
    --pure-white: #FFFFFF;
    --teal-accent: #00D2BE;
}
```

#### Content
- Update text content directly in HTML files
- Replace placeholder images in the `images/` directory
- Modify research papers and community content as needed

#### Functionality
- Form submissions currently show demo behavior
- Connect forms to your backend API by modifying `scripts/main.js`
- Implement user authentication and database integration as needed

## Technical Specifications

### Dependencies
- **Fonts**: Google Fonts (Inter family)
- **Icons**: Font Awesome 6.0.0
- **CSS**: Modern CSS3 with CSS Grid and Flexbox
- **JavaScript**: Vanilla ES6+ (no frameworks required)

### Browser Support
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

### Performance Features
- Optimized CSS with efficient selectors
- Minimal JavaScript for fast loading
- Responsive images and layouts
- Smooth animations and transitions

## Key Features Implementation

### Research Approval System
The website includes a comprehensive research submission system:
- Multi-step submission form with file upload
- Category-based organization
- Peer review workflow visualization
- Expert evaluation process

### Community Building
- Discussion forums organized by topic
- Interest groups for specialized discussions
- Event calendar and virtual meetups
- Member profiles and contribution tracking

### News Integration
- Latest F1 news with categorization
- Race schedule with countdown timers
- Championship standings and results
- Interactive calendar view

## Customization Guide

### Adding New Research Categories
1. Update the category options in `research.html`
2. Add corresponding CSS classes in `main.css`
3. Update filter functionality in `main.js`

### Modifying Community Groups
1. Edit the groups section in `community.html`
2. Update group avatars in the `images/` directory
3. Adjust grid layout if needed in CSS

### Updating Race Schedule
1. Modify race data in `news.html`
2. Update countdown timers in JavaScript
3. Add new flag images for countries

## Security Considerations

### File Uploads
- Implement server-side validation for research paper uploads
- Restrict file types to PDF only
- Scan uploaded files for malware
- Limit file sizes appropriately

### User Input
- Sanitize all form inputs on the server side
- Implement CSRF protection for forms
- Use prepared statements for database queries
- Validate email addresses and other user data

### Content Moderation
- Implement approval workflow for research submissions
- Add content filtering for forum discussions
- Create admin panel for content management
- Set up automated spam detection

## Future Enhancements

### Phase 1 Improvements
- User registration and authentication system
- Database integration for dynamic content
- Real-time chat for community discussions
- Advanced search functionality

### Phase 2 Features
- Mobile app development
- API integration with F1 data sources
- Machine learning for research recommendations
- Video content support

### Phase 3 Expansion
- Multi-language support
- Advanced analytics dashboard
- Integration with social media platforms
- Premium membership features

## Support and Maintenance

### Regular Updates
- Keep Font Awesome and Google Fonts updated
- Monitor browser compatibility
- Update F1 data and schedules regularly
- Maintain security patches

### Performance Monitoring
- Monitor page load times
- Optimize images and assets
- Implement caching strategies
- Track user engagement metrics

## Contact Information

For technical support or customization requests:
- Email: support@h2petrons.com
- Community Forums: Available on the website
- Documentation: This README file

## License

This website template is provided for the H2PETRONS project. All F1-related content should respect Formula 1 trademarks and licensing requirements.

---

**Built with passion for Formula 1 and community engagement** 🏁

