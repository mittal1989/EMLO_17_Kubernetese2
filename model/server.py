import os
from transformers import pipeline, set_seed
from fastapi import FastAPI, File
from fastapi.middleware.cors import CORSMiddleware
import redis
import json
import zlib
from typing import Dict

app = FastAPI(title="Model Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# generator = pipeline('text-generation', model='gpt2')
GPT2_MODEL = os.environ.get("GPT2_MODEL", "gpt2")
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")

@app.on_event("startup")
async def initialize():
    # initializes model, categories, redis connection
    global generator
    print(f"loading model {GPT2_MODEL=}...")
    generator = pipeline('text-generation', model=GPT2_MODEL)
    print(f"loaded model {GPT2_MODEL=}")

    global redis_pool
    print(f"creating redis connection with {REDIS_HOST=} {REDIS_PORT=}")
    redis_pool = redis.ConnectionPool(
        host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=0, decode_responses=True
    )

def get_redis():
    # Here, we re-use our connection pool
    # not creating a new one
    return redis.Redis(connection_pool=redis_pool)

def predict(text):
    op = generator(text, max_length=30, num_return_sequences=1)
    print(op)
    return op[0]

async def write_to_cache(text, result: Dict[str, float]) -> None:
    cache = get_redis()

    hash = zlib.adler32(text)
    cache.set(hash, json.dumps(result))

@app.post("/infer")
async def infer(text):
    predictions = predict(text)

    await write_to_cache(str.encode(text), predictions)

    return predictions['generated_text']

# uvicorn server:app --host 0.0.0.0 --port 8000 --reload