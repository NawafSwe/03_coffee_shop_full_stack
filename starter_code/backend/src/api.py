import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

cors = CORS(app,resources={r"/api/*":{"origins":"*"}})


@app.after_request
def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorizations,true')
        response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
        return response

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
##db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def retrive_drinks():
    drinks = list(map(Drink.short, Drink.query.all()))
    result = {
        'success' : True,
        'drinks': drinks }
    return jsonify(result)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(token):
        drinks = list(map(Drink.long,Drink.query.all()))
        result = {
            'success' :True,
            'drinks' : drinks }
        return jsonify(result)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(token):
    if request.data: 
        new_drink_decoded = json.loads(request.data['title'].decode('utf-8'))
        new_drink = Drink(title=new_drink_decoded['title'],recipe=json.dumps(new_drink_decoded['recipe']))
        new_drink.insert()
        drinks = list(map(Drink.long,Drink.query.all()))
        result={
            'success':True,
            'drink': drinks
            }
        return jsonify(result)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def modiffy_drink(token,id):
            try:
                target_drink = Drink.query.get(id)
                old_drink_decoded = json.loads(request.data.decode('utf-8'))
                if 'title' in  target_drink:
                        setattr( target_drink,'title',old_drink_decoded['title'])
                if 'recipe' in target_drink:
                    setattr(target_drink,'recipe',old_drink_decoded['recipe'])
                target_drink.update()
                drink = list(map(Drink.long,Drink.query.all()))
                result = {
                    'success': True,
                    'drinks': drink }
                return jsonify(result)   
            except:
                abort(404)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token,id):
        try:
            target_drink = Drink.query.get(id)
            target_drink.delete()
            result = {
                    'success':True,
                    'delete': id
            }
            return jsonify(result)
        except: 
            abort(404)
            ## if the drink is not exits

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
        return jsonify({
            'success': False,
            'error':404,
            'message': 'Not Found'

        },404)


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def Auth_Error(e):
     return jsonify(e.error),e.status_code
       
