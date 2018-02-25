from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from config import DevConfig
from sqlalchemy import func 

app = Flask(__name__)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    posts = db.relationship(
        'Post',
        backref='user',
        lazy='subquery'
    )

    def __init__(self, username):
        self.username = username
    
    def __repr__(self):
        return 'User {}'.format(self.username)
tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id') )

)
class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.Text())
    publish_date = db.Column(db.DateTime())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    comments = db.relationship(
        'Comment',
        backref='post',
        lazy='dynamic'
    )

    tags = db.relationship(
        'Tag',
        secondary=tags,
        backref=db.backref('posts', lazy='dynamic')
    )
    
    def __init__(self, title):
        self.title = title
    
    def __repr__(self):
        return "<Post '{}'>".format(self.title)


class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))

    def __init__(self, title):
        self.title = title
    def __repr__(self):
        return "<Tag '{}'>".format(self.title)

class Comment(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    text = db.Column(db.Text())
    date = db.Column(db.DateTime())
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])


def sidebar_data():
    recnet = Post.query.order_by(
        Post.publish_date.desc()
    ).limit(5).all()
    top_tags = db.session.query(
        Tag, func.count(tags.c.post_id).label('total')
    ).join(
        tags
    ).group_by(Tag).order_by('total DESC').limit(5).all()
    return recnet, top_tags



@app.route('/')
@app.route('/<int:page>')
def home(page=1):
    posts = Post.query.order_by(
        Post.publish_date.desc()
    ).paginate(page, 10)
    recent, top_tags = sidebar_data()
    return render_template(
        'home.html',
        posts=posts,
        recent=recent,
        top_tags=top_tags,
    )

@app.route('/posts/<int:post_id>')
def posts(post_id):
    post = Post.query.get(post_id)
    recent, top_tags = sidebar_data()
    return render_template(
        'posts.html',
        post=post,
        recent=recent,
        top_tags=top_tags
    )
@app.route('/tag/<int:tag_id>')
def tag(tag_id):
    tag = Tag.query.get(tag_id)
    recent, top_tags = sidebar_data()
    return render_template(
        'tags.html',
        recent=recent,
        posts=tag.posts,
        top_tags=top_tags,
        tag_id=tag.id
    )

@app.route('/user/<int:user_id>')
def user(user_id):
    user = User.query.get(user_id)
    recent, top_tags = sidebar_data()
    return render_template(
        'user.html',
        recent=recent,
        top_tags=top_tags,
        posts=user.posts
    )


if __name__ == '__main__':
    app.run()
