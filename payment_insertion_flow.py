from prefect import flow, task
import requests
import psycopg2
from config import DB_PARAMS
from utils import log_info, log_error, get_postgres_connection


@task
def calculate_total_payments():
    try:
        conn = get_postgres_connection()
        cur = conn.cursor()

        log_info("Son 30 gün için toplam ödemeler hesaplanıyor...")

        query = """
            SELECT 
                c.customer_id, 
                SUM(p.amount) AS sum_payment
            FROM customers c
            JOIN subscriptions s 
                ON c.customer_id = s.customer_id
            JOIN payments p 
                ON s.subscription_id = p.subscription_id
              WHERE p.payment_date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY c.customer_id;
        """
        cur.execute(query)
        results = cur.fetchall()

        cur.close()
        conn.close()

        log_info(f"Toplam {len(results)} müşteri için ödemeler hesaplandı.")
        return [{"customer_id": row[0], "sum_payment": float(row[1])} for row in results]

    except psycopg2.Error as e:
        log_error("Toplam ödemeler hesaplanırken hata oluştu", e)
        raise

@task
def post_payment_amount(data):
    try:
        url = "http://flask-app:5001/payment_amount"
        headers = {"Content-Type": "application/json"}

        log_info(f"Sonuçlar API'ye gönderiliyor: {url}...")

        response = requests.post(url, json=data, headers=headers)

        if response.status_code in [200, 201]:
            log_info(f"Sonuçlar API'ye başarıyla gönderildi. Status kod: {response.status_code}")
        else:
            log_error(f"API isteğinde hata oluştu. Status kod: {response.status_code}")

        return response.json()

    except requests.RequestException as e:
        log_error("API'ye sonuçlar gönderilirken bağlantı hatası oluştu", e)
        raise


@flow(name="Payment Insertion Flow") #,  retries=3, retry_delay_seconds=300
def payment_insertion_flow():
    try:
        total_payments = calculate_total_payments()

        post_payment_amount(total_payments)

        log_info("Payment Insertion Flow başarıyla tamamlandı.")

    except Exception as e:
        log_error("Payment Insertion Flow sırasında hata oluştu", e)
        raise


if __name__ == "__main__":
    log_info("Payment Insertion Flow başlatılıyor...")
    payment_insertion_flow()
