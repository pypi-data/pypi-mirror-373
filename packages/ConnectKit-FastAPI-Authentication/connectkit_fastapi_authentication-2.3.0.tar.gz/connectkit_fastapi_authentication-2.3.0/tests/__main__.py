import uvicorn
from fastapi import FastAPI, Request
import os

from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.hybrid import  hybrid_method
from sqlalchemy.orm import mapped_column, Mapped

os.environ["DB_ADAPTER"] = "sqlite"
os.environ["DB_NAME"] = ":memory:"

from authentication import setup_app
from database import async_init_default_base, Base


async def startup():
    await async_init_default_base(Base.metadata)


app = FastAPI(on_startup=[startup])
setup_app(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


