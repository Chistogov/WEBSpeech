# -*- coding: utf-8 -*-
from flask import redirect
from userApp import userApp


@userApp.errorhandler(401)
def page_not_found(e):
    return redirect("/login")

# @userApp.errorhandler(404)
# def page_not_found(e):
#     return redirect("/")