from app.auth import router as auth_router
from app.feedback import router as feedback_router
from app.model import router as model_router
from app.user import router as user_router
from fastapi import FastAPI
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(title="Image Prediction API", version="0.0.1")

# add hello world 

@app.get("/")
async def hello_world():

    logger.info("Starting FastAPI application...")
    return {"message": "Hello World from FastAPI!"}


app.include_router(auth_router.router)
app.include_router(model_router.router)
app.include_router(user_router.router)
app.include_router(feedback_router.router)
