from fastapi import FastAPI
from datetime import datetime
import time

app = FastAPI()

start_time = time.time()

@app.get("/health")
def health() :
    uptime = time.time() - start_time
    return {
        "nama": "Arda",
        "nrp": "5025241074",
        "status": "UP",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": f"{uptime:.2f} seconds"
    }