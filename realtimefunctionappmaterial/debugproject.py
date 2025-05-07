import logging
import json
import os
import datetime
import pytz
import requests
from azure.eventhub import EventHubProducerClient, EventData
import azure.functions as func
import openai
import numpy as np
#app = func.FunctionApp()

# Event Hub connection
#connection_str = os.getenv("EVENT_HUB_CONNECTION_STRING")
#eventhub_name = "team14eventhub"

coef_const = -4.0168
coef_indegree = 0.0896
coef_outdegree = 0.0859
coef_in_btc = 0.0132
coef_out_btc = 0.1708
coef_total_btc = -0.0922

# Set OpenAI API key
#need to make sure no one sees this information
openai.api_key = "bam"
openai.organization = "kerchow"


def predict_using_coefficients(transaction_data):
  # Extracting features from the generated data
  indegree = transaction_data['indegree']
  outdegree = transaction_data['outdegree']
  in_btc = transaction_data['in_btc']
  out_btc = transaction_data['out_btc']
  total_btc = transaction_data['total_btc']
  # Compute log-odds (z)
  z = (coef_const + 
      coef_indegree * indegree + 
      coef_outdegree * outdegree + 
      coef_in_btc * in_btc + 
      coef_out_btc * out_btc + 
      coef_total_btc * total_btc)

  # Apply sigmoid function to get the probability
  probability = 1 / (1 + np.exp(-z))  # Sigmoid function

  # Predict the class (1 for malicious, 0 for non-malicious)
  prediction = 1 if probability >= 0.5 else 0

  if prediction == 1:
      print("Malicious transaction detected")
      return "Malicious"
  else:
      print("Non-malicious")
      return "Non-malicious"

def generate_transaction_data():
    prompt = """
    Generate a realistic blockchain transaction record. Return only valid JSON with fields:

    tx_hash: Hash of the bitcoin transaction.
    indegree: Number of transactions that are inputs of tx_hash
    outdegree: Number of transactions that are outputs of tx_hash.
    in_btc: Total number of bitcoins on each incoming edge to tx_hash.
    out_btc: Total number of bitcoins on each outgoing edge from tx_hash. in _btc >= out_btc
    total_btc: in_btc + out_btc.
    mean_in_btc (type double): in_btc / indegree.
    mean_out_btc (type double): out_btc / outdegree.

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
    prediction = predict_using_coefficients(order_data)
    data = {
            "timestamp": est_time,
            "orders": order_data,
            "prediction": prediction
    }
    print(data)
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)
if __name__ == "__main__":
    main()