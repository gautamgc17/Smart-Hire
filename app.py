# Import all the necessary libraries
import numpy as np
from numpy.core.numeric import NaN
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import json
import re
import time
import cv2
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from flask import Flask , render_template , request , url_for , jsonify , Response
from werkzeug.utils import redirect, secure_filename
from flask_mail import Mail , Message
from flask_mysqldb import MySQL
from pyresparser import ResumeParser
from fer import Video
from fer import FER
from video_analysis import extract_text , analyze_tone
from decouple import config


# Access the environment variables stored in .env file
MYSQL_USER = config('mysql_user')
MYSQL_PASSWORD = config('mysql_password')

# To send mail (By interviewee)
MAIL_USERNAME = config('mail_username')
MAIL_PWD = config('mail_pwd')

# For logging into the interview portal
COMPANY_MAIL = config('company_mail')
COMPANY_PSWD = config('company_pswd')

# Create a Flask app
app = Flask(__name__)

# App configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = 'smarthire' 
user_db = MySQL(app)

mail = Mail(app)              
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PWD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_ASCII_ATTACHMENTS'] = True
mail = Mail(app)


# Initial sliding page
@app.route('/')
def home():
    return render_template('index.html')


# Interviewee signup 
@app.route('/signup' , methods=['POST' , 'GET'])
def interviewee():
    if request.method == 'POST' and 'username' in request.form and 'usermail' in request.form and 'userpassword' in request.form:
        username = request.form['username']
        usermail = request.form['usermail']
        userpassword = request.form['userpassword']

        cursor = user_db.connection.cursor()

        cursor.execute("SELECT * FROM candidates WHERE candidatename = % s AND email = %s", (username, usermail))
        account = cursor.fetchone()

        if account:
            err = "Account Already Exists"
            return render_template('index.html' , err = err)
        elif not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', usermail):
            err = "Invalid Email Address !!"
            return render_template('index.html' , err = err)
        elif not re.fullmatch(r'[A-Za-z0-9\s]+', username):
            err = "Username must contain only characters and numbers !!"
            return render_template('index.html' , err = err)
        elif not username or not userpassword or not usermail:
            err = "Please fill out all the fields"
            return render_template('index.html' , err = err)
        else:
            cursor.execute("INSERT INTO candidates VALUES (NULL, % s, % s, % s)" , (username, usermail, userpassword,))
            user_db.connection.commit()
            reg = "You have successfully registered !!"
            return render_template('FirstPage.html' , reg = reg)
    else:
        return render_template('index.html')


# Interviewer signin 
@app.route('/signin' , methods=['POST' , 'GET'])
def interviewer():
    if request.method == 'POST' and 'company_mail' in request.form and 'password' in request.form:
        company_mail = request.form['company_mail']
        password = request.form['password']

        if company_mail == COMPANY_MAIL and password == COMPANY_PSWD:
            return render_template('candidateSelect.html')
        else:
            return render_template("index.html" , err = "Incorrect Credentials")
    else:
        return render_template("index.html")


# personality trait prediction using Logistic Regression and parsing resume
@app.route('/prediction' , methods = ['GET' , 'POST'])
def predict():
    # get form data
    if request.method == 'POST':
        fname = request.form['firstname'].capitalize()
        lname = request.form['lastname'].capitalize()
        age = int(request.form['age'])
        gender = request.form['gender']
        email = request.form['email']
        file = request.files['resume']
        path = './static/{}'.format(file.filename)
        file.save(path)
        val1 = request.form['openness']
        val2 = request.form['neuroticism']
        val3 = request.form['conscientiousness']
        val4 = request.form['agreeableness']
        val5 = request.form['extraversion']
        
        # model prediction
        df = pd.read_csv(r'static\trainDataset.csv')
        le = LabelEncoder()
        df['Gender'] = le.fit_transform(df['Gender'])
        x_train = df.iloc[:, :-1].to_numpy()
        y_train = df.iloc[:, -1].to_numpy(dtype = str)
        lreg = LogisticRegression(multi_class='multinomial', solver='newton-cg',max_iter =1000)
        lreg.fit(x_train, y_train)

        if gender == 'male':
            gender = 1
        elif gender == 'female': 
            gender = 0
        input =  [gender, age, val1, val2, val3, val4, val5]

        pred = str(lreg.predict([input])[0]).capitalize()

        # get data from the resume
        data = ResumeParser(path).get_extracted_data()
        
        result = {'Name':fname+' '+lname , 'Age':age , 'Email':email , 'Mobile Number':data.get('mobile_number', None) , 
        'Skills':str(data['skills']).replace("[" , "").replace("]" , "").replace("'" , "") , 'Degree':data.get('degree' , None)[0] , 'Designation':data.get('designation', None)[0] ,
        'Total Experience':data.get('total_experience') , 'Predicted Personality':pred}

        with open('./static/result.json' , 'w') as file:
            json.dump(result , file)

    return render_template('questionPage.html')


