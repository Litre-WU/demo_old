import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=52, log_level="info", limit_concurrency=10000, limit_max_requests=10000,
                access_log=False)
