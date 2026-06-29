"""Run the backend with `python -m backend`.

Honors HOST/PORT environment variables (most hosts inject $PORT), defaulting to
0.0.0.0:8000 for local use. Equivalent to:
    uvicorn backend.app:app --host $HOST --port $PORT
"""
import os

import uvicorn


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("backend.app:app", host=host, port=port)


if __name__ == "__main__":
    main()