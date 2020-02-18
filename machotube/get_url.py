# -*- coding: UTF-8 -*-
import pymongo
import requests
import lxml

import common.setting as dl_setting
import util.setting as untils_setting

machourl = dl_setting.macho_url
mongo_ip = untils_setting.mongo_ip
print(machourl)

def conn_mongo():
    conn = pymongo.MongoClient('127.0.0.1', 27017)
    return conn

conn = conn_mongo()
col = conn['machotube']

def get_ids(searchword, page):
    if searchword == None:
        url = machourl + '/newest?page=%s' % (str(page))
    else:
        url = machourl + '/search/%s/newest?page=%s' % (str(searchword), str(page))
    res1 = requests.request("GET",url)
    selector = etree.HTML(res1.text)
    vlist = selector.xpath('//div[@class="b-thumb-list js-gallery-list"]/div[@class="b-thumb-list__wrap"]/div[@class="b-thumb-item"]')
    #downedlist= ['4294530','4294530','4294530','1288419','5950251','2843962','6360080','1556151','7779463']
    i=0
    for div_i in vlist:
        pid = div_i.xpath('./div/a/@data-position')
        dataid = div_i.xpath('./div/a/@data-galleryid')
        datathumbid = div_i.xpath('./div/a/@data-thumb-id')
        filename = div_i.xpath('./div/a/@title')[0]
        nexturl = "https://www.machotube.tv" + div_i.xpath('./div/a/@href')[0]
        print(nexturl)
        res_i = requests.request("GET",nexturl)
        selector_i = etree.HTML(res_i.text)
        url_i = selector_i.xpath('.//source/@src')[0]
        tag_i = selector_i.xpath('.//div[@class="b-details__list"]/div[@class="b-details__list"]/a')
        tag_list = []
        for tag_j in tag_i:
            tag_list.append(tag_j.xpath('./text()'))
        update_time = selector_i.xpath('div[@class="b-details__list"]/div[@class="b-details__item"]/div[@class="b-details__info"]')[1]
        update_time = update_time.xpath('./span[@class="b-details__text"]/text()')
        print(url_i)
        v_info = {
            "filename": filename,
            "v_url": nexturl,
            "pid": str(pid),
            "data_id": str(dataid),
            "datathumbid": str(datathumbid),
            "dl_url": url_i,
            "dl_res": "0",
            "tag_list": tag_list,
            "update_time": update_time
        }
        col.insert_one(v_info)
    print(str(page), "结束")
