import tempfile
import os

import main
import utils


def test_render_endpoint(monkeypatch):
    # Monkeypatch the render function to produce a fake PDF file
    def fake_render(yaml_path, output_path, options=None):
        with open(output_path, "wb") as f:
            f.write(b"%PDF-1.4\n%fake pdf\n")

    monkeypatch.setattr(utils, "render_with_rendercv", fake_render)

    client = main.app.test_client()

    tmp = tempfile.NamedTemporaryFile(suffix=".yml", delete=False)
    try:
        tmp.write(b"name: test\n")
        tmp.close()
        with open(tmp.name, "rb") as f:
            data = {
                "file": (f, "test.yml"),
            }
            response = client.post("/render", data=data, content_type="multipart/form-data")

        assert response.status_code == 200
        assert response.headers.get("Content-Type", "").startswith("application/pdf")
        assert response.data.startswith(b"%PDF-1.4")
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
