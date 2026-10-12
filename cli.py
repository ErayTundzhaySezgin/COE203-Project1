import argparse
import csv
import os
import re
from datetime import date, timedelta

REVIEW_GAPS = [1, 3, 7] # 1., 3. ve 7. gün tekrar et

def read_topics(path):
    """Dosyadan egitim konularini okur, bosluklari ve kopyalari atlar."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Hata: '{path}' adinda bir dosya bulunamadi.")
    
    # Robustness (Saglamlik): Dosya boyutu kontrolü (cok buyuk dosyalarla cokertmeyi engelleme)
    if os.path.getsize(path) > 1024 * 1024:
        raise ValueError("Dosya cok buyuk! Gecersiz islem.")

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    topics = []
    for line in lines:
        topic = line.strip()
        # Yorumlari ve bos satirlari atla
        if topic == "" or topic.startswith("#"):
            continue
        # Kopya konulari atla
        if topic not in topics:
            topics.append(topic)
    
    if not topics:
        raise ValueError("Dosya icinde gecerli bir konu bulunamadi.")
    return topics

def make_safe_name(topic):
    """Dosya isimlerinde isletim sistemini bozmamasi icin ozel karakterleri siler."""
    # Regex (re) kullanarak sadece harf, rakam, tire ve bosluga izin ver
    cleaned = re.sub(r"[^\w\- ]", "", topic)
    return cleaned.strip()[:50] # Isim cok uzunsa 50 karakterle sinirla

def export_csv(out_dir, entries):
    """Takvimi Excel vb. programlar icin CSV olarak aktarir (Novelty/Yaraticilik Puanı)."""
    csv_path = os.path.join(out_dir, "schedule_export.csv")
    with open(csv_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Tarih", "Aktivite", "Konu"])
        for day, kind, topic in entries:
            writer.writerow([day, kind, topic])

def organize(topics, out_dir, start_date, generate_csv):
    """Klasorleri, notlari ve takvimi olusturur."""
    os.makedirs(out_dir, exist_ok=True)
    entries = []
    
    for i, topic in enumerate(topics):
        # 1. Klasorleri Olustur (Ornek: 01 - Python Temelleri)
        safe_name = make_safe_name(topic)
        folder_name = f"{i+1:02d} - {safe_name}"
        folder_path = os.path.join(out_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # 2. Not Dosyasini Olustur
        study_day = start_date + timedelta(days=i)
        notes_file = os.path.join(folder_path, "notes.md")
        if not os.path.exists(notes_file):
            with open(notes_file, "w", encoding="utf-8") as f:
                f.write(f"# {topic}\n\nPlanlanan Tarih: {study_day}\n\n## Notlar\n")
        
        # 3. Takvim Icin Verileri Hazirla
        entries.append((study_day, "EGITIM", topic))
        for gap in REVIEW_GAPS:
            review_day = study_day + timedelta(days=gap)
            entries.append((review_day, "TEKRAR", topic))
    
    # Tarihe gore listeyi sirala
    entries.sort(key=lambda x: x[0])
    
    # Normal TXT Takvimini Olustur
    txt_path = os.path.join(out_dir, "schedule.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("KURUMSAL EGITIM TAKVIMI\n=======================\n")
        for day, kind, topic in entries:
            f.write(f"{day} | {kind:<8} | {topic}\n")

    # Eger kullanici istediyse CSV Ciktisi al
    if generate_csv:
        export_csv(out_dir, entries)

def main():
    parser = argparse.ArgumentParser(description="Kurumsal Egitim Planlayici")
    parser.add_argument("topics_file", help="Konularin yazili oldugu txt dosyasi")
    parser.add_argument("--out", default="workspace", help="Cikti klasoru adi")
    parser.add_argument("--start", default=str(date.today() + timedelta(days=1)), help="Baslangic tarihi (YYYY-MM-DD)")
    parser.add_argument("--export-csv", action="store_true", help="Takvimi CSV olarak disari aktarir")
    
    args = parser.parse_args()

    try:
        start_date = date.fromisoformat(args.start)
        topics = read_topics(args.topics_file)
        organize(topics, args.out, start_date, args.export_csv)
        print("Islem basarili! Dosyalar ve takvim olusturuldu.")
    except Exception as e:
        print(f"HATA: {e}")

if __name__ == "__main__":
    main()
