from flask.views import MethodView
from flask_smorest import Blueprint,abort
from flask_jwt_extended import jwt_required,get_jwt
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask,render_template,request,Response,url_for,redirect
import os
import re
from db import db
from datetime import datetime
from models import VideoModel
from models import UserModel
from schemas import VideoSchema 
from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
blp=Blueprint("Videos","videos",description="Operations on videos")

ALLOWED_EXTENSIONS = ['mp4']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_chunk(videoname,byte1=None, byte2=None):
    full_path = 'static/videos/' + videoname+ ".mp4"
    file_size = os.stat(full_path).st_size
    start = 0
    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start
    with open(full_path, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size

@blp.route("/video/<string:video_id>")
class Video1(MethodView):
    @jwt_required(locations='cookies')
    def get(self,video_id):
        video=VideoModel.query.filter_by(id=video_id).first_or_404()
        L=[]
        for i in video.userwithaccess:
            print(i.id)
            L.append(i.id)
        #print(video.userwithaccess)
        print(get_jwt_identity())
        print(get_jwt_identity() in L)
        if (video.ispublic==0 and (get_jwt_identity() in L)) or video.ispublic==1:
            vidname=video.videoname
            range_header = request.headers.get('Range', None)
            byte1, byte2 = 0, None
            if range_header:
                match = re.search(r'(\d+)-(\d*)', range_header)
                groups = match.groups()

                if groups[0]:
                    byte1 = int(groups[0])
                if groups[1]:
                    byte2 = int(groups[1])
       
            chunk, start, length, file_size = get_chunk(vidname,byte1, byte2)
            resp = Response(chunk, 206, mimetype='video/mp4',content_type='video/mp4', direct_passthrough=True)

            resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
            return resp
        else:
            return Response('Access Denied')
        
    @jwt_required(locations='cookies')
    def post(self,video_id):#delete not working
        video=VideoModel.query.filter_by(id=video_id).first_or_404()
        db.session.delete(video)
        db.session.commit()
        #filepath="/static/videos/"+video.videoname+".mp4"
        #os.remove(filepath)
        filename=video.videoname+".mp4"
        path=os.path.join("static/videos",filename)
        os.remove(path)
        return redirect(url_for('Videos.Video2'))
        return Response("deleted!!")
    
@blp.route("/video")        
class Video2(MethodView):
    
    @jwt_required(locations='cookies')
    def post(self):
        if 'video' not in request.files:
            return 'No video file found'
        video = request.files['video']
        videoname=request.form['videoname']
        ispublic=int(request.form['visibility'])
        #usersallowed=request.form['accesses']
        usersallowed=request.form.getlist('users[]')
        usersallowed=[int(i) for i in usersallowed]
        print("Printing usersallowed1", usersallowed)
        print(usersallowed)
        allusersidlist=[]
        allusers=UserModel.query.all()
        for i in allusers:
            allusersidlist.append(i.id)
        allowedusersid=[]
        print("allusersidlist:",end="")
        print(allusersidlist)
        #for i in usersallowed.split(','):
            #allowedusersid.append(int(i))
        allowedusersid=usersallowed
        allowedusersid.append(get_jwt_identity())
        for i in allowedusersid:
            if i not in allusersidlist:
                abort(400, message="invalid users list")
        userwithaccessobjects=[]
        for i in allowedusersid:
            userwithaccess=UserModel.query.filter_by(id=i).first_or_404()
            print(type(userwithaccess))
            userwithaccessobjects.append(userwithaccess)
        print(videoname)
        likes=0
        dislikes=0
        dateuploaded=datetime.now()
        if ispublic==1:
            userwithaccessobjects=list(allusers)
        print(userwithaccessobjects)
        #stmt=insert('videos').values(videoname=videoname,likes=0,dislikes=0,dateuploaded=dateuploaded)
        try:
            db.session.add(VideoModel(videoname=videoname,likes=likes,dislikes=dislikes,dateuploaded=dateuploaded,uploadedby=get_jwt_identity(),ispublic=ispublic,userwithaccess=userwithaccessobjects))
            print(get_jwt_identity())
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message="A video with that name already exists.",
            )
        except SQLAlchemyError as e:
            print(e)
            abort(500, message="An error occurred creating the video.")

        if video.filename == '':
            return 'No video selected'
        if video and allowed_file(video.filename):
            video.save('static/videos/' + videoname+".mp4")
            #return render_template('preview.html', video_name=videoname)
            return redirect(url_for('Videos.Video2'))
        return 'Invalid video file'
    


    @jwt_required(locations='cookies')
    def get(self):
        print("GET ALL VIDEOS")
        vids=VideoModel.query.all()
        usr=UserModel.query.all()
        id=get_jwt_identity()
        current_user=UserModel.query.filter_by(id=id).first_or_404()
        #current_user=current_user.username
        dict1={}
        for i in vids:
            id=VideoModel.query.filter_by(id=i.id).first_or_404()
            print(id.uploadedby)
            u=UserModel.query.filter_by(id=id.uploadedby).first_or_404()
            print(u.username)
            dict1[id.uploadedby]=u.username
        context={"videos":vids,"user":usr,"dict1": dict1,"current_user":current_user}
        return render_template('displayallvids.html',**context)

@blp.route("/videobyuser")
class VideoByUser(MethodView):
    @jwt_required(locations="cookies")
    def get(self):
        id=get_jwt_identity()
        vids=VideoModel.query.filter_by(uploadedby=id).all()
        id=get_jwt_identity()
        current_user=UserModel.query.filter_by(id=id).first_or_404()
        context={"videosbyuser":vids,"current_user":current_user}
        return render_template("videosbyuser.html",**context)