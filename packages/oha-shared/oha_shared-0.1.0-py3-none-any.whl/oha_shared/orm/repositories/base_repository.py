"""
Base repository class for data access with comprehensive functionality.
"""

from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc, asc, func
from ..models.base_model import BaseModel
from ..exceptions import NotFoundError

T = TypeVar('T', bound=BaseModel)


class BaseRepository(Generic[T]):
    """Comprehensive repository class providing all CRUD and advanced operations."""
    
    def __init__(self, model: Type[T], session: Session):
        """
        Initialize repository.
        
        Args:
            model: The model class to manage
            session: Database session
        """
        self.model = model
        self.session = session
    
    # ===== AUDIT FIELD MANAGEMENT =====
    
    def _set_audit_fields(self, entity: T, user_id: Optional[str] = None) -> None:
        """Set audit fields on entity."""
        current_time = datetime.now(timezone.utc)
        
        # Set timestamps
        if hasattr(entity, 'created_at_utc') and getattr(entity, 'created_at_utc') is None:
            setattr(entity, 'created_at_utc', current_time)
        
        if hasattr(entity, 'updated_at_utc'):
            setattr(entity, 'updated_at_utc', current_time)
        
        # Set user audit fields if they exist and user_id provided
        if user_id:
            if hasattr(entity, 'created_by') and getattr(entity, 'created_by') is None:
                setattr(entity, 'created_by', user_id)
            if hasattr(entity, 'updated_by'):
                setattr(entity, 'updated_by', user_id)
    
    def _set_soft_delete_fields(self, entity: T, user_id: Optional[str] = None) -> None:
        """Set soft delete fields on entity."""
        current_time = datetime.now(timezone.utc)
        
        if hasattr(entity, 'is_deleted'):
            setattr(entity, 'is_deleted', True)
        
        if hasattr(entity, 'deleted_at_utc'):
            setattr(entity, 'deleted_at_utc', current_time)
        
        if hasattr(entity, 'deleted_by') and user_id:
            setattr(entity, 'deleted_by', user_id)
    
    def _build_filters_with_deleted(self, filters: Dict[str, Any], include_deleted: bool = False) -> List:
        """Build filter conditions including deleted filter."""
        conditions = []
        
        # Add user filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, (list, tuple)):
                        conditions.append(getattr(self.model, key).in_(value))
                    else:
                        conditions.append(getattr(self.model, key) == value)
        
        # Add deleted filter if model supports soft delete
        if hasattr(self.model, 'is_deleted') and not include_deleted:
            conditions.append(not (getattr(self.model, 'is_deleted')))
        
        return conditions
    
    # ===== CORE REPOSITORY METHODS =====
    
    def findOne(
        self, 
        filters: Optional[Dict[str, Any]] = None, 
        include_deleted: bool = False, 
        throw_error: bool = False
    ) -> Optional[T]:
        """
        Find single entity with filters.
        
        Args:
            filters: Optional filters to apply
            include_deleted: Whether to include soft-deleted entities
            throw_error: Whether to throw error if not found
        
        Returns:
            Entity instance or None
        
        Raises:
            NotFoundError: If throw_error=True and entity not found
        """
        stmt = select(self.model)
        
        # Apply filters
        conditions = self._build_filters_with_deleted(filters or {}, include_deleted)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.limit(1)
        result = self.session.execute(stmt)
        entity = result.scalar_one_or_none()
        
        if entity is None and throw_error:
            raise NotFoundError(f"{self.model.__name__} not found with filters: {filters}")
        
        return entity
    
    def findMany(
        self, 
        filters: Optional[Dict[str, Any]] = None, 
        pagination: Optional[Dict[str, Any]] = None,
        sort_by: Optional[List[Dict[str, str]]] = None,
        include_deleted: bool = False
    ) -> List[T]:
        """
        Find multiple entities with filters, pagination, and sorting.
        
        Args:
            filters: Optional filters to apply
            pagination: Optional pagination dict with 'page' and 'per_page'
            sort_by: Optional list of sort dicts with 'field' and 'direction' ('asc' or 'desc')
            include_deleted: Whether to include soft-deleted entities
        
        Returns:
            List of entities
        """
        stmt = select(self.model)
        
        # Apply filters
        conditions = self._build_filters_with_deleted(filters or {}, include_deleted)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        # Apply sorting
        if sort_by:
            for sort_item in sort_by:
                field = sort_item.get('field')
                direction = sort_item.get('direction', 'asc')
                
                if hasattr(self.model, field):
                    model_field = getattr(self.model, field)
                    if direction.lower() == 'desc':
                        stmt = stmt.order_by(desc(model_field))
                    else:
                        stmt = stmt.order_by(asc(model_field))
        
        # Apply pagination
        if pagination:
            page = pagination.get('page', 1)
            per_page = pagination.get('per_page', 20)
            offset = (page - 1) * per_page
            stmt = stmt.offset(offset).limit(per_page)
        
        result = self.session.execute(stmt)
        return list(result.scalars().all())
    
    def count(
        self, 
        filters: Optional[Dict[str, Any]] = None, 
        include_deleted: bool = False
    ) -> int:
        """
        Count entities with filters.
        
        Args:
            filters: Optional filters to apply
            include_deleted: Whether to include soft-deleted entities
        
        Returns:
            Count of entities
        """
        stmt = select(func.count()).select_from(self.model)
        
        # Apply filters
        conditions = self._build_filters_with_deleted(filters or {}, include_deleted)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        result = self.session.execute(stmt)
        return result.scalar()
    
    def exists(
        self, 
        filters: Optional[Dict[str, Any]] = None, 
        include_deleted: bool = False, 
        throw_error: bool = False
    ) -> bool:
        """
        Check if entity exists with filters.
        
        Args:
            filters: Optional filters to apply
            include_deleted: Whether to include soft-deleted entities
            throw_error: Whether to throw error if not found
        
        Returns:
            True if entity exists, False otherwise
        
        Raises:
            NotFoundError: If throw_error=True and entity not found
        """
        entity = self.findOne(filters, include_deleted, throw_error)
        return entity is not None
    
    # ===== CRUD OPERATIONS =====
    
    def create(self, user_id: Optional[str] = None, **kwargs) -> T:
        """Create a new entity with audit fields."""
        entity = self.model(**kwargs)
        self._set_audit_fields(entity, user_id)
        self.session.add(entity)
        self.session.flush()
        return entity
    
    def update(self, entity_id: Any, user_id: Optional[str] = None, **kwargs) -> Optional[T]:
        """Update entity by ID with audit fields."""
        entity = self.findOne({'id': entity_id}, include_deleted=True)
        if entity:
            for key, value in kwargs.items():
                setattr(entity, key, value)
            self._set_audit_fields(entity, user_id)
            self.session.flush()
        return entity
    
    def hard_delete(self, entity_id: Any) -> bool:
        """Permanently delete entity from database."""
        entity = self.findOne({'id': entity_id}, include_deleted=True)
        if entity:
            self.session.delete(entity)
            self.session.flush()
            return True
        return False
    
    def soft_delete(self, entity_id: Any, user_id: Optional[str] = None) -> bool:
        """Soft delete entity (mark as deleted)."""
        entity = self.findOne({'id': entity_id}, include_deleted=True)
        if entity and hasattr(entity, 'is_deleted'):
            self._set_soft_delete_fields(entity, user_id)
            self.session.flush()
            return True
        return False
    
    # ===== BULK OPERATIONS =====
    
    def bulk_create(self, entities_data: List[Dict[str, Any]], user_id: Optional[str] = None) -> List[T]:
        """Create multiple entities at once with audit fields."""
        entities = []
        for data in entities_data:
            entity = self.model(**data)
            self._set_audit_fields(entity, user_id)
            entities.append(entity)
            self.session.add(entity)
        
        self.session.flush()
        return entities
    
    def bulk_update(self, entities: List[T], user_id: Optional[str] = None, **kwargs) -> List[T]:
        """Update multiple entities at once with audit fields."""
        for entity in entities:
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            self._set_audit_fields(entity, user_id)
        
        self.session.flush()
        return entities
    
    def bulk_delete(self, entity_ids: List[Any], user_id: Optional[str] = None, soft_delete: bool = True) -> int:
        """Delete multiple entities by IDs."""
        deleted_count = 0
        for entity_id in entity_ids:
            if soft_delete:
                if self.soft_delete(entity_id, user_id):
                    deleted_count += 1
            else:
                if self.hard_delete(entity_id):
                    deleted_count += 1
        
        return deleted_count
