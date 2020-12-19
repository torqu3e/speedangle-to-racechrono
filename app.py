from os import environ
from flask import Flask
from flask_restful import Api
from resources import SourceFile


app = Flask(__name__)
# app.config["PROPAGATE_EXCEPTIONS"] = True


api = Api(app)

api.add_resource(SourceFile, "/")

if __name__ == "__main__":
    app.run(port=environ.get("PORT"))
