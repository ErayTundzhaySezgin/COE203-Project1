import argparse
import csv
import os
import re
from datetime import date, timedelta

REVIEW_GAPS = [1, 3, 7]  # Review on days 1, 3, and 7 after the initial training

def read_topics(path):
    """Reads training topics from a file, skipping empty lines and duplicates."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Error: Could not find the file '{path}'.")
    
    # Robustness: File size check (prevent memory overflow with maliciously large files)
    if os.path.getsize(path) > 1024 * 1024:
        raise ValueError("Error: File is too large! Operation aborted.")

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    topics = []
    for line in lines:
        topic = line.strip()
        # Skip empty lines and comments
        if topic == "" or topic.startswith("#"):
            continue
        # Skip duplicates
        if topic not in topics:
            topics.append(topic)
    
    if not topics:
        raise ValueError("Error: No valid topics found in the file.")
    return topics

def make_safe_name(topic):
    """Removes special characters to ensure safe folder names for the OS."""
    # Rigor: Use Regex (re) to allow only alphanumeric characters, dashes, and spaces
    cleaned = re.sub(r"[^\w\- ]", "", topic)
    return cleaned.strip()[:50]  # Truncate if the name is too long

def export_csv(out_dir, entries):
    """Exports the schedule as a CSV file for ERP/Excel integration (Novelty)."""
    csv_path = os.path.join(out_dir, "schedule_export.csv")
    with open(csv_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Activity_Type", "Topic"])
        for day, kind, topic in entries:
            writer.writerow([day, kind, topic])

def organise(topics, out_dir, start_date, generate_csv):
    """Generates the folders, markdown notes, and the schedule."""
    os.makedirs(out_dir, exist_ok=True)
    entries = []
    
    for i, topic in enumerate(topics):
        # 1. Create Folders (e.g., 01 - Python Basics)
        safe_name = make_safe_name(topic)
        folder_name = f"{i+1:02d} - {safe_name}"
        folder_path = os.path.join(out_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # 2. Create Note Files
        study_day = start_date + timedelta(days=i)
        notes_file = os.path.join(folder_path, "notes.md")
        if not os.path.exists(notes_file):
            with open(notes_file, "w", encoding="utf-8") as f:
                f.write(f"# {topic}\n\nScheduled Date: {study_day}\n\n## Notes\n\n## Action Items\n")
        
        # 3. Prepare Data for the Schedule
        entries.append((study_day, "TRAINING", topic))
        for gap in REVIEW_GAPS:
            review_day = study_day + timedelta(days=gap)
            entries.append((review_day, "REVIEW", topic))
    
    # Sort entries by date
    entries.sort(key=lambda x: x[0])
    
    # Generate the standard TXT Schedule
    txt_path = os.path.join(out_dir, "schedule.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("CORPORATE TRAINING SCHEDULE\n===========================\n")
        for day, kind, topic in entries:
            f.write(f"{day} | {kind:<9} | {topic}\n")

    # Generate CSV Output if requested by the user
    if generate_csv:
        export_csv(out_dir, entries)

def main():
    parser = argparse.ArgumentParser(description="Corporate Training & Knowledge Base Organiser")
    parser.add_argument("topics_file", help="Text file containing the topics")
    parser.add_argument("--out", default="workspace", help="Output directory name")
    parser.add_argument("--start", default=str(date.today() + timedelta(days=1)), help="Start date (YYYY-MM-DD)")
    parser.add_argument("--export-csv", action="store_true", help="Export the schedule as a CSV file")
    
    args = parser.parse_args()

    try:
        start_date = date.fromisoformat(args.start)
        topics = read_topics(args.topics_file)
        organise(topics, args.out, start_date, args.export_csv)
        print("Success! Folders, notes, and the schedule have been generated.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
