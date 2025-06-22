from webhook_app.api import main_router
from webhook_app.core.client import app

app.include_router(main_router, prefix="/api/v1")


# healthcheck (опционально)
@app.get("/")
async def root():
    return {"status": "ok"}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)
