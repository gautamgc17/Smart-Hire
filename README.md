# Introduction

__SMART HIRE__ : a project made for "HackUIET" Hackathon with an aim to automate the interview process.

## Objective

- Application to automate the hiring process
- Personality prediction using ML
- Check confidence and other traits using video and tone analysis
- Send mail to selected/rejected candidates automatically in one-click
- Fast recruitment in larger numbers
- Generate concise insights and provide summary of the candidate's profile
- Handy application for HR/Recruiting Team

## Project Workflow
- Interviewee
     - Enter personal details, upload resume, attempt a questionnaire wherein the candidate has to rate himself/herself
     - Personality prediction (based on [Big Five Personality Traits](https://www.thomas.co/resources/type/hr-guides/what-are-big-5-personality-traits) model) with OCEAN values and CV analysis
     - Video recording in browser. The candidate has to answer few questions put up by the HR team on the portal.
     - Face emotion and Speech Analysis to get insights like confidence level, candidate personality traits
     
- Interviewer/HR team/Admin
     - View all the registered candidates’ details
     - View each candidate's profile summary which includes resume, responses to questions, technical skills, personality traits, video and tone analysis result.
     - Update candidate about selection/rejection, further interview process using one-click mail or phone call

## Video Link
[Project Demonstration](https://drive.google.com/drive/folders/1D5i3sphhTIIBBlRkfxhkuGK2vdK1NoXm?usp=sharing)

## Presentation Slides
[Presentation Link](https://docs.google.com/presentation/d/1L1slU4owXQ5fTBK6zP6kCrpBuiCoABMF/edit#slide=id.p1)


<br>

_Though most of the features has been added, yet the complete process is not yet automated as this application is made for HackUIET Hackathon. As of now, the application can be used to store the results of multiple users in mysql server, however sending of mail and candidate profile summary/dashboard can only be generated/viewed for a single user i.e, [topmost user](#Track-candidates)._

<br>

# Installation Guide
This project requires the following tools to get started:

- Python - The programming language used by Flask.
- MySQL -  A relational database management system based on SQL.
- Virtualenv - A tool for creating isolated Python environments.
- VSCode - A lightweight source code editor which can be used to view, edit, run, and debug source code for applications. You can optionally use any other code editor of your choice such as Sublime Text or Atom.
- AWS Account - A subsidiary of Amazon providing on-demand cloud computing platforms and APIs. 

To get started, install Python and MySQL on your local computer if you don't have them already.

Also, create an AWS Free Tier account, if you don't have it. Services like Amazon S3 and Amazon Transcribe API will be used in this project.

## Getting Started

**Step 1. Clone the repository into a new folder and then switch to code directory**

```
$ git clone https://github.com/gautamgc17/smart-hire
$ cd smart-hire
```

**Step 2. Create a Virtual Environment and install Dependencies.**

If you don't have the virtualenv command yet, you can find installation [instructions here](https://virtualenv.readthedocs.io/en/latest/). Learn more about [Virtual Environments](https://www.geeksforgeeks.org/python-virtual-environment/).

```
$ pip install virtualenv
```

Create a new Virtual Environment for the project and activate it.

```
$ virtualenv venv
$ source venv/bin/activate
```
Once the virtual environment is activated, the name of your virtual environment will appear on left side of terminal. In our case, venv named virtual environment is active.

Next, we need to install the project dependencies in this virtual environment, which are listed in `requirements.txt`.

```
(venv) $ pip install -r requirements.txt
```
For NLP operations, the [resume parser](https://omkarpathak.in/pyresparser/) package uses spacy and nltk. Install them using below commands:
```
# spaCy
python -m spacy download en_core_web_sm

# nltk
python -m nltk.downloader words
```


**Step 3. Setup your database to store information of the candidates**

Go to MySQL Command-Line Client, and login to the database server using the username and password. Then execute the below statements:

```
CREATE DATABASE databasename;
USE databasename;
CREATE TABLE candidates (id int(11) NOT NULL AUTO_INCREMENT, candidatename varchar(50) NOT NULL, email varchar(50) NOT NULL, password varchar(50)NOT NULL, PRIMARY KEY(id));
```

![mysql](screenshots/mysql.PNG)

To look at the candidates table structure, execute

```
DESCRIBE candidates; 
```

**Step 4. Set up Amazon Transcribe API for speech to text conversion**

- Sign in to your Amazon console and create a _S3 bucket_ and give it a unique name. Note your AWS region as it will be required later.
- Go to _IAM dashboard_, add a new User. Then click on add permissions and grant the following two permissions - _AmazonTranscribeFullAccess_ and _AmazonS3FullAccess_.
- Then under Security Credentials, click on _Create access key_ to get your credentials i.e,  'aws_access_key_id' and 'aws_secret_access_key'.

![s3-bucket](screenshots/s3.PNG)


**Step 5. Setting up IBM Watson for tone analysis**
- Go to [IBM Cloud catalog](https://cloud.ibm.com/catalog), under category choose _AI / Machine Learning_. Then choose _Tone Analyzer_ service.
- To create an instance of Tone Analyzer service, click on _Create_ on right hand side.
- Now we need 2 things - _service url_ and _api key_. So click on _Manage_ and copy your credentials.

**Step 6. Update environment variables.**

To run the project, you need to configure the application to run locally. This will require updating a set of environment variables specific to your environment.

In the same directory, create a local environment file

```
(venv) $ touch .env   
(venv) $ nano .env    
```

To get help on how to Set and Get Environment Variables in Python, visit [here](https://able.bio/rhett/how-to-set-and-get-environment-variables-in-python--274rgt5).

_Now You have to simply duplicate the __.env.sample__ file and just insert your credentials._

In the file _.env_ , 
- store your aws credentials i.e aws region, unique bucket name, language code, aws access key id and secret key in following variables:

```
my_region = ""
bucket_name = ""
lang_code = ""
aws_access_key_id = ""
aws_secret_key = ""
```

- store your watson tone analyzer credentials in the following variables:

```
ibm_apikey = ""
ibm_url = ""
```
- configure MySql username and password

```
mysql_password = ""
mysql_user = ""
```

- interviewer mail and password

```
mail_username = ""
mail_pwd = ""
```

- company's official email and password for members of HR team to sign in into the portal.
```
company_mail = ""
company_pswd = ""
```
<br>


__So, basically your project structure would look like:__

![project](screenshots/structure.PNG)


**Step 7: Run the server**

Set the FLASK_APP environment variable.
```
(venv) $ export FLASK_APP=app.py
```

Now we're ready to start our flask server:
```
(venv) $ flask run
```
Visit http://127.0.0.1:5000 to see your app in action

<br>

__To know more about how to set up a flask application on Windows, MacOS or Linux, visit [here](https://phoenixnap.com/kb/install-flask#ftoc-heading-12)__

<br>


# Snapshots

### Interviewee Sign Up page

![signup](screenshots/firstpg.png)

### Personality Prediction page

![basicinfo](screenshots/pred.png)

### Streaming Interview of the candidate

![video-stream](screenshots/stream.png)

### 'Thankyou for Taking Interview' Response page

![thankyou](screenshots/thank-resp.PNG)

### Interviewer Sign In page

![signin](screenshots/firstpg(2).png)

### Track candidates

![profiles](screenshots/profiles.PNG)

### Concise insights and summary of candidate profile

![summary](screenshots/info.PNG)

![summary](screenshots/info-2.PNG)

### One-click mail to candidate

![inform](screenshots/mailsent.png)

### Mail to candidate

![email](screenshots/email.PNG)



