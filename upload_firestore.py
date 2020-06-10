from google.cloud import firestore
from openfile import open_lecture_info

lectures = open_lecture_info('/Users/kazuki/VisualStudioCode/scraping/lecture_info/2020/工学部/前学期/*')

for lecture in lectures:
    db = firestore.Client()
    doc_ref = db.collection(u'lecture').document(u'hoge')
    doc_ref.set(lectures[1])