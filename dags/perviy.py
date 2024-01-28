import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

sql_script = '''
    DROP TABLE IF EXISTS presentation.customer_gmvs;
    CREATE TABLE presentation.customer_gmvs AS 
    with cc_gmv AS 
    (SELECT SUM(pi.product_count * pi.product_price) as gmv,
        c.category_name,
        cust.customer_id
    FROM public.purchase_items AS pi
    LEFT JOIN public.purchases AS p
    ON pi.purchase_id = p.purchase_id
    LEFT JOIN public.customers AS cust
    ON cust.customer_id = p.customer_id
    LEFT JOIN public.products AS pr
    ON pr.product_id = pi.product_id
    LEFT JOIN public.categories AS c
    ON pr.category_id = c.category_id
    GROUP BY cust.customer_id, c.category_name),
    para_gmv_c AS
    (SELECT max(gmv) as gmv_max,
        customer_id
    FROM cc_gmv
    group by customer_id),
    cc_table AS 
    (SELECT category_name,
        cc.customer_id
    FROM cc_gmv AS cc
    LEFT JOIN para_gmv_c AS pgc
    ON cc.customer_id = pgc.customer_id AND pgc.gmv_max = cc.gmv)
    
    SELECT 
        NOW() AS created_at, 
        cust.customer_id,
        SUM(pi.product_price * pi.product_count) AS customer_gmv,
        cc.category_name AS customer_category,
        case
            when percent_rank() over gmv_window > 0.95 then '5'
            when percent_rank() over gmv_window > 0.9 then '10'
            when percent_rank() over gmv_window > 0.75 then '25'
            when percent_rank() over gmv_window > 0.5 then '50'
            else '50+'
        end AS customer_group
    FROM public.customers AS cust
    LEFT JOIN public.purchases AS pc 
    ON cust.customer_id = pc.customer_id
    LEFT JOIN purchase_items pi 
    ON pc.purchase_id = pi.purchase_id
    LEFT JOIN cc_table AS cc
    ON cc.customer_id = cust.customer_id
    GROUP BY cust.customer_id, cc.category_name
    window gmv_window as 
      (order by sum(pi.product_price * pi.product_count));
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

with DAG("choco_chaca",
         default_args=DEFAULT_ARGS,
         catchup=False,
         schedule_interval="5 0 * * *",
         max_active_runs=1,
         concurrency=1) as dag:

    task = PostgresOperator(
        task_id="create_customer_gmv",
        postgres_conn_id="dwh_hw",
        sql=sql_script,
    )

    task