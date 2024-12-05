import functions_framework
import time
import logging
from flask import jsonify
from google.cloud import bigquery
from google.auth import default

# Set function variables
PROJECT_ID = "primal-monument-358918"
DATASET_NAME = "BQML"
TABLE_REVIEWS_WITH_SENTIMENT = "Reviews - Wyniki"

# Use Application Default Credentials (ADC)
credentials, project = default(
    scopes=[
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/bigquery",
    ])
CLIENT_BQ = bigquery.Client(credentials=credentials, project=PROJECT_ID)

# Configure logging
logging.basicConfig(level=logging.INFO)

def run_query():
    """
    Executes a BigQuery SQL query to analyze sentiment from product reviews
    and stores the results in a specified BigQuery table.

    Returns:
        tuple: A tuple containing:
            - row_count (int or None): The number of rows processed if successful, else None.
            - error_msg (str or None): Error message if an error occurred, else None.
    """
    query = """
    WITH setiment AS (
    SELECT
      REGEXP_REPLACE(
        JSON_EXTRACT_SCALAR(ml_generate_text_result['candidates'][0]['content']['parts'][0], '$.text'), 
        '"', 
        ''
      ) AS Sentiment,
      * 
    FROM
      ML.GENERATE_TEXT(
        MODEL `BQML.llm_model2`,
        (
          SELECT
            CONCAT('Create a one word sentiment from product_review column. Possible values are positive/negative/neutral ', Product_Review) AS prompt,
            *
          FROM
            `primal-monument-358918.BQML.reviews`
          LIMIT 50 OFFSET 0
        ),
        STRUCT(
          1 AS temperature,
          1 AS max_output_tokens,
          0.2 AS top_p, 
          1 AS top_k))
    ),
    reason AS (
    SELECT
      REGEXP_REPLACE(
        JSON_EXTRACT_SCALAR(ml_generate_text_result['candidates'][0]['content']['parts'][0], '$.text'), 
        '"', 
        ''
      ) AS Reason,
      Product_ID,
      Customer_ID, 
    FROM
      ML.GENERATE_TEXT(
        MODEL `BQML.llm_model2`,
        (
          SELECT
            CONCAT('Create a one word reason from product_review column. Possible values are Quality/Price/Shipping.', Product_Review) AS prompt,
            *
          FROM
            `primal-monument-358918.BQML.reviews`
          LIMIT 50 OFFSET 0
        ),
        STRUCT(
          1 AS temperature,
          1 AS max_output_tokens,
          0.2 AS top_p, 
          1 AS top_k))
    )
    SELECT
      s.Customer_ID,
      s.Product_Category,
      s.Product_ID,
      s.Product_Name,
      s.Price,
      s.Product_Review,
      s.Sentiment,
      r.Reason AS Reason,
      CASE
        WHEN s.Sentiment = "Positive" THEN 1
        WHEN s.Sentiment = "Neutral" THEN 0.5
        WHEN s.Sentiment = "Negative" THEN 0
      END AS Points
    FROM
      setiment AS s
    LEFT JOIN reason AS r
    ON s.Customer_ID = r.Customer_ID AND
    s.Product_ID = r.Product_ID
    """

    job_config = bigquery.QueryJobConfig(
        destination=f"{PROJECT_ID}.{DATASET_NAME}.{TABLE_REVIEWS_WITH_SENTIMENT}",
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    try:
        query_job = CLIENT_BQ.query(query, job_config=job_config)
        result = query_job.result()
        row_count = result.total_rows
        return row_count, None
    except Exception as e:
        logging.error(f"Query failed: {str(e)}")
        return None, str(e)

@functions_framework.http
def hello_http(request):
    """
    HTTP Cloud Function to execute a BigQuery query for sentiment analysis
    and return the execution status and metrics.

    Args:
        request (flask.Request): The HTTP request object.

    Returns:
        flask.Response: JSON response with execution status, error message (if any), and elapsed time.
    """
    start_time = time.time()
    row_count, error_msg = run_query()
    end_time = time.time()
    elapsed_time = end_time - start_time

    if error_msg:
        response_data = {
            "Status": 'Error occurred',
            "Error message": error_msg,
            "Elapsed time": f"{elapsed_time:.2f} seconds",
        }
    else:
        response_data = {
            "Status": 'Successfully',
            "Elapsed time": f"{elapsed_time:.2f} seconds",
            "Executed for number of records": row_count
        }

    return jsonify(response_data), 200
