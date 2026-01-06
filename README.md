# Asana Simulation Data Generator

A comprehensive data generation system for creating realistic seed datasets that simulate a B2B SaaS company's Asana workspace. This tool generates high-quality, representative data for reinforcement learning environments.

## Overview

This project generates a complete SQLite database simulating an Asana workspace for a B2B SaaS company with 5,000-10,000 employees. The data includes realistic entities such as organizations, teams, users, projects, tasks, comments, custom fields, tags, and more.

## Features

- **Realistic Data Generation**: Uses real-world sources and research-backed distributions
- **LLM-Powered Content**: Generates natural task names, descriptions, and comments using OpenAI
- **Temporal Consistency**: Ensures all time-based fields are logically consistent
- **Relational Integrity**: Maintains proper foreign key relationships and business logic
- **Configurable**: Adjustable parameters for organization size, date ranges, and more

## Setup

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (optional, for LLM-generated content)

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd Scalar_ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.examplel .env
# Edit .env and add your OPENAI_API_KEY (if using LLM features)
```

## Usage

### Basic Usage

Run the main script to generate the complete database:

```bash
python src/main.py
```

This will:
1. Initialize the database schema
2. Generate all entities (organizations, teams, users, projects, tasks, etc.)
3. Save the final database to `output/asana_simulation.sqlite`

### Configuration

Edit the `.env` file or set environment variables to customize:

- `ORG_SIZE`: Total number of employees (default: 7500)
- `NUM_TEAMS`: Number of teams (default: 50)
- `START_DATE`: Start date for timeline (default: 2024-01-01)
- `END_DATE`: End date for timeline (default: 2024-07-01)
- `OPENAI_API_KEY`: Your OpenAI API key for LLM generation

### Command Line Options

```bash
python src/main.py --org-size 8000 --num-teams 60 --start-date 2024-01-01 --end-date 2024-07-01
```

## Project Structure

```
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── schema.sql                   # Database schema (DDL)
├── .env.examplel                # Environment variables template
├── src/
│   ├── main.py                  # Entry point / orchestration
│   ├── scrapers/                # Modules for fetching external data
│   │   ├── __init__.py
│   │   └── company_scraper.py
│   ├── generators/              # Data generation logic
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── teams.py
│   │   ├── projects.py
│   │   ├── tasks.py
│   │   ├── comments.py
│   │   ├── custom_fields.py
│   │   └── tags.py
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   └── database.py
│   └── utils/                   # Helpers
│       ├── __init__.py
│       ├── dates.py
│       ├── llm.py
│       └── helpers.py
├── prompts/                     # LLM prompt templates
│   └── task_generation_prompts.txt
└── output/
    └── asana_simulation.sqlite  # Generated database
```

## Data Sources and Methodology

### Real-World Data Sources

- **Company Names**: Scraped from public directories
- **User Names**: Generated using Faker with census-based distributions
- **Project Names**: Derived from common SaaS project patterns
- **Task Descriptions**: Patterns from public issue trackers and templates

### Distribution Research

- Task completion rates based on Asana's "Anatomy of Work" reports
- Due date patterns from sprint duration research
- Team size distributions from industry benchmarks

For detailed methodology, see the documentation file.

## Output

The generated database (`output/asana_simulation.sqlite`) contains:

- 1 Organization
- 50-100 Teams
- 5,000-10,000 Users
- 200-500 Projects
- 5,000-15,000 Tasks (including subtasks)
- Comments, custom fields, tags, and attachments

## Requirements

- Python 3.8+
- SQLite3 (included with Python)
- OpenAI API key (optional, for enhanced content generation)

## License

This project is created as part of a take-home assignment.

## Contact

For questions or issues, please refer to the documentation or open an issue in the repository.

