#!/usr/bin/env python3
from flask import (
    Flask,
    flash,
    render_template,
    request,
    url_for,
    redirect,
    jsonify
    )

import sys

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String
    )

from sqlalchemy.ext.declarative import declarative_base
from flask import make_response

from sqlalchemy.orm import relationship, backref

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from sqlalchemy import create_engine


from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import os
import random
import string
import httplib2
import json
import requests


app = Flask(__name__)

Base = declarative_base()


class Admin(Base):
    __tablename__ = "admin"
    admin_id = Column(Integer, primary_key=True)
    admin_mail = Column(String(100), nullable=False)


class Sports(Base):
    __tablename__ = "sports"
    sports_id = Column(Integer, primary_key=True)
    sports_name = Column(String(100), nullable=False)
    sports_admin = Column(Integer, ForeignKey('admin.admin_id'))
    sports_relation = relationship(Admin)

    @property
    def serialize(self):
        return {
            'id': self.sports_id,
            'name': self.sports_name

        }


class Items(Base):
    __tablename__ = "items"
    item_id = Column(Integer, primary_key=True)
    item_name = Column(String(100), nullable=False)
    item_price = Column(Integer, nullable=False)
    item_brand = Column(String(100), nullable=False)
    item_image = Column(String(1000), nullable=False)
    sports_id = Column(Integer, ForeignKey('sports.sports_id'))
    item_relation = relationship(
        Sports,
        backref=backref("sports", cascade="all,delete"))

    @property
    def serialize(self):
        return {
            'id': self.item_id,
            'name': self.item_name,
            'price': self.item_price,
            'publisher': self.item_brand,
            'image': self.item_image

        }


engine = create_engine('sqlite:///sports.db')
Base.metadata.create_all(engine)

session = scoped_session(sessionmaker(bind=engine))


CLIENT_DATA = json.loads(open("client_secrets.json").read())
CLIENT_ID = CLIENT_DATA["web"]['client_id']


@app.route('/home')
def home():
    items = session.query(Items).all()
    return render_template(
        'showsportitems.html', Items=items, hasRecent=True, category_id=None)


@app.route('/read')
def read():
    sports = session.query(Items).all()
    msg = ""
    for each in sports:
        msg += str(each.item_name)
    return msg


# Method For deleting Category of Sports
@app.route('/deleteCat', methods=['GET', 'POST'])
def deleteSportCat():
    if 'email' not in login_session:
        flash("You must login!!!!")
        return redirect(url_for('login'))
    admin = session.query(Admin).filter_by(
        admin_mail=login_session['email']
        ).one_or_none()
    if admin is None:
        flash("User Not Valid!!!!")
        return redirect(url_for('home'))

    sports = session.query(Sports).filter_by(
        sports_admin=admin.admin_id
        ).all()
    if sports is None:
        flash('There are no categories with such name')
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('deletesportcat.html', sports=sports)
    elif 'POST':
        delete = request.form
        hasDelete = False
        for each in delete:
            hasDelete = True
            category = session.query(Sports).filter_by(
                sports_id=int(delete[each])).one_or_none()
            try:
                session.delete(category)
            except Exception as e:
                print("\n\n\n", e)
        session.commit()
        if hasDelete:
            flash('Deletion Successfull')
        else:
            flash('Select any Category to delete !!! ')
    return redirect(url_for('home'))


# Method For Editing the Sportswear Category
@app.route('/edit')
def editCat():
    categories = session.query(Sports).all()
    if len(categories) == 0:
        flash('No Categories Found To Edit')
    return render_template('editsportcat.html', categoriesList=categories)


@app.route('/sportscat/json')
def categoriesJSON():
    categories = session.query(Sports).all()
    return jsonify(sports=[c.serialize for c in categories])


@app.route('/sports/JSON')
def itemsJSON():
    items = session.query(Items).all()
    return jsonify(sports=[i.serialize for i in items])


# Methd for Creating New Category Of Sport
@app.route('/category/new', methods=['GET', 'POST'])
def newsportcat():
    if 'email' not in login_session:
        flash("You Must Login!!!!")
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('new_category.html')
    else:
        category_name = request.form['category_name']
        if category_name:
            admin = session.query(Admin).filter_by(
                admin_mail=login_session['email']
                ).one_or_none()
            if admin is None:
                return redirect(url_for('home'))
            admin_id = admin.admin_id
            new_sports = Sports(
                sports_name=category_name,
                sports_admin=admin_id
                )
            session.add(new_sports)
            session.commit()
            flash('Hurray!! Added your category')
            return redirect(url_for('home'))
        else:
            flash('Sorry,cannot add category')
            return redirect(url_for('home'))


