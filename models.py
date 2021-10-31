
# This file defines the database models

import datetime
from .common import db, Field, auth
from pydal.validators import *

### Define your table below


def get_user_email():
    return auth.current_user.get('email')


def get_time():
    return datetime.datetime.now().date()


def total():
    return db.input_invoice_details.quantity * db.input_invoice_details.price


#------------------------------------------------------------------------------------------------#
db.define_table(
    'categories',
    Field('name')
)


#------------------------------------------------------------------------------------------------#
db.define_table(
    'product',
    Field('categories_id', 'reference categories',
          filter_out=lambda categories: categories.name if categories else ''),
    Field('product_code'),
    Field('description'),
    Field('quantity', 'integer', default=0),
    Field('unit'),
    Field('created_by', default=get_user_email),
    Field('created_at', default=get_time),
)
db.product.description.requires = IS_NOT_EMPTY()
db.product.id.readable = db.product.id.writable = False
db.product.created_by.readable = db.product.created_by.writable = False
db.product.created_at.readable = db.product.created_at.writable = False
db.product.categories_id.requires = IS_IN_DB(db, db.categories.id, '%(name)s')
#------------------------------------------------------------------------------------------------#
db.define_table(
    'input_invoice',
    Field('name', 'text'),
    Field('created_at', default=get_time)
)

#------------------------------------------------------------------------------------------------#
db.define_table(
    'input_invoice_details',
    Field('input_invoice_id', 'reference input_invoice',
          filter_out=lambda input_invoice: input_invoice.name if input_invoice else ''),
    Field('product_id', 'reference product',
          filter_out=lambda product: product.product_code if product else ''),
    Field('quantity', 'integer'),
    Field('unit_price', 'integer'),
    Field('total_price', compute=lambda row: row.quantity * row.unit_price)
)
db.input_invoice_details.total_price.writable = False
db.input_invoice_details.input_invoice_id.requires = IS_IN_DB(
    db, db.input_invoice.id, '%(name)s')
db.input_invoice_details.product_id.requires = IS_IN_DB(
    db, db.product.id, '%(product_code)s')


# Hoa don va chi tiet hoa don
# Hoa don field ngay tao , ten hoa don
# Chi tiet hoa don field so luong, gia san pham, thanh tien

## always commit your models to avoid problems later
db.commit()
