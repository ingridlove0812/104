import os
import pandas as pd, numpy as np
from w3lib.html import remove_tags, replace_entities
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import jieba_fast as jieba
from collections import defaultdict,Counter
from gensim import corpora,models,similarities
import re
from sklearn.metrics.pairwise import cosine_similarity as cs
import urllib.request
import time
import array as ar
path = 'C:/Users/lailai_tvbs/D/104/'


def getHtml(url):
    hds = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'}
    page1 = urllib.request.Request(url, headers = hds)
    page = urllib.request.urlopen(page1)
    html=page.read()
    return html


def content_clean(content_7):
    tStart = time.time()
    #去除html標記和encode標點符號
    content_tmp = content_7['title'] + content_7['content']
    clean_content = content_tmp.apply(lambda x : ' '.join(remove_tags(replace_entities(x)).split('\n')))
    #將所有英文轉小寫
    clean_content = clean_content.apply(lambda x : np.char.upper(x))
    #匯入停用詞名單
    stopwords = open("stopwords.txt").read().split()
    #用結巴斷詞
    jieba_content = clean_content.apply(lambda x : [w for w in jieba.cut(x) if len(w) > 1 and re.compile(r"[A-Z\u4e00-\u9fa5]").findall(w)])
    jieba_remove = jieba_content.apply(lambda x : [w for w in x if w not in stopwords])
    #將剩下詞組依文章貼回去
    new_content= jieba_remove.apply(lambda x : ' '.join(x))
    content_7.loc[:,'new_content'] = new_content
    tEnd = time.time()
    print ("new_content  -->  runtime : " + str(round((tEnd - tStart)/60,2)) + ' min')
    return content_7#.drop(columns = ['title', 'content'])


def content_clean_post(text):
    tStart = time.time()
    #去除html標記和encode標點符號
    clean_content = ' '.join(remove_tags(replace_entities(text)).split('\n'))
    #將所有英文轉小寫
    clean_content = str(np.char.upper(clean_content))
    #匯入停用詞名單
    stopwords = open("stopwords.txt").read().split()
    #用結巴斷詞
    jieba_content = [w for w in jieba.cut(clean_content) if len(w) > 1 and re.compile(r"[A-Z\u4e00-\u9fa5]").findall(w)]
    jieba_remove = [w for w in jieba_content if w not in stopwords]
    return jieba_remove
    tEnd = time.time()
    print ("new_content  -->  runtime : " + str(round((tEnd - tStart)/60,2)) + ' min')


def tfidf_generate(new_content):
    tStart = time.time()
    #把所有慈整理起來
    documents = new_content
    #把詞切成list
    texts = [[word for word in document.split()] for document in documents]
    #計算總詞頻
    frequency = defaultdict(int)
    for text in texts:
        for word in text:
            frequency[word]+=1
    #將總辭頻前10000挑出來
    texts_top = [i[0] for i in sorted(frequency.items(), key=lambda x:-x[1])[:5000]]
    #將總辭頻低於10的詞拿掉
    texts = [[word for word in text if word in texts_top] for text in texts]
    #建立文本的總詞庫
    dictionary = corpora.Dictionary(texts)
    #將詞庫轉矩陣
    corpus = [dictionary.doc2bow(text) for text in texts]
    #將新的詞庫矩陣算出tfidf
    tfidf = models.TfidfModel(corpus)
    #找出詞庫個數
    featurenum = len(dictionary.token2id.keys())
    #利用詞庫矩陣建立相關索引
    corr = similarities.SparseMatrixSimilarity(tfidf[corpus],num_features=featurenum)
    tEnd = time.time()
    print ("tfidf  -->  runtime : " + str(round((tEnd - tStart)/60,2)) + ' min')
    return dictionary,tfidf,corr


def get_similarity_values_tfidf(dictionary,tfidf,corr,new_content,new_content_all,pid):
#    dictionary = dict_earth; tfidf = tfidf_earth; corr = corr_earth; new_content = new_content_earth
#    tStart = time.time()
    for i in new_content['question_id']:
        vec = dictionary.doc2bow(new_content[new_content['question_id'] == i]['new_content'].to_string(index=False).split(' ')[1:])
        tmp = pd.DataFrame(corr[tfidf[vec]]).sort_values(by = 0, ascending = False)[1:7]
        new_content.loc[new_content[new_content['question_id'] == i].index,'recommendation_list'] = ','.join(list(new_content_all.loc[list(tmp.index),'question_id'].astype(str)))
    result = new_content[['question_id', 'recommendation_list']]
    result.loc[:,'pid'] = pid
