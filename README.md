# RenderCV API wrapper

This small project provides a REST API wrapper around the RenderCV tool. It accepts a YAML file (upload) plus optional JSON options and returns the generated PDF.

Endpoints
- POST /render — form upload: field `file` (YAML), optional form field `options` (JSON string). Returns application/pdf.

Quick start

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Install RenderCV (the actual renderer). This project expects either:

- a Python package named `rendercv` that exposes a `render` function or `RenderCV` class
- OR a CLI command `rendercv` available on PATH

Install RenderCV as appropriate for your environment. This README cannot install it for you.

3. Run the API server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 9000
```

4. Example request (curl):

```bash
curl -X POST \
  -F "file=@cv.yml;type=text/yaml" \
  -F "options={\"template\":\"modern\"}" \
  http://localhost:8000/render --output out.pdf
```

Notes
- The wrapper first attempts to import a `rendercv` python module and call `render` or `RenderCV().render()`.
- If that fails it looks for a `rendercv` CLI binary and invokes it with `--input` and `--output` plus converted flags for options.
- The temporary files are stored in a temp directory; FileResponse is used to stream the PDF back.

If you want me to wire this to a specific version of RenderCV (showing how to call its API), provide the RenderCV import/API docs or paste the package's API surface and I will adapt the wrapper to call it directly.
