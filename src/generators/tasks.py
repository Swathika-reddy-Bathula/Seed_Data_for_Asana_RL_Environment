"""Generate tasks data."""
import random
from typing import List, Dict
from datetime import datetime, timedelta
from utils.helpers import generate_id
from utils.dates import (generate_creation_times, generate_due_date, 
                            generate_completion_date, random_weekday_date)
from utils.llm import LLMGenerator
from scrapers.company_scraper import CompanyScraper


class TaskGenerator:
    """Generates realistic task data."""
    
    PRIORITIES = ["low", "normal", "high", "urgent"]
    PRIORITY_WEIGHTS = [0.20, 0.60, 0.15, 0.05]  # Most tasks are normal priority
    
    def __init__(self):
        """Initialize task generator."""
        self.llm = LLMGenerator()
        self.scraper = CompanyScraper()
    
    def generate_tasks(self, projects: List[Dict], sections: List[Dict], 
                      users: List[Dict], team_memberships: Dict[str, List[str]],
                      start_date: datetime, end_date: datetime,
                      tasks_per_project: int = 30) -> List[Dict]:
        """Generate tasks for projects.
        
        Completion rates by project type (based on Asana research):
        - Sprint projects: 70-85%
        - Bug tracking: 60-70%
        - Ongoing projects: 40-50%
        
        Args:
            projects: List of project dictionaries
            sections: List of section dictionaries (grouped by project)
            users: List of user dictionaries
            team_memberships: Dict mapping team_id to list of user_ids
            start_date: Start of simulation period
            end_date: End of simulation period
            tasks_per_project: Average number of tasks per project
            
        Returns:
            List of task dictionaries
        """
        tasks = []
        
        # Group sections by project
        sections_by_project = {}
        for section in sections:
            pid = section["project_id"]
            if pid not in sections_by_project:
                sections_by_project[pid] = []
            sections_by_project[pid].append(section)
        
        # Generate tasks for each project
        for project in projects:
            project_id = project["project_id"]
            project_type = project.get("project_type", "engineering")
            team_id = project["team_id"]
            
            # Get sections for this project
            project_sections = sections_by_project.get(project_id, [])
            if not project_sections:
                continue
            
            # Determine number of tasks (variation)
            num_tasks = random.randint(int(tasks_per_project * 0.7), int(tasks_per_project * 1.3))
            
            # Generate creation times
            creation_times = generate_creation_times(
                max(datetime.fromisoformat(project["created_at"]), start_date),
                end_date,
                num_tasks
            )
            
            # Get team members for assignment
            team_members = team_memberships.get(team_id, [])
            
            # Completion rate by project type
            if "sprint" in project["name"].lower() or "bug" in project["name"].lower():
                completion_rate = random.uniform(0.70, 0.85)
            elif project_type == "engineering":
                completion_rate = random.uniform(0.65, 0.75)
            else:
                completion_rate = random.uniform(0.40, 0.50)
            
            for created_at in creation_times:
                # Generate task name using LLM or fallback
                task_name = self.llm.generate_task_name(project_type)
                
                # Generate description (20% empty, 50% brief, 30% detailed)
                description = self.llm.generate_task_description(task_name, project_type)
                
                # Assign to section (weighted: more in "To Do" and "In Progress")
                section_weights = [0.35, 0.40, 0.15, 0.10]  # To Do, In Progress, In Review, Done
                if len(project_sections) >= len(section_weights):
                    section = random.choices(project_sections, 
                                           weights=section_weights[:len(project_sections)], 
                                           k=1)[0]
                    section_id = section["section_id"]
                else:
                    section_id = random.choice(project_sections)["section_id"]
                
                # Assignee (15% unassigned per Asana benchmarks)
                assignee_id = None
                if random.random() > 0.15 and team_members:
                    assignee_id = random.choice(team_members)
                
                # Generate due date
                due_date = generate_due_date(created_at, end_date, "realistic")
                
                # Determine completion
                completed = random.random() < completion_rate
                
                # Generate completion date
                completed_at = generate_completion_date(created_at, due_date, completed, end_date)
                
                # Priority
                priority = random.choices(self.PRIORITIES, weights=self.PRIORITY_WEIGHTS, k=1)[0]
                
                # Creator (random user from team or organization)
                creator = random.choice(users) if users else None
                
                task = {
                    "task_id": generate_id(),
                    "project_id": project_id,
                    "section_id": section_id,
                    "parent_task_id": None,  # Top-level tasks, subtasks handled separately
                    "name": task_name,
                    "description": description,
                    "assignee_id": assignee_id,
                    "due_date": due_date.isoformat() if due_date else None,
                    "due_time": None,
                    "created_at": created_at.isoformat(),
                    "completed": completed,
                    "completed_at": completed_at.isoformat() if completed_at else None,
                    "created_by": creator["user_id"] if creator else None,
                    "priority": priority
                }
                tasks.append(task)
        
        return tasks
    
    def generate_subtasks(self, tasks: List[Dict], users: List[Dict],
                         subtask_ratio: float = 0.20) -> List[Dict]:
        """Generate subtasks for existing tasks.
        
        Args:
            tasks: List of parent tasks
            users: List of user dictionaries
            subtask_ratio: Ratio of tasks that should have subtasks
            
        Returns:
            List of subtask dictionaries
        """
        subtasks = []
        
        # Select tasks to have subtasks
        num_parent_tasks = int(len(tasks) * subtask_ratio)
        parent_tasks = random.sample(tasks, min(num_parent_tasks, len(tasks)))
        
        subtask_templates = [
            "Review {task}",
            "Test {task}",
            "Document {task}",
            "Design {task}",
            "Implement {task}",
            "Refactor {task}",
            "Update {task}",
            "Finalize {task}"
        ]
        
        for parent_task in parent_tasks:
            # Generate 2-5 subtasks per parent
            num_subtasks = random.randint(2, 5)
            
            parent_created = datetime.fromisoformat(parent_task["created_at"])
            
            for i in range(num_subtasks):
                # Subtask name based on parent
                template = random.choice(subtask_templates)
                subtask_name = template.format(task=parent_task["name"].lower())
                
                # Subtask creation is after parent
                subtask_created = parent_created + timedelta(days=random.randint(0, 5))
                
                # Completion (subtasks often complete before parent)
                completed = random.random() < 0.70 if parent_task["completed"] else random.random() < 0.30
                
                subtask = {
                    "task_id": generate_id(),
                    "project_id": parent_task["project_id"],
                    "section_id": parent_task["section_id"],
                    "parent_task_id": parent_task["task_id"],
                    "name": subtask_name,
                    "description": "",
                    "assignee_id": parent_task.get("assignee_id"),
                    "due_date": parent_task.get("due_date"),
                    "due_time": None,
                    "created_at": subtask_created.isoformat(),
                    "completed": completed,
                    "completed_at": None,
                    "created_by": parent_task.get("created_by"),
                    "priority": parent_task.get("priority", "normal")
                }
                
                if completed:
                    subtask["completed_at"] = (subtask_created + timedelta(days=random.randint(1, 7))).isoformat()
                
                subtasks.append(subtask)
        
        return subtasks

