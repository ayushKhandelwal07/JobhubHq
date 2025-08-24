import httpx
import asyncio
from typing import Dict, Any, List, Optional
import json
from app.config import settings

class IntegrationService:
    """Service for handling external integrations."""
    
    @staticmethod
    async def get_github_profile(username: str) -> Dict[str, Any]:
        """Get GitHub profile information."""
        try:
            async with httpx.AsyncClient() as client:
                headers = {}
                if settings.GITHUB_TOKEN:
                    headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"
                
                # Get user profile
                profile_response = await client.get(
                    f"https://api.github.com/users/{username}",
                    headers=headers
                )
                profile_data = profile_response.json()
                
                # Get repositories
                repos_response = await client.get(
                    f"https://api.github.com/users/{username}/repos?sort=updated&per_page=10",
                    headers=headers
                )
                repos_data = repos_response.json()
                
                # Get contribution activity
                events_response = await client.get(
                    f"https://api.github.com/users/{username}/events/public?per_page=30",
                    headers=headers
                )
                events_data = events_response.json()
                
                return {
                    "profile": profile_data,
                    "repositories": repos_data,
                    "recent_activity": events_data,
                    "stats": {
                        "public_repos": profile_data.get("public_repos", 0),
                        "followers": profile_data.get("followers", 0),
                        "following": profile_data.get("following", 0),
                        "total_stars": sum(repo.get("stargazers_count", 0) for repo in repos_data),
                        "languages": list(set(repo.get("language") for repo in repos_data if repo.get("language")))
                    }
                }
        except Exception as e:
            return {"error": f"Failed to fetch GitHub data: {str(e)}"}
    
    @staticmethod
    async def get_leetcode_stats(username: str) -> Dict[str, Any]:
        """Get LeetCode statistics (using unofficial API)."""
        try:
            async with httpx.AsyncClient() as client:
                # Using LeetCode GraphQL API
                query = """
                query getUserProfile($username: String!) {
                    matchedUser(username: $username) {
                        username
                        submitStats: submitStatsGlobal {
                            acSubmissionNum {
                                difficulty
                                count
                                submissions
                            }
                        }
                        profile {
                            ranking
                            userAvatar
                            realName
                            aboutMe
                            school
                            websites
                            countryName
                            skillTags
                        }
                    }
                }
                """
                
                response = await client.post(
                    "https://leetcode.com/graphql",
                    json={
                        "query": query,
                        "variables": {"username": username}
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                data = response.json()
                
                if "data" in data and data["data"]["matchedUser"]:
                    user_data = data["data"]["matchedUser"]
                    submit_stats = user_data.get("submitStats", {}).get("acSubmissionNum", [])
                    
                    stats = {
                        "total_solved": sum(stat["count"] for stat in submit_stats),
                        "easy_solved": next((stat["count"] for stat in submit_stats if stat["difficulty"] == "Easy"), 0),
                        "medium_solved": next((stat["count"] for stat in submit_stats if stat["difficulty"] == "Medium"), 0),
                        "hard_solved": next((stat["count"] for stat in submit_stats if stat["difficulty"] == "Hard"), 0),
                        "ranking": user_data.get("profile", {}).get("ranking", 0),
                        "profile": user_data.get("profile", {})
                    }
                    
                    return stats
                else:
                    return {"error": "User not found"}
                    
        except Exception as e:
            return {"error": f"Failed to fetch LeetCode data: {str(e)}"}
    
    @staticmethod
    async def get_linkedin_profile_info(linkedin_url: str) -> Dict[str, Any]:
        """Get LinkedIn profile information (limited due to API restrictions)."""
        # Note: LinkedIn API has strict restrictions
        # This is a placeholder for when proper LinkedIn integration is available
        try:
            # Extract username from URL
            username = linkedin_url.split("/in/")[-1].rstrip("/")
            
            # For now, return basic extracted info
            return {
                "username": username,
                "profile_url": linkedin_url,
                "note": "Full LinkedIn integration requires LinkedIn API access",
                "basic_info": {
                    "profile_exists": True,
                    "url_valid": "/in/" in linkedin_url
                }
            }
        except Exception as e:
            return {"error": f"Failed to process LinkedIn URL: {str(e)}"}
    
    @staticmethod
    async def analyze_github_contributions(username: str) -> Dict[str, Any]:
        """Analyze GitHub contribution patterns."""
        try:
            github_data = await IntegrationService.get_github_profile(username)
            
            if "error" in github_data:
                return github_data
            
            repos = github_data.get("repositories", [])
            events = github_data.get("recent_activity", [])
            
            # Analyze contribution patterns
            contribution_analysis = {
                "commit_frequency": len([e for e in events if e.get("type") == "PushEvent"]),
                "repo_diversity": len(set(e.get("repo", {}).get("name") for e in events)),
                "recent_activity_score": min(len(events), 30),  # Max 30 points
                "language_diversity": len(github_data.get("stats", {}).get("languages", [])),
                "collaboration_score": len([r for r in repos if r.get("fork", False)]),
                "project_complexity": sum(r.get("size", 0) for r in repos[:5])  # Top 5 repos by recency
            }
            
            # Calculate overall activity score
            activity_score = (
                min(contribution_analysis["commit_frequency"] * 2, 20) +
                min(contribution_analysis["repo_diversity"] * 3, 15) +
                min(contribution_analysis["recent_activity_score"], 30) +
                min(contribution_analysis["language_diversity"] * 2, 10) +
                min(contribution_analysis["collaboration_score"], 10) +
                min(contribution_analysis["project_complexity"] / 1000, 15)
            )
            
            return {
                "analysis": contribution_analysis,
                "activity_score": round(activity_score, 2),
                "max_score": 100,
                "percentile": min(round(activity_score), 100)
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze GitHub contributions: {str(e)}"}
    
    @staticmethod
    async def verify_email_deliverability(email: str) -> Dict[str, Any]:
        """Basic email format and domain validation."""
        import re
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_regex, email):
            return {"valid": False, "reason": "Invalid email format"}
        
        domain = email.split("@")[1]
        
        # Basic domain validation
        try:
            async with httpx.AsyncClient() as client:
                # Simple domain check (this is basic - production would use more sophisticated validation)
                response = await client.get(f"https://{domain}", timeout=5.0)
                return {"valid": True, "domain_reachable": response.status_code < 400}
        except:
            return {"valid": True, "domain_reachable": False, "note": "Domain unreachable but email format valid"}
    
    @staticmethod
    async def get_company_info(company_name: str) -> Dict[str, Any]:
        """Get basic company information."""
        # Placeholder for company information lookup
        # In production, this would integrate with services like Clearbit, FullContact, etc.
        return {
            "name": company_name,
            "note": "Company information integration pending",
            "basic_info": {
                "name_provided": bool(company_name),
                "formatted_name": company_name.title() if company_name else ""
            }
        }
