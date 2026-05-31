import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, text, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.article import Article, article_keywords
from app.models.author import Author, article_authors
from app.models.journal import Journal
from app.models.keyword import Keyword

router = APIRouter(prefix="/bi", tags=["BI Analytics"])


def _build_filters(country=None, keyword=None, author_id=None, date_from=None, date_to=None):
    """构建通用过滤条件"""
    filters = []
    if date_from:
        filters.append(Article.published_date >= date.fromisoformat(date_from))
    if date_to:
        filters.append(Article.published_date <= date.fromisoformat(date_to))
    return filters


def _apply_drilldown(stmt, country=None, keyword=None, author_id=None):
    """应用下钻过滤到查询"""
    if country:
        stmt = stmt.join(Article.authors).where(Author.country == country)
    if keyword:
        stmt = stmt.join(Article.keywords).where(Keyword.normalized_keyword == keyword.lower().strip())
    if author_id:
        try:
            aid = uuid.UUID(author_id)
            stmt = stmt.join(Article.authors).where(Author.id == aid)
        except ValueError:
            pass
    return stmt


@router.get("/summary")
async def summary(
    country: str | None = None,
    keyword: str | None = None,
    author_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """仪表板总览"""
    try:
        # 文章总数
        stmt_art = select(func.count(func.distinct(Article.id)))
        if country:
            stmt_art = stmt_art.join(article_authors, Article.id == article_authors.c.article_id)
            stmt_art = stmt_art.join(Author, article_authors.c.author_id == Author.id)
            stmt_art = stmt_art.where(Author.country == country)
        if keyword:
            stmt_art = stmt_art.join(article_keywords, Article.id == article_keywords.c.article_id)
            stmt_art = stmt_art.join(Keyword, article_keywords.c.keyword_id == Keyword.id)
            stmt_art = stmt_art.where(Keyword.normalized_keyword == keyword.lower().strip())
        if author_id:
            try:
                aid = uuid.UUID(author_id)
                stmt_art = stmt_art.join(article_authors, Article.id == article_authors.c.article_id)
                stmt_art = stmt_art.where(article_authors.c.author_id == aid)
            except ValueError:
                pass
        if date_from:
            stmt_art = stmt_art.where(Article.published_date >= date.fromisoformat(date_from))
        if date_to:
            stmt_art = stmt_art.where(Article.published_date <= date.fromisoformat(date_to))
        
        r = db.execute(stmt_art)
        total_articles = r.scalar() or 0

        # 作者总数
        stmt_aut = select(func.count(func.distinct(Author.id)))
        if country:
            stmt_aut = stmt_aut.where(Author.country == country)
        if keyword or author_id:
            stmt_aut = stmt_aut.join(article_authors, Author.id == article_authors.c.author_id)
            stmt_aut = stmt_aut.join(Article, article_authors.c.article_id == Article.id)
            if keyword:
                stmt_aut = stmt_aut.join(article_keywords, Article.id == article_keywords.c.article_id)
                stmt_aut = stmt_aut.join(Keyword, article_keywords.c.keyword_id == Keyword.id)
                stmt_aut = stmt_aut.where(Keyword.normalized_keyword == keyword.lower().strip())
            if author_id:
                try:
                    stmt_aut = stmt_aut.where(article_authors.c.author_id == uuid.UUID(author_id))
                except: pass
        r = db.execute(stmt_aut)
        total_authors = r.scalar() or 0

        # 国家数
        stmt_cty = select(func.count(func.distinct(Author.country))).where(Author.country.isnot(None))
        r = db.execute(stmt_cty)
        total_countries = r.scalar() or 0

        # 期刊数
        r = db.execute(select(func.count(Journal.id)))
        total_journals = r.scalar() or 0

        # 最近更新
        r = db.execute(select(func.max(Article.crawled_at)))
        last_updated = r.scalar()
    except Exception as e:
        # fallback: 无过滤版本
        r = db.execute(select(func.count(Article.id)))
        total_articles = r.scalar() or 0
        r = db.execute(select(func.count(Author.id)))
        total_authors = r.scalar() or 0
        r = db.execute(select(func.count(func.distinct(Author.country))).where(Author.country.isnot(None)))
        total_countries = r.scalar() or 0
        r = db.execute(select(func.count(Journal.id)))
        total_journals = r.scalar() or 0
        r = db.execute(select(func.max(Article.crawled_at)))
        last_updated = r.scalar()

    return {
        "total_articles": total_articles,
        "total_authors": total_authors,
        "total_countries": total_countries,
        "total_journals": total_journals,
        "last_updated": str(last_updated) if last_updated else None,
    }

@router.get("/wordcloud")
async def wordcloud(
    limit: int = Query(80, ge=10, le=200),
    days: int = Query(9999, ge=1, le=9999),
    country: str | None = None,
    keyword: str | None = None,
    author_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Keyword.keyword, func.count(func.distinct(Article.id)).label("cnt"))
        .select_from(Keyword)
        .join(article_keywords, Keyword.id == article_keywords.c.keyword_id)
        .join(Article, Article.id == article_keywords.c.article_id)
    )

    if country:
        stmt = stmt.join(article_authors, Article.id == article_authors.c.article_id).join(Author, article_authors.c.author_id == Author.id).where(Author.country == country)
    if keyword:
        stmt = stmt.where(Keyword.normalized_keyword == keyword.lower().strip())
    if author_id:
        try:
            stmt = stmt.join(article_authors, Article.id == article_authors.c.article_id).join(Author, article_authors.c.author_id == Author.id).where(Author.id == uuid.UUID(author_id))
        except: pass
    if date_from:
        stmt = stmt.where(Article.published_date >= date.fromisoformat(date_from))
    if date_to:
        stmt = stmt.where(Article.published_date <= date.fromisoformat(date_to))

    stmt = stmt.group_by(Keyword.keyword).order_by(text("cnt DESC")).limit(limit)
    result = db.execute(stmt)
    return [{"name": row[0], "value": row[1]} for row in result.all() if row[1] > 0]


