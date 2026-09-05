from math import ceil
from typing import Literal, Optional, Tuple, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload, joinedload
from src.models import PostORM, AuthorORM, TagORM


class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, post_id: int) -> Optional[PostORM]:
        post_find = select(PostORM).where(PostORM.id == post_id)
        return self.db.execute(post_find).scalar_one_or_none()

    def search(
        self,
        query: Optional[str],
        order_by: Literal['id', 'title'],
        direction: Literal['asc', 'desc'],
        page: int,
        per_page: int
    ) -> Tuple[int, List[PostORM]]:
        results = select(PostORM)

        if query:
            results = results.where(PostORM.title.ilike(f'%{query}%'))

        total = self.db.scalar(
            select(func.count()).select_from(
                results.subquery()
            )
        ) or 0

        if total == 0:
            return 0, []

        current_page = min(page, max(1, ceil(total / per_page)))

        order_col = PostORM.id if order_by == 'id' else func.lower(
            PostORM.title
        )

        results = results.order_by(
            order_col.asc() if direction == 'asc' else order_col.desc()
        )

        start = (current_page - 1) * per_page
        items = self.db.execute(
            results.limit(per_page).offset(start)
        ).scalars().all()

        return total, items

    def by_tags(self, tags: List[str]) -> List[PostORM]:
        normalized_tag_names = [
            tag.strip().lower()
            for tag in tags
            if tag.strip()
        ]

        if not normalized_tag_names:
            return []

        post_list = (
            select(PostORM)
            .options(
                selectinload(PostORM.tags),
                joinedload(PostORM.author)
            ).where(
                PostORM.tags.any(
                    func.lower(TagORM.name).in_(normalized_tag_names)
                )
            ).order_by(
                PostORM.id.asc()
            )
        )

        return self.db.execute(post_list).scalars().all()
