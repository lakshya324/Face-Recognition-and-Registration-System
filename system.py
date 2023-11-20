from flask import Flask, render_template, url_for,request,redirect,flash,get_flashed_messages,Response
from flask_sqlalchemy import SQLAlchemy
import datetime , time
import cv2
import os
import numpy as np
import face_recognition
from functions import RegistrationForm,LoginForm,UpdateForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.db'
app.secret_key=str(os.urandom(24))
db=SQLAlchemy(app)

capture=0
grey=0
neg=0
face=0
switch=1
only_face=0
url=''
global_user=None

try:
    os.mkdir('./static/shots')
    os.mkdir('./static/users')
except OSError as error:
    pass

net = cv2.dnn.readNetFromCaffe('./saved_model/deploy.prototxt.txt', './saved_model/res10_300x300_ssd_iter_140000.caffemodel')
camera = cv2.VideoCapture(0)

class user(db.Model):
    username=db.Column(db.String(30),primary_key=True)
    email=db.Column(db.String(30),unique=True,nullable=False)
    password=db.Column(db.String(30),nullable=False)
    date_created=db.Column(db.DateTime,default=datetime.datetime.now)
    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.password}')"

def detect_face(frame,only_face=False):
    global net
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))   
    net.setInput(blob)
    detections = net.forward()
    confidence = detections[0, 0, 0, 2]
    if confidence < 0.5:
        return frame
    box = detections[0, 0, 0, 3:7] * np.array([w, h, w, h])
    (startX, startY, endX, endY) = box.astype("int")
    if only_face:
        try:
            frame=frame[startY:endY, startX:endX]
            (h, w) = frame.shape[:2]
            r = 480 / float(h)
            dim = ( int(w * r), 480)
            frame=cv2.resize(frame,dim)
        except Exception as e:
            pass
    else:
        cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
    return frame

def compare_faces(original_image_path, shot_image_path):
    original_image = face_recognition.load_image_file(original_image_path)
    shot_image = face_recognition.load_image_file(shot_image_path)
    try:
        original_face_encoding = face_recognition.face_encodings(original_image)[0]
        shot_face_encoding = face_recognition.face_encodings(shot_image)[0]
        results = face_recognition.compare_faces([original_face_encoding], shot_face_encoding)
        return results[0]
    except:
        return False

def gen_frames():
    while True:
        success, frame = camera.read()
        if success:
            if face:
                frame = detect_face(frame,False)
            if only_face:
                frame = detect_face(frame,True)
            if grey:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if neg:
                frame = cv2.bitwise_not(frame)
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
        else:
            pass

