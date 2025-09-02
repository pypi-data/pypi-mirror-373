import os, argparse
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=6006)
    parser.add_argument("--host", action='store_true')
    args = parser.parse_args()

    app = FastAPI()
    dist_dir = os.path.join(os.path.dirname(__file__), "js/dist")
    app.mount("/static", StaticFiles(directory=os.path.join(dist_dir, "assets")), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(dist_dir, "index.html"))

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(dist_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_dir, "index.html"))

    params = {'port': args.port}
    if args.host: params['host'] = '0.0.0.0'

    uvicorn.run(app, **params)

if __name__ == '__main__':
    main()
