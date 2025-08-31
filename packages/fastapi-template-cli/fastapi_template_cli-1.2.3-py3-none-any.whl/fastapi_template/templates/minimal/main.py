"""
Minimal FastAPI application.
This is a barebones FastAPI app with a simple Hello World endpoint.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Minimal FastAPI App",
    description="A simple FastAPI application created with fastapi-template-cli",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Root endpoint returning a Hello World message."""
    return {"message": "Hello World from FastAPI!"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
