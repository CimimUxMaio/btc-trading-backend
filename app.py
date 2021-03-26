import model.pricehandler as pricehandler
from model.httperrors import BadParametersError, BotNotFoundError, HttpError, TokenNotFoundError, BotStillRunningError
from model.user import User
from flask.helpers import make_response
from flask.json import jsonify
from model.exchange.fakebinance import FakeBinance
from model.strategies.gridtrading.builder import GridTradingBuilder
import model.config as config
from flask import Flask, request
import jwt
import model.userrepo as userrepo
import hashlib
import datetime
import http
from model.bot import Bot
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

def make_response_message(message, code=http.HTTPStatus.OK):
    return make_response(jsonify({ "message": message }), code)

def generate_token(username):
    return jwt.encode({"username" : username, "exp" : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, config.JWT_SECRET_KEY)

@app.errorhandler(jwt.InvalidTokenError)
def on_invalid_token(e):
    return make_response_message("Invalid credentials", http.HTTPStatus.UNAUTHORIZED)

@app.errorhandler(HttpError)
def on_token_not_found(e: HttpError):
    return make_response_message(str(e), e.code)


def get_user_from_token() -> User:
    if "token" in request.cookies:
        token = request.cookies.get("token")
    elif "token" in request.args:
        token = request.args.get("token")
    else:
        raise TokenNotFoundError()

    token_data = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=["HS256"])
    username = token_data["username"]
    return userrepo.get_by_email(username)


@app.route("/price")
def current_price():
    return make_response(jsonify({"price": pricehandler.INSTANCE.peek_price()}))


@app.route("/users", methods=["POST"])
def create_user():
    if not all(key in request.json for key in ["username", "password"]):
        raise BadParametersError()

    email = request.json["username"]
    password = request.json["password"]

    userrepo.add(User(email, hashlib.sha256(password.encode()).hexdigest()))
    return make_response_message("User successfuly created!")


@app.route("/token", methods=["POST"])
def login():
    response = make_response_message("Invalid credentials", http.HTTPStatus.UNAUTHORIZED)

    auth = request.authorization
    if not auth:
        raise BadParametersError()
    
    user = userrepo.get_by_email(auth.username)
    password_hash = hashlib.sha256(auth.password.encode()).hexdigest()

    if user and user.password_hash == password_hash:
        token = generate_token(user.email)
        response = make_response(jsonify({"token": token}))
        response.set_cookie("token", token)

    return response


@app.route("/token", methods=["DELETE"])
def logout():
    response = make_response("Logout successfull!")
    response.delete_cookie("token")
    return response


@app.route("/bots")
def bots():
    all_bots = [bot.dto() for bot in get_user_from_token().active_bots]
    return make_response(jsonify(all_bots))


@app.route("/bots", methods=["POST"])
def create_bot():
    """
    {
        "inversion",
        "range",
        "levels",
        "startingPrice" (optional)
    }
    """
    if not all(key in request.json for key in ["inversion", "range", "levels"]):
        raise BadParametersError()

    data = request.json

    try:
        inversion = float(data["inversion"])
        range = float(data["range"])
        levels = int(data["levels"])
        starting_price = float(data["startingPrice"]) if "startingPrice" in data else pricehandler.INSTANCE.peek_price()
        name = data["name"] if "name" in data else None
    except ValueError:
        raise BadParametersError()

    builder = GridTradingBuilder()
    builder.set_config(inversion, range, levels, starting_price)
    builder.set_exchange_config(FakeBinance(), pricehandler.INSTANCE)

    strategy = builder.build()
    get_user_from_token().register_bot(strategy, name)

    return make_response_message("Bot created successfully!")

def get_bot_or_error(bot_id):
    bot: Bot = get_user_from_token().get_bot_by_id(bot_id)
    if not bot:
        raise BotNotFoundError()
    
    return bot


@app.route("/bots/<int:bot_id>")
def bot(bot_id):
    bot = get_bot_or_error(bot_id)
    return make_response(jsonify(bot.dto()))


@app.route("/bots/<int:bot_id>", methods=["PUT"])
def stop_bot(bot_id):
    bot = get_bot_or_error(bot_id)    
    bot.stop()
    return make_response_message("Bot stopped successfully!")

@app.route("/bots/<int:bot_id>", methods=["DELETE"])
def delete_bot(bot_id):
    bot = get_bot_or_error(bot_id)
    if not bot.is_terminated():
        raise BotStillRunningError()

    get_user_from_token().unregister_bot(bot_id)
    return make_response_message("Bot unregistered successfully!")


if __name__ == "__main__":
    pricehandler.start_instance()
    app.run()
