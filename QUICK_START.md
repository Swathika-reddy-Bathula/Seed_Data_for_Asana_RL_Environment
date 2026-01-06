# Quick Start Guide

This guide will help you quickly get started and generate the database.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure (Optional)

If you want to use LLM features for enhanced content generation:

1. Copy `.env.examplel` to `.env`:
   ```bash
   cp .env.examplel .env
   ```

2. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_key_here
   ```

**Note**: The code will work without an API key, but will use fallback templates instead of LLM-generated content.

## Step 3: Generate Database

Run the main script:

```bash
python src/main.py
```

This will:
- Create the database schema
- Generate all data (organizations, teams, users, projects, tasks, etc.)
- Save the database to `output/asana_simulation.sqlite`

## Step 4: Verify

Check that the database was created:

```bash
# On Linux/Mac:
ls -lh output/asana_simulation.sqlite

# On Windows:
dir output\asana_simulation.sqlite
```

You can also verify using SQLite:
```bash
sqlite3 output/asana_simulation.sqlite "SELECT COUNT(*) FROM users;"
sqlite3 output/asana_simulation.sqlite "SELECT COUNT(*) FROM tasks;"
```

## Configuration Options

Edit `.env` or set environment variables to customize:

- `ORG_SIZE`: Number of users (default: 7500)
- `NUM_TEAMS`: Number of teams (default: 50)
- `START_DATE`: Simulation start date (default: 2024-01-01)
- `END_DATE`: Simulation end date (default: 2024-07-01)

## Troubleshooting

### Import Errors
If you get import errors, make sure you're running from the project root directory and that all dependencies are installed.

### Database Generation Takes Time
Generating 7,500 users and thousands of tasks can take several minutes. This is normal. The script shows progress logs.

### LLM API Errors
If you see LLM-related errors, the code will automatically fall back to template-based generation. Your database will still be generated successfully.

