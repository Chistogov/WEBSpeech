from flask import send_from_directory
from userApp import userApp
import logging
from userApp.dbc import *
from flask_login import login_required, current_user

# @userApp.context_processor
# def example():
#     if(current_user.is_authenticated):
#         usercons = get_user_cons()
#         return dict(count_app=get_count_app(), usercons=usercons, count_sec_app=get_count_sec_app(), count_cnn_app=get_count_cnn_app(), count_tests=get_count_tests())
#     else:
#         return dict(count_app=0)
#
#
# def get_count_tests():
#     user_tests = db.session.query(Tests.Tests).filter(Tests.Tests.user_id == current_user.id,
#                                                       Tests.Tests.results == None)
#     return len(list(user_tests))
#
# def get_count_cnn_app():
#     pics_in_wait = Appoint.Appoint\
#         .query.filter_by(user_id=current_user.id, from_cnn=True)
#     return len(list(pics_in_wait))
#
# def get_count_app():
#     pics_in_wait = Appoint.Appoint\
#         .query.filter_by(user_id=current_user.id, secondary=False, from_cnn=False)
#     return len(list(pics_in_wait))
#
# def get_count_sec_app():
#     pics_in_wait = Appoint.Appoint\
#         .query.filter_by(user_id=current_user.id, secondary=True)
#     print list(pics_in_wait)
#     return len(list(pics_in_wait))
#
# def get_user_cons():
#     usercons = db.session.query(Usercons.Usercons).filter(Usercons.Usercons.user_id == current_user.id,
#                                                                    Usercons.Usercons.manager == True)
#     return usercons