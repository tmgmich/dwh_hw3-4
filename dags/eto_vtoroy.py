import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

sql_script = '''
    CREATE TABLE IF NOT EXISTS presentation.sales_by_category (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        business_date DATE NOT NULL,
        category_name VARCHAR(255) NOT NULL,
        category_gmv NUMERIC(10,2) NOT NULL
    );
    
    INSERT INTO presentation.sales_by_category (business_date, category_name, category_gmv)
    SELECT 
      DATE(p.purchase_date) AS business_date,
      c.category_name,
      SUM(pi.product_count * pi.product_price) AS category_gmv
    FROM 
      public.purchases p
      JOIN public.purchase_items pi ON p.purchase_id = pi.purchase_id
      JOIN public.products pr ON pi.product_id = pr.product_id
      JOIN public.categories c ON pr.category_id = c.category_id
    WHERE 
      p.purchase_date >= DATE_TRUNC('day', NOW() - INTERVAL '1 DAY') AND p.purchase_date < DATE_TRUNC('day', NOW())
    GROUP BY 
      business_date, category_name;
    
    DELETE FROM presentation.sales_by_category WHERE business_date = DATE_TRUNC('day', NOW() - INTERVAL '1 DAY');
    
'''

DEFAULT_ARGS = {
    'owner': 'vlad',
    'depends_on_past': False,
    'start_date': datetime(2023, 11, 6),
    'email': None,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=120)
}

with DAG("choco_chaca2",
         default_args=DEFAULT_ARGS,
         catchup=False,
         schedule_interval="5 0 * * *",
         max_active_runs=1,
         concurrency=1) as dag:
    task = PostgresOperator(
        task_id="create_category_gmv",
        postgres_conn_id="dwh_hw",
        sql=sql_script,
    )

    task