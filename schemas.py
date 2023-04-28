from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class VideoSchema(Schema):
    user_id = fields.Int(required=True, load_only=True)
    videoname=fields.Str(required=True)
    