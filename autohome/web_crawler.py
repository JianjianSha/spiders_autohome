from urllib import request, parse
import gzip
from bs4 import BeautifulSoup
import re
import time
import json
from tools.dba import mssql_execute, mssql_select
from .car import cardtl, car_join_deduplicate, cardtl_insert_format
from .anti_spider import get_page


def crawl_che168():
    # get checkpoint of crawling
    offset=int(mssql_select("select top 1 cp_val from CarCheckPt where cp_name = 'carcrawlaux'")[0][0])
    # offset = 0
    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'
    }
    url = 'https://pinguapi.che168.com/v1/assesspublic/seriesofrate?_appid=m.m&seriesid=%s&levelid=3&markvalue=&callback=seriesKeepValueCallback'
    def crawl_loop():
        nonlocal offset
        auxs = mssql_select('select top 50 id, src_id from CarCrawlAux where id > %d order by id' % (offset))
        for aux in auxs:
            aurl = url %(aux[1][1:])        # src_id starting with 's' is uid of a car, e.g. 's66'
            req = request.Request(aurl, headers=headers)
            keepvals = []
            try:
                page = request.urlopen(req).read().decode('utf-8')
                page = re.findall("seriesKeepValueCallback\((.+)\)", page)
                if len(page) == 0:
                    continue

                json_ = json.loads(page[0])
                if 'result' not in json_: continue
                results = json_['result']
                for d in results:
                    rate = str(d['keeprate']*100)
                    if '.' in rate:
                        dotidx = rate.index('.')
                        if len(rate)-1-dotidx>2:
                            rate = rate[0:dotidx+3]
                    rate = rate.rstrip('0').rstrip('.')
                    keepvals.append(rate+'%')
                    if len(keepvals)==5: break
                
                # save back to mssql
                mssql_execute("update CarBase set preserve_rate = '%s' where src_id = '%s'"
                    % (','.join(keepvals), aux[1]))
            except Exception as e:
                print('faild: %s'%(aurl), flush=True)
        print(offset, flush=True)
        if len(auxs)>0:
            offset = int(auxs[-1][0])
            return True
        else:
            return False

    while(crawl_loop()):
        mssql_execute("update CarCheckPt set cp_val = %d where cp_name = 'carcrawlaux'" % (offset))

