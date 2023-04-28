from db import db 
class VideoModel(db.Model):
    __tablename__="videos"
    id=db.Column(db.Integer,primary_key=True)
    videoname=db.Column(db.String(100),unique=True,nullable=False)
    likes=db.Column(db.Integer,nullable=False)
    dislikes=db.Column(db.Integer,nullable=False)
    dateuploaded=db.Column(db.DateTime,nullable=False)
    ispublic=db.Column(db.Boolean,nullable=False)
    uploadedby=db.Column(db.Integer,db.ForeignKey('users.id'),unique=False,nullable=False)
    user=db.relationship("UserModel", back_populates="videos")
    userwithaccess = db.relationship("UserModel", back_populates="videoswithaccess", secondary="videos_users")