from flask import *
import pymysql
from passlib.hash import pbkdf2_sha256 as pbk
from functools import wraps

app = Flask(__name__)
app.debug = True


book = [False]

# db = pymysql.connect(host='localhost',
#                      port=3306,
#                      user='root',
#                      passwd='1234',
#                      db='library_management_program'
#                     )

def is_logged_in(f):
    @wraps(f)
    def wrap (*args, **kwargs):
        if 'is_logged' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

def use_db(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        db = pymysql.connect(host='localhost',
                    port=3306,
                    user='root',
                    passwd='1234',
                    db='library_management_program'
                    )
        
        g = f.__globals__                               # 함수 지역변수 선언
                                                        # 개발자의 입장에서는 지역변수 선언 함수의 입장에서는 전역변수 선언
        g['db'] = db
        result = f(*args, **kwargs)
        db.close()

        return result
    return wrap


# wrap을 간단히 생각했을때
# def use_db(func):                 function을 인자 func로 받아온다   
#                                   @wraps은 생각하지 말기
#  def wrap(*args, **kwargs):       function에 어떤 인자가 들어올지 모르기에 *args, **kwargs 선언
#                                   
#                                   조건문이나 자신이 원하는 문구 작성

#         return func()             조건이 맞다면 func(*args, **kwargs) 를 return
#     return wrap                   def wrap 마무리
    

def is_logged_out(f):
    @wraps(f)
    def wraps(*args, **kwargs):
        if 'is_logged' in session:
            return redirect(url_for('login'))
        else:
            return f(*args, **kwargs)
    return wrap


def is_admin_in(f):
    @wraps(f)
    def wrap (*args, **kwargs):
        if session['admin'] == True:
            return f(*args, **kwargs)
        else:
            return render_template('home.html')     
    return wrap


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/introduce')
def introduce():
    return render_template('introduce.html')


@app.route('/register', methods = ['GET', 'POST'])
@use_db
def register():
    if (request.method == 'POST'):
        username = request.form.get('username')
        password = pbk.hash(request.form.get('password'))
        email = request.form.get('email')

        cursor = db.cursor()
        sql =   '''
                    INSERT INTO users (username, password, email)
                    VALUES (%s, %s, %s)
                '''
        print(username)
        print(password)
        print(email)
        cursor.execute(sql, (username, password, email))
        db.commit()
        return render_template('login.html')

    else:
        return render_template('register.html')
    db.close()



@app.route('/login', methods = ['GET', 'POST'])
@use_db
def login():
    if(request.method == 'POST'):
        username = request.form['username']
        password = request.form.get('password')
        sql = '''SELECT * FROM users WHERE username = %s'''
        cursor = db.cursor()
        cursor.execute(sql,[username])
        user = cursor.fetchone()
        
        if(user == None):
            print("유저가 없습니다!")
            return render_template('login.html')

        else:
            if(pbk.verify(password, user[2])):
                if(user[1] == 'admin'):
                    session['admin'] = True
                    session['username'] = user[1]
                    session['is_logged'] = True
                    return render_template('home.html')
                else:
                    session['admin'] = False
                    session['username'] = user[1]
                    session['is_logged'] = True
                    return render_template('home.html')
                    
            else:
                print("정보가 다릅니다")
                return redirect(url_for('login'))
        
    else:

        return render_template('login.html')
    

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/search')
def search():
    return render_template('search.html')
@app.route('/booklist')
@use_db
def booklist():
    bookname = request.args.get('bookname')
    sql = 'SELECT * FROM books WHERE bookname = %s'
    cursor = db.cursor()
    cursor.execute(sql,bookname)
    bookn = cursor.fetchall()
    if(bookn == None):
        print('책이 없슴다')
        return redirect(url_for('home'))
    else:
        return render_template('booklist.html',bookname = bookn)




@app.route('/management')
def management():
    return render_template('management.html')


@app.route('/bookborroworreturn')
def bookborroworreturn():
    return render_template('management/bookborroworreturn.html')
@app.route('/borrowing', methods=['GET', 'POST'])
@use_db
def borrowing():
    if(request.method == 'POST'):
        username = request.form.get('bookborroworreturnname')
        bookcode = request.form.get('bookborroworreturncode')
        cursor = db.cursor()

        sql_select_books_id =    '''
                                    SELECT id FROM books WHERE bookcode = %s
                                '''
        cursor.execute(sql_select_books_id,(bookcode))
        books_id = cursor.fetchone()

        sql_select_users_id =    '''
                                    SELECT id FROM users WHERE username = %s
                                '''
        cursor.execute(sql_select_users_id,[username])
        users_id = cursor.fetchone()

        sql_insert_rental = '''
                                INSERT INTO rentals(users_id, books_id)
                                VALUES (%s, %s)
                            '''
        cursor.execute(sql_insert_rental,[users_id, books_id])
        db.commit()
        return redirect(url_for('bookborroworreturn'))
    else:
        return redirect(url_for('bookborroworreturn'))
@app.route('/returning', methods=['GET', 'POST'])
@use_db
def returning():
    if(request.method == 'POST'):
        username = request.form.get('bookborroworreturnname')
        bookcode = request.form.get('bookborroworreturncode')
        cursor = db.cursor()

        sql_select_books_id =    '''
                                    SELECT id FROM books WHERE bookcode = %s
                                '''
        cursor.execute(sql_select_books_id,(bookcode))
        books_id = cursor.fetchone()

        sql_select_users_id =    '''
                                    SELECT id FROM users WHERE username = %s
                                '''
        cursor.execute(sql_select_users_id,(username))
        users_id = cursor.fetchone()

        sql_delete_rentals = '''
                                DELETE FROM rentals WHERE users_id = %s AND books_id = %s
                            '''
        cursor.execute(sql_delete_rentals,[users_id, books_id])
        db.commit()
        return redirect(url_for('bookborroworreturn'))
    else:
        return redirect(url_for('bookborroworreturn'))


@app.route('/bookwrite')
def bookwrite():
    return render_template('management/bookwrite.html')
@app.route('/writing')
@use_db
def writing():

    bookname = request.args.get('bookwritename')
    bookcode = request.args.get('bookwritecode')
    cursor = db.cursor()

    sql =   ''' 
                INSERT INTO books(bookname, bookcode)
                VALUES (%s, %s)
            '''
   
    cursor.execute(sql,(bookname,bookcode))
    db.commit()
    
    return redirect(url_for('bookwrite'))



@app.route('/bookdelete')
def bookdelete():
    return render_template('management/bookdelete.html')
@app.route('/booksdeleting', methods=['GET', 'POST'])
@use_db
def booksdeleting():
    if(request.method == 'POST'):
        bookcode = request.form.get('bookdeletecode')
        cursor=db.cursor()
        sql_books_delete =  '''
                                DELETE FROM books WHERE bookcode = %s
                            '''
        cursor.execute(sql_books_delete,(bookcode))
        db.commit()
        return redirect(url_for('bookdelete'))
    else:
        return redirect(url_for('bookdelete'))


@app.route('/userdelete')
def userdelete():
    return render_template('management/userdelete.html')
@app.route('/usersdeleting', methods = ['GET', 'POST'])
@use_db
def usersdeleting():
    if(request.method == 'POST'):
        username = request.form.get('usernamedelete')
        cursor=db.cursor()
        sql_users_delete =  '''
                                DELETE FROM users WHERE username = %s
                            '''
        cursor.execute(sql_users_delete, (username))
        db.commit()
        return redirect(url_for('userdelete'))
    else:
        return redirect(url_for('userdelete'))


@app.route('/mybooklist')
@use_db
def mybooklist():
    cursor = db.cursor()
    sql_mybooklist_select_users_id =    '''
                                            SELECT id FROM users WHERE username = %s
                                        '''
    cursor.execute(sql_mybooklist_select_users_id, session['username'])
    users_id = cursor.fetchone()

    sql_mybooklist_select_books_id =    '''
                                            SELECT books_id FROM rentals WHERE users_id = %s
                                        '''
    cursor.execute(sql_mybooklist_select_books_id, users_id)
    books_id = cursor.fetchall()
    
    if(books_id == None):
        return redirect(url_for('home'))
    else:
        rentalbooks=[]
        for i in books_id:
            sql_mybooklist_select_books =   '''
                                                SELECT bookname, bookcode FROM books where id = %s
                                            '''
            cursor.execute(sql_mybooklist_select_books, (i))
            rentalbooks.append(cursor.fetchone())
        
        return render_template('mybooklist.html', rentalbooks = rentalbooks)




if __name__ == '__main__':
    app.secret_key = '1234'
    app.run(host = '0.0.0.0', port = '5000')




# Left List : Book search, My Book List 보여주기, 대여기간... 및 추가기능 그외 대여중인 책 못 빌리는 등 else 처리 