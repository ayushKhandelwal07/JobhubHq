# Google Gemini API Setup Guide for Hackathon

This guide will help you set up Google Gemini API (FREE) for your Portia AI Job Platform hackathon project.

## Why Google Gemini for Hackathon?
- **FREE tier available** - No credit card required
- **Generous limits** - 15 requests per minute, 1500 requests per day
- **High quality** - Powered by Google's latest AI models
- **Easy setup** - Simple API key generation
- **Reliable** - Google's infrastructure
## Step 1: Get Your Gemini API Key

### 1.1 Go to Google AI Studio
- Visit: https://makersuite.google.com/app/apikey
- Sign in with your Google account

### 1.2 Create API Key
1. Click **"Create API Key"**
2. Choose **"Create API Key in new project"**
3. Give your project a name (e.g., "Portia AI Hackathon")
4. Click **"Create API Key"**

### 1.3 Copy Your API Key
- Your API key will look like: `AIzaSyC...` (long string)
- **Copy and save it securely** - you'll need it for the next step
## Step 2: Configure Your Project

### 2.1 Create Environment File
```bash
cd backend
cp env.example .env
```

### 2.2 Add Your Gemini API Key
Edit the `.env` file and add your API key:
```env
# AI Services - Google Gemini (Free for hackathon)
GOOGLE_GEMINI_API_KEY=AIzaSyC...your_actual_api_key_here
```

## 🧪 **Step 3: Test Your Setup**

### 3.1 Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3.2 Run the Test Script
```bash
python test_gemini_agents.py
```

You should see output like:
```
 Starting Google Gemini AI Agent Tests...
==================================================
 Gemini API Key found: AIzaSyC...
 Testing JobTrackerAgent...
 JobTrackerAgent: SUCCESS
   Response: Based on your job application for Software Engineer at Tech Corp...
```
## Gemini API Limits & Pricing

### Free Tier Limits
- **Rate Limit**: 15 requests per minute
- **Daily Limit**: 1,500 requests per day
- **Model**: gemini-pro (latest)

### For Hackathon Use
- **More than enough** for demo and testing
- **No cost** - completely free
- **Reliable** - Google's infrastructure
## Troubleshooting

### Common Issues

#### 1. "API Key not found" Error
```bash
# Make sure your .env file exists and has the correct key
cat .env | grep GOOGLE_GEMINI_API_KEY
```

#### 2. "Quota exceeded" Error
- Check your daily usage at: https://makersuite.google.com/app/apikey
- Wait for daily reset or create a new API key

#### 3. "Invalid API Key" Error
- Verify you copied the entire key correctly
- Make sure there are no extra spaces or characters

#### 4. "Module not found" Error
```bash
# Install the Google Generative AI library
pip install google-generativeai==0.3.2
```
## Hackathon Demo Tips

### 1. **Prepare Demo Data**
Create sample data for your demo:
```python
demo_data = {
    "job_title": "Software Engineer",
    "company": "Tech Corp",
    "resume": "Experienced developer with Python and React",
    "skills": ["Python", "React", "PostgreSQL"]
}
```

### 2. **Test All Agents**
Make sure all 8 agents work before your demo:
```bash
python test_gemini_agents.py
```

### 3. **Backup Plan**
- Have screenshots of working agents
- Prepare demo videos in advance
- Keep your API key handy
## Ready for Hackathon!

Once you've completed these steps:

1.  **API Key configured**
2.  **All agents tested**
3.  **Frontend connected**
4.  **Chrome extension loaded**

Your Portia AI Job Platform is ready for the WeMakeDevs AgentHack 2025!
## Need Help?
- **Google AI Studio**: https://makersuite.google.com/
- **Gemini API Docs**: https://ai.google.dev/docs
- **GitHub Issues**: Create an issue in your project repo

---

**Good luck with your hackathon! **