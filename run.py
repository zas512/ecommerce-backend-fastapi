import sys
import uvicorn

if __name__ == "__main__":
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=4000,
            reload=True,
            log_level="debug",
        )
    except KeyboardInterrupt:
        sys.exit(0)
