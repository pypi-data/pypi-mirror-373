
from base_test import BaseTest
from src.shadowshell.db.db_starter import DbStarter, ModelBase

from sqlalchemy import VARCHAR
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session

class Item(ModelBase):
    
    __tablename__ = 'item'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(32))
   
    def __repr__(self):
        return f"Item(id={self.id!r}, name={self.name!r})"

from sqlalchemy import select

class Test(DbStarter):

    def __init__(self):
        super().__init__()
       
    def get_work_dir(self):
        return '.'
        
    def get_config_file_path(self):
        """ 获取配置文件路径"""
        return f'/Users/shadowwalker/shadowshellxyz/.shadowshell/app.ini'

    def test(self):
        session = Session(self.engine)
        stmt = select(Item).where(Item.name.in_(['养元六个核桃贺岁款六六大顺罐精品型240ml*12罐饮料整箱']))
        for item in session.scalars(stmt):
            print(item)

Test().test()

