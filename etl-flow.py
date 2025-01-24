from prefect import flow, task
import requests
import psycopg2
from utils import log_info, log_error, get_postgres_connection
from db_utils import create_db


@task
def fetch_data_from_api(endpoint):
    try:
        url = f"http://flask-app:5001/{endpoint}?page=1&per_page=500"

        log_info(f"{endpoint} için veri çekiliyor...")

        response = requests.get(url)

        if response.status_code == 200:
            log_info(f"HTTP {response.status_code}: {endpoint} verisi başarıyla çekildi.")
        else:
            log_error(f"HTTP {response.status_code}: {endpoint} isteğinde hata oluştu.")
            raise Exception(f"{endpoint} isteği başarısız. Status kod: {response.status_code}")

        data = response.json()
        log_info(f"{endpoint} verisi başarıyla işlendi: {len(data)} kayıt alındı.")
        return data

    except Exception as e:
        log_error(f"{endpoint} verisi çekilirken hata oluştu", e)
        raise

@task
def insert_to_postgres(data, table):
    try:
        conn = get_postgres_connection()
        cur = conn.cursor()

        log_info(f"{table} tablosuna veri ekleniyor...")

        for record in data:
            cur.execute(
                f"INSERT INTO {table} ({', '.join(record.keys())}) VALUES ({', '.join(['%s'] * len(record))})",
                tuple(record.values())
            )

        conn.commit()
        cur.close()
        conn.close()

        log_info(f"{table} tablosuna veri başarıyla eklendi.")
    
    except psycopg2.Error as e:
        log_error(f"{table} tablosuna veri eklenirken hata oluştu", e)
        raise

@flow(name="ETL Line",retries=0)
def etl_flow():
    try:

        create_db()
        
        customers = fetch_data_from_api("customers")
        subscriptions = fetch_data_from_api("subscriptions")
        payments = fetch_data_from_api("payments")
        usage = fetch_data_from_api("usage")
               
        
        insert_to_postgres(customers, "customers")
        insert_to_postgres(subscriptions, "subscriptions")
        insert_to_postgres(usage, "usage")
        insert_to_postgres(payments, "payments")
                
        
    except Exception as e:
        log_error("ETL akışı sırasında hata oluştu", e)
        raise

if __name__ == "__main__":
    log_info("ETL Akışı başlatılıyor...")
    etl_flow()
