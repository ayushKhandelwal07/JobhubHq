import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any
import asyncio
from datetime import datetime
from app.config import settings

class GoogleSheetsService:
    """Service for Google Sheets integration."""
    
    def __init__(self):
        self.gc = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Sheets client."""
        try:
            if settings.GOOGLE_CREDENTIALS_PATH:
                self.gc = gspread.service_account(filename=settings.GOOGLE_CREDENTIALS_PATH)
        except Exception as e:
            print(f"Google Sheets initialization error: {e}")
            self.gc = None
    
    async def create_job_tracker_sheet(self, user_email: str, sheet_name: str = "Job Applications Tracker") -> Dict[str, Any]:
        """Create a new job tracker spreadsheet."""
        if not self.gc:
            return {"error": "Google Sheets not configured"}
        
        try:
            # Create new spreadsheet
            spreadsheet = self.gc.create(sheet_name)
            
            # Share with user
            spreadsheet.share(user_email, perm_type='user', role='writer')
            
            # Set up headers
            worksheet = spreadsheet.sheet1
            headers = [
                "Job Title",
                "Company", 
                "Location",
                "Salary Range",
                "Status",
                "Applied Date",
                "Response Date",
                "Job URL",
                "Source",
                "Notes",
                "Interview Date",
                "Follow-up Required"
            ]
            
            worksheet.append_row(headers)
            
            # Format headers
            worksheet.format("A1:L1", {
                "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.9},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}
            })
            
            return {
                "spreadsheet_id": spreadsheet.id,
                "spreadsheet_url": spreadsheet.url,
                "sheet_name": sheet_name,
                "success": True
            }
            
        except Exception as e:
            return {"error": f"Failed to create spreadsheet: {str(e)}"}
    
    async def sync_applications_to_sheet(self, spreadsheet_id: str, applications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sync job applications to existing spreadsheet."""
        if not self.gc:
            return {"error": "Google Sheets not configured"}
        
        try:
            spreadsheet = self.gc.open_by_key(spreadsheet_id)
            worksheet = spreadsheet.sheet1
            
            # Clear existing data (except headers)
            worksheet.clear("A2:L1000")
            
            # Prepare data for bulk update
            rows_to_add = []
            for app in applications:
                row = [
                    app.get("job_title", ""),
                    app.get("company", ""),
                    app.get("location", ""),
                    app.get("salary_range", ""),
                    app.get("status", ""),
                    app.get("applied_date", "").split("T")[0] if app.get("applied_date") else "",
                    app.get("response_date", "").split("T")[0] if app.get("response_date") else "",
                    app.get("job_url", ""),
                    app.get("source", ""),
                    app.get("notes", ""),
                    "",  # Interview Date - to be filled manually
                    "No" if app.get("status") in ["rejected", "offer"] else "Yes"  # Follow-up Required
                ]
                rows_to_add.append(row)
            
            # Batch update
            if rows_to_add:
                worksheet.append_rows(rows_to_add)
            
            # Apply conditional formatting for status
            worksheet.format("E:E", {
                "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}
            })
            
            return {
                "success": True,
                "synced_count": len(rows_to_add),
                "spreadsheet_url": spreadsheet.url
            }
            
        except Exception as e:
            return {"error": f"Failed to sync to spreadsheet: {str(e)}"}
    
    async def create_analytics_dashboard_sheet(self, user_email: str, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create analytics dashboard in Google Sheets."""
        if not self.gc:
            return {"error": "Google Sheets not configured"}
        
        try:
            # Create new spreadsheet
            spreadsheet = self.gc.create("Job Search Analytics Dashboard")
            spreadsheet.share(user_email, perm_type='user', role='writer')
            
            # Create multiple worksheets for different analytics
            
            # 1. Summary Dashboard
            summary_sheet = spreadsheet.sheet1
            summary_sheet.update_title("Dashboard Summary")
            
            summary_data = [
                ["Metric", "Value"],
                ["Total Applications", analytics_data.get("total_applications", 0)],
                ["Response Rate", f"{analytics_data.get('response_rate', 0):.1f}%"],
                ["Interview Rate", f"{analytics_data.get('interview_rate', 0):.1f}%"],
                ["Offer Rate", f"{analytics_data.get('offer_rate', 0):.1f}%"],
                ["Average Response Time (days)", analytics_data.get("avg_response_time", 0)],
                ["Active Applications", analytics_data.get("active_applications", 0)]
            ]
            
            summary_sheet.update("A1:B7", summary_data)
            
            # 2. Application Funnel
            funnel_sheet = spreadsheet.add_worksheet(title="Application Funnel", rows="100", cols="10")
            
            funnel_data = analytics_data.get("funnel_data", {})
            funnel_rows = [
                ["Stage", "Count", "Conversion Rate"],
                ["Applied", funnel_data.get("applied", 0), "100%"],
                ["Responded", funnel_data.get("responded", 0), f"{funnel_data.get('response_rate', 0):.1f}%"],
                ["Interviewed", funnel_data.get("interviewed", 0), f"{funnel_data.get('interview_rate', 0):.1f}%"],
                ["Offers", funnel_data.get("offers", 0), f"{funnel_data.get('offer_rate', 0):.1f}%"]
            ]
            
            funnel_sheet.update("A1:C5", funnel_rows)
            
            # 3. Skills Progress
            skills_sheet = spreadsheet.add_worksheet(title="Skills Progress", rows="100", cols="10")
            
            skills_data = analytics_data.get("skills_progress", [])
            skills_rows = [["Skill", "Current Level", "Target Level", "Progress %"]]
            
            for skill in skills_data:
                skills_rows.append([
                    skill.get("skill_name", ""),
                    skill.get("current_level", 0),
                    skill.get("target_level", 0),
                    f"{skill.get('progress_percentage', 0):.1f}%"
                ])
            
            skills_sheet.update("A1", skills_rows)
            
            return {
                "spreadsheet_id": spreadsheet.id,
                "spreadsheet_url": spreadsheet.url,
                "success": True,
                "sheets_created": ["Dashboard Summary", "Application Funnel", "Skills Progress"]
            }
            
        except Exception as e:
            return {"error": f"Failed to create analytics dashboard: {str(e)}"}
    
    async def update_skill_progress(self, spreadsheet_id: str, skill_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update skill progress in existing spreadsheet."""
        if not self.gc:
            return {"error": "Google Sheets not configured"}
        
        try:
            spreadsheet = self.gc.open_by_key(spreadsheet_id)
            skills_sheet = spreadsheet.worksheet("Skills Progress")
            
            # Update skill progress data
            for update in skill_updates:
                skill_name = update.get("skill_name")
                new_progress = update.get("progress_percentage", 0)
                
                # Find the row with this skill
                skill_column = skills_sheet.col_values(1)  # Column A
                if skill_name in skill_column:
                    row_index = skill_column.index(skill_name) + 1
                    skills_sheet.update(f"D{row_index}", f"{new_progress:.1f}%")
            
            return {"success": True, "updated_skills": len(skill_updates)}
            
        except Exception as e:
            return {"error": f"Failed to update skill progress: {str(e)}"}
    
    async def export_data_to_sheets(self, user_email: str, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export comprehensive data to Google Sheets."""
        if not self.gc:
            return {"error": "Google Sheets not configured"}
        
        try:
            # Create comprehensive export spreadsheet
            spreadsheet = self.gc.create(f"Job Search Export - {datetime.now().strftime('%Y-%m-%d')}")
            spreadsheet.share(user_email, perm_type='user', role='writer')
            
            # Export applications
            if "applications" in export_data:
                apps_sheet = spreadsheet.sheet1
                apps_sheet.update_title("Applications")
                
                applications = export_data["applications"]
                if applications:
                    headers = list(applications[0].keys())
                    data = [headers]
                    
                    for app in applications:
                        row = [str(app.get(header, "")) for header in headers]
                        data.append(row)
                    
                    apps_sheet.update("A1", data)
            
            # Export networking contacts
            if "networking_contacts" in export_data:
                network_sheet = spreadsheet.add_worksheet(title="Networking", rows="1000", cols="20")
                
                contacts = export_data["networking_contacts"]
                if contacts:
                    headers = list(contacts[0].keys())
                    data = [headers]
                    
                    for contact in contacts:
                        row = [str(contact.get(header, "")) for header in headers]
                        data.append(row)
                    
                    network_sheet.update("A1", data)
            
            return {
                "spreadsheet_id": spreadsheet.id,
                "spreadsheet_url": spreadsheet.url,
                "success": True
            }
            
        except Exception as e:
            return {"error": f"Failed to export data: {str(e)}"}
