"""LLM integration for content generation."""
import os
import random
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

# Flag to explicitly disable LLM calls (default: disabled to work without API access)
DISABLE_LLM = os.getenv("DISABLE_LLM", "true").lower() == "true"

# Try to import OpenAI, but make it optional
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class LLMGenerator:
    """Handles LLM-based content generation."""
    
    def __init__(self):
        """Initialize LLM generator.

        By default, network LLM calls are disabled so the project
        always runs even without OpenAI quota or an API key.
        Set DISABLE_LLM=false in the environment to enable them.
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None

        if DISABLE_LLM:
            print("Info: DISABLE_LLM is enabled (default). Using template-based generation only.")
            return

        if OPENAI_AVAILABLE and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
                self.client = None
        else:
            print("Warning: OpenAI not available or API key not set. Using fallback generation.")
    
    def generate_task_name(self, project_type: str, context: Optional[dict] = None) -> str:
        """Generate a realistic task name.
        
        Args:
            project_type: Type of project (e.g., 'engineering', 'marketing', 'operations')
            context: Additional context (optional)
            
        Returns:
            Generated task name
        """
        if not self.client:
            return self._fallback_task_name(project_type)
        
        try:
            prompt = self._get_task_name_prompt(project_type, context)
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates realistic task names for project management software."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=50
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating task name with LLM: {e}")
            return self._fallback_task_name(project_type)
    
    def generate_task_description(self, task_name: str, project_type: str) -> str:
        """Generate a realistic task description.
        
        Distribution: 20% empty, 50% 1-3 sentences, 30% detailed with bullet points.
        
        Args:
            task_name: Name of the task
            project_type: Type of project
            
        Returns:
            Generated description (may be empty)
        """
        rand = random.random()
        if rand < 0.20:  # 20% empty
            return ""
        
        if not self.client:
            return self._fallback_description(task_name, project_type, rand)
        
        try:
            detail_level = "brief" if rand < 0.70 else "detailed"
            prompt = f"Generate a {detail_level} task description for a {project_type} project task: '{task_name}'. "
            if detail_level == "brief":
                prompt += "Provide 1-3 sentences."
            else:
                prompt += "Provide a detailed description with 3-5 bullet points."
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates realistic task descriptions for project management."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200 if detail_level == "brief" else 300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating description with LLM: {e}")
            return self._fallback_description(task_name, project_type, rand)
    
    def generate_comment(self, task_name: str, project_type: str) -> str:
        """Generate a realistic comment.
        
        Args:
            task_name: Name of the task
            project_type: Type of project
            
        Returns:
            Generated comment text
        """
        if not self.client:
            return self._fallback_comment()
        
        try:
            comment_types = [
                "Ask a question about the task",
                "Provide an update on progress",
                "Share a relevant link or resource",
                "Request clarification",
                "Note a blocker or issue"
            ]
            comment_type = random.choice(comment_types)
            
            prompt = f"Generate a realistic comment for a task '{task_name}' in a {project_type} project. Comment type: {comment_type}. Keep it concise (1-2 sentences)."
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates realistic work comments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating comment with LLM: {e}")
            return self._fallback_comment()
    
    def _get_task_name_prompt(self, project_type: str, context: Optional[dict]) -> str:
        """Get prompt template for task name generation."""
        templates = {
            "engineering": "Generate a realistic engineering task name following the pattern '[Component] - [Action] - [Detail]'. Examples: 'API Gateway - Implement rate limiting - Add Redis caching', 'Frontend - Refactor authentication flow - Update token handling'",
            "marketing": "Generate a realistic marketing task name following the pattern '[Campaign/Initiative] - [Deliverable]'. Examples: 'Q2 Product Launch - Create landing page', 'Social Media Campaign - Design Instagram posts'",
            "operations": "Generate a realistic operations task name. Examples: 'Update vendor contract for AWS', 'Audit security compliance procedures', 'Onboard new team member'"
        }
        return templates.get(project_type.lower(), templates["engineering"])
    
    def _fallback_task_name(self, project_type: str) -> str:
        """Fallback task name generation without LLM."""
        templates = {
            "engineering": [
                "Implement user authentication",
                "Fix bug in payment processing",
                "Refactor database queries",
                "Add API endpoint for user profiles",
                "Update documentation",
                "Write unit tests for auth module",
                "Optimize database indexes",
                "Deploy staging environment"
            ],
            "marketing": [
                "Create social media campaign",
                "Write blog post about product launch",
                "Design email newsletter template",
                "Analyze website analytics",
                "Update product marketing page",
                "Plan Q2 marketing strategy",
                "Coordinate with PR agency"
            ],
            "operations": [
                "Update vendor contracts",
                "Review security compliance",
                "Onboard new team member",
                "Schedule team meeting",
                "Update process documentation",
                "Review budget allocation"
            ]
        }
        return random.choice(templates.get(project_type.lower(), templates["engineering"]))
    
    def _fallback_description(self, task_name: str, project_type: str, rand: float) -> str:
        """Fallback description generation."""
        if rand < 0.70:
            return f"This task involves working on {task_name.lower()}. Please ensure all requirements are met."
        else:
            return f"""This task involves {task_name.lower()}.

Key requirements:
- Review current implementation
- Make necessary changes
- Test thoroughly
- Update documentation as needed"""
    
    def _fallback_comment(self) -> str:
        """Fallback comment generation."""
        comments = [
            "Looks good! Starting on this now.",
            "Any updates on this?",
            "I've run into a blocker - can we sync?",
            "This is done and ready for review.",
            "Found a related issue, linking it here.",
            "Can we prioritize this?",
            "Great progress so far!"
        ]
        return random.choice(comments)

