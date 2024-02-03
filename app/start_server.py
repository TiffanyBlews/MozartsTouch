import uvicorn

uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=False)