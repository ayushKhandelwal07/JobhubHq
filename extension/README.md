# Portia AI Job Tracker - Chrome Extension

A powerful Chrome extension that automatically tracks job applications across LinkedIn, Indeed, AngelList/Wellfound, and other job platforms using AI-powered agents.

## Features

### 🤖 AI-Powered Job Tracking
- Automatically extracts job details from job posting pages
- Tracks applications across multiple platforms
- Syncs with Portia AI backend for comprehensive analytics

### 📊 Smart Data Extraction
- **LinkedIn**: Job title, company, location, salary, job insights
- **Indeed**: Job details, company ratings, posting dates
- **AngelList/Wellfound**: Startup information, equity, company stage

### 🔄 Seamless Synchronization
- Real-time sync with Portia AI platform
- Local storage for offline access
- Google Sheets integration for external tracking

### 🎯 Intelligent Features
- Auto-tracking based on user preferences
- Duplicate detection and prevention
- Job matching and scoring

## Installation

### Development Installation
1. Clone this repository
2. Open Chrome and go to `chrome://extensions/`
3. Enable "Developer mode" in the top right
4. Click "Load unpacked" and select the `extension` folder
5. The Portia AI Job Tracker icon should appear in your toolbar

### Production Installation
*(Coming soon to Chrome Web Store)*

## Setup

1. **Get API Token**: Register at [Portia AI Platform](http://localhost:3000) and get your API token
2. **Configure Extension**: Click the extension icon and go to Settings
3. **Enter API Token**: Paste your token and enable sync features
4. **Start Tracking**: Visit job pages and track automatically or manually

## Usage

### Automatic Tracking
1. Enable "Auto-track jobs" in settings
2. Visit job pages on supported platforms
3. Jobs will be tracked automatically after 2 seconds

### Manual Tracking
1. Visit any job page on supported platforms
2. Click the "🤖 Track with Portia AI" button
3. Job data will be extracted and saved

### Managing Tracked Jobs
1. Click the extension icon to open popup
2. View tracked jobs count and connection status
3. Access "View All Jobs" to see recent applications
4. Export jobs to CSV or sync to backend

## Supported Platforms

### LinkedIn Jobs
- Full job detail extraction
- Company information and insights
- Salary and benefit information
- Job application tracking

### Indeed
- Job descriptions and requirements
- Company ratings and reviews
- Posting dates and application counts
- Salary information when available

### AngelList/Wellfound
- Startup company information
- Equity and compensation details
- Company stage and size
- Skill tags and requirements

### Extensible Architecture
- Easy to add new job platforms
- Configurable extraction rules
- Platform-specific optimizations

## Configuration

### Extension Settings
- **API Token**: Your Portia AI authentication token
- **Auto-track**: Automatically track jobs when visiting pages
- **Backend Sync**: Sync tracked jobs to Portia AI platform
- **Notifications**: Show tracking notifications

### Advanced Features
- **Duplicate Detection**: Prevents tracking the same job multiple times
- **Data Validation**: Ensures extracted data quality
- **Error Handling**: Graceful handling of extraction failures
- **Performance Optimization**: Minimal impact on page loading

## Data Privacy

### Local Storage
- Job data stored locally in Chrome storage
- No data sent without explicit user consent
- User controls all sync and sharing settings

### Backend Sync
- Only enabled when user provides API token
- All communication over HTTPS
- User can disable sync at any time

### Data Security
- No sensitive personal information stored
- Only job-related public information extracted
- Compliance with Chrome extension security policies

## Development

### Project Structure
```
extension/
├── manifest.json           # Extension configuration
├── background.js          # Service worker for background tasks
├── popup.html/js          # Extension popup interface
├── content-scripts/       # Platform-specific content scripts
│   ├── linkedin.js        # LinkedIn job extraction
│   ├── indeed.js          # Indeed job extraction
│   └── angellist.js       # AngelList/Wellfound extraction
└── icons/                 # Extension icons
```

### Adding New Platforms

1. **Create Content Script**:
   ```javascript
   // content-scripts/newplatform.js
   const PLATFORM_CONFIG = {
     selectors: {
       jobTitle: ['.job-title', 'h1'],
       company: ['.company-name'],
       // ... other selectors
     }
   };
   ```

2. **Update Manifest**:
   ```json
   {
     "content_scripts": [{
       "matches": ["https://newplatform.com/jobs/*"],
       "js": ["content-scripts/newplatform.js"]
     }]
   }
   ```

3. **Add Background Support**:
   - Update URL patterns in background.js
   - Add platform-specific extraction logic

### Testing
- Test on actual job posting pages
- Verify data extraction accuracy
- Check sync functionality with backend
- Test popup interface and settings

## API Integration

### Backend Endpoints
- `POST /api/applications` - Create job application
- `GET /api/applications` - Get tracked applications
- `PUT /api/applications/{id}` - Update application status

### Authentication
- Bearer token authentication
- Token stored securely in Chrome storage
- Automatic retry on authentication failures

## Troubleshooting

### Common Issues

**Extension not tracking jobs**:
- Check if you're on a supported platform
- Verify the page has loaded completely
- Check browser console for errors

**Sync not working**:
- Verify API token is correct
- Check internet connection
- Ensure backend is accessible

**Data extraction incomplete**:
- Some platforms may have updated their HTML structure
- Report issues for platform updates

### Debug Mode
Enable Chrome developer tools and check:
- Console logs for extraction details
- Network tab for API calls
- Storage tab for local data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on target platforms
5. Submit a pull request

### Development Guidelines
- Follow existing code patterns
- Add comprehensive error handling
- Test on multiple job posting formats
- Document new features and changes

## License

This project is part of the Portia AI ecosystem and follows the same licensing terms.

## Support

For issues and feature requests:
- Check existing issues in the repository
- Create detailed bug reports with screenshots
- Include browser version and platform information

---

**Made with ❤️ for the Portia AI Hackathon by WeMakeDevs**
