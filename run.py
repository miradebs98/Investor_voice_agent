#!/usr/bin/env python3
"""
Entry point for running the VC Investor Voice Agent server
"""
import uvicorn
from backend.main import app

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

