# -*- coding: UTF-8 -*-
import sys
import requests
import threading
import datetime

import common.setting as dl_setting
import untils.setting as untils_setting

def Handler(start, end, url, filename):
    headers = {'Range': 'bytes=%d-%d' % (start, end)}
    r = requests.get(url, headers=headers, stream=True,timeout=5)
    # 写入文件对应位置
    with open(filename, "r+b") as fp:
        fp.seek(start)
        var = fp.tell()
        fp.write(r.content)
        
def download_file(url, num_thread = 10):
    r = requests.head(url)
    try:
        file_name = url.split('/')[-1]
        file_size = int(r.headers['content-length'])   # Content-Length获得文件主体的大小，当http服务器使用Connection:keep-alive时，不支持Content-Length
    except:
        print("检查URL，或不支持对线程下载")
        return
    #  创建一个和要下载文件一样大小的文件
    fp = open(file_name, "wb")
    fp.truncate(file_size)
    fp.close()
    # 启动多线程写文件
    part = file_size // num_thread  
    # 如果不能整除，最后一块应该多几个字节
    for i in range(num_thread):
        start = part * i
        if i == num_thread - 1:   # 最后一块
            end = file_size
        else:
            end = start + part
        t = threading.Thread(target=Handler, kwargs={'start': start, 'end': end, 'url': url, 'filename': file_name})
        t.setDaemon(True)
        t.start()
    # 等待所有线程下载完成
    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()
    print('%s 下载完成' % file_name)
    
def main_dl(url):
    start = datetime.datetime.now().replace(microsecond=0)  
    download_file(url)
    end = datetime.datetime.now().replace(microsecond=0)
    use_time = end-start
    print("用时: ", end='')
    print(use_time)
    return 1

def conn_mongo():
    conn = pymongo.MongoClient('127.0.0.1', 27017)
    return conn

if __name__ == '__main__':
    conn = conn_mongo()
    col = conn['machotube']
    v_info = col.find_one({"dl_res": '0'})
    while v_info.count >0:
        dataid_v = v_info['data_id']
        dl_res = main_dl(v_info['dl_url'])

        if dl_res:
            v_info['dl_res'] == '1'
            col.update_one({"data_id": dataid_v}, {'$set': v_info})
        v_info = col.find_one({"dl_res": '0'})