def crawl_config():
    '''crawling the config page of cars'''
    offset=int(mssql_select("select top 1 cp_val from CarCheckPt where cp_name = 'carcrawlaux'")[0][0])
    # offset = 0        # uncomment this line if want to recrawl from the beginning

    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'User-Agent':'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.24 Safari/534.720'
    }

    def crawl_loop():
        def parse_base(items, d):
            for item in items:
                if item['id'] == 567:   # 车型
                    for v in item['valueitems']:
                        cd = cardtl(v['specid'])
                        cd.name=v['value'].strip()
                        d[cd.uid]=cd
                elif item['id'] == 219: # 厂商指导价
                    for v in item['valueitems']:
                        d[v['specid']].guide_price = v['value'].strip()
                elif item['id'] == 218: # 厂商      manufacturer
                    for v in item['valueitems']:
                        d[v['specid']].manufacturer = v['value'].strip()
                elif item['id'] == 220: # 级别      grade
                    for v in item['valueitems']:
                        d[v['specid']].grade = v['value'].strip()
                elif item['name'] == '能源类型':   # 能源类型
                    for v in item['valueitems']:
                        d[v['specid']].energy_type = v['value'].strip()
                elif str(item['name']).startswith('上市'):
                    for v in item['valueitems']:
                        d[v['specid']].ttm = v['value'].strip()
                elif item['id'] == 1185:            # 最大功率 kw
                    for v in item['valueitems']:
                        d[v['specid']].max_power = v['value'].strip()
                elif item['id'] == 1186:            # 最大扭矩 N\cdotm
                    for v in item['valueitems']:
                        d[v['specid']].max_torque = v['value'].strip()
                elif item['id'] == 555:            # 发动机
                    for v in item['valueitems']:
                        d[v['specid']].engine = v['value'].strip()
                elif item['name'] == '变速箱':            # 
                    for v in item['valueitems']:
                        d[v['specid']].gear_box = v['value'].strip()
                elif item['id'] == 222:            # 长宽高
                    for v in item['valueitems']:
                        d[v['specid']].size = v['value'].strip()
                elif item['id'] == 1147:            # 车身结构
                    for v in item['valueitems']:
                        d[v['specid']].structure = v['value'].strip()
                elif item['id'] == 1246:            # 最高车速 km/h
                    for v in item['valueitems']:
                        d[v['specid']].max_speed = v['value'].strip()
                elif item['id'] == 1250:            # 官方百公里加速 0-100 km/h
                    for v in item['valueitems']:
                        d[v['specid']].office_acc_time = v['value'].strip()
                elif item['id'] == 1252:            # 实测百公里加速 0-100 km/h
                    for v in item['valueitems']:
                        d[v['specid']].true_acc_time = v['value'].strip()
                elif item['id'] == 1253:            # 实测百公里制动 100 km/h - 0
                    for v in item['valueitems']:
                        d[v['specid']].true_brake_len = v['value'].strip()
                elif item['id'] == 1251:            # 工信部油耗 L/100km
                    for v in item['valueitems']:
                        d[v['specid']].oil_wear = v['value'].strip()
                
            return d

        def parse_carbox(items, d):
            for item in items:
                if item['id'] == 1172:      # 车门数
                    for v in item['valueitems']:
                        try:
                            d[v['specid']].door_num = int(v['value'].strip())
                        except:
                            d[v['specid']].door_num = -1
                elif item['id'] == 1173:      # 座位数
                    for v in item['valueitems']:
                        try:
                            d[v['specid']].seat_num = int(v['value'].strip())
                        except:
                            d[v['specid']].seat_num = -1
        
        def parse_engine(items, d):
            for item in items:
                if item['id'] == 1182:      # 排量 ml
                    for v in item['valueitems']:
                        d[v['specid']].output_volumn = v['value'].strip()
                elif item['id'] == 1191:      # 汽缸数
                    for v in item['valueitems']:
                        try:
                            d[v['specid']].cylinder_num = int(v['value'].strip())
                        except:
                            d[v['specid']].cylinder_num=-1
                elif item['id'] == 1192:      # 每缸气门数
                    for v in item['valueitems']:
                        try:
                            d[v['specid']].valve_num = int(v['value'].strip())
                        except:
                            d[v['specid']].valve_num = -1
                elif item['id'] == 1294:      # 最大马力 Ps
                    for v in item['valueitems']:
                        d[v['specid']].max_horse = v['value'].strip()  #1294
                # elif item['id'] == 1280:      # 燃料形式
                #     for v in item['valueitems']:
                #         d[v['specid']]. = v['value'].strip()

        def parse_chassis(items, d):
            for item in items:
                if item['id'] == 395:       # 驱动形式  drive_type
                    for v in item['valueitems']:
                        d[v['specid']].drive_type = v['value'].strip()

        nonlocal offset
        # nonlocal headers
        auxs = mssql_select('select top 10 id, src_id, car_name from CarCrawlAux where id > %d order by id' % (offset))
        for aux in auxs:
            time.sleep(0.3)
            aurl = "https://car.autohome.com.cn/config/series/%s.html#pvareaid=3454437" %(aux[1][1:])       # 3170

            req = request.Request(aurl, headers=headers)
            try:
                page = request.urlopen(req).read()
                # page = page.decode('utf-8', 'ignore')
                page = gzip.decompress(page).decode('utf-8')

                page = autohome.get_complete_text_autohome(page)

                config = re.findall('var\s+config\s+=\s+(\{\"message\"\:.+\});',page)
                if len(config)==0: continue

                json_ = json.loads(config[0])
                res = json_['result']
                params = res['paramtypeitems']
                d={}
                for p in params:
                    if p['name'] == '基本参数':
                        parse_base(p['paramitems'], d)
                    elif p['name'] == '车身':
                        parse_carbox(p['paramitems'], d)
                    elif p['name'] == '发动机':
                        parse_engine(p['paramitems'], d)
                    elif p['name'] == '底盘转向':
                        parse_chassis(p['paramitems'], d)
                
                # save to DB
                for k in d:
                    d[k].src_id = aux[1]
                    sql = cardtl_insert_format() % (d[k].cardtl_insert_tuple())
                    mssql_execute(sql)


            except Exception as e:
                print('fail', aurl, e)
                return False

        if len(auxs) > 0:
            offset = int(auxs[-1][0])
            print('offset ', offset, flush=True)
            return True
        else:
            return False

    while(crawl_loop()):
        mssql_execute("update CarCheckPt set cp_val = %d where cp_name = 'carcrawlaux'" % (offset))


if __name__ == '__main__':
    print('crawling start')
    crawl_config()
    print('crawling end')