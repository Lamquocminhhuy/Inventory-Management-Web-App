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
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from .models import get_user_email
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.grid import Grid, GridClassStyleBulma


@action('index', method=["GET", "POST"])
@action('index/<path:path>', method=["GET", "POST"])
@action.uses(db,auth, 'index.html')
def index(path=None):
    # Display data by hand :v
    # rows = db(db.product.created_by == get_user_email()).select()
    grid = Grid(
        path,
        query = db.product.id > 0,
        search_form=None,
        editable=True, deletable=True, details=False, create=True,
     
        grid_class_style=GridClassStyleBulma,
        formstyle=FormStyleBulma,
        search_queries=[['By Name', lambda val: db.product.name.contains(val)],['By Quantity', lambda val: db.product.quantity == val]]


    )
    return dict(grid=grid)

@action('user', method=["GET", "POST"])
@action('user/<path:path>', method=["GET", "POST"])
@action.uses(db,auth, 'user.html')
def index(path=None):
   
    grid = Grid(
        path,
        query = db.auth_user.id > 0,
        search_form=None,
        editable=True, deletable=True, details=False, create=True,
     
        grid_class_style=GridClassStyleBulma,
        formstyle=FormStyleBulma,
        search_queries=[['By Username', lambda val: db.auth_user.username.contains(val)],['By Email', lambda val: db.auth_user.email.contains(val)]],


    )
    return dict(grid=grid)



@action('add', method=["GET", "POST"])
@action.uses(db, auth.user, 'add.html')
def add():
    # Using html form
    # if request.method == "GET":
    #     return dict()
    # else:
    #     print("User", get_user_email(), "Product", request.params.get("name"))
    #     db.product.insert(name = request.params.get("name"))
    #     redirect(URL('add'))

    # Using py4web form
    # Insert form
    form = Form(db.product, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        
        redirect(URL('index'))

    # If this is a Get request, or this is a POST but not accepted request
    return dict(form=form)


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


@action('delete_product/<product_id:int>')
@action.uses(db, session, auth.user)
def delete(product_id=None):
    assert product_id is not None
    db(db.product.id == product_id).delete()
    redirect(URL('index'))
