import sys
from pathlib import Path

# Proje kökünü Python arama yoluna ekle
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pathlib import Path
from mcp.server import MCPServer
from config import ALLOWED_PATHS
from app.document_loader import load_document
import time


# MCP sunucusunu oluştur
mcp = MCPServer("Local Filesystem Assistant")


# is_allowed_path() ise ileride bütün filesystem tool'larının kullanacağı güvenlik kontrolü olacak.
def is_allowed_path(path: Path) -> bool:
    """
    Dosya yolunun izin verilen klasörlerden biri içinde olup olmadığını kontrol eder.
    """

    try:
        path = path.resolve()
        """
        Verilen dosya yolunu tam ve kesin bir yola (absolute path) çevirir (örneğin ../dosya.txt gibi kısaltmaları tam adrese dönüştürür).
        """

        return any(
            path == allowed.resolve()
            or allowed.resolve() in path.parents
            for allowed in ALLOWED_PATHS
        )

    except OSError:
        return False



# @mcp.tool() ile fonksiyonu mcp'nin toolu olarak tanımlıyabiliyoruz 
@mcp.tool()
def search_files(query: str) -> list[str]:
    """
    İzin verilen klasörlerde dosya adına göre arama yapar.
    """

    results = []

    for allowed_path in ALLOWED_PATHS:

        if not allowed_path.exists():
            continue

        for file in allowed_path.rglob("*"): # rglob("*") derinlemesine arama yapar.

            if not file.is_file():
                continue

            if query.lower() in file.name.lower():

                if is_allowed_path(file):
                    results.append(str(file))

    return results


@mcp.tool()
def get_file_info(file_path: str) -> dict:
    """
    Dosyanın temel bilgilerini döndürür.
    """

    path = Path(file_path)

    if not is_allowed_path(path):
        return {
            "error": "Bu dosyaya erişim izni yok."
        }

    if not path.exists():
        return {
            "error": "Dosya bulunamadı."
        }

    if not path.is_file():
        return {
            "error": "Belirtilen yol bir dosya değil."
        }

    stat = path.stat()

    return {
        "name": path.name,
        "path": str(path.resolve()),
        "extension": path.suffix,
        "size_bytes": f"{(stat.st_size/1024)/1024:.2} mb",
        "created": time.ctime(stat.st_birthtime),
        "modified": time.ctime(stat.st_mtime)
    }



@mcp.tool()
def search_content(query: str) -> list[dict]:
    """
    İzin verilen klasörlerde metin içeriğine göre bütün dosyaları tarıyıp 
    eğer içerisinde quey'nin geçtiği bir dosya bulursa dosyanın ismini ve yolunu result değişkenine atıyor.
    """

    results: list[dict[str, str]] = []

    for allowed_path in ALLOWED_PATHS:

        if not allowed_path.exists():
            continue

        for file in allowed_path.rglob("*"):

            # Sadece dosyaları kontrol et
            if not file.is_file():
                continue

            # Güvenlik sınırını kontrol et
            if not is_allowed_path(file):
                continue

            try:
                # Mevcut document_loader sistemini kullan
                text = load_document(file)

            except (ValueError, OSError):
                continue

            # Büyük/küçük harf farkını kaldır
            if query.lower() in text.lower():
                results.append({
                    "name": file.name,
                    "path": str(file.resolve())
                })

    return results


@mcp.tool()
def list_directory(directory_path: str) -> list[str]:
    """
    İzin verilen klasördeki dosya ve klasörleri listeler.
    """

    path = Path(directory_path)

    if not is_allowed_path(path):
        return ["Bu klasöre erişim izni yok."]

    if not path.exists():
        return ["Klasör bulunamadı."]

    if not path.is_dir():
        return ["Belirtilen yol bir klasör değil."]

    results = []

    for item in sorted(path.iterdir()):
        results.append(
            str(item.resolve())
        )

    return results



@mcp.tool()
def get_recent_files(limit: int = 10) -> list[dict[str, str]]:
    """
    İzin verilen klasörlerde son değiştirilen dosyaları bulur.
    """

    files = []

    for allowed_path in ALLOWED_PATHS:

        if not allowed_path.exists():
            continue

        for file in allowed_path.rglob("*"):

            if not file.is_file():
                continue

            if not is_allowed_path(file):
                continue

            try:
                modified_time = file.stat().st_mtime

                files.append({
                    "name": file.name,
                    "path": str(file.resolve()),
                    "modified": str(modified_time)
                })

            except OSError:
                continue

    # En son değiştirilen dosyaları üstte tut
    files.sort(
        key=lambda item: float(item["modified"]),
        reverse=True
    )

    return files[:limit]



@mcp.tool()
def get_rag_index_status(file_path: str) -> dict[str, object]:
    """
    Dosyanın RAG veritabanında indekslenip indekslenmediğini kontrol eder.
    """

    path = Path(file_path)

    if not is_allowed_path(path):
        return {
            "indexed": False,
            "error": "Bu dosyaya erişim izni yok."
        }

    if not path.exists():
        return {
            "indexed": False,
            "error": "Dosya bulunamadı."
        }

    if not path.is_file():
        return {
            "indexed": False,
            "error": "Belirtilen yol bir dosya değil."
        }

    # Proje kökündeki gerçek RAG veritabanını kullan
    database_path = PROJECT_ROOT / "database" / "rag.db"

    from app.database import Database

    database = Database(
        db_path=str(database_path)
    )

    documents = database.get_documents()

    matching_chunks = [
        document
        for document in documents
        if document["source"] == path.name
    ]

    return {
        "indexed": len(matching_chunks) > 0,
        "source": path.name,
        "chunk_count": len(matching_chunks)
    }



if __name__ == "__main__":
    mcp.run()