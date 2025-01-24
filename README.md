# TeknasyonApp

 ## Project Structure

├── config.py                  # Configuration settings for the project
├── etl-flow.py                # ETL workflow definition
├── payment_insertion_flow.py  # Payment insertion workflow definition
├── prefect.yaml               # Prefect project configuration file
├── requirements.txt           # List of dependencies
├── utils.py                   # Helper functions and utilities

## Database Schema

The database schema for this project is built using PostgreSQL. Below are the details of the database tables:

### 1. `customers`
Contains customer-related information:
- **Columns:**
  - `customer_id`: Unique identifier for each customer.
  - `name`: Customer's name.
  - `email`: Customer's email address.
  - `phone`: Customer's phone number.
  - `created_at`: Timestamp of when the customer was added.

### 2. `subscriptions`
Tracks subscriptions associated with customers:
- **Columns:**
  - `subscription_id`: Unique identifier for each subscription.
  - `customer_id`: Foreign key linking to the `customers` table.
  - `subscription_type`: Type of subscription (e.g., Basic, Premium, Enterprise).
  - `start_date`: Start date of the subscription.
  - `end_date`: End date of the subscription.

### 3. `payments`
Logs payments for subscriptions:
- **Columns:**
  - `payment_id`: Unique identifier for each payment.
  - `subscription_id`: Foreign key linking to the `subscriptions` table.
  - `payment_date`: Timestamp of the payment.
  - `amount`: Amount paid for the subscription.

### 4. `usage`
Records service usage metrics:
- **Columns:**
  - `usage_id`: Unique identifier for each usage record.
  - `subscription_id`: Foreign key linking to the `subscriptions` table.
  - `data_usage`: Data consumed (in GB).
  - `call_minutes`: Minutes spent on calls.
  - `sms_count`: Number of SMS sent.

  ### 4. `payment_amount`
Payments made by customers (30 days):
- **Columns:**
  - `id`: Unique identifier for each payment.
  - `customer_id`: Unique identity number of customer 
  - `payment_amount`: The amount the customer pays for the invoice
  - `created_at`: Date of payment
 
  ### 5. `V_customer_usage_summary`
Average data, minutes, and SMS usage of customers:
- **Columns:**
  - `customer_id`: Unique identity number of customer
  - `customer_name`: Customer's name.
  - `avg_data_usage`: Average data usage by customers
  - `avg_call_minutes`: Average minutes usage by customers
  - `avg_sms_count`: Average sms usage by customers

  ### 6. `V_high_value_customers`
Total payments made by customer in the last 30 days, average data, minutes and SMS usage:
- **Columns:**
  - `customer_id`: Unique identity number of customer.
  - `customer_name`: Customer's name.
  - `total_payment_last_30_days`: Total payments made in the last 30 days.
  - `avg_data_usage`: Average data usage by customers.
  - `avg_call_minutes`: Average minutes usage by customers.
  - `avg_sms_count`: Average sms usage by customers.


## Quick Start

This project is fully containerized using Docker. To run the application, follow these simple steps:

 1. Clone the repository:

   -  git clone <repository-url>
   -  cd <repository-folder>

 2. - First, the project (technology-case-de-main) from you must be removed remotely.

 3. Start the application using Docker Compose:

   - docker-compose up

