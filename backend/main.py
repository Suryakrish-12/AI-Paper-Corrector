from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.config import settings
from app.api import auth, users, evaluation, analytics, reports
from app.websocket import manager

# Create database tables automatically on launch
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartEval AI API",
    description="Intelligent Examination Paper Evaluation and Learning Analytics System Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for standard browser calls (Frontend Next.js client)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST endpoints
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(evaluation.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(reports.router, prefix="/api")

@app.get("/")
def root_status():
    return {
        "status": "online",
        "system": "SmartEval AI Engine",
        "environment": settings.ENVIRONMENT,
        "database": "sqlite" if settings.USE_SQLITE else "postgresql",
        "mock_ai": settings.USE_MOCK_AI
    }

@app.websocket("/ws/evaluations")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint to establish push streams for live grading progress.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Wait for client keep-alive pings
            data = await websocket.receive_text()
            await websocket.send_text(f"ack: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
