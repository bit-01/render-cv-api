import tempfile
import os

from fastapi.testclient import TestClient

import main
import utils


def test_render_endpoint(monkeypatch):
    # Monkeypatch the render function to produce a fake PDF file
    def fake_render(yaml_path, output_path, options=None):
        with open(output_path, "wb") as f:
            f.write(b"%PDF-1.4\n%fake pdf\n")

    monkeypatch.setattr(utils, "render_with_rendercv", fake_render)

    client = TestClient(main.app)

    tmp = tempfile.NamedTemporaryFile(suffix=".yml", delete=False)
    try:
        tmp.write(b"name: test\n")
        tmp.close()
        with open(tmp.name, "rb") as f:
            response = client.post("/render", files={"file": ("test.yml", f, "text/yaml")})

        assert response.status_code == 200
        assert response.headers.get("content-type", "").startswith("application/pdf")
        assert response.content.startswith(b"%PDF-1.4")
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
