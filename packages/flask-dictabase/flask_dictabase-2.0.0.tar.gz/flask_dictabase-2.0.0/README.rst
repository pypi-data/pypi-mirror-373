Flask-Dictabase
===============
A dict() like interface to your database.

Install
=======
::

    pip install flask_dictabase

Here is a simple flask app implementation.
::

    import random
    import string

    from flask import (
        Flask,
        render_template,
        redirect
    )
    import flask_dictabase

    app = Flask('User Management')
    # if you would like to specify the SQLAlchemy database then you can do:
    # app.config['DATABASE_URL'] = 'sqlite:///my.db'
    db = flask_dictabase.Dictabase(app)


    class UserClass(flask_dictabase.BaseTable):
        def CustomMethod(self):
            # You can access the db from within a BaseTable object.
            allUsers = self.db.FindAll(UserClass)
            numOfUsers = len(allUsers)
            print('There are {} total users in the database.'.format(numOfUsers)

            # You can also access the app from within a BaseTable object
            if self.app.config.get('SECRET_KEY', None) is None:
                print('This app has no secret key')

    @app.route('/')
    def Index():
        return render_template(
            'users.html',
            users=db.FindAll(UserClass),
        )


    @app.route('/update_user_uption/<userID>/<state>')
    def UpdateUser(userID, state):
        newState = {'true': True, 'false': False}.get(state.lower(), None)
        user = db.FindOne(UserClass, id=int(userID))
        user['state'] = newState # This is immediately saved to the database.
        return redirect('/')


    @app.route('/new')
    def NewUser():
        email = ''.join([random.choice(string.ascii_letters) for i in range(10)])
        email += '@'
        email += ''.join([random.choice(string.ascii_letters) for i in range(5)])
        email += '.com'

        newUser = db.New(UserClass, email=email, state=bool(random.randint(0, 1)))
        print('newUser=', newUser) # This is now immediately saved to the database.
        return redirect('/')


    @app.route('/delete/<userID>')
    def Delete(userID):
        user = db.FindOne(UserClass, id=int(userID))
        print('user=', user)
        if user:
            db.Delete(user) # User is now removed from the database.
        return redirect('/')


    if __name__ == '__main__':
        app.run(
            debug=True,
            threaded=True,
        )

Unsupported Types / Advanced Usage
==================================
If you want to store more complex information like list() and dict(), you can use the .Set() and .Get() helper methods.
These convert your values to/from json to be stored in the db as a string.

::

    myList = [1,2,3,4,5] #
    user = db.FindOne(UserClass, id=1)
    if user:
        user.Set('myList', myList)

    user2 = db.FindOne(UserClass, id=1)
    print('user2.Get('myList')=', user2.Get('myList'))

Output
::

    >>> user2.Get('myList')= [1, 2, 3, 4, 5]

You can use the helper methods .Append() and .SetItem() to easliy save list() and dict()
::

    user.Append('myList', 9)
    print('user2.Get('myList')=', user2.Get('myList'))

Output
::

    >>> user2.Get('myList')= [1, 2, 3, 4, 5, 9]

You can also use a different function to load/dump the values. Like python's pickle module.
::

    import pickle
    myList = [1,2,3,4,5] #
    user = db.FindOne(UserClass, id=1)
    if user:
        user.Set('myList', myList, dumper=pickle.dumps, dumperKwargs={})

    user2 = db.FindOne(UserClass, id=1)
    print('user2.Get('myList')=', user2.Get('myList', loader=pickle.loads))

You can also provide a default argument to .Get()
::

    user = db.FindOne(UserClass, id=1)
    user.Get('missingKey', None) # return None if key is missing, else return the dumped value

You can also use the methods .Append() .Remove() and .SetItem() and .PopItem() to easily manipulate the info stored as JSON
::

    user = db.FindOne(UserClass, id=1)
    user.Set('animals', ['cat', 'dog', 'bird'])

    print('user.Get("animals")=', user.Get('animals'))
    >>> user.Get("animals")= ['cat', 'dog', 'bird']

    user.Append('animals', 'tiger')
    print('user.Get("animals")=', user.Get('animals'))
    >>> user.Get("animals")= ['cat', 'dog', 'bird', 'tiger']

    user.Remove('animals', 'cat')
    print('user.Get("animals")=', user.Get('animals'))
    >>> user.Get("animals")= ['dog', 'bird', 'tiger']

    user.Set('numOfPets', {'cats': 1, 'dog': 1})
    print('user.Get("numOfPets")=', user.Get('numOfPets'))
    >>> user.Get("numOfPets")= {'cats': 1, 'dog': 1}

    user.SetItem('numOfPets', 'cats', 3)
    print('user.Get("numOfPets")=', user.Get('numOfPets'))
    >>> user.Get("numOfPets")= {'cats': 3, 'dog': 1}

    user.PopItem('numOfPets', 'cats')
    print('user.Get("numOfPets")=', user.Get('numOfPets'))
    >>> user.Get("numOfPets")= {'dog': 1}

Variables
=========
Kind of like Global Variables but stored in the database.
Example::

    db.var.Set('nameOfTheVariable', 'valueOfTheVariable')

    # set/get generic variables
    @app.route('/set/<key>/<value>')
    def Set(key, value):
        db.var.Set(key, value)
        return f'Set {key}={value}'


    @app.route('/get/<key>')
    def Get(key):
        return db.var.Get(key)

Database Relationships
======================

You can link database objects together to easily reference one object from another.
Use the `BaseTable.Link()` and `BaseTable.Unlink()` to create/delete the relationships.
Use `BaseTable.Links()` to iterate through the relationships.

::

    class Player(flask_dictabase.BaseTable):
        pass

    player = app.db.NewOrFind(Player, name='Grant')
    print('player=', player)

    class Card(flask_dictabase.BaseTable):
        pass

    SUITS = ['club', 'spade', 'heart', 'diamond']
    VALUES = ['ace', 'jack', 'queen', 'king'] + [i for i in range(2, 10 + 1)]

    # create all the cards in the database
    for suit in SUITS:
        for value in VALUES:
            # note: NewOrFind() will look in the database for the object,
            # if it doesnt find any, it will create a new object.
            app.db.NewOrFind(Card, suit=suit, value=value)

    # give the player some cards
    for i in range(5):
        suit = random.choice(SUITS)
        value = random.choice(VALUES)

        player.Link(
            app.db.NewOrFind(Card, suit=suit, value=value)
        )

    print('The cards in the players hand are:')
    for card in player.Links(Card):
        print('card=', card)

    print('the player is holding the following cards that are hearts')
    for card in player.Links(Card, suit='heart'):
        print('card=', card)

    for index, obj in enumerate(player.Links(Card)):
        if index % 3 == 0:
            player.Unlink(obj)
            print('player discarded the card=', obj)

    card = app.db.NewOrFind(Card, suit='heart', value='queen')
    for obj in card.Links():
        print('the queen of hearts is held by player=', obj)

    >>>
    player= <Player: id=1(type=int), name=Grant(type=str)>
    The cards in the players hand are:
    card= <Card: id=50(type=int), suit=diamond(type=str), value=8(type=str)>
    card= <Card: id=44(type=int), suit=diamond(type=str), value=2(type=str)>
    card= <Card: id=10(type=int), suit=club(type=str), value=7(type=str)>
    card= <Card: id=24(type=int), suit=spade(type=str), value=8(type=str)>
    card= <Card: id=39(type=int), suit=heart(type=str), value=10(type=str)>
    the player is holding the following cards that are hearts
    card= <Card: id=39(type=int), suit=heart(type=str), value=10(type=str)>
    player discarded the card= <Card: id=50(type=int), suit=diamond(type=str), value=8(type=str)>

Find Rows By Range
==================
You can use the '_where' keyword with '_greaterThan', '_lessThan', '_lessThanOrEqualTo', '_greaterThanOrEqualTo', '_equals'.

::

    users = app.db.FindAll(User, _where='age', _greaterThan=18)
    print('These are the users over age 18:')
    for user in users:
        print(user)

    users = app.db.FindAll(User, _where='age', _greaterThanOrEqualTo=18, _lessThanOrEqualTo=25)
    print('These are the users between age 18 and 25:')
    for user in users:
        print(user)

Gunicorn
========

Supports multiple workers (-w config option).
Example::

    gunicorn main:app -w 4 -b localhost:8080
