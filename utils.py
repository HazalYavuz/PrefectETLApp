import psycopg2
from config import DB_PARAMS


def log_error(message, exception=None):
    if exception:
        print(f"[HATA] {message}: {exception}")
    else:
        print(f"[HATA] {message}")


def log_info(message):
    print(f"[BİLGİ] {message}")


def get_postgres_connection():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        log_info("PostgreSQL bağlantısı başarıyla kuruldu.")
        return conn
    except psycopg2.Error as e:
        log_error("PostgreSQL bağlantısı kurulamadı", e)
        raise