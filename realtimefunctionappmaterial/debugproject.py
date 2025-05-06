import logging
import json
import os
import datetime
import pytz
import requests
from azure.eventhub import EventHubProducerClient, EventData
import azure.functions as func
import openai

#app = func.FunctionApp()

# Event Hub connection
#connection_str = os.getenv("EVENT_HUB_CONNECTION_STRING")
#eventhub_name = "team14eventhub"



# Set OpenAI API key
#need to make sure no one sees this information
openai.api_key = "insert_api_key"
openai.organization = "insert_org_id"




def generate_transaction_data():
    prompt = """
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
    return json.loads(message)

#@app.timer_trigger(schedule="0 * * * * *", arg_name="mytimer", run_on_startup=True, use_monitor=True)
def main():
    utc_time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    est_time = utc_time.astimezone(pytz.timezone('America/New_York')).isoformat()

    order_data = generate_transaction_data()
    data = {
            "timestamp": est_time,
            "orders": order_data
    }
    print(data)
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)
if __name__ == "__main__":
    main()