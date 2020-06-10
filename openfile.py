import glob

def open_lecture_info(path):
    lectures = []
    files = glob.glob(path)
    for file in files:
        print(file)
        with open(file, encoding='utf-8') as f:
            lecture = {}
            data = f.read()
            lines = data.split('\n***')
            for line in lines:
                keyValue = line.split(':::')
                if len(keyValue) == 2:
                    lecture[keyValue[0]] = keyValue[1]
                else:
                    lecture[keyValue[0]] = ''
            lectures.append(lecture)

    for lecture in lectures:
        for k, v in lecture.items():
            print(k + ': ' + v)
    
    return lectures

open_lecture_info('/Users/kazuki/VisualStudioCode/scraping/lecture_info/2020/工学部/前学期/*')