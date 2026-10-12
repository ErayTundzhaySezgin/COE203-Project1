# Corporate Training & Knowledge Base Organizer

This project is a CLI-based automation tool designed for corporate environments. It takes a list of training topics and automatically generates a structured workspace, including safe folder directories, Markdown note templates, and a spaced-repetition study schedule. 

## Business Case (Novelty)
Instead of a simple study organizer, this tool is adapted for corporate training schedules. It includes a `--export-csv` feature that allows managers to export the training schedule and integrate it into tools like Microsoft Excel, Google Calendar, or other corporate ERP systems.

## Files and Folders
- `cli.py`: The main Command Line Interface application. It handles argument parsing, file reading, folder creation, and schedule generation.
- `topics.txt`: A sample text file containing the list of topics to be scheduled.
- `contributions/`: This folder contains Markdown files detailing the specific contributions of each team member.
- `.gitignore`: Ensures that generated files (like `workspace/`, CSV exports, and `.txt` schedules) are not tracked by Git, keeping the repository clean.

## Usage
To run the application with default settings (creates a 'workspace' folder and starts tomorrow):
`python cli.py topics.txt`

To specify a custom output folder, a start date, and export the schedule as a CSV file:
`python cli.py topics.txt --out egitim_plani --start 2026-10-15 --export-csv`
