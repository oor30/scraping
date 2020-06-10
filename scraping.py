import requests
from bs4 import BeautifulSoup
from time import sleep
import jaconv

urls = []
with open('/Users/kazuki/VisualStudioCode/scraping/lecture_urls.tsv', encoding='utf-8') as f:
    for line in f:
        urls.append(line)

keys1 = ['開講年度', '授業科目名', '授業科目名（英文）', '担当教員', '科目開講学部・学科', '科目区分', '科目分類', '対象学年', '開講学期・時間割・教室', '授業の形態', '単位', '履修コード', '備考1', 'シラバスURL', '科目ナンバリング']
keys2 = ['授業概要', '到達すべき目標', '授業計画と準備学習', '授業の特色', '学生のアクティブ・ラーニングを促す取組', '使用言語', 'TA，SA配置予定', '基盤的能力専門的能力', '授業時間外の学習', '成績評価の方法', '到達度評価の観点', 'テキスト', 'テキスト(詳細)', '参考文献', '参考文献(詳細)', '担当教員実務経験内容または実践的教育内容', '実践的授業内容等', '備考', 'PAGE TOP']
keys3 = ['授業概要', '到達すべき***目標', '授業計画と***準備学習', '授業の特色', '学生のアク***ティブ・ラー***ニングを***促す取組', '使用言語', 'TA，SA配置***予定', '基盤的能力***専門的能力', '授業時間外***の学習', '成績評価の***方法', '到達度評価***の観点', 'テキスト', 'テキスト***(詳細)', '参考文献', '参考文献***(詳細)', '担当教員実***務経験内容***または実践***的教育内容', '実践的授業***内容等', '備考', 'PAGE TOP']
keys = keys1+keys3

def getLectureInfo(url):
    res = requests.get(url)
    html_doc = res.text
    soup = BeautifulSoup(html_doc, 'html.parser')

    for i in soup.select('br'):
        i.replace_with('***')

    text = soup.get_text()
    lines = [line.strip() for line in text.splitlines() if line.strip() != '']
    
    lec_info = {}
    index = []
    for key in keys:
        index += [lines.index(key)]
        print(index[-1])
    for i in range(len(index) - 1):
        lec_info[keys[i].replace('***', '')] = ''
        for j in range(index[i]+1, index[i+1]):
            lec_info[keys[i].replace('***', '')] += lines[j].replace('***', '\n')
            if j != index[i+1]-1:
                lec_info[keys[i].replace('***', '')] += '/'

    for k, v in lec_info.items():
        print(k + ':' + v)

    year = (int)(lec_info['開講年度'])
    grade = (int)(jaconv.z2h(lec_info['対象学年'][0], digit=True, ascii=True))
    timeroom = lec_info['開講学期・時間割・教室'].split('/')
    dics = []
    for i in timeroom:
        dic = {}
        dic['semester'] = i[0:3]
        dic['week'] = i[4:7]
        dic['period'] = i[8:11]
        dic['room'] = i[12:]
        dics.append(dic)
    print(dics)
    # lec_info['timeroom'] = dics

    return lec_info, dics

from google.cloud import firestore
c = 0
for url in urls:
    lecture_info, dics = getLectureInfo(url)
    lecture_name = lecture_info['授業科目名']

    # fileNeme = '/Users/kazuki/VisualStudioCode/scraping/lecture_info/2020/工学部/前学期/' + lecture_name + '.tsv'
    # with open(fileNeme, 'w', encoding='utf-8') as f:
    #     for k, v in lecture_info.items():
    #         f.write(k + ':::' + v + '\n***')
    db = firestore.Client()
    doc_ref = db.collection(u'lectures').document(lecture_info['授業科目名'])
    doc_ref.set(lecture_info)
    cnt = 0
    for dic in dics:
        doc_ref2 = doc_ref.collection(u'timeroom').document(str(cnt))
        doc_ref2.set(dic)
        cnt += 1
    c += 1
    if c==5:
        break;
    sleep(2)


# db = firestore.Client()
# doc_ref = db.collection(u'lecture').document(u'hoge')
# doc_ref.set(lecture_info)