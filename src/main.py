"""Main orchestration script for generating Asana simulation data."""
import os
import random
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

from utils.helpers import generate_id

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import Database
from generators.users import UserGenerator
from generators.teams import TeamGenerator
from generators.projects import ProjectGenerator
from generators.tasks import TaskGenerator
from generators.comments import CommentGenerator
from generators.custom_fields import CustomFieldGenerator
from generators.tags import TagGenerator
from generators.attachments import AttachmentGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def insert_data(conn, table_name: str, data: list):
    """Insert data into a table.
    
    Args:
        conn: Database connection
        table_name: Name of the table
        data: List of dictionaries with data
    """
    if not data:
        return
    
    columns = list(data[0].keys())
    placeholders = ', '.join(['?' for _ in columns])
    column_names = ', '.join(columns)
    
    sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
    
    values = [tuple(row[col] for col in columns) for row in data]
    
    conn.executemany(sql, values)
    conn.commit()
    logger.info(f"Inserted {len(data)} rows into {table_name}")


def generate_team_memberships(teams: list, users: list, team_memberships_dict: dict) -> list:
    """Generate team membership records.
    
    Team sizes based on industry benchmarks:
    - Small teams (3-7 members): 40%
    - Medium teams (8-15 members): 40%
    - Large teams (16-30 members): 20%
    
    Args:
        teams: List of team dictionaries
        users: List of user dictionaries
        team_memberships_dict: Dictionary to populate with team_id -> user_ids mapping
        
    Returns:
        List of team membership dictionaries
    """
    
    memberships = []
    
    for team in teams:
        team_id = team["team_id"]
        
        # Determine team size
        rand = random.random()
        if rand < 0.40:
            team_size = random.randint(3, 7)  # Small
        elif rand < 0.80:
            team_size = random.randint(8, 15)  # Medium
        else:
            team_size = random.randint(16, 30)  # Large
        
        # Select users for this team
        team_users = random.sample(users, min(team_size, len(users)))
        team_memberships_dict[team_id] = [u["user_id"] for u in team_users]
        
        for user in team_users:
            membership = {
                "membership_id": generate_id(),
                "team_id": team_id,
                "user_id": user["user_id"],
                "role": "member" if random.random() > 0.1 else "admin",
                "joined_at": user["created_at"]  # Join when user is created
            }
            memberships.append(membership)
    
    return memberships


