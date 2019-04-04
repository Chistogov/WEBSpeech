# -*- coding: utf-8 -*-
from flask import Flask
import logging
import sys
from jinja2 import Environment, FileSystemLoader


userApp = Flask(__name__, instance_relative_config=True)

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    userApp.run(debug=False)

# Load the views
from userApp import dependencies
from userApp import calendarController
from userApp import errorController
from userApp import recController
from userApp import indexController
from userApp import configController
from userApp import loginController
from userApp import namesController
from userApp import operationsController
from userApp import Pagination
from userApp import AlchemyEncoder
from userApp import jinjaHelper

from userApp.dbc import *

# Load the config file
userApp.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')
userApp.config.from_object('config')
userApp.secret_key = '2240641'
logging.basicConfig(level = logging.INFO)
db.create_all()

