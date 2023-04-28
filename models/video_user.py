from db import db 
class VideoUsers(db.Model):
    __tablename__="videos_users"
    id=db.Column(db.Integer,primary_key=True)
    video_id=db.Column(db.Integer,db.ForeignKey("videos.id"))
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"))