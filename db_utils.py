from utils import log_info, log_error, get_postgres_connection


log_info("Starting data generation script...")

def create_db():
    conn = get_postgres_connection()
    cur = conn.cursor()

    try:
        
        log_info("Dropping existing tables if any...")
        cur.execute("DROP TABLE IF EXISTS usage, payments, subscriptions, customers, payment_amount CASCADE;")
        
        log_info("Creating 'customers' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255),
                phone VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        log_info("Creating 'subscriptions' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                subscription_id SERIAL PRIMARY KEY,
                customer_id INTEGER REFERENCES customers(customer_id),
                subscription_type VARCHAR(50),
                start_date DATE,
                end_date DATE
            );
        """)
        log_info("Creating 'payments' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                payment_id SERIAL PRIMARY KEY,
                subscription_id INTEGER REFERENCES subscriptions(subscription_id),
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                amount DECIMAL(10, 2)
            );
        """)
        log_info("Creating 'usage' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usage (
                usage_id SERIAL PRIMARY KEY,
                subscription_id INTEGER REFERENCES subscriptions(subscription_id),
                data_usage DECIMAL(10, 2),
                call_minutes DECIMAL(10, 2),
                sms_count INTEGER
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS payment_amount (
                id SERIAL PRIMARY KEY,
                customer_id INT NOT NULL,
                sum_payment NUMERIC(10, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        log_info("Tables created successfully.")
        
        log_info("Creating 'customer_usage_summary' view...")
        cur.execute("""
            CREATE OR REPLACE VIEW public.customer_usage_summary
            AS SELECT c.customer_id,
                c.name AS customer_name,
                round(avg(u.data_usage), 2) AS avg_data_usage,
                round(avg(u.call_minutes), 2) AS avg_call_minutes,
                round(avg(u.sms_count), 2) AS avg_sms_count
            FROM customers c
                JOIN subscriptions s ON c.customer_id = s.customer_id
                JOIN usage u ON s.subscription_id = u.subscription_id
            WHERE s.end_date >= CURRENT_DATE
            GROUP BY c.customer_id, c.name;
        """)

        log_info("Creating 'high_value_customers' view...")
        cur.execute("""
            CREATE OR REPLACE VIEW public.high_value_customers
            AS SELECT c.customer_id,
                c.name AS customer_name,
                sum(p.amount) AS total_payment_last_30_days,
                cus.avg_data_usage,
                cus.avg_call_minutes,
                cus.avg_sms_count
            FROM customers c
                JOIN subscriptions s ON c.customer_id = s.customer_id
                JOIN payments p ON s.subscription_id = p.subscription_id
                JOIN customer_usage_summary cus ON c.customer_id = cus.customer_id
            WHERE p.payment_date >= (CURRENT_DATE - '30 days'::interval)
            GROUP BY c.customer_id, c.name, cus.avg_data_usage, cus.avg_call_minutes, cus.avg_sms_count
            HAVING sum(p.amount) > 500::numeric;
        """)

        conn.commit()
        log_info("Views created successfully.")
    except Exception as e:
        log_error(f"Error setting up database: {e}")
    finally:
        cur.close()
        conn.close()

