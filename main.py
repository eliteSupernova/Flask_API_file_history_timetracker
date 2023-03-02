import base64
import datetime

import pymysql.cursors
from flask import Flask,request,jsonify
from flaskext.mysql import MySQL
app = Flask(__name__)

mysql=MySQL()
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']='password'
app.config['MYSQL_DATABASE_DB']='yt'
app.config['MYSQL_DATABASE_HOST']='localhost'
mysql.init_app(app)

conn=mysql.connect()
cur=conn.cursor(pymysql.cursors.DictCursor)

@app.route('/file',methods=['GET','POST'])
def file():
    try:
        view = 'select * from ytvideos;'
        create = 'create table ytvideos(id int primary key auto_increment,filename varchar(100),file longblob,starttime datetime);'
        cur.execute(create)
        conn.commit()

    except Exception as e:
        print(repr(e))
    new_file = request.files['file']
    base = new_file.read()
    store_file = base64.b64encode(base)
    # print(new_file.filename)
    # print(datetime.datetime.today())
    if request.method == 'POST':
        cur.execute(view)
        viewall=cur.fetchall()
        # print(viewall)
        file_already_exist=[i['filename'] for i in viewall]
        if new_file.filename in file_already_exist:
            print('file already exist')
        else:
            insert = 'insert into ytvideos(filename,file,starttime) values(%s,%s,%s)'
            val = (new_file.filename, store_file, datetime.datetime.today())
            cur.execute(insert, val)
            # cur.execute(alter)
            # cur.execute()
            conn.commit()

        return '1'


@app.route('/update',methods=['GET'])
def update():
    now = datetime.datetime.today()
    alter = 'alter table ytvideos add column(time_ago text(300));'
    view = 'select * from ytvideos;'
    cur.execute(view)
    viewall=cur.fetchall()
    time=[i['starttime'] for i in viewall]
    id=[i['id'] for i in viewall]
    id_time={id[i]:time[i] for i in range(len(viewall))}
    try:
        cur.execute(alter)
        conn.commit()
    except Exception as e:
        print(repr(e))
    for i,j in id_time.items():
        print(i,j)
        diff=now-j
        if diff.total_seconds()/60<60.00:
            new_val=f'{round(diff.total_seconds()/60,2)} min ago'
            cur.execute(('update ytvideos set time_ago=%s where id=%s'),(new_val,i))
            conn.commit()
        else:
            new_val=f'{round(diff.total_seconds()/60,2)} Hours ago'
            cur.execute(('update ytvideos set time_ago=%s where id=%s'),(new_val, i))
            conn.commit()
    return '1'


if __name__ == '__main__':
    app.run(debug=True)

