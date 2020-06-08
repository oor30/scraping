import requests
from bs4 import BeautifulSoup
# from lxml import html

urls = []
with open('lecture_urls.tsv', encoding='utf-8') as f:
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

    tds_label_kougi = soup.find_all('td', class_='label_kougi')
    tds_kougi = soup.find_all('td', class_='kougi')

    tds_label = soup.find_all('td', class_='label')
    tds_left = soup.find_all('td', align='left')

    for i in soup.select('br'):
        i.replace_with('***')
    
    # tds_label_kougi = soup.find_all('td', class_='label_kougi')
    # tds_label = soup.find_all('td', class_='label')

    # labels = []
    # for td in tds_label:
    #     labels += [td.get_text().strip()]
    # print(labels)

    text = soup.get_text()
    lines = [line.strip() for line in text.splitlines() if line.strip() != '']
    for line in lines:
        print(line)
    
    lec_info = {}
    index = []
    for key in keys:
        index += [lines.index(key)]
        print(index[-1])
    for i in range(len(index) - 1):
        lec_info[keys[i].replace('***', '')] = ''
        for j in range(index[i]+1, index[i+1]):
            lec_info[keys[i].replace('***', '')] += lines[j].replace('***', '\n') + '/'

    for k, v in lec_info.items():
        print(k + ':' + v)

    # lec_info1 = {}
    # indexes1 = []
    # for key in keys1:
    #     indexes1 += [lines.index(key)]
    #     print(lines.index(key))
    # for i in range(len(indexes1)-1):
    #     if indexes1[i]+1 != indexes1[i+1]:
    #         lec_info1[keys1[i]] = lines[indexes1[i]+1 : indexes1[i+1]]
    #     else:
    #         lec_info1[keys1[i]] = ['']

    # lec_info2 = {}
    # indexes2 = []
    # for key in keys2:
    #     indexes2 += [lines.index(key)]
    #     print(lines.index(key))
    # for i in range(len(indexes2)-1):
    #     if indexes2[i]+1 != indexes2[i+1]:
    #         lec_info2[keys2[i]] = lines[indexes2[i]+1 : indexes2[i+1]]
    #     else:
    #         lec_info2[keys2[i]] = ['']

    # print(lec_info1)
    # print(lec_info2)

    # lecture_info = {}
    # for td_label_kougi, td_kougi in zip(tds_label_kougi, tds_kougi):
    #     lecture_info[td_label_kougi.get_text().strip()] = td_kougi.get_text().strip().replace('\r\n\r\n', '/').replace('\r', '').replace('\n', '').replace('\u3000', '').replace(' ', '')
    # for td_label, td_left in zip(tds_label, tds_left):
    #     for i in td_left.select('br'):
    #         i.replace_with('/')
    #     lecture_info[td_label.get_text().strip()] = td_left.get_text().strip()
    # # print(tds_left)
    return lec_info

lecture_info = getLectureInfo('https://alss-portal.gifu-u.ac.jp/campusweb/slbssbdr.do?value(risyunen)=2020&value(semekikn)=1&value(kougicd)=1TAA1304D0&value(crclumcd)=T-2018')

with open('lecture_info.tsv', 'w', encoding='utf-8') as f:
    for k, v in lecture_info.items():
        f.write(k + ':' + v + '\n')