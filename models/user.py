from db import db 
class UserModel(db.Model):
    __tablename__="users"
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(80),unique=True,nullable=False)
    password=db.Column(db.String(80),nullable=False)
    videos=db.relationship("VideoModel",back_populates="user",lazy="dynamic")
    videoswithaccess=db.relationship("VideoModel", back_populates="userwithaccess", secondary="videos_users")