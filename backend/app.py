import json
import os
import time

from dotenv import load_dotenv
from fastapi import FastAPI

# from langchain.cache import RedisSemanticCache
from langchain.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.embeddings import GigaChatEmbeddings
from pydantic import BaseModel

from kafka import KafkaConsumer, KafkaProducer

app = FastAPI()

load_dotenv()

time.sleep(5)
chat = GigaChat(
    credentials=os.environ.get("GIGACHAT_API_TOKEN"),
    verify_ssl_certs=False,
    scope="GIGACHAT_API_CORP",
    model="GigaChat-Pro",
)


embeddings = GigaChatEmbeddings(
    credentials=os.getenv("GIGACHAT_API_TOKEN"),
    verify_ssl_certs=False,
    scope="GIGACHAT_API_CORP",
    model="Embeddings",
)

# Kafka configuration
kafka_server = "ed-kafka:29092"
incoming_topic = "user-inputs"
outgoing_topic = "assistant-responses"

# Kafka Producer for sending responses
producer = KafkaProducer(
    bootstrap_servers=[kafka_server],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

# Kafka Consumer for receiving chat messages
consumer = KafkaConsumer(
    incoming_topic,
    bootstrap_servers=[kafka_server],
    auto_offset_reset="latest",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

# langchain.llm_cache = RedisSemanticCache(
#     redis_url="redis://redis-storage:6379",
#     embedding=embeddings,
#     score_threshold=0.01,
# )


class ChatMessage(BaseModel):
    content: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
def health():
    return {"status": "ok"}


def process_message(input_text: str):
    print(f"In process_message: {input_text=}")
    messages = [
        SystemMessage(
            content="Суммаризируй основные идеи текста. Не упускай подробности. Сделай акцент на точных фактах."
        ),
        HumanMessage(
            content=f"Дан текст: {input_text}. Сформулируй основные идеи кратко в 2-3 предложения."
        ),
    ]
    return chat(messages)


@app.on_event("startup")
def startup_event():
    for message in consumer:
        print("Received message:", message.value)
        chat_input = message.value["content"]
        print(chat_input)
        response = process_message(chat_input)
        print("Response:", response.content)
        producer.send(outgoing_topic, {"content": response.content})
        producer.flush()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
