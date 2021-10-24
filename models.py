"""
This file defines the database models
"""
import datetime
from .common import db, Field, auth
from pydal.validators import *

### Define your table below
#
def get_user_email():
    return auth.current_user.get('email')

def get_time():
    return datetime.datetime.utcnow()

db.define_table(
    'categories',
    Field('name')
)


db.define_table(
    'product',
    Field('category' ,'reference categories', filter_out=lambda categories: categories.name if categories else ''),
    Field('name'),
    Field('quantity', 'integer',default=0), 
    Field('unit'),
    Field('created_by', default= get_user_email),
    Field('created_at', default= get_time), 
)

db.product.name.requires = IS_NOT_EMPTY()
db.product.id.readable = db.product.id.writable =False
db.product.created_by.readable = db.product.created_by.writable = False
db.product.created_at.readable = db.product.created_at.writable = False
db.product.category.requires = IS_IN_DB(db, db.categories.id, '%(name)s')

#
## always commit your models to avoid problems later
#
db.commit()
#