@app.route('/',methods=['POST','GET'])
def index():
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        user_name = form.username.data
        user_email=form.email.data
        pass_word = form.password.data
        new_user = user(username=user_name, email=user_email, password=pass_word)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash(f'New User Registered Successfully! username: {user_name}', 'message')
            return redirect(f'/camera/register/{user_name}')
        except:
            flash(f'New User Registered Failed! username: {user_name}', 'error')
            return 'error in sign up'
    return render_template('index.html', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user_name=form.username.data
        user_email=form.email.data
        pass_word = form.password.data
        login_user = user.query.filter_by(username=user_name,email=user_email, password=pass_word).first()
        if login_user:
            flash(f'Login Successful! username: {user_name}', 'success')
            return redirect(f'/camera/{user_name}')
        else:
            flash(f'Login Falied! username: {user_name}', 'error')
            return redirect(url_for('login'))
    return render_template('login.html',form=form)

@app.route('/delete/<string:username>')
def delete(username:str):
    global global_user
    if global_user==username:
        user_to_delete=user.query.get_or_404(username)
        global_user=None

        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            os.remove(f'static/users/{username}.png')
            flash(f'User Deleted Successfully! username:{username}','info')
            return redirect('/')
        except:
            flash(f'User Failed to Delete! username:{username}','error')
            return 'error in delete'
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    global global_user
    global_user=None
    return redirect('/')

@app.route('/update', methods=['POST','GET'])
def update():
    form = UpdateForm()
    if form.validate_on_submit():
        user_name=form.username.data
        user_to_update=user.query.get(user_name)
        if user_to_update:
            user_to_update.password=form.password.data
            try:
                db.session.commit()
                flash(f'User Updated Successfully! username:{user_name}','info')
                return redirect('/login')
            except:
                db.session.rollback()
                flash(f'User Failed to Update!', 'error')
                return 'Error in update'
        else:
            flash(f'User not Found! username:{user_name}','error')
            return 'User not Found'
    return render_template('update.html',form=form)

@app.route('/display_messages')
def display_messages():
    users=user.query.order_by(user.date_created).all()
    flash(f'Flash Message Opened','message')
    return render_template('message.html',users=users)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera/<string:username>',methods=['POST','GET'])
def tasks(username:str):
    global switch,camera,grey,neg,face,only_face,url
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            success, frame = camera.read()
            if success:
                flash(f"User Clicked 'Capture' Button! username:{username}",'message')
                now = datetime.datetime.now()
                url="shot_{}.png".format(str(now).replace(":",''))
                p = os.path.sep.join(['static','shots', url])
                cv2.imwrite(p, frame)
                camera.release()
                cv2.destroyAllWindows()
                return redirect(f'/verify/{username}')
            else:
                flash(f"User Clicked 'Capture' Button! username:{username}",'error')
        elif  request.form.get('grey') == 'Grey':
            grey=not grey
        elif  request.form.get('neg') == 'Negative':
            neg=not neg
        elif  request.form.get('face') == 'Face':
            face=not face
            if only_face:
                only_face=not only_face
            if(face):
                time.sleep(4)
        elif request.form.get('face_only') == 'Face Only':
            only_face=not only_face
            if face:
                face=not face
            if(only_face):
                time.sleep(4)
        elif  request.form.get('stop') == 'Stop/Start':
            if(switch==1):
                switch=0
                camera.release()
                cv2.destroyAllWindows()
            else:
                camera = cv2.VideoCapture(0)
                switch=1
    elif request.method=='GET':
        camera = cv2.VideoCapture(0)
        flash(f'User Camera Feed Opened Successfully! username:{username}','info')
        return render_template('camera_feed.html',use='Login',username=username)
    return render_template('camera_feed.html',use='Login',username=username)

@app.route('/camera/register/<string:username>',methods=['POST','GET'])
def register_tasks(username:str):
    global switch,camera,grey,neg,face,only_face,url
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            success, frame = camera.read()
            if success:
                flash(f"User Registered Successful! username:{username}",'message')
                now = datetime.datetime.now()
                # frame = detect_face(frame, True)
                # if frame is not None:
                    # url_save=f'{username}.png'
                p = os.path.sep.join(['static','users', f'{username}.png'])
                cv2.imwrite(p, frame)
                camera.release()
                cv2.destroyAllWindows()
                return redirect(f'/login')
            else:
                flash(f"User Clicked 'Capture' Button! username:{username}",'error')
        elif  request.form.get('grey') == 'Grey':
            grey=not grey
        elif  request.form.get('neg') == 'Negative':
            neg=not neg
        elif  request.form.get('face') == 'Face':
            face=not face
            if only_face:
                only_face=not only_face
            if(face):
                time.sleep(4)
        elif request.form.get('face_only') == 'Face Only':
            only_face=not only_face
            if face:
                face=not face
            if(only_face):
                time.sleep(4)
        elif  request.form.get('stop') == 'Stop/Start':
            if(switch==1):
                switch=0
                camera.release()
                cv2.destroyAllWindows()
            else:
                camera = cv2.VideoCapture(0)
                switch=1
    elif request.method=='GET':
        camera = cv2.VideoCapture(0)
        flash(f'User registration camera feed is open! username:{username}','info')
        return render_template('camera_feed.html',use='Signup',username=username)
    return render_template('camera_feed.html',use='Signup',username=username)

@app.route('/verify/<string:username>',methods=['POST','GET'])
def verfiy(username:str):
    if request.method=='POST':
        global url,global_user
        check=compare_faces(f'static/users/{username}.png',f'static/shots/{url}')
        if check:
            global_user=username
            return redirect(f'/home/{username}')
        else:
            return redirect(f'/camera/{username}')
    elif request.method=='GET':
        flash(f'User Verification Opened Successfully! username:{username}','info')
        return render_template('verify.html',username=username,url=url)
    return render_template('verify.html',username=username,url=url)

@app.route('/home/<string:username>')
def home(username:str):
    global global_user
    if global_user:
        flash(f'User Home Opened Successfully! username:{username}','info')
        return render_template('home.html',username=username)
    else:
        return redirect('/login')

if __name__=="__main__":
    app.run(host='0.0.0.0',port=5000)
    
camera.release()
cv2.destroyAllWindows()
