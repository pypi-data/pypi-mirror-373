from sqlalchemy import Column, String, Integer, DateTime, Text, BigInteger, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from clickhouse_sqlalchemy import engines
from clickhouse_sqlalchemy.types import DateTime64
from clickhouse_sqlalchemy.types import Map, LowCardinality

class Span(Base):
    __tablename__ = 'direct_otel_spans'
    __table_args__ = (
        engines.MergeTree(
            order_by=['Timestamp']
        ),
    )
    Timestamp = Column(DateTime64(precision=9), nullable=False)

    TraceId = Column(String, primary_key=True, nullable=False)
    SpanId = Column(String, primary_key=True, nullable=False)
    ParentSpanId = Column(String, nullable=True)
    TraceState = Column(String, nullable=True)
    SpanName = Column(String, nullable=False)  # LowCardinality(String)
    SpanKind = Column(String, nullable=False)  # LowCardinality(String)
    ServiceName = Column(String, nullable=False)  # LowCardinality(String)
    ResourceAttributes = Column(
        Map(LowCardinality(String), String),
        nullable=True
    )  # Map(LowCardinality(String), String)
    ScopeName = Column(String, nullable=True)
    ScopeVersion = Column(String, nullable=True)
    SpanAttributes = Column(
        Map(LowCardinality(String), String),
        nullable=True
    )  # Map(LowCardinality(String), String)
    Duration = Column(BigInteger, nullable=False)  # UInt64
    StatusCode = Column(String, nullable=True)  # LowCardinality(String)
    StatusMessage = Column(String, nullable=True)
    Events_Timestamp = Column(String, nullable=True)  # Array(DateTime64(9))
    Events_Name = Column(String, nullable=True)  # Array(LowCardinality(String))
    Events_Attributes = Column(String, nullable=True)  # Array(Map(LowCardinality(String), String))
    Links_TraceId = Column(String, nullable=True)  # Array(String)
    Links_SpanId = Column(String, nullable=True)  # Array(String)
    Links_TraceState = Column(String, nullable=True)  # Array(String)
    Links_Attributes = Column(String, nullable=True)  # Array(Map(LowCardinality(String), String))
