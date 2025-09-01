from .utils.console_encoding import force_utf8
force_utf8()

from .cli import app

if __name__ == "__main__":
    app()
