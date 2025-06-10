from sqlalchemy import Column, Integer, String, JSON, Text, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.declarative import declared_attr

Base = declarative_base()

# Таблица для связи многие-ко-многим между пользователями и категориями
user_categories = Table(
    'user_categories',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text, nullable=True)
    
    users = relationship("User", secondary=user_categories, back_populates="categories")

class SpecificItem(Base):
    __tablename__ = "specific_items"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    description = Column(Text, nullable=True)
    quantity = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    
    user = relationship("User", back_populates="specific_items")
    category = relationship("Category")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    full_name = Column(String)
    phone = Column(String)
    organization_type = Column(String)
    organization_name = Column(String)
    contact_person = Column(String)
    website = Column(String)
    user_type = Column(String)  # 'military' или 'volunteer'
    
    # Отношения
    categories = relationship("Category", secondary=user_categories, back_populates="users")
    specific_items = relationship("SpecificItem", back_populates="user")

    def __repr__(self):
        return f"<User {self.full_name}>"
    
    @property
    def categories_list(self):
        return [category.name for category in self.categories]
    
    @property
    def specific_items_list(self):
        return [
            {
                'name': item.name,
                'description': item.description,
                'quantity': item.quantity,
                'category': item.category.name if item.category else None
            }
            for item in self.specific_items
        ] 