# Record candidate's interview for face emotion and tone analysis
@app.route('/analysis', methods = ['POST'])
def video_analysis():

    # get videos using media recorder js and save
    quest1 = request.files['question1']
    quest2 = request.files['question2']
    quest3 = request.files['question3']
    path1 = "./static/{}.{}".format("question1","webm")
    path2 = "./static/{}.{}".format("question2","webm")
    path3 = "./static/{}.{}".format("question3","webm")
    quest1.save(path1)
    quest2.save(path2)
    quest3.save(path3)

    # speech to text response for each question - AWS
    responses = {'Question 1: Tell something about yourself': [] , 'Question 2: Why should we hire you?': [] , 'Question 3: Where Do You See Yourself Five Years From Now?': []}
    ques = list(responses.keys())

    text1 , data1 = extract_text("question1.webm")
    time.sleep(15)
    responses[ques[0]].append(text1)

    text2 , data2 = extract_text("question2.webm")
    time.sleep(15)
    responses[ques[1]].append(text2)

    text3 , data3 = extract_text("question3.webm")
    time.sleep(15)
    responses[ques[2]].append(text3)

    # tone analysis for each textual answer - IBM
    res1 = analyze_tone(text1)
    tones_doc1 = []

    for tone in res1['document_tone']['tones']:
        tones_doc1.append((tone['tone_name'] , round(tone['score']*100, 2)))

    if 'Tentative' not in [key for key, val in tones_doc1]:
        tones_doc1.append(('Tentative', 0.0))
    if 'Analytical' not in [key for key, val in tones_doc1]:
        tones_doc1.append(('Analytical', 0.0))
    if 'Fear' not in [key for key, val in tones_doc1]:
        tones_doc1.append(('Fear', 0.0))
    if 'Confident' not in [key for key, val in tones_doc1]:
        tones_doc1.append(('Confident', 0.0))
    if 'Joy' not in [key for key, val in tones_doc1]:
        tones_doc1.append(('Joy', 0.0))
        
    tones_doc1 = sorted(tones_doc1)

    res2 = analyze_tone(text2)
    tones_doc2 = []

    for tone in res2['document_tone']['tones']:
        tones_doc2.append((tone['tone_name'] , round(tone['score']*100, 2)))
        
    if 'Tentative' not in [key for key, val in tones_doc2]:
        tones_doc2.append(('Tentative', 0.0))
    if 'Analytical' not in [key for key, val in tones_doc2]:
        tones_doc2.append(('Analytical', 0.0))
    if 'Fear' not in [key for key, val in tones_doc2]:
        tones_doc2.append(('Fear', 0.0))
    if 'Confident' not in [key for key, val in tones_doc2]:
        tones_doc2.append(('Confident', 0.0))
    if 'Joy' not in [key for key, val in tones_doc2]:
        tones_doc2.append(('Joy', 0.0))
        
    tones_doc2 = sorted(tones_doc2)

    res3 = analyze_tone(text3)
    tones_doc3 = []

    for tone in res3['document_tone']['tones']:
        tones_doc3.append((tone['tone_name'] , round(tone['score']*100, 2)))
        
    if 'Tentative' not in [key for key, val in tones_doc3]:
        tones_doc3.append(('Tentative', 0.0))
    if 'Analytical' not in [key for key, val in tones_doc3]:
        tones_doc3.append(('Analytical', 0.0))
    if 'Fear' not in [key for key, val in tones_doc3]:
        tones_doc3.append(('Fear', 0.0))
    if 'Confident' not in [key for key, val in tones_doc3]:
        tones_doc3.append(('Confident', 0.0))
    if 'Joy' not in [key for key, val in tones_doc3]:
        tones_doc3.append(('Joy', 0.0))
        
    tones_doc3 = sorted(tones_doc3)

    # plot tone analysis 
    document_tones = tones_doc1 + tones_doc2 + tones_doc3

    analytical_tone = []
    tentative_tone = []
    fear_tone = []
    joy_tone = []
    confident_tone = []

    for sentiment, score in document_tones:
        if sentiment == "Analytical":
            analytical_tone.append(score)
        elif sentiment == "Tentative":
            tentative_tone.append(score)
        elif sentiment == "Fear":
            fear_tone.append(score)
        elif sentiment == "Joy":
            joy_tone.append(score)
        elif sentiment == "Confident":
            confident_tone.append(score)

    values = np.array([0,1,2])*3
    fig = plt.figure(figsize=(12, 6))
    sns.set_style("whitegrid")
    plt.xlim(-1.5, 10)

    plt.bar(values , analytical_tone , width = 0.4 , label = 'Analytical')
    plt.bar(values+0.4 , confident_tone , width = 0.4 , label = 'Confidence')
    plt.bar(values+0.8 , fear_tone , width = 0.4 , label = 'Fear')
    plt.bar(values-0.4 , joy_tone , width = 0.4 , label = 'Joy')
    plt.bar(values-0.8 , tentative_tone , width = 0.4 , label = 'Tentative')

    plt.xticks(ticks = values , labels = ['Question 1','Question 2','Question 3'] , fontsize = 15 , fontweight = 60)
    plt.yticks(fontsize = 12 , fontweight = 90)
    ax = plt.gca()
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')                    
    ax.xaxis.set_tick_params(pad = 5)
    ax.yaxis.set_tick_params(pad = 5)
    plt.legend()
    plt.savefig(f'./static/tone_analysis.jpg' , bbox_inches = 'tight')

    # save all responses
    with open('./static/answers.json' , 'w') as file:
        json.dump(responses , file)

    # face emotion recognition - plotting the emotions against time in the video
    videos = ["question1.webm", "question2.webm", "question3.webm"]
    frame_per_sec = 100
    size = (1280, 720)

    video = cv2.VideoWriter(f"./static/combined.webm", cv2.VideoWriter_fourcc(*"VP90"), int(frame_per_sec), size)

    # Write all the frames sequentially to the new video
    for v in videos:
        curr_v = cv2.VideoCapture(f'./static/{v}')
        while curr_v.isOpened():
            r, frame = curr_v.read()    
            if not r:
                break
            video.write(frame)         
    video.release()

    face_detector = FER(mtcnn=True)
    input_video = Video(r"./static/combined.webm")
    processing_data = input_video.analyze(face_detector, display = False, save_frames = False, save_video = False, annotate_frames = False, zip_images = False)
    vid_df = input_video.to_pandas(processing_data)
    vid_df = input_video.get_first_face(vid_df)
    vid_df = input_video.get_emotions(vid_df)
    pltfig = vid_df.plot(figsize=(12, 6), fontsize=12).get_figure()
    plt.legend(fontsize = 'large' , loc = 1)
    pltfig.savefig(f'./static/fer_output.png')

    return "success"


