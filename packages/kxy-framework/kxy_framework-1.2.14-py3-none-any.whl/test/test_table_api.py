# !/usr/bin/python
# -*- coding:utf-8 -*-
import re
import traceback

from flask import request,session

from app.api import api
from app import db

from common.result import Result
from common.friendly_exception import FriendlyException
from dto.test_table_dal import TestTableDal
from common.util import Util
from common.auth import user_login_info,auth_module

@api.route("/test_table/list", methods=["GET"])
@user_login_info
@auth_module(module_name="test_table", resource="list")
def test_table_list():
    try:
        PageIndex = int(request.args.get("current", 1))
        PageLimit = int(request.args.get("pageSize", 10))
        
        dal = TestTableDal(session['user']['id'],db.session)
        total,data = dal.Search(request.args,PageIndex, PageLimit)
        return Result.antd_success(Util.formatAntdPageFieldsData(total,data))
    except FriendlyException as fex:
        return Result.friendlyerror(str(fex))
    except Exception as ex:
        return Result.error_msg(traceback.format_exc(limit=1))


@api.route("/test_table/add", methods=["POST"])
@user_login_info
@auth_module(module_name="test_table", resource="add")
def test_table_add():
    try:
        dal = TestTableDal(session['user']['id'],db.session)
        data = dal.AddByJsonData(request.json)
        return Result.success(data.to_basic_dict())
    except FriendlyException as fex:
        return Result.friendlyerror(str(fex))
    except Exception as ex:
        return Result.error_msg(traceback.format_exc(limit=1))

@api.route("/test_table/update", methods=["POST"])
@user_login_info
@auth_module(module_name="test_table", resource="update")
def test_table_update():
    try:
        dal = TestTableDal(session['user']['id'],db.session)
        data = dal.UpdateByJsonData(request.json)
        return Result.success(data.to_basic_dict())
    except FriendlyException as fex:
        return Result.friendlyerror(str(fex))
    except Exception as ex:
        return Result.error_msg(traceback.format_exc(limit=1))

@api.route("/test_table/delete/<int:id>", methods=["GET"])
@user_login_info
@auth_module(module_name="test_table", resource="delete")
def test_table_delete(id):
    try:
        dal = TestTableDal(session['user']['id'],db.session)
        data = dal.Delete(id)
        return Result.success("删除成功")
    except FriendlyException as fex:
        return Result.friendlyerror(str(fex))
    except Exception as ex:
        return Result.error_msg(traceback.format_exc(limit=1))
    
@api.route("/test_table/deletebatch", methods=["POST"])
@user_login_info
@auth_module(module_name="test_table", resource="delete")
def test_table_deletebatch():
    try:
        keys=request.json.get('key')
        if keys:
            dal = TestTableDal(session['user']['id'],db.session)
            dal.deletebatch(keys)
            return Result.success("删除成功")
        else:
            raise FriendlyException('请传入要删除的行')
    except FriendlyException as fex:
        return Result.friendlyerror(str(fex))
    except Exception as ex:
        return Result.error_msg(traceback.format_exc(limit=1))



@api.route("/test_table/get/<int:id>", methods=["GET"])
@user_login_info
@auth_module(module_name="test_table", resource="get")
def test_table_get(id):
    try:
        dal = TestTableDal(session['user']['id'],db.session)
        data = dal.Get(id)
        return Result.success(data.to_basic_dict())
    except FriendlyException as fex:
        return Result.friendlyerror(str(fex))
    except Exception as ex:
        return Result.error_msg(traceback.format_exc(limit=1))
