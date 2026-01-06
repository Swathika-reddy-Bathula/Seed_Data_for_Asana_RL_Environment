"""Generate attachments data."""
import random
from typing import List, Dict
from datetime import datetime, timedelta
from utils.helpers import generate_id
from utils.dates import random_date


class AttachmentGenerator:
    """Generates realistic file attachments for tasks."""
    
    # Common file types by category
    FILE_TYPES = {
        "document": [
            ("document.pdf", "application/pdf", (50000, 5000000)),  # 50KB - 5MB
            ("report.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", (100000, 10000000)),  # 100KB - 10MB
            ("spec.pdf", "application/pdf", (200000, 3000000)),
            ("requirements.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", (150000, 8000000)),
            ("design-brief.pdf", "application/pdf", (300000, 4000000)),
        ],
        "image": [
            ("screenshot.png", "image/png", (50000, 2000000)),  # 50KB - 2MB
            ("mockup.jpg", "image/jpeg", (100000, 3000000)),
            ("diagram.png", "image/png", (80000, 1500000)),
            ("wireframe.png", "image/png", (60000, 1200000)),
            ("logo.svg", "image/svg+xml", (10000, 500000)),
        ],
        "spreadsheet": [
            ("data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", (50000, 2000000)),  # 50KB - 2MB
            ("budget.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", (80000, 3000000)),
            ("tracker.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", (60000, 1500000)),
        ],
        "code": [
            ("config.json", "application/json", (1000, 50000)),  # 1KB - 50KB
            ("script.js", "text/javascript", (5000, 200000)),
            ("styles.css", "text/css", (3000, 150000)),
            ("README.md", "text/markdown", (2000, 100000)),
        ],
        "archive": [
            ("archive.zip", "application/zip", (100000, 10000000)),  # 100KB - 10MB
            ("backup.tar.gz", "application/gzip", (200000, 5000000)),
        ],
        "other": [
            ("notes.txt", "text/plain", (1000, 50000)),
            ("presentation.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", (200000, 8000000)),
            ("video.mp4", "video/mp4", (1000000, 50000000)),  # 1MB - 50MB
        ]
    }
    
    # Base URL patterns for file storage (simulating cloud storage)
    URL_PATTERNS = [
        "https://storage.example.com/files/{id}/{name}",
        "https://cdn.company.com/attachments/{id}/{name}",
        "https://files.company.com/uploads/{id}/{name}",
        "https://s3.amazonaws.com/bucket/{id}/{name}",
    ]
    
    def __init__(self):
        """Initialize attachment generator."""
        pass
    
    def generate_attachments(self, tasks: List[Dict], users: List[Dict],
                           start_date: datetime, end_date: datetime,
                           attachments_per_task: float = 0.3) -> List[Dict]:
        """Generate attachments for tasks.
        
        Distribution: ~0.3 attachments per task on average (30% of tasks have attachments).
        Most tasks have 0-1 attachments, some have 2-3.
        Attachments are uploaded after task creation.
        
        Args:
            tasks: List of task dictionaries
            users: List of user dictionaries
            start_date: Start of simulation period
            end_date: End of simulation period
            attachments_per_task: Average number of attachments per task
            
        Returns:
            List of attachment dictionaries
        """
        attachments = []
        
        # Flatten file types for easier selection
        all_file_types = []
        for category_files in self.FILE_TYPES.values():
            all_file_types.extend(category_files)
        
        for task in tasks:
            task_created = datetime.fromisoformat(task["created_at"])
            task_id = task["task_id"]
            
            # Number of attachments (weighted distribution)
            # 70% no attachments, 20% 1 attachment, 7% 2 attachments, 2% 3 attachments, 1% 4+ attachments
            num_attachments = random.choices(
                [0, 1, 2, 3, 4],
                weights=[0.70, 0.20, 0.07, 0.02, 0.01],
                k=1
            )[0]
            
            if num_attachments == 0:
                continue
            
            # Generate attachment upload times (after task creation, but can be close)
            for i in range(num_attachments):
                # Attachments are often uploaded soon after task creation or comment
                # Exponential distribution with bias toward early uploads
                days_offset = random.expovariate(2.0)  # Faster decay = more early uploads
                days_offset = min(days_offset, (end_date - task_created).days)
                uploaded_at = task_created + timedelta(days=int(days_offset))
                
                if uploaded_at > end_date:
                    continue
                
                # Select file type (weighted by category based on project type)
                project_type = task.get("project_type", "engineering")
                file_category = self._select_file_category(project_type)
                file_name, file_type, size_range = random.choice(self.FILE_TYPES[file_category])
                
                # Generate file size within range
                file_size = random.randint(size_range[0], size_range[1])
                
                # Generate URL
                attachment_id = generate_id()
                url_pattern = random.choice(self.URL_PATTERNS)
                url = url_pattern.format(id=attachment_id, name=file_name)
                
                # Select uploader (often the assignee, creator, or random user)
                if random.random() < 0.5 and task.get("assignee_id"):
                    # 50% by assignee
                    uploader = next((u for u in users if u["user_id"] == task["assignee_id"]), None)
                    if not uploader:
                        uploader = random.choice(users)
                elif random.random() < 0.3 and task.get("created_by"):
                    # 30% by creator
                    uploader = next((u for u in users if u["user_id"] == task["created_by"]), None)
                    if not uploader:
                        uploader = random.choice(users)
                else:
                    # 20% by random user
                    uploader = random.choice(users)
                
                attachment = {
                    "attachment_id": attachment_id,
                    "task_id": task_id,
                    "name": file_name,
                    "file_type": file_type,
                    "file_size": file_size,
                    "url": url,
                    "uploaded_at": uploaded_at.isoformat(),
                    "uploaded_by": uploader["user_id"] if uploader else None
                }
                attachments.append(attachment)
        
        return attachments
    
    def _select_file_category(self, project_type: str) -> str:
        """Select file category based on project type.
        
        Args:
            project_type: Type of project (engineering, marketing, operations)
            
        Returns:
            File category name
        """
        project_type = project_type.lower()
        
        if project_type == "engineering":
            # Engineering projects: more code, documents, diagrams
            return random.choices(
                ["document", "image", "code", "spreadsheet", "other"],
                weights=[0.30, 0.25, 0.25, 0.10, 0.10],
                k=1
            )[0]
        elif project_type == "marketing":
            # Marketing projects: more images, documents, presentations
            return random.choices(
                ["image", "document", "other", "spreadsheet"],
                weights=[0.40, 0.30, 0.20, 0.10],
                k=1
            )[0]
        elif project_type == "operations":
            # Operations projects: more spreadsheets, documents, archives
            return random.choices(
                ["spreadsheet", "document", "archive", "other"],
                weights=[0.40, 0.30, 0.15, 0.15],
                k=1
            )[0]
        else:
            # Default: balanced distribution
            return random.choice(list(self.FILE_TYPES.keys()))

