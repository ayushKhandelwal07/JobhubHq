# Portia AI Job Application Platform

A comprehensive AI-powered job application and recruiting platform built for AgentHack 2025. This platform leverages Portia AI with Google Gemini to automate and enhance every aspect of the job search and recruitment process.

## Overview

The Portia AI Job Application Platform is a full-stack application that combines artificial intelligence with modern web technologies to create an advanced job search and recruitment experience. The platform features both candidate and recruiter interfaces, powered by 7 specialized Portia AI agents.

## Key Features

### AI Agents
1. **Job Application Tracker Agent** - Automatically tracks applications across LinkedIn, Indeed, AngelList
2. **Job Application Agent** - Auto-applies to relevant jobs and sends recruiter outreach
3. **Career Roadmap Agent** - Creates personalized career development plans
4. **Professional Networking Agent** - Expands professional networks through targeted LinkedIn outreach
5. **Candidate Analysis Agent** - Processes and evaluates incoming candidate applications
6. **Interview Coordination Agent** - Manages interview coordination and preparation
7. **Market Analytics Agent** - Provides comprehensive job search analytics and insights

### Chrome Extension
- **Multi-Platform Support**: LinkedIn, Indeed, AngelList/Wellfound
- **Auto-Tracking**: Automatically extracts and tracks job applications
- **Real-time Sync**: Syncs with backend for comprehensive analytics
- **Smart Detection**: Prevents duplicate tracking and validates data quality

### Candidate Features
- **Application Tracking**: Complete job application lifecycle management
- **Auto-Application**: AI-powered job matching and automatic applications
- **Career Roadmaps**: Personalized skill development and career planning
- **Analytics Dashboard**: Comprehensive insights into job search performance
- **Professional Networking**: Automated LinkedIn networking and outreach

### Recruiter Features
- **Candidate Management**: Automated candidate intake and processing
- **Smart Ranking**: AI-powered candidate evaluation and ranking
- **Interview Coordination**: Automated interview scheduling and preparation
- **Analytics & Insights**: Comprehensive recruitment performance metrics

## Architecture

### Backend (FastAPI + PostgreSQL + Celery + Redis)
```
backend/
├── main.py                 # FastAPI application entry point
├── app/
│   ├── agents/            # 7 Portia AI agents implementation
│   │   ├── base.py        # Base agent class
│   │   ├── registry.py    # Agent registry and management
│   │   └── [agent_files]  # Individual agent implementations
│   ├── routers/           # API route handlers
│   ├── services/          # External integrations & business logic
│   ├── models.py          # Database models
│   ├── schemas.py         # Pydantic schemas
│   ├── database.py        # Database configuration
│   ├── config.py          # Application settings
│   ├── tasks.py           # Celery background tasks
│   └── celery_app.py      # Celery configuration
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container configuration
└── docker-compose.yml   # Multi-service orchestration
```

### Frontend (React + TypeScript + Vite + TailwindCSS)
```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   ├── pages/            # Application pages
│   ├── hooks/            # Custom React hooks
│   ├── services/         # API client and services
│   ├── lib/              # Utility functions
│   └── App.tsx           # Main application component
├── package.json          # Dependencies and scripts
└── vite.config.ts        # Vite configuration
```

### Chrome Extension
```
extension/
├── manifest.json         # Extension configuration
├── background.js         # Service worker
├── popup.html/js        # Extension popup interface
├── content-scripts/     # Platform-specific scrapers
│   ├── linkedin.js      # LinkedIn job extraction
│   ├── indeed.js        # Indeed job extraction
│   └── angellist.js     # AngelList job extraction
└── icons/               # Extension icons
```

## Getting Started

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/portia-ai-job-platform.git
cd portia-ai-job-platform
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your configuration

# Start the backend server
python main.py
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env.local

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 4. Chrome Extension Setup
```bash
cd extension

# Load extension in Chrome
1. Open Chrome and go to chrome://extensions/
2. Enable "Developer mode"
3. Click "Load unpacked" and select the extension folder
4. The Portia AI Job Tracker icon should appear in your toolbar
```

## Configuration

### Backend Configuration
Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/portia_jobplatform

# Portia AI Configuration
PORTIA_API_KEY=your_portia_api_key_here

# LLM Configuration - Google Gemini as Primary
GOOGLE_GEMINI_API_KEY=your_gemini_api_key_here

# Alternative LLM providers (optional)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# External APIs for Portia Tools
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
GITHUB_TOKEN=your_github_token

# Google Services for Portia Tools
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_SHEETS_ID=your_google_sheets_id

# Email Configuration for Portia Gmail tool
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Browser Automation for Portia
BROWSERBASE_API_KEY=your_browserbase_api_key_here
BROWSERBASE_PROJECT_ID=your_browserbase_project_id

