import json

import streamlit as st

from kafka import KafkaConsumer, KafkaProducer

# Kafka configuration
# kafka_server = "localhost:9092"
kafka_server = "ed-kafka:29092"
user_input_topic = "user-inputs"
assistant_response_topic = "assistant-responses"

# Kafka Producer for sending user inputs
producer = KafkaProducer(
    bootstrap_servers=[kafka_server],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

# Kafka Consumer for receiving assistant responses
consumer = KafkaConsumer(
    assistant_response_topic,
    bootstrap_servers=[kafka_server],
    auto_offset_reset="latest",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)


st.title("Chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello there! How can I assist you today?"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Send user input to Kafka
    producer.send(user_input_topic, {"content": prompt})
    producer.flush()

# Check for new responses from assistant
consumer.poll(timeout_ms=1000)  # Non-blocking
for message in consumer:
    response = message.value.get("content", "")
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Always show placeholder for incoming assistant messages
with st.chat_message("assistant"):
    st.markdown("...waiting for response...")
