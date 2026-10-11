import os
import datetime
import sys

def create_study_workspace(topics_file: str) -> None:
    """
    Reads a list of topics from a text file, generates a directory structure
    for each topic, creates markdown note templates, and automates a daily
    study schedule.
    """
    if not os.path.exists(topics_file):
        print(f"The input file '{topics_file}' was not found.")
        sys.exit(1)

    with open(topics_file, 'r', encoding='utf-8') as file:
        topics = [line.strip() for line in file if line.strip()]

    start_date = datetime.date.today() + datetime.timedelta(days=1)
    schedule_file_path = "study_schedule.txt"

    with open(schedule_file_path, 'w', encoding='utf-8') as schedule_file:
        schedule_file.write("Automated Study Schedule\n")
        schedule_file.write("========================\n")

        for day_counter, topic in enumerate(topics):
            os.makedirs(topic, exist_ok=True)
            
            study_date = start_date + datetime.timedelta(days=day_counter)
            date_str = study_date.strftime("%Y-%m-%d")
            
            notes_file_path = os.path.join(topic, "notes.md")
            if not os.path.exists(notes_file_path):
                with open(notes_file_path, 'w', encoding='utf-8') as notes_file:
                    notes_file.write(f"# {topic}\n\n**Scheduled Date:** {date_str}\n\n")
            else:
                print(f"Notes file for topic '{topic}' already exists. Skipping creation.")
            
            schedule_file.write(f"{date_str} -> {topic}\n")

if __name__ == "__main__":
    create_study_workspace("topics.txt")