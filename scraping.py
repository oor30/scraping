import requests
from bs4 import BeautifulSoup
from time import sleep
import jaconv
from google.cloud import firestore
import glob

class pycolor:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RETURN = '\033[07m' #反転
    ACCENT = '\033[01m' #強調
    FLASH = '\033[05m' #点滅
    RED_FLASH = '\033[05;41m' #赤背景+点滅
    END = '\033[0m'

# tsvファイルからシラバスURLを取り出す
def openUrls():
    urls = []
    with open('/Users/kazuki/VisualStudioCode/scraping/lecture_urls.tsv', encoding='utf-8') as f:
        for line in f:
            urls.append(line)
    return urls

def getLectureInfo(url):
    # 講義情報ディクショナリのkey
    keys1 = ['開講年度', '授業科目名', '授業科目名（英文）', '担当教員', '科目開講学部・学科', '科目区分', '科目分類', '対象学年', '開講学期・時間割・教室', '授業の形態', '単位', '履修コード', '備考1', 'シラバスURL', '科目ナンバリング']
    keys2 = ['授業概要', '到達すべき目標', '授業計画と準備学習', '授業の特色', '学生のアクティブ・ラーニングを促す取組', '使用言語', 'TA，SA配置予定', '基盤的能力専門的能力', '授業時間外の学習', '成績評価の方法', '到達度評価の観点', 'テキスト', 'テキスト(詳細)', '参考文献', '参考文献(詳細)', '担当教員実務経験内容または実践的教育内容', '実践的授業内容等', '備考', 'PAGE TOP']
    keys3 = ['授業概要', '到達すべき***目標', '授業計画と***準備学習', '授業の特色', '学生のアク***ティブ・ラー***ニングを***促す取組', '使用言語', 'TA，SA配置***予定', '基盤的能力***専門的能力', '授業時間外***の学習', '成績評価の***方法', '到達度評価***の観点', 'テキスト', 'テキスト***(詳細)', '参考文献', '参考文献***(詳細)', '担当教員実***務経験内容***または実践***的教育内容', '実践的授業***内容等', '備考', 'PAGE TOP']
    keys = keys1+keys3

    # htmlを取得
    res = requests.get(url)
    html_doc = res.text
    soup = BeautifulSoup(html_doc, 'html.parser')

    # 改行<br>が次の処理で削除されないように適当な文字で置き換えておく
    for i in soup.select('br'):
        i.replace_with('***')

    # htmlからテキストのみを取り出し、空白文字ごとに区切ってリストに保存
    text = soup.get_text()
    lines = [line.strip() for line in text.splitlines() if line.strip() != '']
    
    # 講義情報のディクショナリを作成
    lecture = {}
    index = []
    for key in keys:
        index += [lines.index(key)]
    for i in range(len(index) - 1):
        lecture[keys[i].replace('***', '')] = ''
        for j in range(index[i]+1, index[i+1]):
            lecture[keys[i].replace('***', '')] += lines[j].replace('***', '\n')
            if j != index[i+1]-1:
                lecture[keys[i].replace('***', '')] += ''
        lecture[keys[i].replace('***', '')] = lecture[keys[i].replace('***', '')].strip()

    for k, v in lecture.items():
        print(pycolor.RED + k + ':' + pycolor.END + v)

    # 開講学期・時間割・教室をディクショナリとして保存
    year = (int)(lecture['開講年度'])
    grade = (int)(jaconv.z2h(lecture['対象学年'][0], digit=True, ascii=True))
    timeroom = lecture['開講学期・時間割・教室'].split('\n')
    dics = {}
    cnt = 0
    for i in timeroom:
        dic = {}
        dic['semester'] = i[0:3]
        dic['week'] = i[4:7]
        dic['period'] = i[8:11]
        dic['room'] = i[12:].strip()
        dics[str(cnt)] = dic
        cnt += 1
    print(dics)
    lecture['timeinfo'] = dics

    return lecture

# 講義情報をtsvファイルに保存
def saveLectures(lectures):
    for lecture in lectures:
        lectureName = lecture['授業科目名']
        fileNeme = '/Users/kazuki/VisualStudioCode/scraping/lectures/2020/工学部/前学期/' + lectureName + '.tsv'
        with open(fileNeme, 'w', encoding='utf-8') as f:
            for k, v in lecture.items():
                if k == 'timeinfo':
                    f.write(k + ':::<dicTimeinfo>\n')
                    for k2, v2 in v.items():
                        f.write(k2 + ':::<dic>\n')
                        for k3, v3 in v2.items():
                            f.write(k3 + ':::' + v3 + '\n')
                        f.write('<dic/>\n')
                    f.write('<dicTimeinfo/>\n')
                    
                else:    
                    f.write(k + ':::' + v + '***\n')

# 講義情報をtsvファイルから開く
def openLectures(filePath): 
    lectures = []
    files = glob.glob(filePath)
    for file in files:
        with open(file, encoding='utf-8') as f:
            lecture = {}
            data = f.read()
            data = data.split('timeinfo')
            lines = data[0].split('***\n')
            timeinfo = data[1].split('\n')

            for line in lines:
                if ':::' in line:
                    keyValue = line.split(':::')
                    if len(keyValue) == 2:
                        lecture[keyValue[0]] = keyValue[1]
                    else:
                        lecture[keyValue[0]] = ''

            dicTimeinfo = {}
            inDic = False
            for line in timeinfo:
                keyValue = line.split(':::')
                if len(keyValue) == 2 and keyValue[1] == '<dic>':
                    inDic = True
                    dic = {}
                    dicTimeinfo[keyValue[0]] = dic
                elif keyValue[0] == '<dic/>':
                    inDic = False
                elif inDic:
                    dic[keyValue[0]] = keyValue[1]
            lecture['timeinfo'] = dicTimeinfo
            print(dicTimeinfo)

            lectures.append(lecture)

    for lecture in lectures:
        for k, v in lecture['timeinfo'].items():
            print(k+ ':')
            for k2, v2 in v.items():
                print(k2 + ':' + v2)
    print(lectures[0])
    
    return lectures
 
# シラバスURLリストから講義情報リストへ変換
def urlsToLectures(urls):
    c = 0
    lectures = []
    for url in urls:
        lectures.append(getLectureInfo(url))
        c += 1
        if c==1:
            break
    return lectures

# 講義情報をFirestoreにアップロード
def uploadFirestore(lectures):
    for lecture in lectures:
        db = firestore.Client()
        doc_ref = db.collection(u'lectures').document(lecture['授業科目名'])
        doc_ref.set(lecture)

# lectures = urlsToLectures(openUrls())
# saveLectures(lectures)
# uploadFirestore(lectures)
lectures = openLectures('/Users/kazuki/VisualStudioCode/scraping/lectures/2020/工学部/前学期/*')
uploadFirestore(lectures)
