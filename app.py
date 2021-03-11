from model.strategies.tradingstrategy import TradingStrategy
from model.httperrors import BadParametersError, BotNotFoundError, HttpError, TokenNotFoundError
import sys
from model.user import User
from os import error
import flask
from flask.helpers import make_response
from flask.json import jsonify
from werkzeug.utils import redirect
from model.exchange.fakebinance import FakeBinance
import time
from model.strategies import gridtrading
import model.config as config
import model.args as args
import model.utils as utils
from flask import Flask, request
import jwt
import model.userrepo as userrepo
import hashlib
import datetime
import http
import model.logger as logger
from model.bot import Bot

# exchange = FakeBinance()
# strategy = gridtrading.GridTrading(args.ARGS.inversion, args.ARGS.range / 100, args.ARGS.levels, exchange, starting_price=args.ARGS.starting_price)

# def run_strategy():
#     try:
#         while True:
#             time.sleep(config.STEP_FREQUENCY * 60)
#             strategy.update()
#             if strategy.should_exit():
#                 break
#     except BaseException as e:
#         strategy.on_exit()
#         utils.raise_exception(e)

# run_strategy()

app = Flask(__name__)

@app.errorhandler(jwt.InvalidTokenError)
def on_invalid_token(e):
    return make_response("Invalid credentials", http.HTTPStatus.UNAUTHORIZED)

@app.errorhandler(HttpError)
def on_token_not_found(e: HttpError):
    return make_response(str(e), e.code)


def get_user_from_token() -> User:
    if "token" in request.cookies:
        token = request.cookies.get("token")
        token_data = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=["HS256"])
        username = token_data["username"]
        return userrepo.get_by_user(username)
    else:
        raise TokenNotFoundError()


@app.route("/test")
def test():
    return "Hello world!"


@app.route("/users", methods=["POST"])
def create_user():
    if not all(key in request.json for key in ["username", "password"]):
        raise BadParametersError()

    username = request.json["username"]
    password = request.json["password"]
    userrepo.add(User(username, hashlib.sha256(password.encode()).hexdigest()))
    return make_response("User successfuly created!")


@app.route("/token", methods=["POST"])
def login():
    response = make_response("Invalid credentials", http.HTTPStatus.UNAUTHORIZED)

    auth = request.authorization
    user = userrepo.get_by_user(auth.username)
    password_hash = hashlib.sha256(auth.password.encode()).hexdigest()

    if user and user.password_hash == password_hash:
        token = jwt.encode({"username" : user.username, "exp" : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, config.JWT_SECRET_KEY)
        response = make_response("Login successfull!")
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
    return jsonify(all_bots)


@app.route("/bots", methods=["POST"])
def create_bot():
    """
    {
        "inversion",
        "range",
        "levels",
        "starting_price" (optional)
    }
    """
    if not all(key in request.json for key in ["inversion", "range", "levels"]):
        raise BadParametersError()

    data = request.json

    try:
        inversion = float(data["inversion"])
        range = float(data["range"])
        levels = int(data["levels"])
        starting_price = float(data["starting_price"]) if "starting_price" in data else None
    except ValueError:
        raise BadParametersError()

    strategy = gridtrading.GridTrading(inversion, range, levels, FakeBinance(), starting_price=starting_price)
    bot = Bot(strategy)
    
    get_user_from_token().register_bot(bot)
    return make_response("Bot created successfully!")


@app.route("/bots/<int:bot_id>")
def bot(bot_id):
    bot: Bot = get_user_from_token().get_bot_by_id(bot_id)
    if not bot:
        raise BotNotFoundError()
    
    return jsonify(bot.dto())


@app.route("/bots/<int:bot_id>", methods=["DELETE"])
def stop_bot(bot_id):
    bot: Bot = get_user_from_token().get_bot_by_id(bot_id)
    if not bot:
        raise BotNotFoundError()
    
    bot.stop()
    return make_response("Bot stopped successfully!")