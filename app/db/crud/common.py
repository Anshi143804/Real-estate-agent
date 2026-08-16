from __future__ import annotations

from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import Select, delete, select
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
    """
    Generic CRUD helper.

    Every repository inherits from this class.
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    def create(self, db: Session, **kwargs) -> ModelType:
        obj = self.model(**kwargs)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------

    def get(self, db: Session, obj_id: Any) -> Optional[ModelType]:
        return db.get(self.model, obj_id)

    def get_all(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelType]:
        stmt = (
            select(self.model)
            .offset(skip)
            .limit(limit)
        )

        return db.scalars(stmt).all()

    def first(
        self,
        db: Session,
        stmt: Select,
    ) -> Optional[ModelType]:
        return db.scalar(stmt)

    def all(
        self,
        db: Session,
        stmt: Select,
    ) -> Sequence[ModelType]:
        return db.scalars(stmt).all()

    def exists(self, db: Session, obj_id: Any) -> bool:
        return self.get(db, obj_id) is not None

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def update(
        self,
        db: Session,
        obj: ModelType,
        **kwargs,
    ) -> ModelType:

        for key, value in kwargs.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        db.commit()
        db.refresh(obj)

        return obj

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    def delete(
        self,
        db: Session,
        obj: ModelType,
    ) -> None:

        db.delete(obj)
        db.commit()

    def delete_by_id(
        self,
        db: Session,
        obj_id: Any,
    ) -> bool:

        obj = self.get(db, obj_id)

        if obj is None:
            return False

        db.delete(obj)
        db.commit()

        return True

    def delete_all(
        self,
        db: Session,
    ) -> None:

        stmt = delete(self.model)

        db.execute(stmt)
        db.commit()

    # ------------------------------------------------------------------
    # SESSION HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def commit(db: Session):
        db.commit()

    @staticmethod
    def refresh(
        db: Session,
        obj: ModelType,
    ):
        db.refresh(obj)