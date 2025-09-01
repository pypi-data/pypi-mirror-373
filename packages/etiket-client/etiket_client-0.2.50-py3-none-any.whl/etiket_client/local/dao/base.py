from sqlalchemy import select, delete
class dao_base:
    @staticmethod
    def _create(create_schema, model, session):
        model_db = model(**create_schema.model_dump(by_alias=True))
        session.add(model_db)
        session.commit()
        return model_db
    
    @staticmethod
    def _read_all(model, read_schema, session, string_query,
                  is_equal_query, orderby, offset, limit):
        stmt = dao_base._query(model, string_query, is_equal_query,
                                orderby, offset, limit)
        result = session.execute(stmt).scalars().all()
        return [read_schema.model_validate(res) for res in result]

    @staticmethod
    def _update(model, update_schema, session, exclude = None):
        update_schema_dict = update_schema.model_dump(exclude_unset=True, by_alias=True, exclude=exclude)
        for k, v in update_schema_dict.items():
            if v is not None:
                setattr(model, k, v)
        session.commit()
        return model
    
    @staticmethod
    def _delete(model, condition, session):
        stmt = delete(model).where(condition)
        session.execute(stmt)
        session.commit()
    
    @staticmethod
    def _query(model, string_query, is_equal_query, 
                orderby, offset = None, limit = None):
        stmt = select(model)
        if orderby is not None:
            stmt = stmt.order_by(orderby)
        if string_query:
            for k,v in string_query.items():
                if v is not None:
                    stmt = stmt.where(k.ilike(f"%{v}%"))
        if is_equal_query:
            for k,v in is_equal_query.items():
                if v is not None:
                    stmt = stmt.where(k == v)
        
        if offset : stmt = stmt.offset(offset)
        if limit : stmt = stmt.limit(limit)
        return stmt
    
    @staticmethod
    def _unique(model, condition, session):
        stmt = select(model).where(condition)
        if len(session.execute(stmt).scalars().all()) != 0:
            return False
        return True