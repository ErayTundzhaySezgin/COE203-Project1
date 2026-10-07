# Study Organizer - Personal Automation Tool

## Overview
This project is a Personal Automation Tool built for the COE203 course. It automatically generates a structured daily study schedule, creates dedicated folders, and initializes markdown notes for each topic to keep your studies organized.

## Features
- **File I/O:** Reads study topics from a text file (`topics.txt`).
- **Loops & Functions:** Iterates through topics to construct modular directories.
- **Automation:** Calculates and assigns a daily study date starting from tomorrow, then logs the entire plan into `study_schedule.txt`.

## Usage Instructions
1. Ensure `topics.txt` is located in the same directory as the script.
2. Add your study topics line by line in `topics.txt`.
3. Run the script via terminal:
   ```bash
   python study_organizer.py
   
