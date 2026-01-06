from flask import Flask, request, send_file, abort
import tempfile
import os
import json
from utils import render_with_rendercv

app = Flask(__name__)


@app.route("/render", methods=["POST"])
def render_endpoint():
    """Accepts a YAML file upload (form field `file`) and optional JSON-formatted options
    (form field `options`). Calls RenderCV (python API if available, otherwise CLI) to produce
    a PDF and returns it as a response.
    """
    # Ensure file part is present
    if "file" not in request.files:
        abort(400, description="Missing 'file' form field")

    upload = request.files["file"]
    if upload.filename == "":
        abort(400, description="Empty filename in upload")

    # Create a temporary working directory
    tmpdir = tempfile.mkdtemp(prefix="rendercv_")
    try:
        yml_path = os.path.join(tmpdir, upload.filename)
        # Save uploaded file
        upload.save(yml_path)

        # Parse options JSON if provided
        options = request.form.get("options")
        opts = json.loads(options) if options else {}

        output_path = os.path.join(tmpdir, "output.pdf")

        # Call the wrapper which either uses python API or CLI
        try:
            render_with_rendercv(yml_path, output_path, opts)
        except Exception as e:
            abort(500, description=f"Render failed: {e}")

        if not os.path.exists(output_path):
            abort(500, description="RenderCV did not produce an output file")

        # Return file using Flask's send_file. We serve as an attachment named render.pdf.
        return send_file(output_path, mimetype="application/pdf", as_attachment=True, download_name="render.pdf")
    finally:
        # NOTE: we do not remove tmpdir here because WSGI servers may still be reading the file.
        # If you need aggressive cleanup, run a background thread or external cleaner.
        pass
