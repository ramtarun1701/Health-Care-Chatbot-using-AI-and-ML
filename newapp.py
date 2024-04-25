#pip install -U spacy
#python -m spacy download en_core_web_md
#pip install -U wheel
        

import pathlib
from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
import pandas
#from werkzeug import secure_filename
import mysql.connector
import sys
import glob
import math
import numpy as np
from gtts import gTTS 
import speech_recognition as sr
import spacy
nlp = spacy.load("en_core_web_md")

noise_test=["is","a","this","an","the","are","?","for","of","who","in","many","they",
            "by","who","what","why","when","where","does","how","there","which","any",
            "it","have","if","on","or","st","nd","/","and","has","can","you","was","i am",]

def remove_noise(input_text):
    words=input_text.split()
    noise_free_words=[word for word in words if word not in noise_test]
    noise_free_text=" ".join(noise_free_words)
    return noise_free_text

app = Flask(__name__)
db= mysql.connector.connect(user='root', database='chatbot1')

std_embeddings_index = {}
with open('numberbatch-en.txt', encoding="utf8") as f:
    for line in f:
        values = line.split(' ')
        word = values[0]
        embedding = np.asarray(values[1:], dtype='float32')
        std_embeddings_index[word] = embedding

def cosineValue(v1,v2):
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0, 0, 0
    for i in range(len(v1)):
        x = v1[i];
        y = v2[i];
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y
    return sumxy/math.sqrt(sumxx*sumyy)


def get_sentence_vector(sentence, std_embeddings_index = std_embeddings_index ):
    sent_vector = 0
    for word in sentence.lower().split():
        if word not in std_embeddings_index :
            word_vector = np.array(np.random.uniform(-1.0, 1.0, 300))
            std_embeddings_index[word] = word_vector
        else:
            word_vector = std_embeddings_index[word]
        sent_vector = sent_vector + word_vector

    return sent_vector

def cosine_sim(sent1, sent2):
    return cosineValue(get_sentence_vector(sent1), get_sentence_vector(sent2))

def read_file(filename):
    with open(filename, 'rb') as f:
        photo = f.read()
        sys.setdefaultencoding('utf-8')
    return photo

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/adminlogin')
def adminlogin():
    return render_template('adminlogin.html')


@app.route('/upload')
def Upload():
    return render_template('upload.html')


@app.route('/adminlogin', methods=['POST'])
def do_adminlogin():
    flag=False
    username=request.form['username']
    password=request.form['password']
    if username=='admin' and password=='admin':
        session['logged_in'] = True
        flag=True
    else:
        flag=False
    if flag:
        return render_template('adminhome.html')
    else:
        return render_template('adminlogin.html')

@app.route('/Query')
def QueryDB():
    file = pathlib.Path("welcome.mp3")
    if file.exists ():
        os.remove("welcome.mp3")
    ques=[]
    ans=[]
    s3=" "
    r = sr.Recognizer()                                                                                   
    with sr.Microphone() as source:                                                                       
        print("Speak:")                                                                                   
        audio = r.listen(source)   

    try:
        s3=r.recognize_google(audio)
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

    print ("Ur Spech is  ",s3)
    s2=remove_noise(s3)
    statement1 = nlp(s3)
    cursor = db.cursor()
    rows_count=cursor.execute("select * from quest")
    data=cursor.fetchall()
    ind=0
    ind1=0
    max1=0.0
    for item in data:
        ques.append(item[1])
        ans.append(item[2])
        ss1=str(item[1])
        s1=remove_noise(ss1)
        
        
        statement2 = nlp(ss1)
        cs=statement1.similarity(statement2)
        print( item[1],'  ',item[2],'  ',cs)
        if(cs>max1):
            print("Hello")
            max1=cs
            ind1=ind
        ind=ind+1
    
    answer=ans[ind1]
    if(max1>=.75):
        mytext = answer
        language = 'en'
        myobj = gTTS(text=answer, lang=language, slow=False) 
        myobj.save("welcome1.mp3") 
        os.system("welcome1.mp3")
        return render_template('adminhome1.html',ques=s3,msg=answer)
    else:
        cursor1 = db.cursor()
        print ("s is  ",s3)
        cursor1.execute('insert into suggestion(quest) values("%s")' % (s3))
        db.commit()
        mytext = "Answer not Available"
        language = 'en'
        myobj = gTTS(text=mytext, lang=language, slow=False) 
        myobj.save("welcome1.mp3") 
        os.system("welcome1.mp3")
        return render_template('adminhome1.html',ques=s3,msg="Answer not Available")

      
@app.route('/textQuery',methods=['POST','GET'])
def textQueryDB():
    file = pathlib.Path("welcome.mp3")
    if file.exists ():
        os.remove("welcome.mp3")
        
    ques=[]
    ans=[]
    s3=request.form['t1']
 
    print ("Ur Spech is  ",s3)
    s2=remove_noise(s3)
    statement1 = nlp(s3)
    cursor = db.cursor()
    rows_count=cursor.execute("select * from quest")
    data=cursor.fetchall()
    ind=0
    ind1=0
    max1=0.0
    for item in data:
        ques.append(item[1])
        ans.append(item[2])
        ss1=str(item[1])
        s1=remove_noise(ss1)
        
        
        statement2 = nlp(ss1)
        cs=statement1.similarity(statement2)
        print( item[1],'  ',item[2],'  ',cs)
        if(cs>max1):
            print("Hello")
            max1=cs
            ind1=ind
        ind=ind+1
    
    answer=ans[ind1]
    if(max1>=.75):
        mytext = answer
        language = 'en'
        myobj = gTTS(text=answer, lang=language, slow=False) 
        myobj.save("welcome1.mp3") 
        os.system("welcome1.mp3")
        return render_template('adminhome1.html',ques=s3,msg=answer)
    else:
        cursor1 = db.cursor()
        print ("s is  ",s3)
        cursor1.execute('insert into suggestion(quest) values("%s")' % (s3))
        db.commit()
        mytext = "Answer not Available"
        language = 'en'
        myobj = gTTS(text=mytext, lang=language, slow=False) 
        myobj.save("welcome1.mp3") 
        os.system("welcome1.mp3")
        return render_template('adminhome1.html',ques=s3,msg="Answer not Available")



@app.route('/suggestion')
def suggestionDB():
    cursor = db.cursor()
    rows_count=cursor.execute("select * from suggestion")
    data=cursor.fetchall()
    return render_template('adminhome2.html',ddata=data)


@app.route('/uploadDB', methods=['POST'])
def do_uploadDB():
    f = request.files['files']
    df = pandas.read_csv(f)
    print(df)
   # cursor1 = db.cursor()
   # cursor1.execute("delete from quest")
   # db.commit()
    
    for index, row in df.iterrows():
        cursor = db.cursor()
        cursor.execute('insert into quest(question,answer) values("%s", "%s")' % \
             (row['question'],row['answer']))
        db.commit()
    return render_template('adminhome1.html',msg="File UploadedSuccessfully")



@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()
 
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=8000)