import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink,db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# CORS Headers
@app.after_request
def after_request(response):
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
    )
    response.headers.add(
        "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
    )
    return response

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()



# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks/",endpoint='drinks')
@requires_auth('get:drinks')
def drinks(payload):
    
    try:
        drinks = db.session.query(Drink)
        drinks = [drink.short() for drink in drinks]
    except:
        abort(404)   

    if len(drinks) == 0:
        abort(404)

    return jsonify(       
        {
            "success": True, 
            "drinks": drinks
        }
    )


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks-detail/", endpoint='drinks_detail')
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    try:
        drinks = db.session.query(Drink)
        drinks = [drink.long() for drink in drinks]      
    except:
        abort(404)

    if len(drinks) == 0:
        abort(404)

    return jsonify(       
        {
            "success": True, 
            "drinks": drinks
        }
    )


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/",endpoint='post_drink', methods=["POST"])
@requires_auth('post:drinks')
def post_drink(payload):
    try:
        #data = request.json
        data = request.get_json()
        #drink = Drink(title=data['title'], recipe=json.dumps(data['recipe']))
        drink = Drink(title=data.get("title", None), recipe=json.dumps(data.get("recipe", None)))

        drink.insert()

        drink = [drink.long()]
    except:
        abort(404)

    return jsonify({"success": True, "drinks": drink})


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
@app.route("/drinks/<id>",endpoint='update_drink', methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink(payload,id=None):
    try:
        data = request.json
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        drink.title = data['title']
        drink.update()

        drink = [drink.long()]
    except:
        abort(404)

    return jsonify({"success": True, "drinks": drink})


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
@app.route("/drinks/<id>",endpoint='delete_drink', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(payload,id=None):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        drink.delete()
    except:
        abort(404)
    #drink = [drink.long()]
  
    return jsonify({"success": True, "delete": drink.id})



# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(401)
def unauthourized(error):
    return jsonify({
        "success": False, 
        "error": 403,
        "message": "unauthorized"
        }), 403

@app.errorhandler(403)
def unauth(error):
    return jsonify({
        "success": False, 
        "error": 403,
        "message": "forbidden"
        }), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
        }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
        }), 422

@app.errorhandler(405)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 405,
        "message": "method not allowed"
        }), 405
@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "bad request"
        }), 400




'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def auth_error(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response
  