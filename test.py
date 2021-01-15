# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 10:54:53 2021

@author: lailai_tvbs
"""


import pandas as pd
import time
from recom import getHtml
import requests
from flask_batch.client import Batching
import json

#post
url = 'http://34.80.91.60:8000/post_recommend'
myobj = {'pid' : """1dcb10b2-4b5e-42cb-b4cb-58a9094825df""",
        'text' : """"我在傳產工作很久了，被輪調了許多單位，整間公司都單位幾乎都去過,好像人家所謂的跑龍套，現在28歲了，也迷茫了，目前在鈑金業，當初選擇是因為離家近，然後配合缺工獎勵金，加班費，後來覺得現場人員取代性高，和起薪低，靠加班。
28歲想再次轉換跑道，不限職業.地點.行業
因為家人和個人狀態都可以往其他縣市，甚至外地發展都可以接受，隨組織派遣
只要公司肯給員工  肯教育員工 可照顧員工 我都願意
(沒有第二外語能力)

求學與就業經歷:

     高中就讀台中高工機械科,半工半讀在大甲誠岱機械廠（起重機械產品-俗稱天車）現場單位工作3年

      大學就讀國立勤益科技大學企管系.在誠岱公司管理部實習協辦3年，1年支援國內業務部，對於各單位工作之流程皆能熟悉概況。

     退伍後繼續回誠岱公司任職.生產管理專員2年。

    108年3月至明昌國際公司（工具箱產品)先在板金課沖床組，109年4月調到點焊課，因應工作需求，也會到其它廠區（大發.大馬.水美.幼獅）/部門（板金.點焊.塗裝.裝配.倉庫）工作站支援 。     -在職中-

做好自我約束管理，天道酬勤。
人生一切難題，知識給你答案。
策劃-決策-嘗試-修正
1.人是容易懶惰安逸的，務必時時刻刻修正自己，保持自律，自律就是自由。
2.敬業樂群，以廠為家，跟隨組織成長，與時俱進。
"""}
tStart = time.time()
#return_post(text)
x = requests.post(url, json = myobj)
print(x.text)
tEnd = time.time()
print ("content  -->  runtime : " + str(tEnd - tStart) + ' sec')

#get
tStart = time.time()
full = pd.read_json(getHtml('http://34.80.91.60:8000/recommend_list'))
tEnd = time.time()
print ("content  -->  runtime : " + str(tEnd - tStart) + ' sec')