# Edit the Sportswear category specifically
@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def editSportscategory(category_id):
    if 'email' not in login_session:
        flash("You Need To Login")
        return redirect(url_for('login'))
    admin = session.query(Admin).filter_by(
        admin_mail=login_session['email']
        ).one_or_none()
    if admin is None:
        flash("Not A Valid User!!!")
        return redirect(url_for('home'))
    sports = session.query(Sports).filter_by(
        sports_id=category_id
        ).one_or_none()
    if sports is None:
        flash('Category Not Found To Edit')
        return redirect(url_for('home'))
    login_admin_id = admin.admin_id
    admin_id = sports.sports_admin
    if login_admin_id != admin_id:
        flash('You are not authorized to edit this category')
        return redirect(url_for('home'))

    if request.method == 'POST':
        category_name = request.form['category_name']
        sports.sports_name = category_name
        session.add(sports)
        session.commit()
        flash('Updation Successfull')
        return redirect(url_for('home'))
    else:
        sports = session.query(Sports).filter_by(
            sports_id=category_id
            ).one_or_none()
        return render_template(
            'editsportcategory.html',
            sports_name=sports.sports_name,
            id_category=category_id)


@app.route('/category/<int:category_id>/items.json')
def one_category_json(category_id):
    catsingle = session.query(Items).filter_by(sports_id=category_id).all()
    return jsonify(Catsingle=[each.serialize for each in catsingle])


# This method shows all the items in a particular sport
@app.route('/category/items')
def showitems():
    if request.method == 'GET':
        category_list = session.query(Items).filter_by(sports_id=1).all()
    return render_template('showsportitems.html', categories=category_list)


# This method gives the details of the item
@app.route(
    '/category/<int:category_id>/items/<int:itemid>',
    methods=['GET', 'POST']
    )
def sportitemdetails(category_id, itemid):
    if request.method == 'GET':
        item = session.query(Items).filter_by(
            sports_id=category_id,
            item_id=itemid
            ).one_or_none()
        return render_template(
            'item_details.html',
            Sname=item.item_name,
            Sprice=item.item_price,
            Sbrand=item.item_brand,
            Simage=item.item_image,
            )


# method editing the wearing items
@app.route(
    '/category/<int:categoryid>/items/<int:itemid>/edit',
    methods=['GET', 'POST']
    )
def editsportitem(categoryid, itemid):
    if 'email' not in login_session:
        flash("You Must Login!!!!")
        return redirect(url_for('login'))

    admin = session.query(Admin).filter_by(
        admin_mail=login_session['email']
        ).one_or_none()
    if admin is None:
        flash("Not A Valid User")
        return redirect(url_for('home'))

    categoryname = session.query(Sports).filter_by(
        sports_id=categoryid
        ).one_or_none()
    if not categoryname:
        flash('Sorry! Category not found')
        return redirect(url_for('home'))

    item = session.query(Items).filter_by(
        item_id=itemid,
        sports_id=categoryid
        ).one_or_none()
    if not item:
        flash('Item invalid,Please check the name!!')
        return redirect(url_for('home'))

    login_admin_id = admin.admin_id
    admin_id = categoryname.sports_admin

    if login_admin_id != admin_id:
        flash('Sorry! You are not authorized to edit')
        return redirect(url_for('home'))
    if request.method == 'POST':
        name = request.form['Sname']
        image = request.form['Simage']
        price = request.form['Sprice']
        brand = request.form['Sbrand']
        item = session.query(Items).filter_by(
            sports_id=categoryid,
            item_id=itemid
            ).one_or_none()
        if item:
            item.item_name = name
            item.item_image = image
            item.item_price = price
            item.item_brand = brand
        else:
            flash('Sorry! no items found')
            return redirect(url_for('home'))
        session.add(item)
        session.commit()
        flash('Hurray!! Succesfully Updated')
        return redirect(url_for('home'))
    else:
        edit = session.query(Items).filter_by(item_id=itemid).one_or_none()
        if edit:
            return render_template(
                'edit_item.html',
                Sname=edit.item_name,
                Sprice=edit.item_price,
                Sbrand=edit.item_brand,
                Simage=edit.item_image,
                catid=categoryid,
                Sid=itemid)
        else:
            return 'no items'


# deletes the wear item
@app.route('/category/<int:categoryid>/items/<int:itemid>/delete')
def deletesportitem(categoryid, itemid):
    if 'email' not in login_session:
        flash("You Must Login")
        return redirect(url_for('login'))
    admin = session.query(Admin).filter_by(
        admin_mail=login_session['email']
        ).one_or_none()
    if admin is None:
        flash("Not a Valid User")
        return redirect(url_for('home'))

    categoryname = session.query(Sports).filter_by(
        sports_id=categoryid
        ).one_or_none()
    if not categoryname:
        flash('Sorry!! Category not found')
        return redirect(url_for('home'))

    item = session.query(Items).filter_by(
        sports_id=categoryid,
        item_id=itemid
        ).one_or_none()
    if not item:
        flash('Sorry! Invalid item')
        return redirect(url_for('home'))

    login_admin_id = admin.admin_id
    admin_id = categoryname.sports_admin

    if login_admin_id != admin_id:
        flash('Sorry! You are not authorized to delete this item')
        return redirect(url_for('home'))
    item = session.query(Items).filter_by(
        sports_id=categoryid, item_id=itemid).one_or_none()
    if item:
        name = item.item_name
        session.delete(item)
        session.commit()
        flash('Hurray!! Successfully deleted '+str(name))
        return redirect(url_for('home'))
    else:
        flash('Sorry!! Item Not found')
        return redirect(url_for('home'))


