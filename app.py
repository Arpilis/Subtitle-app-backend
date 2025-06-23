@app.get("/")
def ping():
    return {"status": "ok"}
