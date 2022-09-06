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


#Run all start of application
#db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks")
def get_drinks():

    drinksList = Drink.query.order_by(Drink.id).all()
    drinks = [drink.short() for drink in drinksList]

    if len(drinks) == 0:
        abort(404)

    return jsonify(
        {
            "success": True,
            "drinks": drinks,
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
@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def get_drinks_detail():

    drinksList = Drink.query.order_by(Drink.id).all()
    drinks_with_detail = [drink.long() for drink in drinksList]

    if len(drinks_with_detail) == 0:
        abort(404)

    return jsonify(
        {
            "success": True,
            "drinks": drinks_with_detail,
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
@app.route("/drinks", methods=["POST"])
@requires_auth('post:drinks')
def create_drink():

    body = request.get_json()

    if body is None or len(body.keys()) < 1:
        abort(400)

    if "title" and "recipe" not in body:
        abort(400)

    try:
        new_title = body.get("title", None)
        new_recipe = body.get("recipe", None)

        json_recipe = json.dumps([new_recipe])

        drink = Drink(title=new_title, recipe=json_recipe)
        drink.insert()

        return jsonify(
            {
            "success": True,
            "drinks": [drink.long()],
            }
        )
    
    except:
        abort(422)


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
@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink(id):

    body = request.get_json()

    if body is None or len(body.keys()) < 1:
        abort(400)

    if "title" not in body:
        abort(400)

    new_title = body.get("title", None)

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)
    try:
        drink.title = new_title
        drink.update()

        return jsonify(
            {
            "success": True,
            "drinks": [drink.long()],
            }
        )

    except:
        abort(422)

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

@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(id):

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)

    try:
        drink.delete()

        return jsonify(
            {
            "success": True,
            "deleted": id,
            }
        )

    except:
        abort(422)




'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def bad_request(ex):

    authResp = ex.error
    authStatusCode = ex.status_code

    return jsonify({"success": False, "error": authStatusCode, "message": authResp['description']}), authStatusCode


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404, "message": "resource not found"}),
        404,
    )

@app.errorhandler(422)
def unprocessable(error):
    return (
        jsonify({"success": False, "error": 422, "message": "unprocessable"}),
        422,
    )

@app.errorhandler(500)
def bad_request(error):
    return jsonify({"success": False, "error": 500, "message": "Internal Server Error"}), 500



if __name__ == "__main__":
    app.debug = True
    app.run()