#    tEnd = time.time()
#    print ("recommendation_list  -->  runtime : " + str(round((tEnd - tStart)/60,2)) + ' min')
    return result


def get_similarity_values_tfidf_post(dictionary,tfidf,corr,text,new_content_all):
#    dictionary = dict_earth; tfidf = tfidf_earth; corr = corr_earth; new_content = new_content_earth
    tStart = time.time()
    vec = dictionary.doc2bow(content_clean_post(text))
    tmp = pd.DataFrame(corr[tfidf[vec]]).sort_values(by = 0, ascending = False)[2:8]
    return ','.join(list(new_content_all.loc[list(tmp.index),'question_id'].astype(str)))
#    delete_tuple_insert_data('RS_Recommend_List', result)
    tEnd = time.time()
    print ("recommendation_list  -->  runtime : " + str(round((tEnd - tStart)/60,2)) + ' min')


def tmp_save(filename,data):
    global path
    tStart = time.time()
    data.to_parquet(path + filename + ".gzip", engine='pyarrow', compression = 'gzip')
    tEnd = time.time()
    print ("tmp_save  -->  runtime : " + str(round((tEnd - tStart)/60,2)) + ' min')


def tmp_read(filename):
    global path
    tStart = time.time()
    tmp = pd.read_parquet(path + filename + ".gzip", engine='fastparquet')
    tEnd = time.time()
    print ("tmp_read  -->  runtime : " + str(round((tEnd - tStart)/60,2)) + ' min')
    return tmp

#每天半夜進行全部問題推薦的更新
def daily_update():
    global path
    #匯入資料
    df = pd.read_csv(path + 'giver_question_behaviors_for_exam.csv', encoding = 'utf8')
    df1 = pd.read_csv(path + 'giver_questions_for_exam.csv', encoding = 'utf8')
    df1.loc[df1[df1['title'].isnull()].index.tolist(),'title'] = ''
    df1.loc[df1[df1['content'].isnull()].index.tolist(),'content'] = ''
    #將新文章進行斷詞和原本的斷詞結果合併
    content_old = tmp_read('content_all')
    content_new = df1[~df1['question_id'].isin(content_old['question_id'])]
    content_all = pd.concat([content_old, content_clean(content_new)])
    tmp_save('content_all',content_all)
    #建立tfidf
    dictionary,tfidf,corr = tfidf_generate(content_all['new_content'])
    final_result = pd.DataFrame(columns = ['question_id', 'recommendation_list', 'pid'])
    #針對不同使用者進行文章推薦，這裡在get_similarity_values_tfidf應該要再多一步，給出推監名單之前先篩選出特地使用者互動過的相關問題
    tStart = time.time()
    for pid in list(set(df['pid'])):
        content_sub = content_all[content_all['question_id'].isin(df.loc[df['pid'] == pid,'question_id'])]
        result = get_similarity_values_tfidf(dictionary,tfidf,corr,content_sub,content_all, pid)
        final_result = final_result.append(result, ignore_index = True)
    tEnd = time.time()
    print ("recommendation_list  -->  runtime : " + str(round((tEnd - tStart)/60,2)) + ' min')
    return final_result


#使用者新增問題的當下自動推出的推薦
def post_update(pid, text):
    global path
    #匯入資料
    df = pd.read_csv(path + 'giver_question_behaviors_for_exam.csv', encoding = 'utf8')
    df1 = pd.read_csv(path + 'giver_questions_for_exam.csv', encoding = 'utf8')
    df1.loc[df1[df1['title'].isnull()].index.tolist(),'title'] = ''
    df1.loc[df1[df1['content'].isnull()].index.tolist(),'content'] = ''
    #將新文章進行斷詞和原本的斷詞結果合併
    content_old = tmp_read('content_all')
    content_new = df1[~df1['question_id'].isin(content_old['question_id'])]
    content_all = pd.concat([content_old, content_clean(content_new)])
    tmp_save('content_all',content_all)
    #建立tfidf
    dictionary,tfidf,corr = tfidf_generate(content_all['new_content'])
    #針對不同使用者進行文章推薦，這裡在get_similarity_values_tfidf應該要再多一步，給出推監名單之前先篩選出特地使用者互動過的相關問題
    result = get_similarity_values_tfidf_post(dictionary,tfidf,corr,text,content_all)
    return result