@router.get("/countries")
async def country_distribution(
    keyword: str | None = None,
    author_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Author.country, func.count(func.distinct(Article.id)).label("cnt"))
        .select_from(Author)
        .join(article_authors, Author.id == article_authors.c.author_id)
        .join(Article, Article.id == article_authors.c.article_id)
        .where(Author.country.isnot(None))
    )
    if keyword:
        stmt = stmt.join(article_keywords, Article.id == article_keywords.c.article_id).join(Keyword, article_keywords.c.keyword_id == Keyword.id).where(Keyword.normalized_keyword == keyword.lower().strip())
    if author_id:
        try:
            stmt = stmt.where(Author.id == uuid.UUID(author_id))
        except: pass
    if date_from:
        stmt = stmt.where(Article.published_date >= date.fromisoformat(date_from))
    if date_to:
        stmt = stmt.where(Article.published_date <= date.fromisoformat(date_to))
    stmt = stmt.group_by(Author.country).order_by(text("cnt DESC"))
    result = db.execute(stmt)
    return [{"country": row[0], "count": row[1]} for row in result.all()]


@router.get("/trends")
async def publication_trends(
    months: int = Query(12, ge=1, le=120),
    country: str | None = None,
    keyword: str | None = None,
    author_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(
        func.to_char(Article.published_date, "YYYY-MM").label("month"),
        func.count(Article.id).label("cnt"),
    )
    # date_from/date_to 优先；没传时回退 months
    if date_from:
        stmt = stmt.where(Article.published_date >= date.fromisoformat(date_from))
    elif months:
        stmt = stmt.where(Article.published_date >= func.current_date() - text(f"interval '{months} months'"))
    if country:
        stmt = stmt.join(article_authors, Article.id == article_authors.c.article_id).join(Author, article_authors.c.author_id == Author.id).where(Author.country == country)
    if keyword:
        stmt = stmt.join(article_keywords, Article.id == article_keywords.c.article_id).join(Keyword, article_keywords.c.keyword_id == Keyword.id).where(Keyword.normalized_keyword == keyword.lower().strip())
    if author_id:
        try:
            stmt = stmt.join(article_authors, Article.id == article_authors.c.article_id).join(Author, article_authors.c.author_id == Author.id).where(Author.id == uuid.UUID(author_id))
        except: pass
    stmt = stmt.group_by(text("month")).order_by(text("month"))
    result = db.execute(stmt)
    return [{"date": row[0], "count": row[1]} for row in result.all()]


@router.get("/top-authors")
async def top_authors(
    limit: int = Query(20, ge=5, le=100),
    country: str | None = None,
    keyword: str | None = None,
    author_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Author.id, Author.name, Author.country, func.count(Article.id).label("cnt"))
        .select_from(Author)
        .join(article_authors, Author.id == article_authors.c.author_id)
        .join(Article, Article.id == article_authors.c.article_id)
    )
    if country:
        stmt = stmt.where(Author.country == country)
    if keyword:
        stmt = stmt.join(article_keywords, Article.id == article_keywords.c.article_id).join(Keyword, article_keywords.c.keyword_id == Keyword.id).where(Keyword.normalized_keyword == keyword.lower().strip())
    if author_id:
        try:
            stmt = stmt.where(Author.id == uuid.UUID(author_id))
        except: pass
    if date_from:
        stmt = stmt.where(Article.published_date >= date.fromisoformat(date_from))
    if date_to:
        stmt = stmt.where(Article.published_date <= date.fromisoformat(date_to))
    stmt = stmt.group_by(Author.id, Author.name, Author.country).order_by(text("cnt DESC")).limit(limit)
    result = db.execute(stmt)
    return [{"id": str(row[0]), "name": row[1], "country": row[2], "count": row[3]} for row in result.all()]