# Shows the categories of sport items
@app.route('/category/<int:category_id>/items')
def showcatitems(category_id):
    if request.method == 'GET':
        items = session.query(Items).filter_by(sports_id=category_id).all()
        if len(items) == 0:
            flash('Sorry! No Items Found ')
        return render_template(
            'showsportitems.html', Items=items, category_id=category_id)


# Add new item of wear
@app.route('/category/<int:categoryid>/items/new', methods=['GET', 'POST'])
def newsportitem(categoryid):
    if 'email' not in login_session:
        flash("You Must Login!!")
        return redirect(url_for('login'))

    admin = session.query(Admin).filter_by(
        admin_mail=login_session['email']
        ).one_or_none()
    if admin is None:
        flash("Sorry!! User Not Valid")
        return redirect(url_for('home'))

    categoryname = session.query(Sports).filter_by(
        sports_id=categoryid
        ).one_or_none()
    if not categoryname:
        flash('Sorry,Category Not Found')
        return redirect(url_for('home'))

    login_admin_id = admin.admin_id
    admin_id = categoryname.sports_admin
    if (login_admin_id != admin_id):
        flash('Sorry! You are not authorized to add item')
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('addsportitem.html', cat_id=categoryid)
    else:
        name = request.form['Sname']
        image = request.form['Simage']
        price = request.form['Sprice']
        brand = request.form['Sbrand']
        sid = categoryid
        new_item = Items(
            item_name=name,
            item_price=price,
            item_brand=brand,
            item_image=image,
            sports_id=sid
            )
        session.add(new_item)
        session.commit()
        flash('Hurray!!!Item added Successfully')
        return redirect(url_for('home'))


# Routing for login
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# llogin and displaying flash profile


# GConnect
@app.route('/gconnect', methods=['POST', 'GET'])
def gConnect():
    if request.args.get('state') != login_session['state']:
        response.make_response(json.dumps('Invalid State paramenter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    request.get_data()
    code = request.data.decode('utf-8')

# Obtaining code authorization

    try:
        # Upgrading the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps("""Failed to upgrade the authorisation code"""), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
#  Check the validation of access token

    access_token = credentials.access_token
    myurl = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    header = httplib2.Http()
    result = json.loads(header.request(myurl, 'GET')[1].decode('utf-8'))

    # If there is an error in the access token info, then it should be abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify whether the access token is used for the intended user or not.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps(
                            """Token's user ID does not
                            match given user ID."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app or not.

    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            """Token's client ID
            does not match app's."""),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for future use.

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'
            ), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Getting the user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # It add provider to login session

    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    admin_id = userID(login_session['email'])
    if not admin_id:
        admin_id = createNewUser(login_session)
    login_session['admin_id'] = admin_id
    flash("Successfully Logged In %s" % login_session['email'])
    return "Verified Successfully"


# when new user enters
def createNewUser(login_session):
    email = login_session['email']
    newAdmin = Admin(admin_mail=email)
    session.add(newAdmin)
    session.commit()
    admin = session.query(Admin).filter_by(admin_mail=email).first()
    admin_Id = admin.admin_id
    return admin_Id


def userID(admin_mail):
    try:
        admin = session.query(Admin).filter_by(admin_mail=admin_mail).one()
        return admin.admin_id
    except Exception as e:
        print(e)
        return None


# Gdisconnect- disconnects a connected user
@app.route('/gdisconnect')
def gdisconnect():
    # It will only disconnect a connected user.
    del login_session['email']
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected'
            ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    header = httplib2.Http()
    result = header.request(url, 'GET')[0]

    if result['status'] == '200':

        # Resetting user's session.

        del login_session['access_token']
        del login_session['gplus_id']
        response = redirect(url_for('home'))
        response.headers['Content-Type'] = 'application/json'
        flash("Signed Out Successfully,Thankyou", "success")
        return response
    else:

        # If given token is invalid, unable  revoke token
        response = make_response(json.dumps(
            ' It has failed to revoke token for user'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response


# method for logout
@app.route('/logout')
def logout():
    if login_session.get('email', None):
        gdisconnect()
        return redirect(url_for('home'))
    flash('Already Logged out!!')
    return redirect(url_for('home'))


@app.context_processor
def inject_all():
    category = session.query(Sports).all()
    return dict(mycategories=category)


if __name__ == '__main__':
    app.secret_key = "Irshad"
    app.run(host="localhost", port=5000)
