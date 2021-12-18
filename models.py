
# This file defines the database models

import datetime
from .common import db, Field, auth
from pydal.validators import *



# Get user email
def get_user_email():
    return auth.current_user.get('email')

# Method get time 
def get_time(): 
    return datetime.datetime.now().date()

# Calculating totol of invoice
def total():
    return db.input_invoice_details.quantity * db.input_invoice_details.price



# Category table
db.define_table(
    'categories',
    Field('name')
)


# Product table
db.define_table(
    'product',
    Field('categories_id', 'reference categories',
          filter_out=lambda categories: categories.name if categories else ''),
    Field('product_code'),
    Field('description'),
    Field('unit'),
    Field('created_by', default=get_user_email),
    Field('created_at', default=get_time),
)

db.product.description.requires = IS_NOT_EMPTY()
db.product.id.readable = db.product.id.writable = False
db.product.created_by.readable = db.product.created_by.writable = False
db.product.created_at.readable = db.product.created_at.writable = False
db.product.categories_id.requires = IS_IN_DB(db, db.categories.id, '%(name)s')

# Input invoice table
db.define_table(
    'input_invoice',
    Field('name', 'text'),
    Field('customer_name','text'),
    Field('customer_address','text'),
    Field('created_at', default=get_time)
)

# Input invoice details
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

# Output (Export) invoice
db.define_table(
    'output_invoice',
    Field('name', 'text'),
    Field('customer_name','text'),
    Field('customer_address','text'),
    Field('created_at', default=get_time)
)

# Output (Export) invoice details
db.define_table(
    'output_invoice_details',
    Field('output_invoice_id', 'reference output_invoice',
          filter_out=lambda output_invoice: output_invoice.name if output_invoice else ''),
    Field('product_id', 'reference product',
          filter_out=lambda product: product.product_code if product else ''),
    Field('quantity', 'integer'),
    Field('unit_price', 'integer'),
    Field('total_price', compute=lambda row: row.quantity * row.unit_price)
)


## always commit your models to avoid problems later
db.commit()
