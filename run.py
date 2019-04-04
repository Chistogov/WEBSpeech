# -*- coding: utf-8 -*-
import sys

from userApp import userApp

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    userApp.run(debug=True)
