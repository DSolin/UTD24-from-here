import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User, Favorite
from app.models.article import Article
from app.api.auth import get_current_user

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get("")
async def list_favorites(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        raise HTTPException(401, "Sign in required")
    
    stmt = (
        select(Favorite)
        .options(selectinload(Favorite.article).selectinload(Article.journal))
        .options(selectinload(Favorite.article).selectinload(Article.authors))
        .where(Favorite.user_id == user.id)
        .order_by(Favorite.created_at.desc())
    )
    result = db.execute(stmt)
    favs = result.scalars().all()
    
    items = []
    for fav in favs:
        a = fav.article
        items.append({
            "id": str(fav.id),
            "article_id": str(a.id),
            "title": a.title,
            "abstract": (a.abstract or "")[:300],
            "doi": a.doi,
            "published_date": str(a.published_date) if a.published_date else None,
            "journal": {"id": str(a.journal.id) if a.journal else None, "name": a.journal.name if a.journal else None, "abbreviation": a.journal.abbreviation if a.journal else None},
            "authors": [{"id": str(au.id), "name": au.name} for au in (a.authors or [])[:5]],
            "favorited_at": str(fav.created_at) if fav.created_at else None,
        })
    return {"total": len(items), "items": items}


@router.post("/{article_id}")
async def add_favorite(
    article_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        raise HTTPException(401, "Sign in required")
    try:
        aid = uuid.UUID(article_id)
    except ValueError:
        raise HTTPException(400, "Invalid article ID")
    
    r = db.execute(select(Favorite).where(Favorite.user_id == user.id, Favorite.article_id == aid))
    if r.scalar_one_or_none():
        return {"message": "Already favorited", "article_id": article_id}
    
    fav = Favorite(id=uuid.uuid4(), user_id=user.id, article_id=aid)
    db.add(fav)
    db.commit()
    return {"message": "Favorited", "article_id": article_id}


@router.delete("/{article_id}")
async def remove_favorite(
    article_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        raise HTTPException(401, "Sign in required")
    try:
        aid = uuid.UUID(article_id)
    except ValueError:
        raise HTTPException(400, "Invalid article ID")
    
    r = db.execute(select(Favorite).where(Favorite.user_id == user.id, Favorite.article_id == aid))
    fav = r.scalar_one_or_none()
    if not fav:
        raise HTTPException(404, "Not favorited")
    
    await db.delete(fav)
    db.commit()
    return {"message": "Unfavorited", "article_id": article_id}


@router.get("/check/{article_id}")
async def check_favorite(
    article_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user:
        return {"favorited": False}
    try:
        aid = uuid.UUID(article_id)
    except ValueError:
        return {"favorited": False}
    r = db.execute(select(Favorite).where(Favorite.user_id == user.id, Favorite.article_id == aid))
    return {"favorited": r.scalar_one_or_none() is not None}
