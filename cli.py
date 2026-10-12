"""
Corporate Training & Knowledge Base Organizer (cli.py)
------------------------------------------------------
Bu arac, bir egitim veya proje konusunu okur, her bir konu icin 
guvenli klasorler/not dosyasi olusturur ve hem okunabilir bir metin 
hem de is dunyasinda (Excel vb.) kullanilabilecek bir CSV takvimi uretir.

Kullanim:
    python cli.py topics.txt
    python cli.py topics.txt --out egitim_plani --start 2026-10-15 --export-csv
"""

import argparse
import csv
import logging
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import List, Tuple

# Loglama ayarları (Print yerine daha profesyonel bir yaklaşım - Rigor)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# İlk eğitimden sonraki tekrar/gözden geçirme günleri
REVIEW_GAPS = [1, 3, 7] 


def read_topics(path: str) -> List[str]:
    """Dosyadan konuları okur. Boşlukları, yorumları ve kopyaları atlar."""
    file = Path(path)
    if not file.is_file():
        raise FileNotFoundError(f"'{path}' adinda bir dosya bulunamadi.")

    # Robustness: Dosya boyutu kontrolü (Çok büyük dosyalarla sistemi çökertmeyi engelleme)
    if file.stat().st_size > 1024 * 1024:  # 1 MB sınırı
        raise ValueError("Dosya cok buyuk! Lutfen daha kucuk bir dosya yukleyin.")

    try:
        lines = file.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        raise ValueError(f"'{path}' dosyasi UTF-8 formatinda olmalidir.")

    topics = []
    seen = set()
    for line in lines:
        topic = line.strip()
        # Boş satırları veya '#' ile başlayan yorumları atla
        if not topic or topic.startswith("#"):
            continue
        if topic.lower() in seen:
            logging.warning(f"Kopya konu atlandi: '{topic}'")
            continue
        seen.add(topic.lower())
        topics.append(topic)

    if not topics:
        raise ValueError(f"'{path}' icerisinde gecerli bir egitim konusu bulunamadi.")
    return topics


def make_folder_name(number: int, topic: str) -> str:
    """Konu adını, işletim sistemini bozmayacak güvenli bir klasör adına çevirir."""
    # Robustness: Sadece harf, rakam, tire ve boşluğa izin ver. Özel karakterleri sil.
    cleaned = re.sub(r"[^\w\- ]", "", topic)
    cleaned = " ".join(cleaned.split())[:50]  # Çok uzun isimleri kes
    if not cleaned:
        cleaned = "Bilinmeyen_Konu"
    return f"{number:02d} - {cleaned}"


def build_schedule(topics: List[str], start: date, gaps: List[int] = REVIEW_GAPS) -> List[Tuple[date, str, str]]:
    """Tarihe göre sıralanmış bir eğitim/tekrar takvimi oluşturur."""
    entries = []
    for i, topic in enumerate(topics):
        study_day = start + timedelta(days=i)
        entries.append((study_day, "EGITIM", topic))
        for gap in gaps:
            entries.append((study_day + timedelta(days=gap), "TEKRAR", topic))
    entries.sort(key=lambda entry: entry[0])
    return entries


def write_notes(folder: Path, topic: str, study_day: date) -> bool:
    """notes.md dosyasını oluşturur. Önceden varsa, veriyi silmemek için atlar."""
    notes = folder / "notes.md"
    if notes.exists():
        return False
    
    content = (
        f"# {topic}\n\n"
        f"**Planlanan İlk Eğitim Tarihi:** {study_day}\n\n"
        f"## Eğitim Notları\n\n"
        f"## Alınan Aksiyonlar / Sorular\n\n"
    )
    notes.write_text(content, encoding="utf-8")
    return True


def export_schedule_to_csv(out_dir: Path, entries: List[Tuple[date, str, str]]) -> Path:
    """Takvimi, diğer iş uygulamaları (Excel, Google Calendar vb.) için CSV'ye aktarır. (Novelty/Business Case)"""
    csv_path = out_dir / "schedule_export.csv"
    with csv_path.open(mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Tarih", "Aktivite_Turu", "Konu_Basligi"])
        for day, kind, topic in entries:
            writer.writerow([day, kind, topic])
    return csv_path


def organize(topics: List[str], out_dir: Path, start: date, generate_csv: bool) -> int:
    """Klasörleri ve notları oluşturur, takvimi yazar."""
    out_dir.mkdir(parents=True, exist_ok=True)
    created = 0

    for i, topic in enumerate(topics):
        folder = out_dir / make_folder_name(i + 1, topic)
        folder.mkdir(exist_ok=True)
        study_day = start + timedelta(days=i)
        if write_notes(folder, topic, study_day):
            created += 1

    # Normal txt Takvimi
    lines = ["KURUMSAL EGITIM TAKVIMI", "=" * 25]
    entries = build_schedule(topics, start)
    for day, kind, topic in entries:
        lines.append(f"{day} | {kind:<8} | {topic}")
    
    (out_dir / "schedule.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # CSV Export (Eğer istenmişse)
    if generate_csv:
        export_schedule_to_csv(out_dir, entries)
        logging.info("CSV disari aktarimi basariyla tamamlandi.")

    return created


def parse_date(text: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{text}' gecersiz! Ornek format: 2026-10-15")


def main():
    parser = argparse.ArgumentParser(description="Kurumsal egitim klasorleri ve planlayicisi olusturur.")
    parser.add_argument("topics_file", help="Her satirinda bir konu olan metin dosyasi (orn: topics.txt)")
    parser.add_argument("--out", default="workspace", help="Cikti klasoru adi (varsayilan: workspace)")
    parser.add_argument("--start", type=parse_date,
                        default=date.today() + timedelta(days=1),
                        help="Ilk egitim tarihi YYYY-MM-DD (varsayilan: yarin)")
    # Novelty/Rigor eklentisi: Opsiyonel CSV çıktısı
    parser.add_argument("--export-csv", action="store_true", 
                        help="Takvimi diger sistemlere entegre etmek icin CSV olarak disari aktarir.")
    
    args = parser.parse_args()

    try:
        topics = read_topics(args.topics_file)
        created = organize(topics, Path(args.out), args.start, args.export_csv)
    except (OSError, ValueError) as error:
        logging.error(error)
        return 1

    logging.info(f"{len(topics)} konu okundu, {created} yeni not dosyasi olusturuldu.")
    logging.info(f"Takvim '{args.out}' klasorune kaydedildi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
