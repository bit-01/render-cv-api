import subprocess
import shutil
import os


def render_with_rendercv(yaml_path: str, output_path: str, options: dict = None):
    """Try to render using RenderCV python API; fall back to CLI.

    - yaml_path: path to input YAML file
    - output_path: path to write resulting PDF
    - options: dict of additional options (attempted to be passed to API or converted to CLI flags)

    This function raises an exception if neither API nor CLI is available or if rendering fails.
    """
    options = options or {}

    import_error = None

    # 1) Try Python API
    try:
        import rendercv

        # Common possible API shapes — try a few
        if hasattr(rendercv, "render"):
            # rendercv.render(input_yaml, output_pdf, **options)
            rendercv.render(yaml_path, output_path, **options)
            return

        if hasattr(rendercv, "RenderCV"):
            # rendercv.RenderCV().render(...)
            renderer = rendercv.RenderCV()
            if hasattr(renderer, "render"):
                renderer.render(yaml_path, output_path, **options)
                return

        # If API shape is different we fall through to CLI fallback
    except Exception as e:
        import_error = e

    # 2) Try CLI tool
    cli = shutil.which("rendercv")
    if cli:
        cmd = [cli, "render", yaml_path, "--pdf-path", output_path]
        # Convert options to CLI args: key -> --key value
        for k, v in options.items():
            flag = f"--{k.replace('_','-')}"
            if isinstance(v, bool):
                if v:
                    cmd.append(flag)
            else:
                cmd.extend([flag, str(v)])

        subprocess.run(cmd, check=True)
        if os.path.exists(output_path):
            return
        raise RuntimeError("RenderCV CLI finished but output file was not created")

    # If we reach here, we couldn't find either API or CLI
    raise RuntimeError(
        "RenderCV python package not importable and CLI 'rendercv' not found. "
        f"Import error: {import_error}"
    )
