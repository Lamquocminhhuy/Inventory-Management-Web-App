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
from py4web.utils.form import Form, FormStyleBulma, FormStyleBootstrap4, FormStyleDefault
from py4web.utils.grid import Grid, GridClassStyleBulma, GridClassStyle

import json


@action('dashboard')
@action.uses(db, auth.user, 'dashboard.html')
def dashboard():

    return dict()


@action('index', method=["GET", "POST"])
@action('index/<path:path>', method=["GET", "POST"])
@action.uses(db, auth.user, 'index.html')
def index(path=None):

    raw_categories = db.executesql("SELECT * FROM categories;")  # Tuple
    categories = dict((y, x) for x, y in raw_categories)
    # print(categories)
    grid = Grid(
        path, query=db.product.id > 0,
        search_form=None, editable=True, deletable=True, details=False, create=True,
        grid_class_style=GridClassStyleBulma, formstyle=FormStyleBulma, rows_per_page=4,
        search_queries=[
            ['By Name', lambda val: db.product.name.contains(val)],
            ['By Quantity', lambda val: db.product.quantity == val],
            ['By Category', lambda val: db.product.category ==
                categories[str(val)]],
        ]
    )
    #Count total product
    total = db(db.product.id > 0).select()
    outOfStock = db(db.product.quantity == 0).select()
    return dict(grid=grid, total=len(total), outOfStock=len(outOfStock))


@action('category', method=["GET", "POST"])
@action('category/<path:path>', method=["GET", "POST"])
@action.uses(db, auth.user, 'category.html')
def category(path=None):
    # Display data by hand :v
    # rows = db(db.product.created_by == get_user_email()).select()
    grid = Grid(
        path,
        query=db.categories.id > 0,
        search_form=None,
        editable=True, deletable=True, details=False, create=True,
        grid_class_style=GridClassStyleBulma,
        formstyle=FormStyleBulma,
        search_queries=[
            ['By Name', lambda val: db.categories.name.contains(val)]]


    )
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
        search_queries=[['By Username', lambda val: db.auth_user.username.contains(
            val)], ['By Email', lambda val: db.auth_user.email.contains(val)]],


    )
    return dict(grid=grid)


@action('add/<invoice_id:int>', method=["GET", "POST"])
@action.uses(db, auth.user, 'add.html')
def add(invoice_id=None):
    # Using html form
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
    else:
        print("User", get_user_email(), "Product", request.params.get("name"))
        # db.input_invoice.insert(name = request.params.get("name"))
        redirect(URL('add', invoice_id))


@action('add_post/<invoice_id:int>', method=["GET", "POST"])
@action.uses(db, auth.user, 'add.html')
def add_post(invoice_id=None):
    assert invoice_id is not None

    db.input_invoice_details.insert(
        input_invoice_id=invoice_id,
        product_id=request.params.get("productId"),
        quantity=int(request.params.get("quantity")),
        unit_price=int(request.params.get("unit_price"))
    )

    redirect(URL('add', invoice_id))
    # Using py4web form
    # Insert form
    # form = Form(db.product, csrf_session=session, formstyle=FormStyleBulma)
    # if form.accepted:

    #     redirect(URL('index'))

    # If this is a Get request, or this is a POST but not accepted request
    # return dict(form=form)


# @action('edit_product/<product_id:int>', method=["GET", "POST"])
# @action.uses(db, session, auth.user, 'edit.html')
# def edit(product_id=None):
#     assert product_id is not None
#     # p = db(db.product.id == product_id).select()
#     p = db.product[product_id]
#     if p is None:
#         # Nothing found to be edited!
#         redirect(URL('index'))
#     form = Form(db.product, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         redirect(URL('index'))
#     return dict(form=form)


@action('delete_product/<input_invoice_details_id:int>/<invoice_id:int>')
@action.uses(db, session, auth.user)
def delete(input_invoice_details_id, invoice_id=None):
    assert input_invoice_details_id, invoice_id is not None
    db(db.input_invoice_details.id == input_invoice_details_id).delete()
    # print(input_invoice_details_id,invoice_id)
    redirect(URL('add', invoice_id))


@action('admin', method=["GET", "POST"])
@action.uses(db, auth.user, 'admin.html')
def admin():
    if request.method == 'GET':
        products = db(db.product.id > 0).select()
        invoices = db(db.input_invoice.id > 0).select()
        return dict(products=products, invoices=invoices)


@action('test', method=["GET", "POST"])
@action.uses(db, auth.user, 'test.html')
def test():
    if request.method == 'GET':
        return dict()
    else:
        products = request.json
        redirect(URL('index'))
