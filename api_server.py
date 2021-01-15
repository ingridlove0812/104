# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 20:29:42 2021

@author: Ingrid
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 15:04:52 2020

@author: bruceyu1113
"""
from flask import jsonify,request,Flask
from flask_caching import Cache
from random import randint
from datetime import datetime, time,date, timedelta
import pandas as pd
from recom import tmp_save, tmp_read, daily_update, post_update
import os
os.chdir('C:/Users/lailai_tvbs/D/104')
import numpy as np


def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config["JSON_AS_ASCII"] = False
    app.config['CACHE_TYPE']='simple'
    cache = Cache()
    cache.init_app(app)
    @app.route('/')
    @cache.cached(timeout=5)
    def home():
        return f'<h1>104 Recommend API</h1>'


    @app.route('/recommend_list')
    def result():
        minute = datetime.now().minute
        table = cache.get('recommend')
        content = cache.get('news_content_tmp')
        pid = request.args.get('pid', '', type = str)
        question_id = request.args.get('question_id', '', type = str)
        if not table or (minute > 0 and minute <= 5):
#            tmp = daily_update()
#            tmp_save('table',tmp)
            tmp = tmp_read('table')
            table = tmp.to_json(force_ascii=False)
            cache.set('news_content_tmp',content,timeout=86100)
            cache.set('recommend',table,timeout = 86100)
            if pid != '' or question_id != '':
                if pid != '' and question_id == '':
                    filt_tmp = tmp[tmp['pid'] == pid]
                elif pid == '' and question_id != '':
                    filt_tmp = tmp[tmp['question_id'] == question_id]
                else:
                    filt_tmp = tmp[(tmp['pid'] == pid) & (tmp['question_id'] == question_id)]
                filt = filt_tmp.to_json(force_ascii=False)
                return filt
            else:
                return table
        else:
            if pid != '' and question_id != '':
                if pid != '' and question_id == '':
                    filt_tmp = tmp[tmp['pid'] == pid]
                elif pid == '' and question_id != '':
                    filt_tmp = tmp[tmp['question_id'] == question_id]
                else:
                    filt_tmp = tmp[(tmp['pid'] == pid) & (tmp['question_id'] == question_id)
                filt = filt_tmp.to_json(force_ascii=False)
                return filt
            else:
                return table


   
    @app.route('/post_recommend',methods=['POST'])
    def return_recommend():
        temp_json = request.get_json(force=True)
        recommend_list = post_update(temp_json['pid'],temp_json['text'])
        return jsonify(recommend_list)


    @app.errorhandler(404)
    def not_found(error=None):
        message={
                'status':404,
                'message': 'Not Found ' + request.url
                }
        resp = jsonify(message)
        resp.status_code = 404
        return resp
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5050,debug=True, use_reloader=False)
