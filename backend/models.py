import uuid
from sqlalchemy import Column, String, Integer, JSON, Text, inspect
from database import Base

def generate_uuid():
    return str(uuid.uuid4())

class DatasetMeta(Base):
    __tablename__ = "datasets"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, default="admin")
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    row_count = Column(Integer, nullable=False)
    column_count = Column(Integer, nullable=False)
    columns = Column(JSON, nullable=False)
    preview = Column(JSON, nullable=False)
    uploaded_at = Column(String, nullable=False)
    status = Column(String, nullable=False, default="ready")

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class ReportMeta(Base):
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    dataset_id = Column(String, nullable=True)
    query = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    insights = Column(JSON, nullable=False)
    created_at = Column(String, nullable=False)
    status = Column(String, nullable=False, default="completed")

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class QueryLogDB(Base):
    __tablename__ = "query_logs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    query = Column(Text, nullable=False)
    dataset_id = Column(String, nullable=True)
    response_time_ms = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class WorkspaceDB(Base):
    __tablename__ = "workspaces"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    color = Column(String, nullable=True)
    dataset_ids = Column(JSON, nullable=False, default=list)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