def main():
    """Main function to generate all data."""
    
    # Configuration
    org_size = int(os.getenv("ORG_SIZE", "7500"))
    num_teams = int(os.getenv("NUM_TEAMS", "50"))
    start_date_str = os.getenv("START_DATE", "2024-01-01")
    end_date_str = os.getenv("END_DATE", "2024-07-01")
    
    start_date = datetime.fromisoformat(start_date_str)
    end_date = datetime.fromisoformat(end_date_str)
    
    logger.info("Starting Asana simulation data generation")
    logger.info(f"Organization size: {org_size} users")
    logger.info(f"Number of teams: {num_teams}")
    logger.info(f"Date range: {start_date.date()} to {end_date.date()}")
    
    # Initialize database
    db = Database()

    # Always start from a clean database file to avoid UNIQUE constraint conflicts
    if os.path.exists(db.db_path):
        os.remove(db.db_path)
        logger.info(f"Removed existing database at {db.db_path} for a clean run")

    with db as db:
        logger.info("Initializing database schema...")
        db.initialize_schema()
        
        # Generate organization
        logger.info("Generating organization...")
        org_id = generate_id()
        org_data = [{
            "organization_id": org_id,
            "name": "Acme Corporation",
            "domain": "acme.com",
            "created_at": start_date.isoformat()
        }]
        insert_data(db.conn, "organizations", org_data)
        
        # Generate users
        logger.info(f"Generating {org_size} users...")
        user_gen = UserGenerator()
        users = user_gen.generate_users(org_size, org_id, start_date, end_date)
        insert_data(db.conn, "users", users)
        logger.info(f"Generated {len(users)} users")
        
        # Generate teams
        logger.info(f"Generating {num_teams} teams...")
        team_gen = TeamGenerator()
        teams = team_gen.generate_teams(num_teams, org_id, start_date, end_date)
        insert_data(db.conn, "teams", teams)
        logger.info(f"Generated {len(teams)} teams")
        
        # Generate team memberships
        logger.info("Generating team memberships...")
        team_memberships_dict = {}
        memberships = generate_team_memberships(teams, users, team_memberships_dict)
        insert_data(db.conn, "team_memberships", memberships)
        logger.info(f"Generated {len(memberships)} team memberships")
        
        # Generate projects and sections
        logger.info("Generating projects and sections...")
        project_gen = ProjectGenerator()
        projects, sections = project_gen.generate_projects(
            random.randint(200, 500), teams, users, start_date, end_date
        )
        insert_data(db.conn, "projects", projects)
        insert_data(db.conn, "sections", sections)
        logger.info(f"Generated {len(projects)} projects and {len(sections)} sections")
        
        # Generate tags
        logger.info("Generating tags...")
        tag_gen = TagGenerator()
        tags = tag_gen.generate_tags(org_id, 30)
        insert_data(db.conn, "tags", tags)
        logger.info(f"Generated {len(tags)} tags")
        
        # Generate tasks
        logger.info("Generating tasks...")
        task_gen = TaskGenerator()
        tasks = task_gen.generate_tasks(
            projects, sections, users, team_memberships_dict,
            start_date, end_date, tasks_per_project=30
        )
        insert_data(db.conn, "tasks", tasks)
        logger.info(f"Generated {len(tasks)} tasks")
        
        # Generate subtasks
        logger.info("Generating subtasks...")
        subtasks = task_gen.generate_subtasks(tasks, users, subtask_ratio=0.20)
        if subtasks:
            insert_data(db.conn, "tasks", subtasks)
            logger.info(f"Generated {len(subtasks)} subtasks")
        
        # Generate comments
        logger.info("Generating comments...")
        comment_gen = CommentGenerator()
        comments = comment_gen.generate_comments(tasks + subtasks, users, start_date, end_date)
        insert_data(db.conn, "comments", comments)
        logger.info(f"Generated {len(comments)} comments")
        
        # Generate attachments
        logger.info("Generating attachments...")
        attachment_gen = AttachmentGenerator()
        attachments = attachment_gen.generate_attachments(tasks + subtasks, users, start_date, end_date)
        if attachments:
            insert_data(db.conn, "attachments", attachments)
            logger.info(f"Generated {len(attachments)} attachments")
        
        # Generate custom fields
        logger.info("Generating custom fields...")
        custom_field_gen = CustomFieldGenerator()
        custom_field_defs = custom_field_gen.generate_custom_fields(projects)
        insert_data(db.conn, "custom_field_definitions", custom_field_defs)
        logger.info(f"Generated {len(custom_field_defs)} custom field definitions")
        
        # Generate custom field values
        logger.info("Generating custom field values...")
        custom_field_values = custom_field_gen.generate_custom_field_values(tasks + subtasks, custom_field_defs)
        insert_data(db.conn, "custom_field_values", custom_field_values)
        logger.info(f"Generated {len(custom_field_values)} custom field values")
        
        # Generate task tags
        logger.info("Generating task-tag associations...")
        task_tags = tag_gen.generate_task_tags(tasks + subtasks, tags)
        if task_tags:
            insert_data(db.conn, "task_tags", task_tags)
            logger.info(f"Generated {len(task_tags)} task-tag associations")
        
        logger.info("Data generation completed successfully!")
        logger.info(f"Database saved to: {db.db_path}")
        
        # Print summary statistics
        cursor = db.conn.cursor()
        tables = ["organizations", "teams", "users", "team_memberships", "projects", 
                 "sections", "tasks", "comments", "attachments", "custom_field_definitions", 
                 "custom_field_values", "tags", "task_tags"]
        
        logger.info("\n=== Database Summary ===")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            logger.info(f"{table}: {count} rows")


if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    main()

