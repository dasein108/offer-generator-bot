from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


# def start_rest_server():
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# import uvicorn
# uvicorn.run(app, host="0.0.0.0", port=8888)