@router.get("/author-trend")
async def author_trend(
    author_id: str = Query(...),
    months: int = Query(24, ge=1, le=120),
    db: AsyncSession = Depends(get_db),
):
    try:
        aid = uuid.UUID(author_id)
    except ValueError:
        return []
    stmt = (
        select(func.to_char(Article.published_date, "YYYY-MM").label("month"), func.count(Article.id).label("cnt"))
        .select_from(Article)
        .join(article_authors, Article.id == article_authors.c.article_id)
        .where(article_authors.c.author_id == aid)
        .where(Article.published_date >= func.current_date() - text(f"interval '{months} months'"))
        .group_by(text("month")).order_by(text("month"))
    )
    result = db.execute(stmt)
    return [{"date": row[0], "count": row[1]} for row in result.all()]


@router.get("/top-journals")
async def top_journals(
    country: str | None = None,
    keyword: str | None = None,
    author_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Journal.id, Journal.name, Journal.abbreviation, func.count(Article.id).label("cnt"))
        .select_from(Journal)
        .join(Article, Journal.id == Article.journal_id)
    )
    if country:
        stmt = stmt.join(article_authors, Article.id == article_authors.c.article_id).join(Author, article_authors.c.author_id == Author.id).where(Author.country == country)
    if keyword:
        stmt = stmt.join(article_keywords, Article.id == article_keywords.c.article_id).join(Keyword, article_keywords.c.keyword_id == Keyword.id).where(Keyword.normalized_keyword == keyword.lower().strip())
    if author_id:
        try:
            stmt = stmt.join(article_authors, Article.id == article_authors.c.article_id).where(article_authors.c.author_id == uuid.UUID(author_id))
        except: pass
    if date_from:
        stmt = stmt.where(Article.published_date >= date.fromisoformat(date_from))
    if date_to:
        stmt = stmt.where(Article.published_date <= date.fromisoformat(date_to))
    stmt = stmt.group_by(Journal.id, Journal.name, Journal.abbreviation).order_by(text("cnt DESC"))
    result = db.execute(stmt)
    return [{"id": str(row[0]), "name": row[1], "abbreviation": row[2], "count": row[3]} for row in result.all()]


@router.get("/author-network")
async def author_network(
    limit: int = Query(50, ge=10, le=200),
    country: str | None = None,
    keyword: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """作者合作网络"""
    where_clauses = ["aa1.article_id = aa2.article_id", "aa1.author_id < aa2.author_id"]
    if country:
        where_clauses.append("a1.country = :country AND a2.country = :country")
    if keyword:
        # 复杂查询简化为子查询
        pass  # 暂不实现

    base_sql = f"""
        SELECT a1.name AS source_name, a2.name AS target_name, COUNT(*) AS weight
        FROM article_authors aa1
        JOIN article_authors aa2 ON aa1.article_id = aa2.article_id AND aa1.author_id < aa2.author_id
        JOIN authors a1 ON aa1.author_id = a1.id
        JOIN authors a2 ON aa2.author_id = a2.id
        {"WHERE " + " AND ".join(where_clauses) if where_clauses else ""}
        GROUP BY a1.name, a2.name
        ORDER BY weight DESC
        LIMIT :limit
    """
    try:
        params = {"limit": limit}
        if country:
            params["country"] = country
        result = db.execute(text(base_sql), params)
        rows = result.all()
    except:
        return {"nodes": [], "links": []}

    nodes_map = {}
    links = []
    for src, tgt, w in rows:
        if src not in nodes_map:
            nodes_map[src] = len(nodes_map)
        if tgt not in nodes_map:
            nodes_map[tgt] = len(nodes_map)
        links.append({"source": src, "target": tgt, "weight": w})
    nodes = [{"id": name, "name": name, "symbolSize": 10 + i * 0.3} for name, i in nodes_map.items()]
    return {"nodes": nodes, "links": links}


@router.get("/journals-stats")
async def journals_stats(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Journal.id, Journal.name, Journal.abbreviation, Journal.publisher, Journal.issn, Journal.platform, Journal.utd24_index, func.count(Article.id).label("article_count"))
        .outerjoin(Article, Journal.id == Article.journal_id)
        .group_by(Journal.id).order_by(Journal.utd24_index)
    )
    result = db.execute(stmt)
    return [{"id": str(row[0]), "name": row[1], "abbreviation": row[2], "publisher": row[3], "issn": row[4], "platform": row[5], "utd24_index": row[6], "article_count": row[7] or 0} for row in result.all()]
