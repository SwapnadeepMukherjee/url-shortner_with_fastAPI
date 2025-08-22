from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Dict
import hashlib
import base64
import string
import random

app = FastAPI(title="URL Shortener")

# In-memory DB: short_code -> long_url
db: Dict[str, str] = {}

BASE_URL = "http://short.url/"  # Replace with real domain

class URLIn(BaseModel):
    long_url: str

class URLOut(BaseModel):
    short_url: str

@app.get("/", response_class=PlainTextResponse)
def root():
    return "URL Shortener service is running. See /docs for API."

def generate_short_code(long_url: str, length=6) -> str:
    """Generate a unique short code using a hash (for demo, can use random/base62)."""
    # Hash + base64 (collision risk is very low for demo; in prod will need to add check/retry or use DB ID)
    m = hashlib.md5(long_url.encode()).digest()
    b64 = base64.urlsafe_b64encode(m).decode()
    return b64[:length]

@app.post("/shorten", response_model=URLOut)
def create_short_url(payload: URLIn):
    long_url = payload.long_url
    short_code = generate_short_code(long_url)
    # Uniqueness check; if collision, refine code:
    while short_code in db and db[short_code] != long_url:
        # If collision, use a random base62 string
        short_code = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    db[short_code] = long_url
    return URLOut(short_url=BASE_URL + short_code)

@app.get("/{short_code}")
def resolve_short_url(short_code: str):
    if short_code not in db:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return {"long_url": db[short_code]}
    # Or, to redirect:
    # from fastapi.responses import RedirectResponse
    # return RedirectResponse(url=db[short_code])