# Interview completed response message
@app.route('/recorded')
def response():
    return render_template('recorded.html')


# Display results to interviewee
@app.route('/info')
def info():
    with open('./static/result.json' , 'r') as file:
        output = json.load(file)

    with open('./static/answers.json' , 'r') as file:
        answers = json.load(file)

    return render_template('result.html' , output = output , responses = answers)


# Send job confirmation mail to selected candidate
@app.route('/accept' , methods=['GET'])
def accept():

    with open('./static/result.json' , 'r') as file:
        output = json.load(file)
    
    name = output['Name']
    email = output['Email']
    position = "Software Development Engineer"

    msg = Message(f'Job Confirmation Letter', sender = MAIL_USERNAME, recipients = [email])
    msg.body = f"Dear {name},\n\n" + f"Thank you for taking the time to interview for the {position} position. We enjoyed getting to know you. We have completed all of our interviews.\n\n"+ f"I am pleased to inform you that we would like to offer you the {position} position. We believe your past experience and strong technical skills will be an asset to our organization. Your starting salary will be $15,000 per year with an anticipated start date of July 1.\n\n"+ f"The next step in the process is to set up meetings with our CEO, Rahul Dravid\n\n."+ f"Please respond to this email by June 23 to let us know if you would like to accept the SDE position.\n\n" + f"I look forward to hearing from you.\n\n"+ f"Sincerely,\n\n"+ f"Harsh Verma\nHuman Resources Director\nPhone: 555-555-1234\nEmail: feedbackmonitor123@gmail.com"
    mail.send(msg)

    return "success"

# Send mail to rejected candidate
@app.route('/reject' , methods=['GET'])
def reject():

    with open('./static/result.json' , 'r') as file:
        output = json.load(file)
    
    name = output['Name']
    email = output['Email']
    position = "Software Development Engineer"

    msg = Message(f'Your application to Smart Hire', sender = MAIL_USERNAME, recipients = [email])
    msg.body = f"Dear {name},\n\n" + f"Thank you for taking the time to consider Smart Hire. We wanted to let you know that we have chosen to move forward with a different candidate for the {position} position.\n\n"+ f"Our team was impressed by your skills and accomplishments. We think you could be a good fit for other future openings and will reach out again if we find a good match.\n\n"+ f"We wish you all the best in your job search and future professional endeavors.\n\n"+ f"Regards,\n\n"+ f"Harsh Verma\nHuman Resources Director\nPhone: 555-555-1234\nEmail: feedbackmonitor123@gmail.com"
    mail.send(msg)

    return "success"


if __name__ == '__main__':
    app.run(debug = True)
