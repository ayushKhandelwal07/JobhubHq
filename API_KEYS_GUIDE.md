# API Keys & Credentials Guide

## For AgentHack 2025

This guide shows you exactly where to find all the API keys and credentials needed for your Portia AI Job Platform.

---

## 1. Google Gemini API Key (REQUIRED - FREE)

### Where to Get It:
- **Website**: https://makersuite.google.com/app/apikey
- **Cost**: FREE (no credit card needed)
- **Limits**: 15 requests/minute, 1500 requests/day

### Steps:
1. **Visit** https://makersuite.google.com/app/apikey
2. **Sign in** with your Google account
3. **Click** "Create API Key"
4. **Choose** "Create API Key in new project"
5. **Name** your project: `Portia AI Hackathon`
6. **Click** "Create API Key"
7. **Copy** your key (looks like: `AIzaSyC...`)

### Add to Project:
```env
GOOGLE_GEMINI_API_KEY=AIzaSyC...your_actual_key_here
```

---

## 2. LinkedIn API Keys (Optional - For Job Scraping)

### Where to Get Them:
- **Website**: https://www.linkedin.com/developers/
- **Cost**: FREE (with limits)

### Steps:
1. **Visit** https://www.linkedin.com/developers/
2. **Sign in** with LinkedIn account
3. **Click** "Create App"
4. **Fill** app details:
   - App name: `Portia Job Tracker`
   - LinkedIn Page: Your profile
   - App Logo: Upload any image
5. **Get** Client ID and Client Secret

### Add to Project:
```env
LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here
```

---

## 3. GitHub Personal Access Token (Optional - For GitHub Integration)

### Where to Get It:
- **Website**: https://github.com/settings/tokens
- **Cost**: FREE

### Steps:
1. **Visit** https://github.com/settings/tokens
2. **Click** "Tokens (classic)"
3. **Click** "Generate new token (classic)"
4. **Select scopes**:
   -  `repo` (Full control of private repositories)
   -  `read:user` (Read user profile data)
   -  `read:org` (Read organization data)
5. **Click** "Generate token"
6. **Copy** the token (starts with `ghp_`)

### Add to Project:
```env
GITHUB_TOKEN=ghp_your_github_token_here
```

---
## 4. Google Sheets API (Optional - For Data Sync)

### Where to Get It:
- **Website**: https://console.cloud.google.com/
- **Cost**: FREE (with limits)

### Steps:
1. **Visit** https://console.cloud.google.com/
2. **Create** new project or select existing
3. **Enable** Google Sheets API
4. **Create** Service Account:
   - Go to "IAM & Admin" → "Service Accounts"
   - Click "Create Service Account"
   - Download JSON credentials file
5. **Share** your Google Sheet with the service account email

### Add to Project:
```env
GOOGLE_CREDENTIALS_PATH=path/to/your/credentials.json
GOOGLE_SHEETS_ID=your_google_sheet_id_here
```

---
## 5. Email SMTP Settings (Optional - For Email Features)

### Gmail Setup:
1. **Enable 2-Factor Authentication** on your Gmail
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Use** your Gmail address and app password

### Add to Project:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
```

---
## 6. JWT Secret Key (REQUIRED - For Authentication)

### Generate Your Own:
```bash
# In terminal, generate a random string
openssl rand -hex 32
```

### Or Use Online Generator:
- **Website**: https://generate-secret.vercel.app/32
- **Copy** the generated string

### Add to Project:
```env
JWT_SECRET_KEY=your_super_secret_jwt_key_here
```

---
## 7. Database URL (REQUIRED - For Data Storage)

### For Local Development:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/portia_jobplatform
```

### For Production (Free Options):
- **Neon**: https://neon.tech/ (PostgreSQL, free tier)
- **Supabase**: https://supabase.com/ (PostgreSQL, free tier)
- **Railway**: https://railway.app/ (PostgreSQL, free tier)

---
## 8. Redis URL (Optional - For Background Tasks)

### For Local Development:
```env
REDIS_URL=redis://localhost:6379
```

### For Production (Free Options):
- **Redis Cloud**: https://redis.com/try-free/ (free tier)
- **Upstash**: https://upstash.com/ (free tier)

---
## Complete .env File Example

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/portia_jobplatform

# AI Services - Google Gemini (Free for hackathon)
GOOGLE_GEMINI_API_KEY=AIzaSyC...your_actual_key_here

# External APIs (Optional)
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
GITHUB_TOKEN=ghp_your_github_token

# Google Services (Optional)
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_SHEETS_ID=your_google_sheets_id

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Redis (Optional)
REDIS_URL=redis://localhost:6379

# JWT Configuration (REQUIRED)
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Application Settings
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads
```

---
## Quick Start for Hackathon

### Minimum Required (Just to get started):
```env
# AI Services - Google Gemini (REQUIRED)
GOOGLE_GEMINI_API_KEY=AIzaSyC...your_actual_key_here

# JWT Configuration (REQUIRED)
JWT_SECRET_KEY=your_super_secret_jwt_key_here

# Database (REQUIRED)
DATABASE_URL=postgresql://postgres:password@localhost:5432/portia_jobplatform
```

### Steps:
1. **Get Gemini API Key** (5 minutes)
2. **Generate JWT Secret** (1 minute)
3. **Set up Database** (5 minutes)
4. **Test everything** (2 minutes)

---
## Priority Order for Hackathon

1. ** HIGH PRIORITY** (Must have):
   -  Google Gemini API Key
   -  JWT Secret Key
   -  Database URL

2. **🟡 MEDIUM PRIORITY** (Nice to have):
   - GitHub Token
   - LinkedIn API Keys
   - Email SMTP

3. **🟢 LOW PRIORITY** (Optional):
   - Google Sheets API
   - Redis URL

---
## Pro Tips for Hackathon

### 1. **Start with Minimum Setup**
- Get only the required keys first
- Test the basic functionality
- Add more integrations later

### 2. **Use Free Services**
- All services listed above have free tiers
- Perfect for hackathon demos
- No credit card required

### 3. **Keep Keys Secure**
- Never commit `.env` file to git
- Use different keys for demo vs production
- Rotate keys after hackathon

### 4. **Document Your Setup**
- Take screenshots of working features
- Record demo videos
- Keep API keys handy for judges

---
## Need Help?

### Common Issues:
- **"API Key not found"**: Check your `.env` file exists
- **"Invalid API Key"**: Copy the entire key, no extra spaces
- **"Quota exceeded"**: Wait for daily reset or create new key
- **"Database connection failed"**: Check DATABASE_URL format

### Resources:
- **Google AI Studio**: https://makersuite.google.com/
- **LinkedIn Developers**: https://www.linkedin.com/developers/
- **GitHub Settings**: https://github.com/settings/tokens
- **Google Cloud Console**: https://console.cloud.google.com/

---

** You're ready to build an amazing hackathon project! Good luck! **