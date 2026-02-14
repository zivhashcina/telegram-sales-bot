from sqlalchemy import Column, Integer, BigInteger, String, Text, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    language_code = Column(String(10))
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_interaction = Column(DateTime, default=datetime.utcnow)
    total_clicks = Column(Integer, default=0)
    total_views = Column(Integer, default=0)

    interactions = relationship("Interaction", back_populates="user")
    searches = relationship("Search", back_populates="user")

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    price = Column(Float)
    affiliate_link = Column(String(500))
    image_url = Column(String(500))
    tags = Column(JSON)
    views = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    interactions = relationship("Interaction", back_populates="product")

class Interaction(Base):
    __tablename__ = 'interactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    action = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="interactions")
    product = relationship("Product", back_populates="interactions")

class Search(Base):
    __tablename__ = 'searches'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    query = Column(String(200))
    results_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="searches")

class Campaign(Base):
    __tablename__ = 'campaigns'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    message = Column(Text)
    filter_criteria = Column(JSON)
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    created_by = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)
