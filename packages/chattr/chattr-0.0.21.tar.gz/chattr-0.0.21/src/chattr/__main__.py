from gradio import Blocks

from chattr.gui import app_block


def main() -> None:
    """Initializes and launches the Gradio-based Chattr application server with API access, monitoring, and PWA support enabled."""
    app: Blocks = app_block()
    app.queue(api_open=True).launch(
        server_port=7860,
        debug=True,
        show_api=True,
        enable_monitoring=True,
        show_error=True,
        pwa=True,
    )


if __name__ == "__main__":
    main()
