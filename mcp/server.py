from pathlib import Path

from mcp.server import MCPServer

from config import ALLOWED_PATHS

import time


mcp = MCPServer("Local Filesystem Assistant")

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

    results = []

    for allowed_path in ALLOWED_PATHS:

        if not allowed_path.exists():
            continue

        for file in allowed_path.rglob("*"):

            if not file.is_file() or not is_allowed_path(file):
                continue

            try:
                text = file.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )
            except (OSError, UnicodeError):
                continue

            if query.lower() in text.lower():
                results.append({
                    "name": file.name,
                    "path": str(file.resolve())
                })

    return results



if __name__ == "__main__":
    mcp.run()