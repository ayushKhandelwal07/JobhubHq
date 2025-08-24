import httpx
import asyncio
from typing import Dict, Any, List
from bs4 import BeautifulSoup
import re
from datetime import datetime
from app.config import settings

class JobScrapingService:
    """Service for scraping job postings from various platforms."""
    
    @staticmethod
    async def scrape_jobs(platform: str, keywords: str, location: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Main method to scrape jobs from specified platform."""
        if platform.lower() == "linkedin":
            return await JobScrapingService.scrape_linkedin_jobs(keywords, location, limit)
        elif platform.lower() == "indeed":
            return await JobScrapingService.scrape_indeed_jobs(keywords, location, limit)
        elif platform.lower() == "angellist":
            return await JobScrapingService.scrape_angellist_jobs(keywords, location, limit)
        else:
            return []
    
    @staticmethod
    async def scrape_linkedin_jobs(keywords: str, location: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape LinkedIn jobs (Note: LinkedIn has strict anti-scraping measures).
        This is a simplified version for demonstration purposes.
        Production implementation would require LinkedIn API or authorized scraping methods.
        """
        try:
            # For demo purposes, return mock data
            # In production, this would use LinkedIn API or authorized scraping
            mock_jobs = []
            
            for i in range(min(limit, 5)):  # Limit to 5 mock jobs
                job = {
                    "job_title": f"Software Engineer - {keywords}",
                    "company": f"TechCorp {i+1}",
                    "location": location or "Remote",
                    "job_url": f"https://linkedin.com/jobs/view/123456{i}",
                    "description": f"We are looking for a talented {keywords} professional to join our team...",
                    "salary_range": "$80,000 - $120,000",
                    "posted_date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "requirements": ["Python", "React", "AWS", "Docker"],
                    "employment_type": "Full-time",
                    "experience_level": "Mid-level",
                    "platform": "linkedin",
                    "scraped_at": datetime.utcnow().isoformat()
                }
                mock_jobs.append(job)
            
            return mock_jobs
            
        except Exception as e:
            return [{"error": f"LinkedIn scraping error: {str(e)}"}]
    
    @staticmethod
    async def scrape_indeed_jobs(keywords: str, location: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape Indeed jobs.
        Note: This is a simplified implementation for demonstration.
        """
        try:
            mock_jobs = []
            
            for i in range(min(limit, 5)):
                job = {
                    "job_title": f"{keywords} Developer",
                    "company": f"InnovateCorp {i+1}",
                    "location": location or "New York, NY",
                    "job_url": f"https://indeed.com/viewjob?jk=abc123{i}",
                    "description": f"Join our team as a {keywords} developer with competitive benefits...",
                    "salary_range": "$70,000 - $110,000",
                    "posted_date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "requirements": ["JavaScript", "Node.js", "MongoDB", "Git"],
                    "employment_type": "Full-time",
                    "experience_level": "Entry-level",
                    "platform": "indeed",
                    "scraped_at": datetime.utcnow().isoformat()
                }
                mock_jobs.append(job)
            
            return mock_jobs
            
        except Exception as e:
            return [{"error": f"Indeed scraping error: {str(e)}"}]
    
    @staticmethod
    async def scrape_angellist_jobs(keywords: str, location: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape AngelList (Wellfound) jobs.
        Note: This is a simplified implementation for demonstration.
        """
        try:
            mock_jobs = []
            
            for i in range(min(limit, 5)):
                job = {
                    "job_title": f"Senior {keywords} Engineer",
                    "company": f"StartupCo {i+1}",
                    "location": location or "San Francisco, CA",
                    "job_url": f"https://angel.co/company/startup{i}/jobs/123456",
                    "description": f"Exciting opportunity for a {keywords} engineer at a fast-growing startup...",
                    "salary_range": "$90,000 - $140,000 + equity",
                    "posted_date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "requirements": ["Python", "Django", "PostgreSQL", "Redis"],
                    "employment_type": "Full-time",
                    "experience_level": "Senior-level",
                    "platform": "angellist",
                    "company_stage": "Series A",
                    "equity_offered": True,
                    "scraped_at": datetime.utcnow().isoformat()
                }
                mock_jobs.append(job)
            
            return mock_jobs
            
        except Exception as e:
            return [{"error": f"AngelList scraping error: {str(e)}"}]
    
    @staticmethod
    async def extract_job_details(job_url: str) -> Dict[str, Any]:
        """Extract detailed job information from a job posting URL."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(job_url, timeout=10.0)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Generic job detail extraction
                # This would be customized for each platform
                job_details = {
                    "url": job_url,
                    "title": soup.find("title").text if soup.find("title") else "N/A",
                    "description": soup.get_text()[:1000] + "..." if len(soup.get_text()) > 1000 else soup.get_text(),
                    "extracted_at": datetime.utcnow().isoformat()
                }
                
                return job_details
                
        except Exception as e:
            return {"error": f"Failed to extract job details: {str(e)}"}
    
    @staticmethod
    async def search_jobs_multi_platform(keywords: str, location: str = "", limit_per_platform: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Search jobs across multiple platforms simultaneously."""
        platforms = ["linkedin", "indeed", "angellist"]
        
        # Run scraping tasks concurrently
        tasks = [
            JobScrapingService.scrape_jobs(platform, keywords, location, limit_per_platform)
            for platform in platforms
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Organize results by platform
        platform_results = {}
        for platform, result in zip(platforms, results):
            if isinstance(result, Exception):
                platform_results[platform] = [{"error": str(result)}]
            else:
                platform_results[platform] = result
        
        return platform_results
    
    @staticmethod
    def filter_jobs_by_criteria(jobs: List[Dict[str, Any]], criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter jobs based on specified criteria."""
        filtered_jobs = []
        
        for job in jobs:
            if "error" in job:
                continue
                
            # Apply filters
            if criteria.get("min_salary"):
                # Extract salary from salary_range string
                salary_text = job.get("salary_range", "")
                salary_numbers = re.findall(r'\$?(\d{1,3}(?:,\d{3})*)', salary_text)
                if salary_numbers:
                    min_salary = int(salary_numbers[0].replace(",", ""))
                    if min_salary < criteria["min_salary"]:
                        continue
            
            if criteria.get("remote_only") and "remote" not in job.get("location", "").lower():
                continue
            
            if criteria.get("experience_level"):
                job_experience = job.get("experience_level", "").lower()
                required_experience = criteria["experience_level"].lower()
                if required_experience not in job_experience:
                    continue
            
            if criteria.get("required_skills"):
                job_requirements = " ".join(job.get("requirements", [])).lower()
                job_description = job.get("description", "").lower()
                job_text = job_requirements + " " + job_description
                
                required_skills = criteria["required_skills"]
                skills_found = sum(1 for skill in required_skills if skill.lower() in job_text)
                skill_match_threshold = criteria.get("skill_match_threshold", 0.5)
                
                if skills_found / len(required_skills) < skill_match_threshold:
                    continue
            
            filtered_jobs.append(job)
        
        return filtered_jobs
    
    @staticmethod
    def calculate_job_match_score(job: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Calculate how well a job matches a user's profile."""
        score = 0.0
        max_score = 100.0
        
        # Skills match (40% of total score)
        user_skills = [skill.lower() for skill in user_profile.get("skills", [])]
        job_requirements = [req.lower() for req in job.get("requirements", [])]
        job_description = job.get("description", "").lower()
        
        skills_matched = 0
        for skill in user_skills:
            if any(skill in req for req in job_requirements) or skill in job_description:
                skills_matched += 1
        
        if user_skills:
            skills_score = (skills_matched / len(user_skills)) * 40
            score += skills_score
        
        # Location match (20% of total score)
        preferred_locations = user_profile.get("preferred_locations", [])
        job_location = job.get("location", "").lower()
        
        if not preferred_locations or any(loc.lower() in job_location for loc in preferred_locations) or "remote" in job_location:
            score += 20
        
        # Experience level match (20% of total score)
        user_experience = user_profile.get("experience_years", 0)
        job_experience = job.get("experience_level", "").lower()
        
        if ("entry" in job_experience and user_experience <= 2) or \
           ("mid" in job_experience and 2 <= user_experience <= 5) or \
           ("senior" in job_experience and user_experience >= 5):
            score += 20
        
        # Company preferences (10% of total score)
        preferred_companies = user_profile.get("preferred_companies", [])
        job_company = job.get("company", "").lower()
        
        if not preferred_companies or any(comp.lower() in job_company for comp in preferred_companies):
            score += 10
        
        # Salary match (10% of total score)
        min_salary_preference = user_profile.get("min_salary", 0)
        job_salary_text = job.get("salary_range", "")
        salary_numbers = re.findall(r'\$?(\d{1,3}(?:,\d{3})*)', job_salary_text)
        
        if salary_numbers:
            job_min_salary = int(salary_numbers[0].replace(",", ""))
            if job_min_salary >= min_salary_preference:
                score += 10
        elif min_salary_preference == 0:  # No salary preference
            score += 10
        
        return min(score, max_score)
