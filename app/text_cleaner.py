import re
import unicodedata

try:
    from ftfy import fix_text
    FTFY_AVAILABLE = True
except ImportError:
    FTFY_AVAILABLE = False


def normalize_newlines(text: str) -> str:
    """
    Satır sonlarını standart hale getirir.
    """
    return (
        text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )


def normalize_unicode(text: str) -> str:
    """
    Unicode karakterleri standart forma getirir (NFKC).
    Örn: farklı gösterilen aynı karakterleri, ligature'ları
    (ﬁ -> fi) birleştirir. PDF ve Word çıktılarında önemlidir.
    """
    return unicodedata.normalize("NFKC", text)


def remove_control_characters(text: str) -> str:
    """
    Null dahil, görünmez kontrol karakterlerini kaldırır.
    \n, \t gibi anlamlı karakterler korunur.
    """
    return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)


def remove_invisible_characters(text: str) -> str:
    """
    PDF, Word ve HTML belgelerinde oluşabilen görünmez
    Unicode karakterlerini temizler (zero-width space vb.).
    """
    return re.sub(
        r"[\u200B-\u200D\uFEFF]",
        "",
        text
    )


def fix_hyphenation(text: str) -> str:
    """
    PDF'lerde satır sonunda tire ile bölünmüş kelimeleri birleştirir.
    Örn: "bilgi-\nsayar" -> "bilgisayar"
    """
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)


def remove_long_separators(text: str) -> str:
    """
    ===== veya ----- gibi uzun ayırıcı çizgileri kaldırır.
    """
    text = re.sub(r"={5,}", "", text)
    text = re.sub(r"-{5,}", "", text)
    return text


def normalize_whitespace(text: str) -> str:
    """
    Fazla boşlukları tek boşluğa indirir.
    Satır sonlarını korur.
    """
    return re.sub(
        r"[ \t]+",
        " ",
        text
    )


def remove_extra_blank_lines(text: str) -> str:
    """
    Üç ve daha fazla boş satırı iki satıra indirir.
    """
    return re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )


def fix_text_encoding(text: str) -> str:
    """
    Mojibake (â€™, Ã¶, Ã¼ vb.) ve bazı Unicode
    kodlama problemlerini düzeltir.
    """

    if not FTFY_AVAILABLE:
        return text

    return fix_text(text)


def clean_text(text: str) -> str:
    """
    Doküman metnini embedding işleminden önce temizler.

    Bu fonksiyon belgeye özel değildir.
    Her türlü metin dosyasında güvenle çalışacak şekilde
    tasarlanmıştır.
    """

    if not text:
        return ""

    cleaning_pipeline = [

        normalize_newlines,

        normalize_unicode,

        fix_text_encoding,

        remove_control_characters,

        remove_invisible_characters,

        fix_hyphenation,

        remove_long_separators,

        normalize_whitespace,

        remove_extra_blank_lines,

    ]

    '''
    Önce satır sonlarını normalize ediyoruz.
    Sonra Unicode'u standart hale getiriyoruz.
    Ardından varsa encoding sorunlarını düzeltiyoruz.
    Daha sonra kontrol ve görünmez karakterleri temizliyoruz.
    Son olarak satır sonlarını kullanan fix_hyphenation() çalışıyor.
        
    '''

    for cleaner in cleaning_pipeline:
        text = cleaner(text)

    return text.strip()




# hybrid search için gerekli olan fonksiyonlar 

def normalize_text(text: str) -> str:
    """
    Hybrid Search için metni normalize eder.
    """

    text = text.lower()

    text = re.sub(
        r"[^\w\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def keyword_score(
    query: str,
    content: str
) -> float:
    """
    Sorgu ile içerik arasındaki kelime eşleşme skorunu hesaplar.
    """

    query_words = set(
        normalize_text(query).split()
    )

    content_words = set(
        normalize_text(content).split()
    )

    if not query_words:
        return 0.0

    matched_words = query_words & content_words

    return len(matched_words) / len(query_words)