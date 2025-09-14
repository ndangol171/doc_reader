
import hashlib
import requests
from pathlib import Path

PDFS = [
  ("Operation Overload", "https://checkfirst.network/wp-content/uploads/2024/06/Operation_Overload_WEB.pdf"),
  ("Storm-1516 Technical Report", "https://www.sgdsn.gouv.fr/files/files/Publications/20250507_TLP-CLEAR_NP_SGDSN_VIGINUM_Technical%20report_Storm-1516.pdf"),
  ("Doppelgänger Campaign Report", "https://www.auswaertiges-amt.de/resource/blob/2682484/2da31936d1cbeb9faec49df74d8bbe2e/technischer-bericht-desinformationskampagne-doppelgaenger-1--data.pdf")
]


def download_all(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for title, url in PDFS:
        fn = out_dir / (title.replace(' ', '_') + '.pdf')
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        fn.write_bytes(r.content)
        saved.append(fn)
    return saved


def sha256_file(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()
