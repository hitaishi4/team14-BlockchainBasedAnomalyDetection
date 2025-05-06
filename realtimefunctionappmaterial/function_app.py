import logging
import json
import os
import datetime
import pytz
import requests
from azure.eventhub import EventHubProducerClient, EventData
import azure.functions as func
import openai

app = func.FunctionApp()

# Event Hub connection
connection_str = os.getenv("EVENT_HUB_CONNECTION_STRING")
eventhub_name = "team14eventhub"



# Set OpenAI API key
openai.api_key = os.getenv("OPEN_AI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG_ID")



# Configure logging
logging.basicConfig(level=logging.INFO)


def generate_transaction_data():
    prompt ="""
    Generate a realistic blockchain transaction record. Return only valid JSON with fields:

    tx_hash: Hash of the bitcoin transaction.
    indegree: Number of transactions that are inputs of tx_hash
    outdegree: Number of transactions that are outputs of tx_hash.
    in_btc: Total number of bitcoins on each incoming edge to tx_hash.
    out_btc: Total number of bitcoins on each outgoing edge from tx_hash.
    total_btc: Net number of bitcoins flowing in and out from tx_hash.
    mean_in_btc: Average number of bitcoins flowing in for tx_hash.
    mean_out_btc: Average number of bitcoins flowing out for tx_hash.

    Respond only with a JSON object.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        n=1,
        stop=None,
    )
    message = response.choices[0].message['content']
    try:
        data = json.loads(message)
        logging.info(f"Generated transaction data: {data}")
        return data
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON: {e}")
        return None

# Function to send data to Event Hub
def send_to_eventhub(data):
    try:
        producer = EventHubProducerClient.from_connection_string(conn_str=connection_str, eventhub_name=eventhub_name)
        event_data_batch = producer.create_batch()
        event_data_batch.add(EventData(json.dumps(data)))
        producer.send_batch(event_data_batch)
        producer.close()
        logging.info("Data sent to Event Hub successfully.")
    except Exception as e:
        logging.error(f"Error sending data to Event Hub: {e}")
        raise

@app.timer_trigger(schedule="0 * * * * *", arg_name="mytimer", run_on_startup=True, use_monitor=True)
def main(mytimer: func.TimerRequest) -> None:
    try:
        if mytimer.past_due:
            logging.info('The timer is past due!')

        utc_time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        est_time = utc_time.astimezone(pytz.timezone('America/New_York')).isoformat()
        logging.info(f"Function triggered at: {est_time}")

        order_data = generate_transaction_data()
        if order_data:
            data = {
                "timestamp": est_time,
                "orders": order_data
            }
            logging.info(f"Data to be sent to Event Hub: {data}")
            send_to_eventhub(data)
        else:
            logging.error("Failed to retrieve order data.")

    except Exception as e:
        logging.error(f"Error in function execution: {e}")
