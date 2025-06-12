
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes.users import router as users_router
from modules.database import Database
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI(title="AuthX API", version="1.0.0")

@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    if request.url.path == "/":
        response = await call_next(request)
        return response
    
    api_key = request.headers.get("x-api-key")
    if api_key != "adminkey":
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    response = await call_next(request)
    return response

@app.on_event("startup")
async def startup_event():
    await Database.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await Database.close()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)

@app.get("/")
async def root():
    return {"message": "AuthX API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
