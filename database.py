from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError
import pandas as pd
from typing import List, Dict

Base = declarative_base()

class Site(Base):
    __tablename__ = 'sites'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    xpath = Column(String, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine('sqlite:///zuzublics.db')
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def save_to_db(df: pd.DataFrame):
    records = df.to_dict(orient='records')
    with SessionLocal() as session:
        for record in records:
            exists = session.query(Site).filter(Site.url == record['url']).first()
            if not exists:
                try:
                    session.add(Site(**record))
                    session.commit()
                except IntegrityError as e:
                    session.rollback()
                    print(f"URL уже существует: {record['url']}")
        
def get_all_sites() -> pd.DataFrame:
    with SessionLocal() as session:
        sites = session.query(Site).all()
        data = [
            {
                'title': site.title,
                'url': site.url,
                'xpath': site.xpath
            }
            for site in sites
        ]
    
    return pd.DataFrame(data)
