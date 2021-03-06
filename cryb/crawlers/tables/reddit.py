
import marshmallow_sqlalchemy as ma
import sqlalchemy as sql

from .common import Database


class Board(Database.Table):
    __tablename__ = 'reddit_board'

    id = sql.Column(sql.String(), primary_key=True)
    name = sql.Column(sql.String(), nullable=False)
    description = sql.Column(sql.String())


class BoardSchema(ma.SQLAlchemyAutoSchema):
    Meta = Database.schema_metadata(Board)


class Thread(Database.Table):
    __tablename__ = 'reddit_thread'

    id = sql.Column(sql.String(), primary_key=True)
    board_id = sql.Column(sql.String(), sql.ForeignKey('reddit_board.id'))
    author = sql.Column(sql.String(), nullable=False)
    title = sql.Column(sql.String(), nullable=False)
    text = sql.Column(sql.String(), nullable=False)
    created_on = sql.Column(sql.DateTime, nullable=False)
    comments = sql.Column(sql.Integer, nullable=False)


class ThreadSchema(ma.SQLAlchemyAutoSchema):
    Meta = Database.schema_metadata(Thread)


class Comment(Database.Table):
    __tablename__ = 'reddit_comment'

    id = sql.Column(sql.String(), primary_key=True)
    thread_id = sql.Column(sql.String(), sql.ForeignKey('reddit_thread.id'))
    author = sql.Column(sql.String(), nullable=False)
    text = sql.Column(sql.String(), nullable=False)
    created_on = sql.Column(sql.DateTime, nullable=False)
    parent_comment_id = sql.Column(sql.String())


class CommentSchema(ma.SQLAlchemyAutoSchema):
    Meta = Database.schema_metadata(Comment)
