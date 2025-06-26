# … /generate endpoint ends here …

@app.get("/")
def ping():
    return {"status": "ok"}
