import sys
sys.path.insert(0, r'c:\Anu\APT\apt\army\fortwilliam\code\fwDemo\backend')

# Import with fresh module cache
import importlib
if 'routers.analysis_router' in sys.modules:
    del sys.modules['routers.analysis_router']

from database import SessionLocal
from routers.analysis_router import analyze_a_vehicles
import asyncio

async def test():
    db = SessionLocal()
    try:
        result = await analyze_a_vehicles(db)
        print("Section 4 title:", result["section4"]["title"])
        print("Section 5 title:", result["section5"]["title"])
    finally:
        db.close()

asyncio.run(test())
