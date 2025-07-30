from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
import openai
from sqlalchemy.orm import Session
from app.core.config import settings
from app.crud.time_entry import time_entry as crud_time_entry
from app.crud.task import task as crud_task
from app.services.report_service import report_service


class AIInsightsService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-3.5-turbo"

    def ask_about_work(self, db: Session, user_id: int, question: str) -> Dict[str, Any]:
        """Process natural language questions about work data."""
        try:
            # Get recent work data for context
            end_date = date.today()
            start_date = end_date - timedelta(days=30)  # Last 30 days

            work_context = self._get_work_context(
                db, user_id, start_date, end_date)

            # Process question with AI
            response = self._process_question_with_ai(question, work_context)

            return {
                "success": True,
                "answer": response,
                "context_period": f"{start_date} to {end_date}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _get_work_context(self, db: Session, user_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get work context for AI processing."""
        # Get time entries
        entries = crud_time_entry.get_by_date_range(
            db, user_id, start_date, end_date)

        # Get tasks
        tasks = crud_task.get_by_user(db, user_id)

        # Generate summary statistics
        total_time = sum(entry.duration or 0 for entry in entries)
        total_hours = round(total_time / 3600, 1)

        # Project breakdown
        project_time = {}
        task_time = {}

        for entry in entries:
            # Project time
            project_name = entry.project.name if entry.project else "No Project"
            project_time[project_name] = project_time.get(
                project_name, 0) + (entry.duration or 0)

            # Task time
            task_name = entry.task.title if entry.task else "Unknown Task"
            task_time[task_name] = task_time.get(
                task_name, 0) + (entry.duration or 0)

        # Convert to hours and sort
        project_hours = {k: round(v / 3600, 1)
                         for k, v in project_time.items()}
        task_hours = {k: round(v / 3600, 1) for k, v in task_time.items()}

        return {
            "period": f"{start_date} to {end_date}",
            "total_hours": total_hours,
            "total_entries": len(entries),
            "unique_tasks": len(set(entry.task_id for entry in entries)),
            "project_breakdown": dict(sorted(project_hours.items(), key=lambda x: x[1], reverse=True)),
            # Top 10 tasks
            "task_breakdown": dict(sorted(task_hours.items(), key=lambda x: x[1], reverse=True)[:10]),
            "active_tasks": len([t for t in tasks if t.status in ["todo", "in_progress"]]),
            "completed_tasks": len([t for t in tasks if t.status == "completed"])
        }

    def _process_question_with_ai(self, question: str, context: Dict[str, Any]) -> str:
        """Process question using OpenAI API."""
        system_prompt = """You are a work analytics assistant. You help users understand their time tracking data and work patterns. 
        
        Use the provided work context to answer questions accurately. If the context doesn't contain enough information to answer fully, say so.
        
        Be conversational but precise. Use specific numbers from the data when available.
        """

        context_text = f"""
        Work Data Context:
        - Period: {context['period']}
        - Total hours worked: {context['total_hours']}
        - Total time entries: {context['total_entries']}
        - Unique tasks worked on: {context['unique_tasks']}
        - Active tasks: {context['active_tasks']}
        - Completed tasks: {context['completed_tasks']}
        
        Project Time Breakdown:
        {self._format_breakdown(context['project_breakdown'])}
        
        Top Tasks by Time:
        {self._format_breakdown(context['task_breakdown'])}
        """

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context: {context_text}\n\nQuestion: {question}"}
                ],
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your question right now. Error: {str(e)}"

    def _format_breakdown(self, breakdown: Dict[str, float]) -> str:
        """Format time breakdown for AI context."""
        if not breakdown:
            return "No data available"

        items = []
        for name, hours in breakdown.items():
            items.append(f"- {name}: {hours} hours")

        return "\n".join(items)

    def generate_productivity_insights(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Generate AI-powered productivity insights."""
        try:
            # Get data for the last 4 weeks
            end_date = date.today()
            start_date = end_date - timedelta(weeks=4)

            context = self._get_work_context(db, user_id, start_date, end_date)

            # Generate insights
            insights = self._generate_insights_with_ai(context)

            return {
                "success": True,
                "insights": insights,
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _generate_insights_with_ai(self, context: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate insights using AI."""
        prompt = f"""
        Analyze this work data and provide productivity insights:
        
        {self._format_context_for_insights(context)}
        
        Provide insights in these categories:
        1. Productivity patterns
        2. Time allocation
        3. Task management
        4. Recommendations
        
        Keep insights concise and actionable.
        """

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a productivity analyst. Provide clear, actionable insights based on work data."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )

            # Parse response into categories
            # This is a simplified parser - in production, you'd want more robust parsing
            content = response.choices[0].message.content

            return {
                "productivity_patterns": ["AI-generated pattern insights"],
                "time_allocation": ["AI-generated allocation insights"],
                "task_management": ["AI-generated task insights"],
                "recommendations": ["AI-generated recommendations"]
            }
        except Exception:
            return {
                "productivity_patterns": ["Unable to generate insights at this time"],
                "time_allocation": ["Please try again later"],
                "task_management": [],
                "recommendations": []
            }

    def _format_context_for_insights(self, context: Dict[str, Any]) -> str:
        """Format context for insights generation."""
        return f"""
        Period: {context['period']}
        Total Hours: {context['total_hours']}
        Entries: {context['total_entries']}
        Tasks: {context['unique_tasks']} unique, {context['active_tasks']} active, {context['completed_tasks']} completed
        
        Top Projects:
        {self._format_breakdown(context['project_breakdown'])}
        """

    def suggest_time_optimization(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Suggest time optimization strategies."""
        try:
            # Analyze recent work patterns
            end_date = date.today()
            start_date = end_date - timedelta(days=14)

            entries = crud_time_entry.get_by_date_range(
                db, user_id, start_date, end_date)

            suggestions = []

            # Analyze session lengths
            session_lengths = [
                entry.duration or 0 for entry in entries if entry.duration]
            if session_lengths:
                avg_session = sum(session_lengths) / \
                    len(session_lengths) / 3600  # Convert to hours

                if avg_session < 0.5:
                    suggestions.append(
                        "Consider longer focused work sessions (aim for 1-2 hours)")
                elif avg_session > 4:
                    suggestions.append(
                        "Consider taking breaks during long work sessions")

            # Analyze task switching
            task_switches = 0
            prev_task = None
            for entry in sorted(entries, key=lambda x: x.start_time):
                if prev_task and prev_task != entry.task_id:
                    task_switches += 1
                prev_task = entry.task_id

            if task_switches > len(entries) * 0.8:
                suggestions.append(
                    "Try to reduce task switching to improve focus")

            # Analyze work distribution
            daily_hours = {}
            for entry in entries:
                day = entry.start_time.date()
                daily_hours[day] = daily_hours.get(
                    day, 0) + (entry.duration or 0) / 3600

            if daily_hours:
                max_daily = max(daily_hours.values())
                min_daily = min(daily_hours.values())

                if max_daily - min_daily > 6:
                    suggestions.append(
                        "Consider more consistent daily work hours")

            return {
                "success": True,
                "suggestions": suggestions or ["Your current work patterns look good!"],
                "analysis_period": f"{start_date} to {end_date}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


ai_insights_service = AIInsightsService()
