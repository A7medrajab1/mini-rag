from fastapi import FastAPI
app = FastAPI(
    title="Mini RAG API",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/welcome")
def welcome_message():
    return {"message": "Welcome to the FastAPI application!"}

