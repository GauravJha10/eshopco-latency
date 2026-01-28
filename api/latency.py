from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATA_PATH = Path(__file__).parent / "telemetry.json"

class Payload(BaseModel):
    regions: List[str]
    threshold_ms: float

@app.post("/api/latency")
async def latency_metrics(payload: Payload):
    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    result = {}

    for region in payload.regions:
        records = [r for r in data if r["region"] == region]

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        result[region] = {
            "avg_latency": round(statistics.mean(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(statistics.mean(uptimes), 2),
            "breaches": sum(1 for l in latencies if l > payload.threshold_ms)
        }

    return result
