"""Application entry point for the Smart Finance AI API."""

from pathlib import Path

from fastapi import FastAPI, HTTPException  # type: ignore
from fastapi.staticfiles import StaticFiles

if __package__:
    from .routes.finance import router as finance_router
else:
    from routes.finance import router as finance_router

FRONTEND_DIRECTORY = Path(__file__).resolve().parent.parent / "frontend" / "dist"

app = FastAPI(
    title="Smart Finance AI API",
    description="Personal finance calculations and transaction validation.",
    version="0.1.0",
)

app.include_router(finance_router)


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    """Report that the API is available and identify the dashboard."""
    return {"message": "Smart Finance AI API is running.", "dashboard": "/"}


if FRONTEND_DIRECTORY.is_dir():
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIRECTORY), html=True),
        name="frontend",
    )
else:
    @app.get("/", include_in_schema=False)
    def frontend_not_built() -> None:
        """Explain how to build the React dashboard when its bundle is absent."""
        raise HTTPException(
            status_code=503,
            detail="React dashboard is not built. Run 'npm install' and 'npm run build' in frontend/.",
        )
