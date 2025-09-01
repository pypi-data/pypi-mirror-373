from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from urllib.parse import quote_plus as urlquote

db = create_engine(f"mysql+pymysql://yywsxyzl:{urlquote('xyzl2@24')}@localhost:3306/yyws_xyzl_view", echo=True)

# 建立映射关系
BaseEntity = declarative_base()
