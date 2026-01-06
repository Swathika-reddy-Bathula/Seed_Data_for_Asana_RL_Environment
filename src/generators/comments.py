"""Generate comments data."""
import random
from typing import List, Dict
from datetime import datetime, timedelta
from utils.helpers import generate_id
from utils.dates import random_date
from utils.llm import LLMGenerator


class CommentGenerator:
    """Generates realistic comments/stories."""
    
    def __init__(self):
        """Initialize comment generator."""
        self.llm = LLMGenerator()
    
    def generate_comments(self, tasks: List[Dict], users: List[Dict],
                         start_date: datetime, end_date: datetime,
                         comments_per_task: float = 1.5) -> List[Dict]:
        """Generate comments for tasks.
        
        Distribution: ~1.5 comments per task on average.
        Comments are generated after task creation.
        
        Args:
            tasks: List of task dictionaries
            users: List of user dictionaries
            start_date: Start of simulation period
            end_date: End of simulation period
            comments_per_task: Average number of comments per task
            
        Returns:
            List of comment dictionaries
        """
        comments = []
        
        for task in tasks:
            task_created = datetime.fromisoformat(task["created_at"])
            task_id = task["task_id"]
            
            # Number of comments (Poisson-like distribution)
            num_comments = random.choices(
                [0, 1, 2, 3, 4, 5],
                weights=[0.30, 0.35, 0.20, 0.10, 0.04, 0.01],
                k=1
            )[0]
            
            # Generate comment times (after task creation)
            comment_times = []
            current_time = task_created
            for _ in range(num_comments):
                # Comments happen over time, with more early on
                days_offset = random.expovariate(0.3)  # Exponential decay
                days_offset = min(days_offset, (end_date - current_time).days)
                comment_time = current_time + timedelta(days=int(days_offset))
                if comment_time > end_date:
                    break
                comment_times.append(comment_time)
                current_time = comment_time
        
            for comment_time in comment_times:
                # Select user (often the assignee or creator)
                if random.random() < 0.6 and task.get("assignee_id"):
                    # 60% by assignee
                    commenter = next((u for u in users if u["user_id"] == task["assignee_id"]), None)
                    if not commenter:
                        commenter = random.choice(users)
                elif random.random() < 0.3 and task.get("created_by"):
                    # 30% by creator
                    commenter = next((u for u in users if u["user_id"] == task["created_by"]), None)
                    if not commenter:
                        commenter = random.choice(users)
                else:
                    # 10% by random user
                    commenter = random.choice(users)
                
                # Generate comment text
                comment_text = self.llm.generate_comment(task["name"], task.get("project_type", "engineering"))
                
                comment = {
                    "comment_id": generate_id(),
                    "task_id": task_id,
                    "user_id": commenter["user_id"],
                    "text": comment_text,
                    "created_at": comment_time.isoformat()
                }
                comments.append(comment)
        
        return comments

