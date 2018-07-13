#!/usr/bin/python
# -*- coding: UTF-8 -*-

from flask import Flask, render_template, request, flash, redirect, url_for
# 操作mysql数据库
from flask_sqlalchemy import SQLAlchemy
# 创建表单类
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
# 验证是否有数据
from wtforms.validators import DataRequired

# 编码格式
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:3306/flask_books'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'iwillwin'
# 创建数据库对象
db = SQLAlchemy(app)
'''
1、 配置数据库
    a. 导入SQLalchemy扩展
    b. 创建db对象，并配置参数
    c. 终端创建数据库
2、 添加书和作者模型
    a. 模型继承db.Model
    b. 创建表名__tablename__
    c. 创建字段db.Column
    d. 关系引用, db.relationship
3、 添加数据
    a. 数据库中添加作者信息
    b. 数据库中添加书籍信息
4、 使用模板显示数据库查询的数据
    a. 查询所有信息，并传递给模板
    b. 模板中按照格式，依次for循环作者和书籍信息
5、 使用WTF显示表单
    a. 自定义表单类form
    b. 在模板中显示
    c. 设置secre_key、编码，以及在模板中添加csrf_token，否则会报错
6、 实现相关的增删逻辑
    a. 增加数据
    b. 删除书籍
    c. 删除作者
'''

# 定义查询模型
class Search(FlaskForm):
    bookName = StringField('书名：', validators = [DataRequired()])
    authorName = StringField('作者名：', validators = [DataRequired()])
    submit = SubmitField('提交')

# 定义作者模型
class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)
    # 关系引用
    books = db.relationship('Book', backref = 'author')

    def __repr__(self):
        return 'Author: %s' % self.name
# 书籍模型
class Book(db.Model):
    # 表名
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    # 外键
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

    def __repr__(self):
        return 'Author: %s %s' % (self.name, self.author_id)

@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    # 查询数据库是否有该ID的书
    book = Book.query.get(book_id)

    # 如果有删除
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print e
            flash('删除书籍出错')
            db.session.rollback()
    else:
        # 没有该书籍，提示错误
        flash('书籍找不到')

    # 重定向到当前网址
    # url_for,需要传入视图函数名，返回该视图函数对应的路由地址
    return redirect((url_for('index')))

@app.route('/delete_author/<author_id>')
def delete_author(author_id):
    # 查询数据库是否有该ID的作者
    author = Author.query.get(author_id)

    # 如果有就删除，先删除书
    if author:
        try:
            Book.query.filter_by(author_id=author.id).delete()
            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            print e
            flash('删除作者出错')
            db.session.rollback()
    else:
        # 没有该作者，提示错误
        flash('作者找不到')

    # 重定向到当前网址
    # url_for,需要传入视图函数名，返回该视图函数对应的路由地址
    return redirect((url_for('index')))

@app.route('/', methods=['GET', 'POST'])
def index():
    # 创建自定义表单对象
    search_from = Search()

    '''
    验证逻辑：
    1. 调用WTF的函数实现验证
    2. 验证通过获取数据
    3. 判断作者是否存在
    4. 如果作者存在，判断书籍是否存在，没有重复书籍就添加数据，如果重复就提示错误
    5. 如果作者不存在，添加作者和书籍
    6. 验证不通过就提示错误
    '''
    # if request.method == 'POST':
    #     return "%d" % (search_from.validate_on_submit())

    # 1. 调用WTF的函数实现验证
    if search_from.validate_on_submit():
        # 2. 验证通过获取数据
        author_name = search_from.authorName.data
        book_name = search_from.bookName.data

        # 3. 判断作者是否存在
        author = Author.query.filter_by(name = author_name).first()

        # 4. 如果作者存在
        if author:
            # 判断书籍是否存在，没有重复书籍就添加数据，如果重复就提示错误
            book = Book.query.filter_by(name = book_name).first()
            if book:
                flash("已存在同名书籍")
            else:
                try:
                    new_book = Book(name = book_name, author_id = author.id)
                    db.session.add(new_book)
                    db.session.commit()
                except Exception as e:
                    print e
                    flash("添加书失败")
                    db.session.rollback()
        # 5. 如果作者不存在，添加作者和书籍
        else:
            try:
                new_author = Author(name=author_name)
                db.session.add(new_author)
                db.session.commit()

                new_book = Book(name = book_name, author_id = new_author.id)
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                print e
                flash("添加作者和书籍失败")
                db.session.rollback()
    else:
        # 6. 验证不通过就提示错误
        if request.method == 'POST':
            flash('参数不全')

    # 查询作者所有信息
    authors = Author.query.all()

    return render_template('books.html', authors=authors, form=search_from)

if __name__ == '__main__':
    db.drop_all()
    db.create_all()

    # 生成数据
    au1 = Author(name = '老王')
    au2 = Author(name = '老惠')
    au3 = Author(name = '老刘')
    # 交给用户会话
    db.session.add_all([au1, au2, au3])
    # 提交到数据库
    db.session.commit()

    bk1 = Book(name = 'java提高', author_id = au1.id)
    bk2 = Book(name = 'C++从入门到放弃', author_id = au2.id)
    bk3 = Book(name = 'python提高', author_id = au3.id)
    bk4 = Book(name = '劲椎病治疗', author_id = au2.id)
    bk5 = Book(name = 'python入门', author_id = au1.id)

    db.session.add_all([bk1, bk2, bk3, bk4, bk5])
    db.session.commit()

    app.run(debug=True)
