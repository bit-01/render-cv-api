from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os
import json
from utils import render_with_rendercv

app = FastAPI(title="RenderCV API")


@app.post("/render")
async def render_endpoint(file: UploadFile = File(...), options: str = Form(None)):
    """Accepts a YAML file upload and optional JSON-formatted options (as a form field).
    Calls RenderCV (python API if available, otherwise CLI) to produce a PDF and returns it.
    """
    # Create a temporary working directory
    tmpdir = tempfile.mkdtemp(prefix="rendercv_")
    try:
        yml_path = os.path.join(tmpdir, file.filename)
        # Save uploaded file
        with open(yml_path, "wb") as f:
            f.write(await file.read())

        # Parse options JSON if provided
        opts = json.loads(options) if options else {}

        output_path = os.path.join(tmpdir, "output.pdf")

        # Call the wrapper which either uses python API or CLI
        try:
            render_with_rendercv(yml_path, output_path, opts)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Render failed: {e}")

        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="RenderCV did not produce an output file")

        # Return file using FileResponse (fast and handles streaming)
        return FileResponse(output_path, media_type="application/pdf", filename="render.pdf")
    finally:
        # We intentionally do not remove tmpdir immediately because FileResponse may still be reading the file.
        # The directory will be left for cleanup by OS or the process lifecycle. If you need aggressive cleanup,
        # implement a background task to remove it after response completes.
        pass
