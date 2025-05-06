🔁 Real-Time Blockchain Transaction Generator with OpenAI & Azure (Python 3.9)
This folder contains an Azure Function App (using Python 3.9) simulates real-time Bitcoin transactions using OpenAI's GPT-3.5 turbo model and streams them to Azure Event Hub for downstream analytics or processing. It runs on a timer trigger (every minute), generating synthetic blockchain transaction records (e.g., tx_hash, in/out BTC, net flow) and logs structured JSON data. 

💡 Features:
GPT-powered blockchain data generation
Azure Timer Trigger Function (CRON: 0 * * * * *)
Secure environment variable usage (OPEN_AI_API_KEY, EVENT_HUB_CONNECTION_STRING, etc.)
Event Hub integration via azure-eventhub
JSON logging & UTC to EST timestamping
Python 3.9 compatible


🔁 Debug
Includes a local debug script for standalone testing of OpenAI response generation. If you run into trouble with your openai prompts not going through like I did, this is the way to solve that problem.
