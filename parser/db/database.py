from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from .models import Product

DATABASE_URL = 'postgresql://eldos:1@localhost/mart'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData()
metadata.create_all(bind=engine)
Product.metadata.create_all(bind=engine)