"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and templates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from os import truncate
from types import MethodType
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A, P
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from .models import get_user_email
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.grid import Grid, GridClassStyleBulma, GridClassStyle
import json


@action('dashboard')
@action.uses(db, auth.user, 'dashboard.html')
def dashboard():
    return dict()


@action('index', method=["GET", "POST"])
@action.uses(db, auth.user, 'index.html')
def index():
    if request.method == 'GET':
        products = db(db.product.id > 0).select()
        invoices = db(db.input_invoice.id > 0).select()
        return dict(products=products, invoices=invoices)


@action('product', method=["GET", "POST"])
@action('product/<path:path>', method=["GET", "POST"])
@action.uses(db, auth.user, 'product.html')
def product(path=None):

    raw_categories = db.executesql("SELECT * FROM categories;")
    categories = dict((y, x) for x, y in raw_categories)
    print(categories)
    grid = Grid(
        path, query=db.product.id > 0,
        search_form=None, editable=True, deletable=True, details=False, create=True,
        grid_class_style=GridClassStyleBulma, formstyle=FormStyleBulma, rows_per_page=4,
        search_queries=[
            ['By Code', lambda val: db.product.product_code.contains(val)],
            ['By Category', lambda val: db.product.categories_id == categories[str(val)]]
        ])
    #Count total product
    total = db(db.product.id > 0).select()
    return dict(grid=grid, total=len(total))


@action('category', method=["GET", "POST"])
@action('category/<path:path>', method=["GET", "POST"])
@action.uses(db, auth.user, 'category.html')
def category(path=None):

    grid = Grid(
        path,
        query=db.categories.id > 0,
        search_form=None,
        editable=True, deletable=True, details=False, create=True,
        grid_class_style=GridClassStyleBulma,
        formstyle=FormStyleBulma,
        search_queries=[
            ['By Name', lambda val: db.categories.name.contains(val)]])
    #Count total product
    total = db(db.categories.id > 0).select()

    return dict(grid=grid, total=len(total))


@action('user', method=["GET", "POST"])
@action('user/<path:path>', method=["GET", "POST"])
@action.uses(db, auth.user, 'user.html')
def user(path=None):

    grid = Grid(
        path,
        query=db.auth_user.id > 0,
        search_form=None,
        editable=True, deletable=True, details=False, create=True,
        grid_class_style=GridClassStyleBulma,
        formstyle=FormStyleBulma,
        search_queries=[
            ['By Username', lambda val: db.auth_user.username.contains(val)],
            ['By Email', lambda val: db.auth_user.email.contains(val)]])
    return dict(grid=grid)


@action('get_invoice/<invoice_id:int>', method=["GET"])
@action.uses(db, auth.user, 'invoice.html')
def get_invoice(invoice_id=None):

    if request.method == "GET":
        total = 0
        total_product = []

        invoice = db(db.input_invoice.id == invoice_id).select()

        invoice_details = db(
            db.input_invoice.id == db.input_invoice_details.input_invoice_id == invoice_id).select()

        products = db(db.product.id > 0).select()

        for i in invoice_details:
            total += int(i.total_price)
            total_product.append(i.product_id)

        return dict(invoice=invoice, invoice_details=invoice_details, total=total, products=products, total_products=len(total_product))


@action('post_invoice/<invoice_id:int>', method=["GET", "POST"])
@action.uses(db, auth.user, 'add.html')
def post_invoice(invoice_id=None):
    assert invoice_id is not None

    db.input_invoice_details.insert(
        input_invoice_id=invoice_id,
        product_id=request.params.get("productId"),
        quantity=int(request.params.get("quantity")),
        unit_price=int(request.params.get("unit_price"))
    )
   
  

    redirect(URL('get_invoice', invoice_id))


@action('create_invoice', method=["POST"])
@action.uses(db, auth.user)
def create_invoice():
    if request.params.get("name"):

        db.input_invoice.insert(name=request.params.get("name"))
        invoice = db(db.input_invoice.name ==
                     request.params.get("name")).select()
        invoice_id = invoice[0].id

    redirect(URL('get_invoice', invoice_id))


@action('delete_invoice', method=["POST"])
@action.uses(db, auth.user)
def delete_invoice():
    if request.params.get("id"):

        db(db.input_invoice.id == request.params.get("id")).delete()

    redirect(URL('index'))


@action('delete_product/<input_invoice_details_id:int>/<invoice_id:int>')
@action.uses(db, session, auth.user)
def delete(input_invoice_details_id, invoice_id=None):
    assert input_invoice_details_id, invoice_id is not None
    db(db.input_invoice_details.id == input_invoice_details_id).delete()

    redirect(URL('get_invoice', invoice_id))


@action('test', method=["GET", "POST"])
@action.uses(db, auth.user, 'test.html')
def test():
    if request.method == 'GET':
        return dict()
    else:
        products = request.json

        redirect(URL('index'))

@action('print-invoice/<invoice_id:int>', method=["GET"])
@action.uses(db, auth.user, 'hoadon.html')
def invoiceJson(invoice_id):
    total = 0
    total_product = []
    invoice = db(db.input_invoice.id == invoice_id).select()
    invoice_details = db(db.input_invoice.id == db.input_invoice_details.input_invoice_id ==  invoice_id).select()
    for i in invoice_details:
        total += int(i.total_price)
        total_product.append(i.product_id)

  
   
    # return dict json 
    products = db(db.product.id > 0).select()
    return dict(invoice=invoice, details = invoice_details, total = total, total_product = len(total_product), products = products)


@action('customer-infor/<invoice_id:int>', method=["POST"])
@action.uses(db, auth.user)
def customer(invoice_id = None):
    assert invoice_id is not None
    invoice = db(db.input_invoice.id == invoice_id)
    invoice.update(customer_name=request.params.get("fullname"),customer_address=request.params.get("address"))
    

    redirect(URL('get_invoice', invoice_id))

# @action('edit_product/<product_id:int>', method=["GET", "POST"])
# @action.uses(db, session, auth.user, 'edit.html')
# def edit(product_id=None):
#     assert product_id is not None
#     # p = db(db.product.id == product_id).select()
#        p = db.product[product_id]
#     if p is None:
#         # Nothing found to be edited!
#         redirect(URL('index'))
#     form = Form(db.product, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         redirect(URL('index'))
#     return dict(form=form)
