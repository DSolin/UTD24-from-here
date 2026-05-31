
import uuid
from datetime import date, datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, text, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.article import Article
from app.models.author import Author
from app.models.journal import Journal
from app.models.keyword import Keyword
from app.models.user import Favorite

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get("")
async def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    query: str | None = None,
    journal_id: str | None = None,
    keyword: str | None = None,
    author: str | None = None,
    country: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = "published_date",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
):

    
    # 基础查询
    stmt = select(Article).options(
        selectinload(Article.journal),
        selectinload(Article.authors),
        selectinload(Article.keywords),
    )
    
    # 全文搜索
    if query:
        search_term = f"%{query}%"
        stmt = stmt.where(
            or_(
                Article.title.ilike(search_term),
                Article.abstract.ilike(search_term),
            )
        )
    
    # 期刊筛选
    if journal_id:
        try:
            jid = uuid.UUID(journal_id)
            stmt = stmt.where(Article.journal_id == jid)
        except ValueError:
            pass
    
    # 关键词筛选
    if keyword:
        stmt = stmt.join(Article.keywords).where(
            Keyword.normalized_keyword.ilike(f"%{keyword.lower()}%")
        )

    # 作者筛选
    if author:
        stmt = stmt.join(Article.authors).where(
            Author.name.ilike(f"%{author}%")
        )
    
    # 国家筛选
    if country:
        stmt = stmt.join(Article.authors).where(
            Author.country.ilike(f"%{country}%")
        )
    
    # 日期范围
    if date_from:
        stmt = stmt.where(Article.published_date >= date.fromisoformat(date_from))
    if date_to:
        stmt = stmt.where(Article.published_date <= date.fromisoformat(date_to))
    
    # 排序
    sort_col = getattr(Article, sort_by, Article.published_date)
    if sort_order == "desc":
        stmt = stmt.order_by(sort_col.desc())
    else:
        stmt = stmt.order_by(sort_col.asc())
    
    # 总数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (db.execute(count_stmt)).scalar() or 0
    
    # 分页
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    result = db.execute(stmt)
    articles = result.unique().scalars().all()
    
    # 格式化
    items = []
    for a in articles:
        items.append({
            "id": str(a.id),
            "title": a.title,
            "abstract": a.abstract[:300] + "..." if a.abstract and len(a.abstract) > 300 else a.abstract,
            "doi": a.doi,
            "published_date": str(a.published_date) if a.published_date else None,
            "volume": a.volume,
            "issue": a.issue,
            "pages": a.pages,
            "journal": {
                "id": str(a.journal.id) if a.journal else None,
                "name": a.journal.name if a.journal else None,
                "abbreviation": a.journal.abbreviation if a.journal else None,
            },
            "authors": [
                {"id": str(au.id), "name": au.name, "country": au.country}
                for au in a.authors[:10]
            ],
            "keywords": [
                {"id": str(k.id), "keyword": k.keyword}
                for k in a.keywords[:10]
            ],
            "source_url": a.source_url,
        })
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


@router.get("/{article_id}")
async def get_article(article_id: str, db: AsyncSession = Depends(get_db)):
    """文章详情"""
    try:
        aid = uuid.UUID(article_id)
    except ValueError:
        raise HTTPException(400, "Invalid article ID")
    
    stmt = select(Article).options(
        selectinload(Article.journal),
        selectinload(Article.authors),
        selectinload(Article.keywords),
    ).where(Article.id == aid)
    
    result = db.execute(stmt)
    a = result.unique().scalar_one_or_none()
    
    if not a:
        raise HTTPException(404, "Article not found")
    
    return {
        "id": str(a.id),
        "title": a.title,
        "abstract": a.abstract,
        "doi": a.doi,
        "published_date": str(a.published_date) if a.published_date else None,
        "published_online_date": str(a.published_online_date) if a.published_online_date else None,
        "volume": a.volume,
        "issue": a.issue,
        "pages": a.pages,
        "article_type": a.article_type,
        "pdf_url": a.pdf_url,
        "source_url": a.source_url,
        "citation_count": a.citation_count or 0,
        "journal": {
            "id": str(a.journal.id) if a.journal else None,
            "name": a.journal.name if a.journal else None,
            "abbreviation": a.journal.abbreviation if a.journal else None,
            "publisher": a.journal.publisher if a.journal else None,
            "issn": a.journal.issn if a.journal else None,
        },
        "authors": [
            {
                "id": str(au.id),
                "name": au.name,
                "affiliation": au.affiliation,
                "country": au.country,
            }
            for au in a.authors
        ],
        "keywords": [
            {"id": str(k.id), "keyword": k.keyword}
            for k in a.keywords
        ],
    }


@router.get("/export/csv")
async def export_csv(
    query: str | None = None,
    journal_id: str | None = None,
    author: str | None = None,
    country: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """导出 CSV"""
    from fastapi.responses import StreamingResponse
    import csv, io
    
    stmt = select(Article).options(
        selectinload(Article.journal),
        selectinload(Article.authors),
        selectinload(Article.keywords),
    )
    if query:
        stmt = stmt.where(Article.title.ilike(f"%{query}%"))
    if journal_id:
        try:
            stmt = stmt.where(Article.journal_id == uuid.UUID(journal_id))
        except ValueError: pass
    if author:
        stmt = stmt.join(Article.authors).where(Author.name.ilike(f"%{author}%"))
    if country:
        stmt = stmt.join(Article.authors).where(Author.country.ilike(f"%{country}%"))
    if date_from:
        stmt = stmt.where(Article.published_date >= date.fromisoformat(date_from))
    if date_to:
        stmt = stmt.where(Article.published_date <= date.fromisoformat(date_to))
    stmt = stmt.order_by(Article.published_date.desc()).limit(2000)
    
    result = db.execute(stmt)
    rows = result.unique().scalars().all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Title", "Authors", "Journal", "DOI", "Published", "Keywords", "Abstract"])
    for a in rows:
        writer.writerow([
            a.title[:200] if a.title else "",
            "; ".join(au.name for au in (a.authors or [])[:10]),
            a.journal.name if a.journal else "",
            a.doi or "",
            str(a.published_date) if a.published_date else "",
            "; ".join(k.keyword for k in (a.keywords or [])[:10]),
            (a.abstract or "")[:500],
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=utd24_articles.csv"}
    )
