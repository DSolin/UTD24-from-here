"""FastAPI 入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import get_settings
from app.database import engine, SessionLocal, Base

settings = get_settings()

from app.models.user import User, Favorite
from app.models.journal import Journal
from app.models.article import Article, article_keywords
from app.models.author import Author, article_authors
from app.models.keyword import Keyword
from app.models.dashboard import UserDashboardLayout, CrawlLog

def init_db():
    import uuid as _uuid
    from sqlalchemy import select

    Base.metadata.create_all(bind=engine)

    jids = [
        "a0000001-0000-4000-a000-000000000001","a0000002-0000-4000-a000-000000000002",
        "a0000003-0000-4000-a000-000000000003","a0000004-0000-4000-a000-000000000004",
        "a0000005-0000-4000-a000-000000000005","a0000006-0000-4000-a000-000000000006",
        "a0000007-0000-4000-a000-000000000007","a0000008-0000-4000-a000-000000000008",
        "a0000009-0000-4000-a000-000000000009","a000000a-0000-4000-a000-00000000000a",
        "a000000b-0000-4000-a000-00000000000b","a000000c-0000-4000-a000-00000000000c",
        "a000000d-0000-4000-a000-00000000000d","a000000e-0000-4000-a000-00000000000e",
        "a000000f-0000-4000-a000-00000000000f","a0000010-0000-4000-a000-000000000010",
        "a0000011-0000-4000-a000-000000000011","a0000012-0000-4000-a000-000000000012",
        "a0000013-0000-4000-a000-000000000013","a0000014-0000-4000-a000-000000000014",
        "a0000015-0000-4000-a000-000000000015","a0000016-0000-4000-a000-000000000016",
        "a0000017-0000-4000-a000-000000000017","a0000018-0000-4000-a000-000000000018",
    ]

    journals = [
        ("The Accounting Review","AR","AAA","0001-4826","aaahq"),
        ("Journal of Accounting and Economics","JAE","Elsevier","0165-4101","elsevier"),
        ("Journal of Accounting Research","JAR","Wiley","0021-8456","wiley"),
        ("Journal of Finance","JF","Wiley","0022-1082","wiley"),
        ("Journal of Financial Economics","JFE","Elsevier","0304-405X","elsevier"),
        ("The Review of Financial Studies","RFS","Oxford","0893-9454","oxford"),
        ("Information Systems Research","ISR","INFORMS","1047-7047","informs"),
        ("INFORMS Journal on Computing","JOC","INFORMS","1091-9856","informs"),
        ("MIS Quarterly","MISQ","U of Minnesota","0276-7783","misq"),
        ("Journal of Consumer Research","JCR","Oxford","0093-5301","oxford"),
        ("Journal of Marketing","JM","AMA/SAGE","0022-2429","sage"),
        ("Journal of Marketing Research","JMR","AMA/SAGE","0022-2437","sage"),
        ("Marketing Science","MKS","INFORMS","0732-2399","informs"),
        ("Management Science","MS","INFORMS","0025-1909","informs"),
        ("Operations Research","OR","INFORMS","0030-364X","informs"),
        ("Journal of Operations Management","JOM","Wiley","0272-6963","wiley"),
        ("M&SOM","M&SOM","INFORMS","1523-4614","informs"),
        ("Production and Operations Management","POM","SAGE","1059-1478","sage"),
        ("Academy of Management Journal","AMJ","AOM","0001-4273","aom"),
        ("Academy of Management Review","AMR","AOM","0363-7425","aom"),
        ("Administrative Science Quarterly","ASQ","SAGE","0001-8392","sage"),
        ("Organization Science","OS","INFORMS","1047-7039","informs"),
        ("JIBS","JIBS","Springer","0047-2506","springer"),
        ("Strategic Management Journal","SMJ","Wiley","0143-2095","wiley"),
    ]

    db = SessionLocal()
    try:
        for i, (name, abbr, pub, issn, plat) in enumerate(journals):
            result = db.execute(select(Journal).where(Journal.issn == issn)).scalar_one_or_none()
            if result:
                result.name = name
                result.abbreviation = abbr
                result.publisher = pub
                result.platform = plat
            else:
                db.add(Journal(
                    id=_uuid.UUID(jids[i]),
                    name=name, abbreviation=abbr, publisher=pub,
                    issn=issn, platform=plat, utd24_index=i+1,
                ))
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME, version=settings.APP_VERSION,
    description="UTD from here",
    docs_url="/docs", redoc_url="/redoc", lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

from app.api.health import router as health_router
app.include_router(health_router, prefix="/api/v1")
from app.api.articles import router as articles_router
from app.api.bi import router as bi_router
from app.api.auth import router as auth_router
from app.api.favorites import router as favorites_router
from app.api.crawler import router as crawler_router

app.include_router(articles_router, prefix="/api/v1")
app.include_router(bi_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(favorites_router, prefix="/api/v1")
app.include_router(crawler_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    import os as _os3
    index_path = _os3.path.join(_os3.path.dirname(__file__), "..", "static", "index.html")
    if _os3.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": f"Welcome to {settings.APP_NAME}", "version": settings.APP_VERSION}


import os as _os
_static_dir = _os.path.join(_os.path.dirname(__file__), "..", "static")
if _os.path.exists(_os.path.join(_static_dir, "index.html")):
    app.mount("/assets", StaticFiles(directory=_os.path.join(_static_dir, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        index_path = _os.path.join(_os.path.dirname(__file__), "..", "static", "index.html")
        if _os.path.exists(index_path):
            return FileResponse(index_path)
        return {"detail": "Frontend not built"}