# Redis
REDIS_URL=redis://localhost:6379

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### Frontend Configuration
Create a `.env.local` file in the frontend directory:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Portia AI Integration

The platform uses maximum Portia AI integration with the following features:

### Controllable Agent Framework
- Structured planning for all agents
- Human-in-the-loop decision points
- Plan validation and approval workflows

### Tool Connectivity
- **Gmail Tool** - Email scanning and automation
- **Google Sheets Tool** - Data sync and tracking
- **Google Calendar Tool** - Meeting scheduling
- **GitHub Tool** - Code analysis and repository management
- **LinkedIn Tool** - Professional networking and automation
- **Browser Tool** - Web automation for job sites
- **Web Research Tools** - Market intelligence gathering

### Secure Execution
- Portia Cloud storage for all plans
- Encrypted credential management
- User-specific plan execution contexts

### Human-in-the-Loop Workflows
- Job application approval before submission
- Connection request approval for networking
- Candidate analysis bias review
- Interview scheduling confirmation
- Market research insight validation

## API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### Core System
- `GET /api/health` - System health check
- `GET /api/system/status` - Comprehensive system status
- `GET /api/portia/portia-status` - Portia AI system status

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

#### Portia AI Agents
- `POST /api/portia/track-applications` - Track job applications with Gmail + Sheets
- `POST /api/portia/auto-apply` - Auto-apply to jobs with browser automation
- `POST /api/portia/career-roadmap` - Create career roadmap with GitHub + LinkedIn analysis
- `POST /api/portia/expand-network` - Expand professional network with LinkedIn automation
- `POST /api/portia/analyze-candidate` - Comprehensive candidate analysis with bias detection
- `POST /api/portia/schedule-interview` - Schedule interviews with Calendar + Gmail
- `POST /api/portia/market-analysis` - Job market analysis with web research

## Agent Architecture

Each Portia AI agent is implemented in its own file for maximum organization:

```
backend/app/agents/
├── base.py                  # Base PortiaJobAgent class
├── registry.py              # Agent registry and utilities
├── job_tracker.py           # Job Application Tracker Agent
├── job_application.py       # Auto Job Application Agent  
├── career_roadmap.py        # Career Roadmap Agent
├── networking.py            # Professional Networking Agent
├── candidate_analysis.py    # Candidate Analysis Agent
├── interview_coordination.py # Interview Coordination Agent
└── market_analytics.py      # Market Analytics Agent
```

### Agent Usage
```python
from app.agents import get_agent

# Get agent by name
job_tracker = get_agent("job_tracker")
result = await job_tracker.track_applications(email, user_id)
```

## Development

### Adding New Agents
1. Create agent file in `backend/app/agents/`
2. Implement agent class extending `PortiaJobAgent`
3. Register agent in `registry.py`
4. Update exports in `__init__.py`

### Testing
```bash
# Backend testing
cd backend
python -m pytest tests/

# Frontend testing
cd frontend
npm test
```

## Deployment

### Using Docker
```bash
cd backend
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis cache
- FastAPI backend
- Celery worker
- Celery scheduler

### Manual Deployment
1. Set up PostgreSQL and Redis instances
2. Configure environment variables for production
3. Deploy backend to cloud provider (AWS, GCP, Heroku)
4. Build and deploy frontend to static hosting (Vercel, Netlify)
5. Publish Chrome extension to Chrome Web Store

## AgentHack 2025

This project is built for AgentHack 2025 with maximum Portia AI integration:

### Hackathon Features
- **7 Specialized Portia AI Agents** - Each handling specific job search tasks
- **Complete Tool Integration** - Gmail, GitHub, LinkedIn, Calendar, Browser automation
- **Human-in-the-Loop Workflows** - Approval systems for critical decisions
- **Google Gemini Integration** - FREE LLM for unlimited development and testing
- **Production-Ready Architecture** - Scalable, maintainable, and well-documented

### Competitive Advantages
- **Maximum Portia Integration** - Showcases all major Portia features
- **Real-World Problem Solving** - Addresses actual job search pain points
- **Professional Architecture** - Enterprise-level code organization
- **Comprehensive Solution** - Covers entire hiring lifecycle
- **Modern Tech Stack** - Latest technologies and best practices

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **WeMakeDevs** for organizing AgentHack 2025
- **Portia AI** for providing the agent framework and tools
- **Google** for Gemini AI integration
- **Open source contributors** for the technologies used

## Support

For issues and feature requests:
- Create an issue in this repository
- Include detailed bug reports with screenshots
- Specify browser version and platform information

---

**Built for AgentHack 2025 - Maximum Portia AI Integration**