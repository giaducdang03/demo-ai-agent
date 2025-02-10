import time
import asyncio
from fastapi import FastAPI, Request #type: ignore
from fastapi.middleware.cors import CORSMiddleware #type: ignore
from api.routes import router
from starlette.middleware.base import BaseHTTPMiddleware #type: ignore

app = FastAPI()

class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await asyncio.wait_for(call_next(request), timeout=10.0)
        except asyncio.TimeoutError:
            return {"error": "Request timeout"}

class TimerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

# Add middleware
app.add_middleware(TimeoutMiddleware)
app.add_middleware(TimerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Chatbot Microservice"}

app.include_router(router, prefix="/api/v1")