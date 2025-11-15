#!/usr/bin/env python3
"""
Entry point for running the VC Investor Voice Agent server
"""
import uvicorn
from backend.main import app

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Disable reload in production
    )

