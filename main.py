from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify, request
import csv
import psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, time
import datetime as DT
# import pandas as pd
# import numpy as np
# from sklearn.linear_model import LinearRegression
# import statsmodels.api as sm
from datetime import datetime
from sklearn.metrics import mean_absolute_error, r2_score
# from docx import Document
# from docx.shared import Pt
# from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
# from docx.oxml.ns import nsdecls
# from docx.oxml import parse_xml
import random
from random import randint


# Задачи
# Сортировка по дате на странице просмотра
# Сделать текст красный при минусах, красный при плюсах в отчете
# Изменить функцию изменение IZm

from random import randint

# Создание экземляра класса
app = Flask(__name__)
# Создание ключа для сессий
app.secret_key = "super secret key"

# Подключение к базе данных
def get_db_connection():
   conn = psycopg2.connect(host='localhost',
                           database='Analiz',
                           user='postgres',
                           password='Lada$')
   return conn

# Главная страница приложения
@app.route('/')
def index():
    return render_template('in.html')


# @app.route('/u')
# def u():
#     return render_template('u.html')

# Страничка регистрации пользователя
@app.route('/registr', methods=['GET', 'POST'])
def registr():
    # Получение данных
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        print("ХЗ")
        # Create variables for easy access
        name = request.form['fullname']
        login = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']

        print(name, login, password, email, phone)

        # Хеширование пароля
        hash = generate_password_hash(password)
        check_password_hash(hash, password)

        # Открытие курсора для работы с БД
        conn = get_db_connection()
        cur = conn.cursor()


        # Check if account exists using MySQL
        cur.execute('SELECT * FROM users WHERE login = %s', (login,))
        account = cur.fetchone()
        print(account)

        cur.execute('SELECT * FROM adm WHERE login = %s', (login,))
        accountadm = cur.fetchone()
        # Проверка аккаунта
        if account:
            flash('Account already exists!')
        elif accountadm:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', login):
            flash('Username must contain only characters and numbers!')
        elif not login or not password or not email:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            # Добавление нового пользователя в базу
            cur.execute("INSERT INTO users (name, login, password, email, phone) VALUES (%s,%s,%s,%s,%s) RETURNING id_user",
                           (name, login, hash, email, phone))
            # Возвращенный id нового пользователя заносим в id_u
            id_u = cur.fetchall()[0]
            # print("ID покупателя: ", id_c[0])

            # Обновляем базу
            conn.commit()

            # Вывод сообщения при успеной регистрации
            flash('You have successfully registered!')

        # Закрываем подключение к базе
        cur.close()
        conn.close()

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    # Возвращаем страницу регистации, если никакие данные не поступают
    return render_template('registr.html')

@app.route('/registradm', methods=['GET', 'POST'])
def registradm():
    # Получение данных
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        print("нЯ")
        # Create variables for easy access
        name = request.form['fullname']
        login = request.form['username']
        password = request.form['password']
        email = request.form['email']

        print(name, login, password, email)

        # Хеширование пароля
        hash = generate_password_hash(password)
        check_password_hash(hash, password)

        # Открытие курсора для работы с БД
        conn = get_db_connection()
        cur = conn.cursor()


        # Check if account exists using MySQL
        cur.execute('SELECT * FROM adm WHERE login = %s', (login,))
        account = cur.fetchone()
        print(account)

        cur.execute('SELECT * FROM users WHERE login = %s', (login,))
        accountus = cur.fetchone()
        # Проверка аккаунта
        if account:
            flash('Account already exists!')
        elif accountus:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', login):
            flash('Username must contain only characters and numbers!')
        elif not login or not password or not email:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            # Добавление нового пользователя в базу
            cur.execute("INSERT INTO adm (name, login, email, password) VALUES (%s,%s,%s,%s) RETURNING id_adm",
                           (name, login, email, hash ))

            # Обновляем базу
            conn.commit()

            # Вывод сообщения при успеной регистрации
            flash('You have successfully registered!')

        # Закрываем подключение к базе
        cur.close()
        conn.close()

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    # Возвращаем страницу регистации, если никакие данные не поступают
    return render_template('registrAdm.html')

# Страничка входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        login = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if account exists using MySQL
        cur.execute('SELECT * FROM users WHERE login = %s', (login,))
        # Fetch one record and return result

        account = cur.fetchone()
        # Если аккаунт есть
        if account:
            # Достаем пароль из базы
            password_rs = account[5]
            # If account exists in users table in out database
            # Сравниваем пароль из базы и введенный
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                # Открываем сессию - пользователь в системе
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[2]
                # Получаем текущую дату и время
                d = datetime.now().date()
                t = datetime.now().time()

                # Добавляем запись о входе пользователя в аккаунт в базу
                cur.execute("INSERT INTO vhod_v_acc (date_vhod, time_vhod, id_user) VALUES (%s,%s,%s)",
                            (d, t, account[0]))
                conn.commit()

                # Redirect to home page
                # Переадресуем на домашнюю страницу
                return redirect(url_for('prosmotr'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password')

        # Если аккаунт в таблице Users не найден, смотрим таблицу Администарторы
        else:
            cur.execute('SELECT * FROM adm WHERE login = %s', (login,))
            account = cur.fetchone()
            if account:
                password_rs = account[4]
                print("Тут есть")
                print(password_rs)
                # If account exists in users table in out database
                if check_password_hash(password_rs, password):
                    # Create session data, we can access this data in other routes
                    session['loggedin'] = True
                    session['id'] = account[0]
                    session['username'] = account[2]

                    d = datetime.now().date()
                    t = datetime.now().time()

                    # Добавляем запись о входе пользователя в аккаунт в базу
                    cur.execute("INSERT INTO adm_actions (id_ac, date, time, id_adm) VALUES (%s,%s,%s,%s)",
                                (3, d, t, account[0]))
                    conn.commit()
                    # Переадресуем на домашнюю страницу администратора
                    return redirect(url_for('homeadm'))
            # Account doesnt exist or username/password incorrect
            # Если все мимо

            flash('Incorrect username/password')
        cur.close()
        conn.close()
    return render_template('base.html')

# Страничка выхода из системы
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))


# Домашняя страница пользователя
@app.route('/homeadm', methods=['POST', 'GET'])
def homeadm():

    # Check if user is loggedin
    if 'loggedin' in session:
        # Текущие время и дата
        d = datetime.now().date()
        t = datetime.now().time()

        conn = get_db_connection()
        cur = conn.cursor()
        res = []
        vosrast = []

        # Получаем всю информацию о текущем пользователе
        cur.execute('SELECT * FROM adm WHERE id_adm = %s', [session['id']])
        acc = cur.fetchone()


        return render_template('homeadm.html', username=session['username'], res=res, vosrast=vosrast, acc=acc)
    return redirect(url_for('login'))

# Страница удаления пользователя
@app.route('/delpols', methods=['POST', 'GET'])
def delpols():

    # Check if user is loggedin
    if 'loggedin' in session:
        # Текущие время и дата
        d = datetime.now().date()
        t = datetime.now().time()

        conn = get_db_connection()
        cur = conn.cursor()

        # Получаем всю информацию о текущем пользователе
        cur.execute('SELECT * FROM adm WHERE id_adm = %s', [session['id']])
        acc = cur.fetchone()

        # Получаем всю информацию о текущем пользователе
        cur.execute('SELECT * FROM users')
        users = cur.fetchall()

        if request.method == 'POST':
            id = request.form['user']
            print(id)
            try:
                cur.execute(
                    "DELETE FROM users WHERE id_user = %s;",
                    (id,))
                conn.commit()
                print("Прошел")
                d = datetime.now().date()
                t = datetime.now().time()

                # Добавляем запись о удалении администратором в аккаунт в базу
                cur.execute("INSERT INTO adm_actions (id_ac, date, time, id_adm) VALUES (%s,%s,%s,%s)",
                            (2, d, t, acc[0]))
                conn.commit()
                print("Прошел тут")
                cur.close()
                conn.close()
                return redirect(url_for('homeadm'))
            except:
                return "Ошибка"

        return render_template('delpols.html', username=session['username'], acc=acc, users=users)
    return redirect(url_for('login'))

@app.route('/aktiv', methods=['POST', 'GET'])
def aktiv():

    # Check if user is loggedin
    if 'loggedin' in session:
        # Текущие время и дата
        d = datetime.now().date()
        t = datetime.now().time()

        conn = get_db_connection()
        cur = conn.cursor()
        res = []
        vosrast = []

        # Получаем всю информацию о текущем пользователе
        cur.execute('SELECT * FROM users WHERE id_user = %s', [session['id']])
        acc = cur.fetchone()

        if request.method == 'POST':
        # Получение информации
            date = request.form['date']
            inn = request.form['inn']
            pok1 = request.form['pok1']
            pok2 = request.form['pok2']
            pok3 = request.form['pok3']
            pok4 = request.form['pok4']
            pok5 = request.form['pok5']
            pok6 = request.form['pok6']
            pok7 = request.form['pok7']
            pok8 = request.form['pok8']
            pok9 = request.form['pok9']
            pok10 = request.form['pok10']
            pok11 = request.form['pok11']
            pok12 = request.form['pok12']
            pok13 = request.form['pok13']
            pok14 = request.form['pok14']
            pok15 = request.form['pok15']
            pok16 = request.form['pok16']
            pok17 = request.form['pok17']

            # Изменение формата дат с str на date
            date = DT.datetime.strptime(date, '%d.%m.%Y').date()

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                       SELECT * FROM vn_aktivs WHERE year = %s and INN = %s and id_user = %s
                    """, (date, inn, acc[0],))
            proverk1 = cur.fetchone()

            cur.execute("""
                       SELECT * FROM ob_aktivs WHERE year = %s and INN = %s and id_user = %s
                            """, (date, inn, acc[0],))
            proverk2 = cur.fetchone()

            if proverk1 != None or proverk2 != None:
                return "На эту дату уже записаны данные!"

            cur.execute(
                        """
                             INSERT INTO vn_aktivs (INN, year, id_user, nemater_akt, res_issl_rasrab, nemater_poisk_akt,
                             mater_poisk_akt, ostov_sredstva, dohod_vlog_v_mat, fin_vlog, otlog_nalog_aktiv, proch_vneob_akt,
                             avans_na_kap_str, nezav_str)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """, (inn, date, acc[0], pok1, pok2, pok3, pok4, pok5, pok6, pok7, pok8, pok9, pok10, pok11,))
            conn.commit()

            cur.execute(
            """
                 INSERT INTO ob_aktivs  (INN, year, id_user, zapas, nalog_na_dob_st_po_pr_cen, debitor_zadolg, finans_vlog,
                  deneg_sredstv, proch_obor_aktiv)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (inn, date, acc[0], pok12, pok13, pok14, pok15, pok16, pok17,))
            conn.commit()

            cur.close()
            conn.close()
            return render_template('aktiv.html', username=session['username'], acc=acc)
        cur.close()
        conn.close()
        return render_template('aktiv.html', username=session['username'], acc=acc)
    # User is not loggedin redirect to login page

    return redirect(url_for('login'))

# Ввод данных (Пассивы)
@app.route('/passiv', methods=['POST', 'GET'])
def passiv():

    # Check if user is loggedin
    if 'loggedin' in session:
        # Текущие время и дата
        d = datetime.now().date()
        t = datetime.now().time()

        conn = get_db_connection()
        cur = conn.cursor()
        res = []
        vosrast = []

        # Получаем всю информацию о текущем пользователе
        cur.execute('SELECT * FROM users WHERE id_user = %s', [session['id']])
        acc = cur.fetchone()

        if request.method == 'POST':
        # Получение информации
            date = request.form['date']
            inn = request.form['inn']
            pok1 = request.form['pok1']
            pok2 = request.form['pok2']
            pok3 = request.form['pok3']
            pok4 = request.form['pok4']
            pok5 = request.form['pok5']
            pok6 = request.form['pok6']
            pok7 = request.form['pok7']
            pok8 = request.form['pok8']
            pok9 = request.form['pok9']
            pok10 = request.form['pok10']
            pok11 = request.form['pok11']
            pok12 = request.form['pok12']
            pok13 = request.form['pok13']
            pok14 = request.form['pok14']
            pok15 = request.form['pok15']

            conn = get_db_connection()
            cur = conn.cursor()

            # Изменение формата дат с str на date
            date = DT.datetime.strptime(date, '%d.%m.%Y').date()

            cur.execute("""
                           SELECT * FROM kap_reserv WHERE year = %s and INN = %s and id_user = %s
                        """, (date, inn, acc[0],))
            proverk1 = cur.fetchone()

            cur.execute("""
                           SELECT * FROM dolgosr_obzat WHERE year = %s and INN = %s and id_user = %s
                                """, (date, inn, acc[0],))
            proverk2 = cur.fetchone()

            cur.execute("""
                          SELECT * FROM kratkosr_obzat WHERE year = %s and INN = %s and id_user = %s
                                        """, (date, inn, acc[0],))
            proverk3 = cur.fetchone()

            if proverk1 != None or proverk2 != None or proverk3 != None:
                return "На эту дату уже записаны данные!"

            cur.execute(
                        """
                             INSERT INTO kap_reserv (INN, year, id_user, yst_kap, sob_akci, pereocenka_vn_akt, 
                             dobav_kap, reserv_kap, neraspred_prib)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """, (inn, date, acc[0], pok1, pok2, pok3, pok4, pok5, pok6,))
            conn.commit()

            cur.execute(
            """
                 INSERT INTO dolgosr_obzat  (INN, year, id_user, zaymn_sredstva, otl_nalog_ob, ocenoch_ob, 
                 proch_ob)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (inn, date, acc[0], pok7, pok8, pok9, pok10,))
            conn.commit()

            cur.execute(
            """
                 INSERT INTO kratkosr_obzat  (INN, year, id_user, zaymn_sredstva, kredit_zadolg, dohod_bydysh_periodov, 
                 ocenoch_ob, proch_ob)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (inn, date, acc[0], pok11, pok12, pok13, pok14, pok15,))
            conn.commit()

            cur.close()
            conn.close()
            return render_template('aktiv.html', username=session['username'], acc=acc)

        cur.close()
        conn.close()
        return render_template('passiv.html', username=session['username'], acc=acc)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Ввод данных (Финансовые результаты)
@app.route('/fin_res', methods=['POST', 'GET'])
def fin_res():

    # Check if user is loggedin
    if 'loggedin' in session:
        # Текущие время и дата
        d = datetime.now().date()
        t = datetime.now().time()

        conn = get_db_connection()
        cur = conn.cursor()
        res = []
        vosrast = []


        # Получаем всю информацию о текущем пользователе
        cur.execute('SELECT * FROM users WHERE id_user = %s', [session['id']])
        acc = cur.fetchone()

        if request.method == 'POST':
        # Получение информации
            date = request.form['date']
            inn = request.form['inn']
            pok1 = request.form['pok1']
            pok2 = request.form['pok2']
            pok3 = request.form['pok3']
            pok4 = request.form['pok4']
            pok5 = request.form['pok5']
            pok6 = request.form['pok6']
            pok7 = request.form['pok7']
            pok8 = request.form['pok8']
            pok9 = request.form['pok9']
            pok10 = request.form['pok10']
            pok11 = request.form['pok11']
            pok12 = request.form['pok12']
            pok13 = request.form['pok13']
            pok14 = request.form['pok14']

            conn = get_db_connection()
            cur = conn.cursor()

            # Изменение формата дат с str на date
            date = DT.datetime.strptime(date, '%d.%m.%Y').date()

            cur.execute("""
                        SELECT * FROM fin_res WHERE year = %s and INN = %s and id_user = %s
                """, (date, inn, acc[0],))
            proverk1 = cur.fetchone()

            cur.execute("""
                                SELECT * FROM nalog_na_pribl WHERE year = %s and INN = %s and id_user = %s
                        """, (date, inn, acc[0],))
            proverk2 = cur.fetchone()

            if proverk1 != None or proverk2 != None:
                return "На эту дату уже записаны данные!"

            cur.execute(
                        """
                             INSERT INTO fin_res (INN, year, id_user, vrychka, sebest_prodag, kommerchesk_rashod, 
                             ypravl_rashod, dohod_ot_ychast_v_dr_org, procent_k_polych, procent_k_yplat, proch_dohod, 
                             proch_rashod)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """, (inn, date, acc[0], pok1, pok2, pok3, pok4, pok5, pok6, pok7, pok8, pok9))
            conn.commit()

            cur.execute(
            """
                 INSERT INTO nalog_na_pribl  (INN, year, id_user, tek_nalog_na_pribl, otlog_nalog_na_pribl, 
                 izm_ot_nalog_ob, izm_ot_nalog_act, proch)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (inn, date, acc[0], pok10, pok11, pok13, pok14, pok12))
            conn.commit()


            cur.close()
            conn.close()
            return render_template('fin_res.html', username=session['username'], acc=acc)

        cur.close()
        conn.close()
        return render_template('fin_res.html', username=session['username'], acc=acc)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Просмотр
@app.route('/prosmotr', methods=['POST', 'GET'])
def prosmotr():

    # Check if user is loggedin
    if 'loggedin' in session:
        # Текущие время и дата
        d = datetime.now().date()
        t = datetime.now().time()

        conn = get_db_connection()
        cur = conn.cursor()
        res = []
        vosrast = []

        # Получаем всю информацию о текущем пользователе
        cur.execute('SELECT * FROM users WHERE id_user = %s', [session['id']])
        acc = cur.fetchone()

        cur.execute('SELECT * FROM vn_aktivs WHERE id_user = %s ORDER BY year, inn', [session['id']])
        vn_aktive = cur.fetchall()
        vn_aktive_len = len(vn_aktive)

        cur.execute('SELECT * FROM ob_aktivs WHERE id_user = %s ORDER BY year, inn', [session['id']])
        ob_aktive = cur.fetchall()
        ob_aktive_len = len(ob_aktive)

        cur.execute("""
                    SELECT balans_aktiv.id, balans_aktiv.id_vn_akt, balans_aktiv.id_ob_akt, itog_vn, itog_ob, balans FROM balans_aktiv 
                        JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
                        JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
                        WHERE vn_aktivs.id_user = %s and ob_aktivs.id_user = %s 
                        ORDER BY vn_aktivs.year, ob_aktivs.year, ob_aktivs.inn;
        """, (acc[0], acc[0],))
        balans_aktiv = cur.fetchall()

        cur.execute('SELECT * FROM kap_reserv WHERE id_user = %s ORDER BY year, inn', [session['id']])
        kap_reserv = cur.fetchall()
        kap_reserv_len = len(kap_reserv)
        cur.execute('SELECT * FROM kratkosr_obzat WHERE id_user = %s ORDER BY year, inn', [session['id']])
        kratkosr_obzat = cur.fetchall()
        kratkosr_obzat_len = len(kratkosr_obzat)
        cur.execute('SELECT * FROM dolgosr_obzat WHERE id_user = %s ORDER BY year, inn', [session['id']])
        dolgosr_obzat = cur.fetchall()
        dolgosr_obzat_len = len(dolgosr_obzat)

        cur.execute("""
                SELECT balans_passiv.id, balans_passiv.id_kap, balans_passiv.id_krat, id_dolg, itog_kap, itog_krat, itog_dolg, balans FROM balans_passiv
                JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
                JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
                JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
                WHERE kap_reserv.id_user = %s and kratkosr_obzat.id_user = %s and dolgosr_obzat.id_user = %s 
                ORDER BY kap_reserv.year, kap_reserv.inn
            """, (acc[0], acc[0], acc[0],))
        balans_passiv = cur.fetchall()

        cur.execute('SELECT * FROM fin_res WHERE id_user = %s ORDER BY year, inn', [session['id']])
        fin_res = cur.fetchall()
        fin_res_len = len(fin_res)
        cur.execute('SELECT * FROM nalog_na_pribl WHERE id_user = %s ORDER BY year, inn', [session['id']])
        nalog_na_prib = cur.fetchall()

        nalog_na_prib_len = len(nalog_na_prib)

        cur.execute("""
                    SELECT fin_res_rashchet.id, id_nalog_na_pribl, id_fin_res, val_pr, pr_ot_prodag, prib_do_nalog, nalog_na_pr, chist_pribl FROM fin_res_rashchet 
                    JOIN fin_res ON (fin_res.id = fin_res_rashchet.id_fin_res)
                    JOIN nalog_na_pribl ON (nalog_na_pribl.id = fin_res_rashchet.id_nalog_na_pribl)
                    WHERE fin_res.id_user = %s and nalog_na_pribl.id_user = %s 
                    ORDER BY fin_res.year, fin_res.inn 
                """, (acc[0], acc[0], ))
        fin_res_rashch = cur.fetchall()



        return render_template('prosmotr.html', username=session['username'], acc=acc, vn_aktive=vn_aktive, vn_aktive_len=vn_aktive_len,
                               ob_aktive=ob_aktive, ob_aktive_len=ob_aktive_len,
                               balans_aktiv=balans_aktiv, kap_reserv=kap_reserv,  kap_reserv_len=kap_reserv_len,
                               kratkosr_obzat=kratkosr_obzat, kratkosr_obzat_len=kratkosr_obzat_len, dolgosr_obzat_len=dolgosr_obzat_len,
                               dolgosr_obzat=dolgosr_obzat, balans_passiv=balans_passiv, fin_res=fin_res, nalog_na_prib=nalog_na_prib,
                               fin_res_rashch=fin_res_rashch, nalog_na_prib_len=nalog_na_prib_len, fin_res_len=fin_res_len)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Получение данных для анализа
@app.route('/analiz', methods=['POST', 'GET'])
def analiz():

    # Check if user is loggedin
    if 'loggedin' in session:
        # Текущие время и дата
        d = datetime.now().date()
        t = datetime.now().time()

        conn = get_db_connection()
        cur = conn.cursor()
        res = []
        vosrast = []

        # Получаем всю информацию о текущем пользователе
        cur.execute('SELECT * FROM users WHERE id_user = %s', [session['id']])
        acc = cur.fetchone()

        cur.execute("""
                   SELECT vn_aktivs.year FROM vn_aktivs, ob_aktivs, kap_reserv, dolgosr_obzat, kratkosr_obzat
                        WHERE vn_aktivs.year=ob_aktivs.year and vn_aktivs.year=kap_reserv.year and
                        vn_aktivs.year=dolgosr_obzat.year and vn_aktivs.year=kratkosr_obzat.year and 
                        vn_aktivs.id_user = %s and ob_aktivs.id_user = %s 
                        and kap_reserv.id_user = %s and dolgosr_obzat.id_user = %s and kratkosr_obzat.id_user = %s
                        GROUP BY vn_aktivs.year
                        ORDER BY vn_aktivs.year
                        
        """, (acc[0], acc[0], acc[0], acc[0], acc[0],))
        years = cur.fetchall()

        cur.execute("""
                   SELECT vn_aktivs.inn FROM vn_aktivs, ob_aktivs, kap_reserv, dolgosr_obzat, kratkosr_obzat
                        WHERE vn_aktivs.inn=ob_aktivs.inn and vn_aktivs.inn=kap_reserv.inn and
                        vn_aktivs.inn=dolgosr_obzat.inn and vn_aktivs.inn=kratkosr_obzat.inn and 
                        vn_aktivs.id_user = %s and ob_aktivs.id_user = %s 
                        and kap_reserv.id_user = %s and dolgosr_obzat.id_user = %s and kratkosr_obzat.id_user = %s
                        GROUP BY vn_aktivs.inn
        """, (acc[0], acc[0], acc[0], acc[0], acc[0],))
        inns = cur.fetchall()


        if request.method == "POST":
            year1 = request.form['years']
            year2 = request.form['years2']
            inn = request.form['inn']
            data_year1 = datetime.strptime(year1, "%Y-%m-%d").date()
            data_year2 = datetime.strptime(year2, "%Y-%m-%d").date()

            if data_year1 == data_year2:
                return "Начало и конец периода совпадают!"

            if data_year1 > data_year2:
                return "Первая дата должна быть раньше второй!"

            cur.execute("""
                               SELECT balans_aktiv.id FROM balans_aktiv
            	                    JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
            	                    JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
            	                    WHERE vn_aktivs.id_user = %s and ob_aktivs.id_user = %s
            	                    and vn_aktivs.inn = %s and ob_aktivs.inn = %s
            	                    and vn_aktivs.year >= %s and vn_aktivs.year <= %s
            	                    and ob_aktivs.year >= %s and ob_aktivs.year <= %s
            	                    ORDER BY vn_aktivs.year, ob_aktivs.year;
                    """, (acc[0], acc[0], inn, inn, data_year1, data_year2, data_year1, data_year2,))
            aktiv = cur.fetchall()

            cur.execute("""
                                      SELECT balans_passiv.id FROM balans_passiv
            	                            JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
            	                            JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
            	                            JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
            	                            WHERE kap_reserv.id_user = %s and dolgosr_obzat.id_user = %s and kratkosr_obzat.id_user = %s
            	                            and kap_reserv.inn = %s and dolgosr_obzat.inn = %s and kratkosr_obzat.inn = %s
            	                            and kap_reserv.year >= %s and kap_reserv.year <= %s
            	                            and dolgosr_obzat.year >= %s and dolgosr_obzat.year <= %s
            	                            and kratkosr_obzat.year >= %s and kratkosr_obzat.year <= %s
            	                            ORDER BY kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year;
                            """, (
            acc[0], acc[0], acc[0], inn, inn, inn, data_year1, data_year2, data_year1, data_year2, data_year1,
            data_year2,))
            passiv = cur.fetchall()

            if len(aktiv) < 2 or len(passiv) < 2:
                return "Недостаточно записей! Проверьте ИНН и записи на домашней странице"

            return redirect(url_for('Anotchet', inn=inn, data_year1=data_year1, data_year2=data_year2))

        return render_template('analiz.html', username=session['username'], acc=acc, years=years, inns=inns)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Функция для генерации текстового файла
def generate_text_file(aktiv, PROCENT, IZM, IMUSH, data_year1, data_year2, STOIMCHIST):
    with open('report.txt', 'w') as file:
        file.write('Анализ финансового положения\n\n')
        file.write('1.1 Структура имущества и источники его формирования\n\n')

        # Запись заголовков таблицы
        headers = ["Показатель"]

        headers.extend(["Зн. п. в % к валюте баланса на н.п.",
                        "Зн. п. в % к валюте баланса на к. п.",
                        "Из. за ан. п. (тыс. руб)",
                        "Из. за ан. п. (%)"])

        file.write("{:<60} {:<40} {:<40} {:<40} {:<40}\n".format(*headers))

        # Запись данных
        for i in range(len(IMUSH)):
            row = [IMUSH[i]]
            row.extend([PROCENT[i][0], PROCENT[i][1], IZM[i][0], IZM[i][1]])
            file.write("{:<60} {:<40} {:<40} {:<40} {:<40}\n".format(*row))

        text = """
        Структура активов организации на последний день анализируемого периода {0} характеризуется соотношением:
        {1}% внеоборотных активов и {2}% текущих. Активы организации за анализируемый период
        {3}
        на {4} (на {5}).

        {6}

        {7}

        {8}

        {9}
        """.format(data_year2, PROCENT[0][1], PROCENT[3][1], "увеличились" if IZM[12][0] > 0 else "уменьшились",
                   abs(IZM[12][0]), IZM[12][1],
                   "Имеет место рост внеоборотных и оборотных активов, что положительно характеризует динамику изменения имущественного положения организации." if
                                  IZM[0][1] > 0 and IZM[3][
                                      1] > 0 else "Отсутствует рост внеоборотных и оборотных активов.",
                   "Имеет место увеличение собственного капитала, что положительно характеризует динамику изменения имущественного положения организации." if
                                  IZM[7][1] > 0 else "Собственный капитал уменьшился.",
                   "Имеет место снижение долгосрочных и краткосрочных обязательств, что положительно характеризует динамику изменения имущественного положения организации." if
                                  IZM[8][1] > 0 and IZM[10][
                                      1] > 0 else "Долгосрочные и краткосрочные обязательства увеличились.",
                   "Имеет место укрепление валюты баланса, что положительно характеризует динамику изменения имущественного положения организации." if
                                  IZM[12][1] > 0 else "Валюта баланса уменьшилась.")


        file.write(text)
    return 'report.txt'

# Маршрут для генерации отчета
@app.route('/generate_report', methods=['GET', 'POST'])
def generate_report():
    # Здесь вы можете получить данные из базы данных Postgresql
    # Например, data = get_data_from_database()
    inn = request.args.get('inn')
    data_year1 = request.args.get('data_year1')  # Получение числа из параметров запроса
    data_year2 = request.args.get('data_year2')  # Получение массива из параметров запроса

    print(inn, data_year1, data_year2)
    data_year1 = datetime.strptime(data_year1, '%a, %d %b %Y %H:%M:%S %Z')
    data_year2 = datetime.strptime(data_year2, '%a, %d %b %Y %H:%M:%S %Z')

    data_year1 = data_year1.strftime("%Y-%m-%d")
    data_year2 = data_year2.strftime("%Y-%m-%d")

    conn = get_db_connection()
    cur = conn.cursor()

    # Получаем всю информацию о текущем пользователе
    cur.execute('SELECT * FROM users WHERE id_user = %s', [session['id']])
    acc = cur.fetchone()

    cur.execute("""
                       SELECT vn_aktivs.id, ob_aktivs.id, vn_aktivs.year, ob_aktivs.year, itog_vn, ostov_sredstva, nemater_akt, itog_ob, zapas, debitor_zadolg, 
                            deneg_sredstv, balans FROM balans_aktiv
    	                    JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
    	                    JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
    	                    WHERE vn_aktivs.id_user = %s and ob_aktivs.id_user = %s
    	                    and vn_aktivs.inn = %s and ob_aktivs.inn = %s
    	                    and vn_aktivs.year >= %s and vn_aktivs.year <= %s
    	                    and ob_aktivs.year >= %s and ob_aktivs.year <= %s
    	                    ORDER BY vn_aktivs.year, ob_aktivs.year;
            """, (acc[0], acc[0], inn, inn, data_year1, data_year2, data_year1, data_year2,))
    aktiv = cur.fetchall()

    cur.execute("""
                              SELECT kap_reserv.id, dolgosr_obzat.id, kratkosr_obzat.id, kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year, 
                                    itog_kap, itog_dolg, dolgosr_obzat.zaymn_sredstva, itog_krat, kratkosr_obzat.zaymn_sredstva,
                                    balans, kap_reserv.yst_kap FROM balans_passiv
    	                            JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
    	                            JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
    	                            JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
    	                            WHERE kap_reserv.id_user = %s and dolgosr_obzat.id_user = %s and kratkosr_obzat.id_user = %s
    	                            and kap_reserv.inn = %s and dolgosr_obzat.inn = %s and kratkosr_obzat.inn = %s
    	                            and kap_reserv.year >= %s and kap_reserv.year <= %s
    	                            and dolgosr_obzat.year >= %s and dolgosr_obzat.year <= %s
    	                            and kratkosr_obzat.year >= %s and kratkosr_obzat.year <= %s
    	                            ORDER BY kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year;
                    """, (
    acc[0], acc[0], acc[0], inn, inn, inn, data_year1, data_year2, data_year1, data_year2, data_year1, data_year2,))
    passiv = cur.fetchall()

    cur.execute("""
                              SELECT vn_aktivs.id, ob_aktivs.id, vn_aktivs.year, ob_aktivs.year, itog_vn, ostov_sredstva, nemater_akt, itog_ob, zapas, debitor_zadolg, 
                                   deneg_sredstv, balans FROM balans_aktiv
           	                    JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
           	                    JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
           	                    WHERE vn_aktivs.id_user = %s and ob_aktivs.id_user = %s
           	                    and vn_aktivs.inn = %s and ob_aktivs.inn = %s
           	                    and vn_aktivs.year = %s
           	                    and ob_aktivs.year = %s
           	                    ORDER BY vn_aktivs.year, ob_aktivs.year;
                   """, (acc[0], acc[0], inn, inn, data_year1, data_year1,))
    nach_aktiv = cur.fetchone()

    cur.execute("""
                              SELECT vn_aktivs.id, ob_aktivs.id, vn_aktivs.year, ob_aktivs.year, itog_vn, ostov_sredstva, nemater_akt, itog_ob, zapas, debitor_zadolg, 
                                   deneg_sredstv, balans FROM balans_aktiv
           	                    JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
           	                    JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
           	                    WHERE vn_aktivs.id_user = %s and ob_aktivs.id_user = %s
           	                    and vn_aktivs.inn = %s and ob_aktivs.inn = %s
           	                    and vn_aktivs.year = %s
           	                    and ob_aktivs.year = %s
           	                    ORDER BY vn_aktivs.year, ob_aktivs.year;
                   """, (acc[0], acc[0], inn, inn, data_year2, data_year2,))
    kon_aktiv = cur.fetchone()

    cur.execute("""
                                     SELECT kap_reserv.id, dolgosr_obzat.id, kratkosr_obzat.id, kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year, 
                                           itog_kap, itog_dolg, dolgosr_obzat.zaymn_sredstva, itog_krat, kratkosr_obzat.zaymn_sredstva,
                                           balans FROM balans_passiv
           	                            JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
           	                            JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
           	                            JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
           	                            WHERE kap_reserv.id_user = %s and dolgosr_obzat.id_user = %s and kratkosr_obzat.id_user = %s
           	                            and kap_reserv.inn = %s and dolgosr_obzat.inn = %s and kratkosr_obzat.inn = %s
           	                            and kap_reserv.year = %s 
           	                            and dolgosr_obzat.year = %s 
           	                            and kratkosr_obzat.year = %s
           	                            ORDER BY kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year;
                           """, (
        acc[0], acc[0], acc[0], inn, inn, inn, data_year1, data_year1, data_year1,))
    nach_passiv = cur.fetchone()

    cur.execute("""
                                     SELECT kap_reserv.id, dolgosr_obzat.id, kratkosr_obzat.id, kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year, 
                                           itog_kap, itog_dolg, dolgosr_obzat.zaymn_sredstva, itog_krat, kratkosr_obzat.zaymn_sredstva,
                                           balans FROM balans_passiv
           	                            JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
           	                            JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
           	                            JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
           	                            WHERE kap_reserv.id_user = %s and dolgosr_obzat.id_user = %s and kratkosr_obzat.id_user = %s
           	                            and kap_reserv.inn = %s and dolgosr_obzat.inn = %s and kratkosr_obzat.inn = %s
           	                            and kap_reserv.year = %s 
           	                            and dolgosr_obzat.year = %s 
           	                            and kratkosr_obzat.year = %s
           	                            ORDER BY kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year;
                           """, (
        acc[0], acc[0], acc[0], inn, inn, inn, data_year2, data_year2, data_year2,))
    kon_passiv = cur.fetchone()

    IMUSH = ["1. Внеоборотные активы", " в том числе: основные средства", " нематериальные активы",
             "2. Оборотные активы", " в том числе: запасы", " дебиторская задолженность",
             " денежные средства и краткосрочные финансовые вложения", "1. Собственный капитал",
             "2. Долгосрочные обязательства", " в том числе: заемные средства", "3. Краткосрочные обязательства",
             " в том числе: заемные средства", "Валюта баланса"]

    PROCENT, IZM = Imush(IMUSH, aktiv, passiv, nach_aktiv, kon_aktiv, nach_passiv, kon_passiv)

    STOIMCHIST = ["1. Чистые активы", "2. Уставной капитал", "3. Превышение чистых активов над уставным капиталом"]

    generate_text_file(aktiv, PROCENT, IZM, IMUSH, data_year1, data_year2, STOIMCHIST)

    return jsonify({'message': 'Отчет сформирован'})

# Маршрут для скачивания отчета
@app.route('/download_report', methods=['GET'])
def download_report():
    return send_file('report.txt', as_attachment=True)






# Проба создания pdf файла
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

def add_page_number(canvas, width, page_number):
    canvas.setFont("Arial", 10)  # Установка шрифта и размера текста для номера страницы
    canvas.drawRightString(width - 50, 20, f'Страница {page_number}')  # Позиционирование текста с учетом ширины
def generate_pdf_report22(aktiv, PROCENT, IZM, IMUSH, data_year1, data_year2, STOIMCHIST, CHIST, lYEARS):
    # Создаем имя файла с уникальной меткой времени
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    report_filename = f'report_{timestamp}.pdf'

    # Переворачиваем размеры страницы для ландшафтной ориентации
    landscape_letter = (letter[1], letter[0])

    c = canvas.Canvas(report_filename, pagesize=landscape_letter)
    width, height = landscape_letter  # Обновленные размеры для ландшафтной ориентации

    # Зарегистрируйте шрифт
    pdfmetrics.registerFont(TTFont('Arial', 'arialmt.ttf'))  # Убедитесь, что файл Arial.ttf доступен

    # Используйте шрифт Arial для отображения текста
    c.setFont("Arial", 12)

    # Заголовок
    c.drawString(30, height - 30, 'Анализ финансового положения')
    c.drawString(30, height - 50, '1.1 Структура имущества и источники его формирования')

    c.setFont("Arial", 8)

    # Заголовки таблицы
    headers = ["Показатель", "Зн. п. в % к валюте баланса на н.п.", "Зн. п. в % к валюте баланса на к. п.",
               "Из. за ан. п. (тыс. руб)", "Из. за ан. п. (%)"]
    x_pos, y_pos = 30, height - 70

    for header in headers:
        c.drawString(x_pos, y_pos, header)
        x_pos += 150  # Смещаемся по горизонтали

    y_pos -= 20  # Переходим на следующую строку

    # Данные таблицы
    for i in range(len(IMUSH)):
        x_pos = 30  # Обнуляем начальную позицию x для каждой строки
        row = [IMUSH[i]] + [str(x) for x in [PROCENT[i][0], PROCENT[i][1], IZM[i][0], IZM[i][1]]]
        for item in row:
            c.drawString(x_pos, y_pos, item)
            x_pos += 150  # Смещение по горизонтали
        y_pos -= 20  # Переход на следующую строку


    analysis_text = """
    - Структура активов организации на последний день анализируемого периода {0} характеризуется соотношением: 
    {1}% внеоборотных активов и {2}% текущих. 
    - Активы организации за анализируемый период {3} на {4} (на {5}).
    - {6}
    - {7}
    - {8}
    - {9}
    """.format(data_year2, PROCENT[0][1], PROCENT[3][1], "увеличились" if IZM[12][0] > 0 else "уменьшились",
               abs(IZM[12][0]), IZM[12][1],"Имеет место рост внеоборотных и оборотных активов,что положительно характеризует динамику\n изменения имущественного положения организации."
               if IZM[0][1] > 0 and IZM[3][1] > 0 else "Отсутствует рост внеоборотных и оборотных активов.",
           "Имеет место увеличение собственного капитала,что положительно характеризует динамику\n изменения имущественного положения организации."
               if IZM[7][1] > 0 else "Собственный капитал уменьшился.",
           "Имеет место снижение долгосрочных и краткосрочных обязательств,что положительно характеризует динамику\n изменения имущественного положения организации."
               if IZM[8][1] > 0 and IZM[10][1] > 0 else "Долгосрочные и краткосрочные обязательства увеличились.",
           "Имеет место укрепление валюты баланса, что положительно характеризует динамику\n изменения имущественного положения организации."
               if IZM[12][1] > 0 else "Валюта баланса уменьшилась.")

    text = c.beginText(30, y_pos - 30)
    text.setFont("Arial", 12)

    text.textLines(analysis_text.strip())
    c.drawText(text)
    #Номер страницы
    page_number = 1
    #Вызов функции для добавления страницы
    add_page_number(c, width, page_number)
    page_number += 1

    c.showPage()
    # Используйте шрифт Arial для отображения текста
    c.setFont("Arial", 12)
    # Заголовок
    c.drawString(30, height - 30, 'Анализ финансового положения')
    c.drawString(30, height - 50, '1.2 Оценка стоимости чистых активов организации')

    c.setFont("Arial", 8)
    # Заголовки таблицы
    headers = ["Показатель", "Зн. п. в % к валюте баланса на н.п.", "Зн. п. в % к валюте баланса на к. п.",
               "Из. за ан. п. (тыс. руб)", "Из. за ан. п. (%)"]
    x_pos, y_pos = 30, height - 70

    for header in headers:
        c.drawString(x_pos, y_pos, header)
        x_pos += 150  # Смещаемся по горизонтали
    y_pos -= 20  # Переходим на следующую строку

    # Данные таблицы
    for i in range(len(STOIMCHIST)):
        x_pos = 30  # Обнуляем начальную позицию x для каждой строки
        row = [STOIMCHIST[i]] + [str(x) for x in [CHIST[i][2], CHIST[i][3], CHIST[i][4], CHIST[i][5]]]
        for item in row:
            c.drawString(x_pos, y_pos, item)
            x_pos += 150  # Смещение по горизонтали
        y_pos -= 20  # Переход на следующую строку

    analysis_text2 = """
        - {0}
        - {1}
        """.format("Чистые активы превосходят уставной капитал, что характеризует положительное влияние на финансы компании."
                                       if CHIST[2][lYEARS-1] > 0
                                        else "Имеются потенциальные проблемы в финансовой устойчивости организации. Компания имеет недостаточно активов\n для покрытия своих обязательств.",
                   "Чистые активы на конец периода превосходят чистые активы на начало периода, что характеризует положительное влияние\n на финансы компании."
                                       if CHIST[0][lYEARS+2] > 0 else "Компания понесла убытки или сократила свои активы. Это может быть признаком\n финансовых трудностей или неэффективности управлением ресурсами. Для улучшения финансовой устойчивости нужно улучшить \n операционную деятельность, привлечь дополнительный капитала или заняться реструктуризацией долга."
                   )

    text = c.beginText(30, y_pos - 30)
    text.setFont("Arial", 12)

    text.textLines(analysis_text2.strip())
    c.drawText(text)
    add_page_number(c, width, page_number)
    page_number += 1
    c.save()

    return report_filename

@app.route('/generate_report22', methods=['GET','POST'])
def generate_report22():
    # Генерируем отчет
    print("Хожу тут")
    inn = request.args.get('inn')
    data_year1 = request.args.get('data_year1')  # Получение числа из параметров запроса
    data_year2 = request.args.get('data_year2')  # Получение массива из параметров запроса
    print(inn, data_year1, data_year2)

    data_year1 = datetime.strptime(data_year1, '%a, %d %b %Y %H:%M:%S %Z')
    data_year2 = datetime.strptime(data_year2, '%a, %d %b %Y %H:%M:%S %Z')

    data_year1 = data_year1.strftime("%Y-%m-%d")
    data_year2 = data_year2.strftime("%Y-%m-%d")

    conn = get_db_connection()
    cur = conn.cursor()

    # Получаем всю информацию о текущем пользователе
    cur.execute('SELECT * FROM users WHERE id_user = %s', [session['id']])
    acc = cur.fetchone()

    cur.execute("""
                       SELECT vn_aktivs.id, ob_aktivs.id, vn_aktivs.year, ob_aktivs.year, itog_vn, ostov_sredstva, nemater_akt, itog_ob, zapas, debitor_zadolg, 
                            deneg_sredstv, balans, finans_vlog FROM balans_aktiv
    	                    JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
    	                    JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
    	                    WHERE vn_aktivs.id_user = %s and ob_aktivs.id_user = %s
    	                    and vn_aktivs.inn = %s and ob_aktivs.inn = %s
    	                    and vn_aktivs.year >= %s and vn_aktivs.year <= %s
    	                    and ob_aktivs.year >= %s and ob_aktivs.year <= %s
    	                    ORDER BY vn_aktivs.year, ob_aktivs.year;
            """, (acc[0], acc[0], inn, inn, data_year1, data_year2, data_year1, data_year2,))
    aktiv = cur.fetchall()

    cur.execute("""
                              SELECT kap_reserv.id, dolgosr_obzat.id, kratkosr_obzat.id, kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year, 
                                    itog_kap, itog_dolg, dolgosr_obzat.zaymn_sredstva, itog_krat, kratkosr_obzat.zaymn_sredstva,
                                    balans, kap_reserv.yst_kap, dohod_bydysh_periodov FROM balans_passiv
    	                            JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
    	                            JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
    	                            JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
    	                            WHERE kap_reserv.id_user = %s and dolgosr_obzat.id_user = %s and kratkosr_obzat.id_user = %s
    	                            and kap_reserv.inn = %s and dolgosr_obzat.inn = %s and kratkosr_obzat.inn = %s
    	                            and kap_reserv.year >= %s and kap_reserv.year <= %s
    	                            and dolgosr_obzat.year >= %s and dolgosr_obzat.year <= %s
    	                            and kratkosr_obzat.year >= %s and kratkosr_obzat.year <= %s
    	                            ORDER BY kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year;
                    """, (
    acc[0], acc[0], acc[0], inn, inn, inn, data_year1, data_year2, data_year1, data_year2, data_year1, data_year2,))
    passiv = cur.fetchall()

    cur.execute("""
                               SELECT vn_aktivs.id, ob_aktivs.id, vn_aktivs.year, ob_aktivs.year, itog_vn, ostov_sredstva, nemater_akt, itog_ob, zapas, debitor_zadolg, 
                                    deneg_sredstv, balans, finans_vlog FROM balans_aktiv
            	                    JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
            	                    JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
            	                    WHERE vn_aktivs.id_user = %s and ob_aktivs.id_user = %s
            	                    and vn_aktivs.inn = %s and ob_aktivs.inn = %s
            	                    and vn_aktivs.year = %s
            	                    and ob_aktivs.year = %s
            	                    ORDER BY vn_aktivs.year, ob_aktivs.year;
                    """, (acc[0], acc[0], inn, inn, data_year1, data_year1,))
    nach_aktiv = cur.fetchone()

    cur.execute("""
                               SELECT vn_aktivs.id, ob_aktivs.id, vn_aktivs.year, ob_aktivs.year, itog_vn, ostov_sredstva, nemater_akt, itog_ob, zapas, debitor_zadolg, 
                                    deneg_sredstv, balans, finans_vlog FROM balans_aktiv
            	                    JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
            	                    JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
            	                    WHERE vn_aktivs.id_user = %s and ob_aktivs.id_user = %s
            	                    and vn_aktivs.inn = %s and ob_aktivs.inn = %s
            	                    and vn_aktivs.year = %s
            	                    and ob_aktivs.year = %s
            	                    ORDER BY vn_aktivs.year, ob_aktivs.year;
                    """, (acc[0], acc[0], inn, inn, data_year2, data_year2,))
    kon_aktiv = cur.fetchone()

    cur.execute("""
                                      SELECT kap_reserv.id, dolgosr_obzat.id, kratkosr_obzat.id, kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year, 
                                            itog_kap, itog_dolg, dolgosr_obzat.zaymn_sredstva, itog_krat, kratkosr_obzat.zaymn_sredstva,
                                            balans, kap_reserv.yst_kap, dohod_bydysh_periodov FROM balans_passiv
            	                            JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
            	                            JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
            	                            JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
            	                            WHERE kap_reserv.id_user = %s and dolgosr_obzat.id_user = %s and kratkosr_obzat.id_user = %s
            	                            and kap_reserv.inn = %s and dolgosr_obzat.inn = %s and kratkosr_obzat.inn = %s
            	                            and kap_reserv.year = %s 
            	                            and dolgosr_obzat.year = %s 
            	                            and kratkosr_obzat.year = %s
            	                            ORDER BY kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year;
                            """, (
        acc[0], acc[0], acc[0], inn, inn, inn, data_year1, data_year1, data_year1,))
    nach_passiv = cur.fetchone()

    cur.execute("""
                                      SELECT kap_reserv.id, dolgosr_obzat.id, kratkosr_obzat.id, kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year, 
                                            itog_kap, itog_dolg, dolgosr_obzat.zaymn_sredstva, itog_krat, kratkosr_obzat.zaymn_sredstva,
                                            balans, kap_reserv.yst_kap, dohod_bydysh_periodov FROM balans_passiv
            	                            JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
            	                            JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
            	                            JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
            	                            WHERE kap_reserv.id_user = %s and dolgosr_obzat.id_user = %s and kratkosr_obzat.id_user = %s
            	                            and kap_reserv.inn = %s and dolgosr_obzat.inn = %s and kratkosr_obzat.inn = %s
            	                            and kap_reserv.year = %s 
            	                            and dolgosr_obzat.year = %s 
            	                            and kratkosr_obzat.year = %s
            	                            ORDER BY kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year;
                            """, (
        acc[0], acc[0], acc[0], inn, inn, inn, data_year2, data_year2, data_year2,))
    kon_passiv = cur.fetchone()

    IMUSH = ["1. Внеоборотные активы", " в том числе: основные средства", " нематериальные активы",
             "2. Оборотные активы", " в том числе: запасы", " дебиторская задолженность",
             "ден. ср. и кр. фин. вложения", "1. Собственный капитал",
             "2. Долгосрочные обязательства", " в том числе: заемные средства", "3. Краткосрочные обязательства",
             " в том числе: заемные средства", "Валюта баланса"]

    PROCENT, IZM, lYEARS = Imush(IMUSH, aktiv, passiv, nach_aktiv, kon_aktiv, nach_passiv, kon_passiv)

    # Вторая таблица
    STOIMCHIST = ["1. Чистые активы", "2. Уставной капитал", "3. Превыш. чист. активов над уст. кап."]
    cur.execute("""
                                      SELECT kap_reserv.yst_kap, balans, kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year FROM balans_passiv
            	                            JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
            	                            JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
            	                            JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
            	                            WHERE kap_reserv.id_user = %s and dolgosr_obzat.id_user = %s and kratkosr_obzat.id_user = %s
            	                            and kap_reserv.inn = %s and dolgosr_obzat.inn = %s and kratkosr_obzat.inn = %s
            	                            and kap_reserv.year = %s 
            	                            and dolgosr_obzat.year = %s 
            	                            and kratkosr_obzat.year = %s
            	                            ORDER BY kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year;
                            """, (
        acc[0], acc[0], acc[0], inn, inn, inn, data_year1, data_year1, data_year1,))
    nach_yst = cur.fetchone()

    cur.execute("""
                                      SELECT kap_reserv.yst_kap, balans, kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year FROM balans_passiv
            	                            JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
            	                            JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
            	                            JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
            	                            WHERE kap_reserv.id_user = %s and dolgosr_obzat.id_user = %s and kratkosr_obzat.id_user = %s
            	                            and kap_reserv.inn = %s and dolgosr_obzat.inn = %s and kratkosr_obzat.inn = %s
            	                            and kap_reserv.year = %s 
            	                            and dolgosr_obzat.year = %s 
            	                            and kratkosr_obzat.year = %s
            	                            ORDER BY kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year;
                            """, (
        acc[0], acc[0], acc[0], inn, inn, inn, data_year2, data_year2, data_year2,))
    kon_yst = cur.fetchone()
    CHIST = Stoimchist(STOIMCHIST, nach_yst, kon_yst, lYEARS, nach_aktiv, kon_aktiv, nach_passiv, kon_passiv, passiv)

    report_filename = generate_pdf_report22(aktiv, PROCENT, IZM, IMUSH, data_year1, data_year2, STOIMCHIST, CHIST, lYEARS)
    try:
        return send_file(report_filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)})



# Вычисление данных для 1.1
def Imush(IMUSH, aktiv, passiv, nach_aktiv, kon_aktiv, nach_passiv, kon_passiv):

    YEARS = []
    for i in range(len(aktiv)):
        YEARS.append(aktiv[i][2])
    lYEARS = len(YEARS)
    lIMUSH = len(IMUSH)
    print('lYEARS = ', YEARS)
    print('lYEARS = ', lYEARS)

    N = 2
    PROCENT = [0] * lIMUSH
    for i in range(lIMUSH):
        PROCENT[i] = [0] * N

    print('PROCENT = ', PROCENT)
    k = 4
    p = 6

    for i in range(lIMUSH):
        if i < 7:
            PROCENT[i][0] = round(int(nach_aktiv[k]) / int(nach_aktiv[11]) * 100, 2)
            PROCENT[i][1] = round(int(kon_aktiv[k]) / int(kon_aktiv[11]) * 100, 2)
            k += 1
        else:
            PROCENT[i][0] = round(int(nach_passiv[p]) / int(nach_passiv[11]) * 100, 2)
            PROCENT[i][1] = round(int(kon_passiv[p]) / int(kon_passiv[11]) * 100, 2)
            p += 1
    print(PROCENT)

    N = 2
    IZM = [0] * lIMUSH
    for i in range(lIMUSH):
        IZM[i] = [0] * N
    k = 4
    p = 6
    for i in range(lIMUSH):
        if i < 7:
            IZM[i][0] = round(int(kon_aktiv[k]) - int(nach_aktiv[k]), 2)
            IZM[i][1] = round((int(kon_aktiv[k]) - int(nach_aktiv[k])) / int(nach_aktiv[k]) * 100, 2)

            k += 1
        else:
            IZM[i][0] = round(int(kon_passiv[p]) - int(nach_passiv[p]), 2)
            IZM[i][1] = round((int(kon_passiv[p]) - int(nach_passiv[p])) / int(nach_passiv[p]) * 100, 2)
            p += 1
    print(IZM)
    return PROCENT, IZM, lYEARS

# Вычисление данных для 1.2
def Stoimchist(STOIMCHIST, nach_yst, kon_yst, lYEARS, nach_aktiv, kon_aktiv, nach_passiv, kon_passiv, passiv):
    lSTOIMCHIST = len(STOIMCHIST)

    N = lYEARS + 2 + 2
    CHIST = [0] * lSTOIMCHIST
    for i in range(lSTOIMCHIST):
        CHIST[i] = [0] * N

    for i in range(lSTOIMCHIST):
        if i == 0:
            k = lYEARS
            for j in range(lYEARS):
                CHIST[i][j] = round(int(passiv[j][11] - passiv[j][7] - passiv[j][9]), 2)
            CHIST[i][k] = round(int(nach_passiv[11] - nach_passiv[7] - nach_passiv[9]) / int(nach_passiv[11]) * 100, 2)
            k += 1
            CHIST[i][k] = round(int(kon_passiv[11] - kon_passiv[7] - kon_passiv[9]) / int(kon_passiv[11]) * 100, 2)
            k += 1
            CHIST[i][k] = round(int(kon_passiv[11] - kon_passiv[7] - kon_passiv[9]) - int(
                nach_passiv[11] - nach_passiv[7] - nach_passiv[9]), 2)
            k += 1
            CHIST[i][k] = round((int(kon_passiv[11] - kon_passiv[7] - kon_passiv[9]) - int(
                nach_passiv[11] - nach_passiv[7] - nach_passiv[9])) / int(
                nach_passiv[11] - nach_passiv[7] - nach_passiv[9]) * 100, 2)
        if i == 1:
            k = lYEARS
            for j in range(lYEARS):
                CHIST[i][j] = int(passiv[j][12])
            CHIST[i][k] = round(int(nach_yst[0]) / int(nach_yst[1]) * 100, 2)
            k += 1
            CHIST[i][k] = round(int(kon_yst[0]) / int(kon_yst[1]) * 100, 2)
            k += 1
            CHIST[i][k] = round(int(kon_yst[0]) - int(nach_yst[0]), 2)
            k += 1
            CHIST[i][k] = round((int(kon_yst[0]) - int(nach_yst[0])) / int(nach_yst[0]) * 100, 2)
        if i == 2:
            k = lYEARS
            for j in range(lYEARS):
                CHIST[i][j] = round(int(passiv[j][11] - passiv[j][7] - passiv[j][9]) - int(passiv[j][12]), 2)
            CHIST[i][k] = round(int(nach_passiv[11] - nach_passiv[7] - nach_passiv[9]) / int(nach_passiv[11]) * 100,
                                2) - round(int(nach_yst[0]) / int(nach_yst[1]) * 100, 2)
            k += 1
            CHIST[i][k] = round(
                round(int(kon_passiv[11] - kon_passiv[7] - kon_passiv[9]) / int(kon_passiv[11]) * 100, 2) - round(
                    int(kon_yst[0]) / int(kon_yst[1]) * 100, 2))
            k += 1
            CHIST[i][k] = round(int(kon_passiv[11] - kon_passiv[7] - kon_passiv[9]) - int(
                nach_passiv[11] - nach_passiv[7] - nach_passiv[9]), 2) - round(int(kon_yst[0]) - int(nach_yst[0]), 2)
            k += 1
            CHIST[i][k] = round((int(kon_passiv[11] - kon_passiv[7] - kon_passiv[9]) - int(
                nach_passiv[11] - nach_passiv[7] - nach_passiv[9])) / int(
                nach_passiv[11] - nach_passiv[7] - nach_passiv[9]) * 100, 2) - round(
                (int(kon_yst[0]) - int(nach_yst[0])) / int(nach_yst[0]) * 100, 2)
    print("Чистые активы")
    print(CHIST)
    return CHIST

# Вычисление данных для 1.3.1
def Finustoich(FINUST, aktiv, passiv, lYEARS):

    lFINUST = len(FINUST)

    N = lYEARS + 2
    FIN = [0] * lFINUST
    for i in range(lFINUST):
        FIN[i] = [0] * N

    for i in range(lFINUST):
        if i == 0:
            k = lYEARS
            for j in range(lYEARS):
                FIN[i][j] = round(int(passiv[j][6]) / int(passiv[j][11]), 2)
            FIN[i][k] = round(FIN[i][k-1] - FIN[i][0], 2)
            k += 1
            FIN[i][k] = 'Отношение собственного капитала к общей сумме капитала. Оптимальное значение: 0,55-0,7.'
        if i == 1:
            k = lYEARS
            for j in range(lYEARS):
                FIN[i][j] = round(int(passiv[j][7] + passiv[j][9]) / int(passiv[j][6]), 2)
            FIN[i][k] = round(FIN[i][k - 1] - FIN[i][0], 2)
            k += 1
            FIN[i][k] = 'Отношение заемного капитала к собственному. Оптимальное значение: 0,43-0,82.'
        if i == 2:
            k = lYEARS
            for j in range(lYEARS):
                print(passiv[j][6])
                print(aktiv[j][4])
                print(aktiv[j][7])
                print(int(passiv[j][6] - aktiv[j][4]))
                FIN[i][j] = round((int(passiv[j][6] - aktiv[j][4]))/int(aktiv[j][7]), 2)

            FIN[i][k] = round(FIN[i][k-1] - FIN[i][0], 2)
            k += 1
            FIN[i][k] = 'Отношение собственных оборотных средств к оборотным активам. Нормальное значение: не менее 0,1.'
        if i == 3:
            k = lYEARS
            for j in range(lYEARS):
                FIN[i][j] = round(int(aktiv[j][4]) / int(passiv[j][6]), 2)
            FIN[i][k] = round(FIN[i][k - 1] - FIN[i][0], 2)
            k += 1
            FIN[i][k] = 'Отношение стоимости внеоборотных активов к величине собственного капитала организации.'
        if i == 4:
            k = lYEARS
            for j in range(lYEARS):
                FIN[i][j] = round(int(passiv[j][6] + passiv[j][7]) / int(passiv[j][11]), 2)
            FIN[i][k] = round(FIN[i][k - 1] - FIN[i][0], 2)
            k += 1
            FIN[i][k] = 'Отношение собственного капитала и долгосрочных обязательств к общей сумме капитала. Нормальное значение: не менее 0,7.'
        if i == 5:
            k = lYEARS
            for j in range(lYEARS):
                FIN[i][j] = round(int(passiv[j][6] - aktiv[j][4]) / int(passiv[j][6]), 2)
            FIN[i][k] = round(FIN[i][k - 1] - FIN[i][0], 2)
            k += 1
            FIN[i][k] = 'Отношение собственных оборотных средств к источникам собственных средств. Оптимальное значение: 0,2 и более.'
        if i == 6:
            k = lYEARS
            for j in range(lYEARS):
                FIN[i][j] = round(int(aktiv[j][7]) / int(passiv[j][11]), 2)
            FIN[i][k] = round(FIN[i][k - 1] - FIN[i][0], 2)
            k += 1
            FIN[i][k] = 'Отношение оборотных средств к стоимости всего имущества.'
        if i == 7:
            k = lYEARS
            for j in range(lYEARS):
                FIN[i][j] = round(int(aktiv[j][10]) / int(aktiv[j][7]), 2)
            FIN[i][k] = round(FIN[i][k - 1] - FIN[i][0], 2)
            k += 1
            FIN[i][k] = 'Отношение наиболее мобильной части оборотных средств (денежных средств и финансовых вложений) к общей стоимости оборотных активов.'
        if i == 8:
            k = lYEARS
            for j in range(lYEARS):
                FIN[i][j] = round(int(passiv[j][6] - aktiv[j][4]) / int(aktiv[j][8]), 2)
            FIN[i][k] = round(FIN[i][k - 1] - FIN[i][0], 2)
            k += 1
            FIN[i][
                k] = 'Отношение собственных оборотных средств к стоимости запасов. Нормальное значение: 0,5 и более.'
        if i == 9:
            k = lYEARS
            for j in range(lYEARS):
                FIN[i][j] = round(int(passiv[j][9]) / int(passiv[j][9] + passiv[j][7]), 2)
            FIN[i][k] = round(FIN[i][k - 1] - FIN[i][0], 2)
            k += 1
            FIN[i][
                k] = 'Отношение краткосрочной задолженности к общей сумме задолженности.'
    return FIN

# Вычисление данных для 1.3.2
def SobOborotAct(SOBOBOROTACT, aktiv, passiv, lYEARS, nach_aktiv, kon_aktiv, nach_passiv, kon_passiv):

    lSOBOBOROTACT = len(SOBOBOROTACT)

    N = lYEARS + 2
    SobObAct = [0] * lSOBOBOROTACT
    for i in range(lSOBOBOROTACT):
        SobObAct[i] = [0] * N

    for i in range(lSOBOBOROTACT):

        if i == 0:
            SobObAct[i][0] = round(int(nach_passiv[6] - nach_aktiv[4]), 2)
            SobObAct[i][1] = round(int(kon_passiv[6] - kon_aktiv[4]), 2)
            k = 2
            for j in range(lYEARS):
                SobObAct[i][k] = round(int(passiv[j][6] - aktiv[j][4] - aktiv[j][8]), 2)
                k += 1
        if i == 1:
            SobObAct[i][0] = round(int(nach_passiv[6] + nach_passiv[7] - nach_aktiv[4]), 2)
            SobObAct[i][1] = round(int(kon_passiv[6] + kon_passiv[7] - kon_aktiv[4]), 2)
            k = 2
            for j in range(lYEARS):
                SobObAct[i][k] = round(int(passiv[j][6] + passiv[j][7]  - aktiv[j][4] - aktiv[j][8]), 2)
                k += 1
        if i == 2:
            SobObAct[i][0] = round(int(nach_passiv[6] + nach_passiv[7] + nach_passiv[10] - nach_aktiv[4]), 2)
            SobObAct[i][1] = round(int(kon_passiv[6] + kon_passiv[7] + kon_passiv[10] - kon_aktiv[4]), 2)
            k = 2
            for j in range(lYEARS):
                SobObAct[i][k] = round(int(passiv[j][6] + passiv[j][7] + passiv[j][10] - aktiv[j][4] - aktiv[j][8]), 2)
                k += 1
    return SobObAct, N

# Вычисление данных для 1.4.1
def KOELIK(KOEFLIKV, aktiv, passiv, lYEARS):

    lKOEFLIKV = len(KOEFLIKV)

    N = lYEARS + 2
    KOE = [0] * lKOEFLIKV
    for i in range(lKOEFLIKV):
        KOE[i] = [0] * N

    for i in range(lKOEFLIKV):
        if i == 0:
            k = lYEARS
            for j in range(lYEARS):
                KOE[i][j] = round(int(aktiv[j][7]) / int(passiv[j][9]), 2)
            KOE[i][k] = round(KOE[i][k-1] - KOE[i][0], 2)
            k += 1
            KOE[i][k] = '2 и более'
        if i == 1:
            k = lYEARS
            for j in range(lYEARS):
                KOE[i][j] = round(int(aktiv[j][7] - aktiv[j][8]) / int(passiv[j][9]), 2)
            KOE[i][k] = round(KOE[i][k-1] - KOE[i][0], 2)
            k += 1
            KOE[i][k] = 'не менее 0.8'
        if i == 2:
            k = lYEARS
            for j in range(lYEARS):
                KOE[i][j] = round(int(aktiv[j][10] - aktiv[j][12]) / int(passiv[j][9] - passiv[j][13]), 2)
            KOE[i][k] = round(KOE[i][k-1] - KOE[i][0], 2)
            k += 1
            KOE[i][k] = '0.2 и более'
    return KOE


def SootAct(SOOTACTIV1, SOOTACTIV2, kon_aktiv, kon_passiv):

    lSOOTACTIV1 = len(SOOTACTIV1)
    lSOOTACTIV2 = len(SOOTACTIV2)
    N = 6

    SOOT = [0] * lSOOTACTIV1
    for i in range(lSOOTACTIV1):
        SOOT[i] = [0] * N

    for i in range(lSOOTACTIV1):
        if i == 0:
            SOOT[i][0] = SOOTACTIV1[i]
            SOOT[i][1] = round(int(kon_aktiv[10]) + int(kon_aktiv[12]), 2)
            SOOT[i][2] = '≥'
            SOOT[i][3] = SOOTACTIV2[i]
            SOOT[i][4] = round(int(kon_passiv[14]), 2)
            SOOT[i][5] = SOOT[i][1] - SOOT[i][4]
        if i == 1:
            SOOT[i][0] = SOOTACTIV1[i]
            SOOT[i][1] = round(int(kon_aktiv[9]), 2)
            SOOT[i][2] = '≥'
            SOOT[i][3] = SOOTACTIV2[i]
            SOOT[i][4] = round(int(kon_passiv[9] - kon_passiv[14]), 2)
            SOOT[i][5] = SOOT[i][1] - SOOT[i][4]
        if i == 2:
            SOOT[i][0] = SOOTACTIV1[i]
            SOOT[i][1] = round(int(kon_aktiv[13] + kon_aktiv[8] + kon_aktiv[14]), 2)
            SOOT[i][2] = '≥'
            SOOT[i][3] = SOOTACTIV2[i]
            SOOT[i][4] = round(int(kon_passiv[7]), 2)
            SOOT[i][5] = SOOT[i][1] - SOOT[i][4]
        if i == 3:
            SOOT[i][0] = SOOTACTIV1[i]
            SOOT[i][1] = round(int(kon_aktiv[4]), 2)
            SOOT[i][2] = '≤'
            SOOT[i][3] = SOOTACTIV2[i]
            SOOT[i][4] = round(int(kon_passiv[6]), 2)
            SOOT[i][5] = SOOT[i][1] - SOOT[i][4]
    return SOOT

def Obzor(OBZOR, fin, lYEARSFIN):
    lOBZOR = len(OBZOR)

    N = lYEARSFIN + 3
    OBZRESDEYTORG = [0] * lOBZOR
    for i in range(lOBZOR):
        OBZRESDEYTORG[i] = [0] * N

    for i in range(lOBZOR):
        if i == 0:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                OBZRESDEYTORG[i][j] = round(int(fin[j][5]), 2)
            OBZRESDEYTORG[i][k] = round(int(OBZRESDEYTORG[i][k-1] - OBZRESDEYTORG[i][0]), 2)
            k += 1
            if OBZRESDEYTORG[i][0] != 0:
                OBZRESDEYTORG[i][k] = round((OBZRESDEYTORG[i][lYEARSFIN - 1] - OBZRESDEYTORG[i][0])/(OBZRESDEYTORG[i][0]) * 100, 2)
            else:
                OBZRESDEYTORG[i][k] = 0
            k += 1
            sr = 0
            for j in range(lYEARSFIN):
                sr += int(OBZRESDEYTORG[i][j])
            OBZRESDEYTORG[i][k] = round(sr / lYEARSFIN, 3)
        if i == 1:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                OBZRESDEYTORG[i][j] = round(int(fin[j][6] + fin[j][8] + fin[j][9]), 2)
            OBZRESDEYTORG[i][k] = round(int(OBZRESDEYTORG[i][k - 1] - OBZRESDEYTORG[i][0]), 2)
            k += 1
            if OBZRESDEYTORG[i][0] != 0:
                OBZRESDEYTORG[i][k] = round((OBZRESDEYTORG[i][lYEARSFIN - 1] - OBZRESDEYTORG[i][0]) / (OBZRESDEYTORG[i][0]) * 100, 2)
            else:
                OBZRESDEYTORG[i][k] = 0
            k += 1
            sr = 0
            for j in range(lYEARSFIN):
                sr += int(OBZRESDEYTORG[i][j])
            OBZRESDEYTORG[i][k] = round(sr / lYEARSFIN, 3)
        if i == 2:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                OBZRESDEYTORG[i][j] = round(int(fin[j][10]), 2)
            OBZRESDEYTORG[i][k] = round(int(OBZRESDEYTORG[i][k - 1] - OBZRESDEYTORG[i][0]), 2)
            k += 1
            if OBZRESDEYTORG[i][0] != 0:
                OBZRESDEYTORG[i][k] = round((OBZRESDEYTORG[i][lYEARSFIN - 1] - OBZRESDEYTORG[i][0]) / (OBZRESDEYTORG[i][0]) * 100, 2)
            else:
                OBZRESDEYTORG[i][k] = 0
            k += 1
            sr = 0
            for j in range(lYEARSFIN):
                sr += int(OBZRESDEYTORG[i][j])
            OBZRESDEYTORG[i][k] = round(sr / lYEARSFIN, 3)
        if i == 3:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                OBZRESDEYTORG[i][j] = round(int(fin[j][12] + fin[j][14] - fin[j][15]), 2)
            OBZRESDEYTORG[i][k] = round(int(OBZRESDEYTORG[i][k - 1] - OBZRESDEYTORG[i][0]), 2)
            k += 1
            if OBZRESDEYTORG[i][0] != 0:
                OBZRESDEYTORG[i][k] = round((OBZRESDEYTORG[i][lYEARSFIN - 1] - OBZRESDEYTORG[i][0]) / (OBZRESDEYTORG[i][0]) * 100, 2)
            else:
                OBZRESDEYTORG[i][k] = 0
            k += 1
            sr = 0
            for j in range(lYEARSFIN):
                sr += int(OBZRESDEYTORG[i][j])
            OBZRESDEYTORG[i][k] = round(sr / lYEARSFIN, 3)
        if i == 4:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                OBZRESDEYTORG[i][j] = round(int(fin[j][10] + fin[j][12] + fin[j][14] - fin[j][15]), 2)
            OBZRESDEYTORG[i][k] = round(int(OBZRESDEYTORG[i][k - 1] - OBZRESDEYTORG[i][0]), 2)
            k += 1
            if OBZRESDEYTORG[i][0] != 0:
                OBZRESDEYTORG[i][k] = round((OBZRESDEYTORG[i][lYEARSFIN - 1] - OBZRESDEYTORG[i][0]) / (OBZRESDEYTORG[i][0]) * 100, 2)
            else:
                OBZRESDEYTORG[i][k] = 0
            k += 1
            sr = 0
            for j in range(lYEARSFIN):
                sr += int(OBZRESDEYTORG[i][j])
            OBZRESDEYTORG[i][k] = round(sr / lYEARSFIN, 3)
        if i == 5:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                OBZRESDEYTORG[i][j] = round(int(fin[j][13]), 2)
            OBZRESDEYTORG[i][k] = round(int(OBZRESDEYTORG[i][k - 1] - OBZRESDEYTORG[i][0]), 2)
            k += 1
            if OBZRESDEYTORG[i][0] != 0:
                OBZRESDEYTORG[i][k] = round((OBZRESDEYTORG[i][lYEARSFIN - 1] - OBZRESDEYTORG[i][0]) / (OBZRESDEYTORG[i][0]) * 100, 2)
            else:
                OBZRESDEYTORG[i][k] = 0
            k += 1
            sr = 0
            for j in range(lYEARSFIN):
                sr += int(OBZRESDEYTORG[i][j])
            OBZRESDEYTORG[i][k] = round(sr / lYEARSFIN, 3)
        if i == 6:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                OBZRESDEYTORG[i][j] = -round(int(fin[j][17] + fin[j][22]), 2)
            OBZRESDEYTORG[i][k] = round(int(OBZRESDEYTORG[i][k - 1] - OBZRESDEYTORG[i][0]), 2)
            k += 1
            if OBZRESDEYTORG[i][0] != 0:
                OBZRESDEYTORG[i][k] = -round((OBZRESDEYTORG[i][lYEARSFIN - 1] - OBZRESDEYTORG[i][0])/(OBZRESDEYTORG[i][0]) * 100, 2)
            else:
                OBZRESDEYTORG[i][k] = 0
            k += 1
            sr = 0
            for j in range(lYEARSFIN):
                sr += int(OBZRESDEYTORG[i][j])
            OBZRESDEYTORG[i][k] = round(sr / lYEARSFIN, 3)
        if i == 7:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                OBZRESDEYTORG[i][j] = round(int(fin[j][23]), 2)
            OBZRESDEYTORG[i][k] = round(int(OBZRESDEYTORG[i][k - 1] - OBZRESDEYTORG[i][0]), 2)
            k += 1
            if OBZRESDEYTORG[i][0] != 0:
                OBZRESDEYTORG[i][k] = round((OBZRESDEYTORG[i][lYEARSFIN - 1] - OBZRESDEYTORG[i][0])/(OBZRESDEYTORG[i][0]) * 100, 2)
            else:
                OBZRESDEYTORG[i][k] = 0
            k += 1
            sr = 0
            for j in range(lYEARSFIN):
                sr += int(OBZRESDEYTORG[i][j])
            OBZRESDEYTORG[i][k] = round(sr / lYEARSFIN, 3)
        if i == 8:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                OBZRESDEYTORG[i][j] = round(int(fin[j][23]), 2)
            OBZRESDEYTORG[i][k] = round(int(OBZRESDEYTORG[i][k - 1] - OBZRESDEYTORG[i][0]), 2)
            k += 1
            if OBZRESDEYTORG[i][0] != 0:
                OBZRESDEYTORG[i][k] = round((OBZRESDEYTORG[i][lYEARSFIN - 1] - OBZRESDEYTORG[i][0])/(OBZRESDEYTORG[i][0]) * 100, 2)
            else:
                OBZRESDEYTORG[i][k] = 0
            k += 1
            sr = 0
            for j in range(lYEARSFIN):
                sr += int(OBZRESDEYTORG[i][j])
            OBZRESDEYTORG[i][k] = round(sr / lYEARSFIN, 3)
    return OBZRESDEYTORG

def AnalizRent(RENTABEL, fin, lYEARSFIN):
    lRENTABEL = len(RENTABEL)

    N = lYEARSFIN + 2
    RENT = [0] * lRENTABEL
    for i in range(lRENTABEL):
        RENT[i] = [0] * N

    for i in range(lRENTABEL):
        if i == 0:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                RENT[i][j] = round((int(fin[j][10])/int(fin[j][5])) * 100, 2)
            RENT[i][k] = round(int(RENT[i][k - 1] - RENT[i][0]), 2)
            k += 1
            RENT[i][k] = round(
                (RENT[i][lYEARSFIN - 1] - RENT[i][0]) / (RENT[i][0]) * 100, 2)
        if i == 1:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                RENT[i][j] = round((int(fin[j][16] + fin[j][13])/int(fin[j][5])) * 100, 2)
            RENT[i][k] = round(int(RENT[i][k - 1] - RENT[i][0]), 2)
            k += 1
            RENT[i][k] = round(
                (RENT[i][lYEARSFIN - 1] - RENT[i][0]) / (RENT[i][0]) * 100, 2)
        if i == 2:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                RENT[i][j] = round((int(fin[j][23])/int(fin[j][5])) * 100, 2)
            RENT[i][k] = round(int(RENT[i][k - 1] - RENT[i][0]), 2)
            k += 1
            RENT[i][k] = round(
                (RENT[i][lYEARSFIN - 1] - RENT[i][0]) / (RENT[i][0]) * 100, 2)

        if i == 3:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                RENT[i][j] = round((int(fin[j][10])/int(fin[j][6] + fin[j][8] + fin[j][9])) * 100, 2)
            RENT[i][k] = round(int(RENT[i][k - 1] - RENT[i][0]), 2)
            k += 1
            RENT[i][k] = round(
                (RENT[i][lYEARSFIN - 1] - RENT[i][0]) / (RENT[i][0]) * 100, 2)

        if i == 4:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                RENT[i][j] = round((int(fin[j][16] + fin[j][13])/int(fin[j][13])), 2)
            RENT[i][k] = round(int(RENT[i][k - 1] - RENT[i][0]), 2)
            k += 1
            RENT[i][k] = round(
                (RENT[i][lYEARSFIN - 1] - RENT[i][0]) / (RENT[i][0]) * 100, 2)
    return RENT

def AnalizRent2(RENTABEL2, fin, lYEARSFIN, aktiv, passiv):
    lRENTABEL2 = len(RENTABEL2)

    N = lYEARSFIN + 2
    RENT2 = [0] * lRENTABEL2
    for i in range(lRENTABEL2):
        RENT2[i] = [0] * N

    for i in range(lRENTABEL2):
        if i == 0:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                RENT2[i][j] = round((int(fin[j][23]) / (int(passiv[j][6] + passiv[j+1][6])/2)) * 100, 3)
            RENT2[i][k] = round(RENT2[i][k - 1] - RENT2[i][0], 3)
            k += 1
            RENT2[i][k] = '18% и более'

        if i == 1:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                RENT2[i][j] = round((int(fin[j][23]) / (int(aktiv[j][4] + aktiv[j+1][4] + aktiv[j][7] + aktiv[j+1][7])/2)) * 100, 3)
            RENT2[i][k] = round(RENT2[i][k - 1] - RENT2[i][0], 3)
            k += 1
            RENT2[i][k] = 'не менее 9%'

        if i == 2:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                RENT2[i][j] = round((int(fin[j][10] + fin[j][12] + fin[j][14] - fin[j][15]) / (int(passiv[j][6] + passiv[j+1][6] + passiv[j][7] + passiv[j+1][7])/2)) * 100, 2)
            RENT2[i][k] = round(RENT2[i][k - 1] - RENT2[i][0], 3)
            k += 1
            RENT2[i][k] = '-'
    return RENT2

def Oborach(OBORACHIV, fin, lYEARSFIN,  aktiv, passiv):

    global SRactiv
    lOBORACHIV = len(OBORACHIV)

    N = lYEARSFIN + lYEARSFIN + 1
    OBR = [0] * lOBORACHIV
    for i in range(lOBORACHIV):
        OBR[i] = [0] * N
    OboAktiv = []
    for i in range(lOBORACHIV):
        if i == 0:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                OBR[i][j] = round(365 / (int(fin[j][5]) / (int(aktiv[j][7] + aktiv[j + 1][7]) / 2)), 1)
            for j in range(lYEARSFIN):
                OBR[i][k] = round((int(fin[j][5]) / (int(aktiv[j][7] + aktiv[j + 1][7]) / 2)), 2)
                k += 1
            OBR[i][k] = round(int(OBR[i][lYEARSFIN - 1] - OBR[i][0]), 2)

        if i == 1:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                OBR[i][j] = round(365 / (int(fin[j][5]) / (int(aktiv[j][8] + aktiv[j + 1][8]) / 2)), 1)
            for j in range(lYEARSFIN):
                OBR[i][k] = round((int(fin[j][5]) / (int(aktiv[j][8] + aktiv[j + 1][8]) / 2)), 2)
                k += 1
            OBR[i][k] = round(int(OBR[i][lYEARSFIN - 1] - OBR[i][0]), 2)

        if i == 2:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                OBR[i][j] = round(365 / (int(fin[j][5]) / (int(aktiv[j][9] + aktiv[j + 1][9]) / 2)), 1)
            for j in range(lYEARSFIN):
                OBR[i][k] = round((int(fin[j][5]) / (int(aktiv[j][9] + aktiv[j + 1][9]) / 2)), 2)
                k += 1
            OBR[i][k] = round(int(OBR[i][lYEARSFIN - 1] - OBR[i][0]), 2)

        if i == 3:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                OBR[i][j] = round(365 / (int(fin[j][5]) / (int(passiv[j][14] + passiv[j + 1][14]) / 2)), 1)
            for j in range(lYEARSFIN):
                OBR[i][k] = round((int(fin[j][5]) / (int(passiv[j][14] + passiv[j + 1][14]) / 2)), 2)
                k += 1
            OBR[i][k] = round(int(OBR[i][lYEARSFIN - 1] - OBR[i][0]), 2)


        if i == 4:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                OBR[i][j] = round(365 / (int(fin[j][5]) / (int(aktiv[j][11] + aktiv[j + 1][11]) / 2)), 1)
            for j in range(lYEARSFIN):
                OBR[i][k] = round((int(fin[j][5]) / (int(aktiv[j][11] + aktiv[j + 1][11]) / 2)), 2)
                if j == 0:
                    OboAktiv.append(round((int(fin[j][5]) / (int(aktiv[j][11] + aktiv[j + 1][11]) / 2)), 2))
                if j == lYEARSFIN-1:
                    OboAktiv.append(round((int(fin[j][5]) / (int(aktiv[j][11] + aktiv[j + 1][11]) / 2)), 2))
                k += 1
            OBR[i][k] = round(int(OBR[i][lYEARSFIN - 1] - OBR[i][0]), 2)

        if i == 5:
            k = lYEARSFIN
            for j in range(lYEARSFIN):
                OBR[i][j] = round(365 / (int(fin[j][5]) / (int(passiv[j][6] + passiv[j + 1][6]) / 2)), 1)
            for j in range(lYEARSFIN):
                OBR[i][k] = round((int(fin[j][5]) / (int(passiv[j][6] + passiv[j + 1][6]) / 2)), 2)
                k += 1
            OBR[i][k] = round(int(OBR[i][lYEARSFIN - 1] - OBR[i][0]), 2)

        SRactiv1 = 0.0
        for j in range(lYEARSFIN):
            SRactiv1 += OBR[4][j]
        SRactiv = SRactiv1/lYEARSFIN

    return OBR, SRactiv, OboAktiv

def FactornAnaliz(fin, lYEARSFIN,  aktiv, passiv, lYEARS):

    if lYEARSFIN == 2:

        FACTOR = []
        ACTsr = [] # 2 элемента
        SOBKAPsr = [] # 2 элемента
        RENT = []
        OBOR = []
        DOLE = []
        PROM = []

        ACTsr.append((int(aktiv[0][11] + aktiv[1][11]) / 2))
        ACTsr.append((int(aktiv[lYEARS-2][11] + aktiv[lYEARS-1][11]) / 2))


        SOBKAPsr.append((int(passiv[0][6] + passiv[1][6]) / 2))
        SOBKAPsr.append((int(passiv[lYEARS-2][6] + passiv[lYEARS-1][6]) / 2))

        RENT.append((int(fin[0][23])) / int(fin[0][5]))
        RENT.append((int(fin[lYEARSFIN-1][23])) / int(fin[lYEARSFIN-1][5]))

        print('RENT = ', RENT)
        OBOR.append((int(fin[0][5])) / ACTsr[0])
        OBOR.append(int(fin[lYEARSFIN-1][5]) / ACTsr[1])

        print('OBOR = ', OBOR)
        DOLE.append(ACTsr[0] / SOBKAPsr[0])
        DOLE.append(ACTsr[1] / SOBKAPsr[1])

        print('DOLE = ', DOLE)
        PROM.append(RENT[0]*OBOR[0]*DOLE[0])
        PROM.append(RENT[1]*OBOR[0]*DOLE[0])
        PROM.append(RENT[1]*OBOR[1]*DOLE[0])
        PROM.append(RENT[1]*OBOR[1]*DOLE[1])

        print('PROM = ', PROM)
        k = 1
        for i in range(len(PROM)-1):
            FACTOR.append(round((PROM[k]-PROM[i]) * 100, 4))
            k += 1
        Res = 0
        for i in range(len(FACTOR)):
            Res += FACTOR[i]
        FACTOR.append(round(Res, 4))

    else:
        FACTOR = []
        ACTsr = []  # 2 элемента
        SOBKAPsr = []  # 2 элемента
        RENT = []
        OBOR = []
        DOLE = []
        PROM1 = []
        PROM2 = []
        ACTsr.append((int(aktiv[0][11] + aktiv[1][11]) / 2))
        ACTsr.append((int(aktiv[lYEARS - 3][11] + aktiv[lYEARS - 2][11]) / 2))
        ACTsr.append((int(aktiv[lYEARS - 2][11] + aktiv[lYEARS - 1][11]) / 2))

        SOBKAPsr.append((int(passiv[0][6] + passiv[1][6]) / 2))
        SOBKAPsr.append((int(passiv[lYEARS - 3][6] + passiv[lYEARS - 2][6]) / 2))
        SOBKAPsr.append((int(passiv[lYEARS - 2][6] + passiv[lYEARS - 1][6]) / 2))

        RENT.append((int(fin[0][23])) / int(fin[0][5]))
        RENT.append((int(fin[lYEARSFIN - 2][23])) / int(fin[lYEARSFIN - 2][5]))
        RENT.append((int(fin[lYEARSFIN - 1][23])) / int(fin[lYEARSFIN - 1][5]))

        OBOR.append((float(fin[0][5])) / ACTsr[0])
        OBOR.append(float(fin[lYEARSFIN - 2][5]) / ACTsr[1])
        OBOR.append(float(fin[lYEARSFIN - 1][5]) / ACTsr[2])

        DOLE.append(ACTsr[0] / SOBKAPsr[0])
        DOLE.append(ACTsr[1] / SOBKAPsr[1])
        DOLE.append(ACTsr[2] / SOBKAPsr[2])

        PROM1.append(RENT[0] * OBOR[0] * DOLE[0])
        PROM1.append(RENT[2] * OBOR[0] * DOLE[0])
        PROM1.append(RENT[2] * OBOR[2] * DOLE[0])
        PROM1.append(RENT[2] * OBOR[2] * DOLE[2])

        PROM2.append(RENT[1] * OBOR[1] * DOLE[1])
        PROM2.append(RENT[2] * OBOR[1] * DOLE[1])
        PROM2.append(RENT[2] * OBOR[2] * DOLE[1])
        PROM2.append(RENT[2] * OBOR[2] * DOLE[2])

        k = 1
        for i in range(len(PROM1) - 1):
            FACTOR.append(round((PROM1[k] - PROM1[i]) * 100, 4))
            k += 1

        Res1 = 0
        for i in range(len(FACTOR)):
            Res1 += FACTOR[i]
        FACTOR.append(Res1)

        k = 1
        for i in range(len(PROM2) - 1):
            FACTOR.append(round((PROM2[k] - PROM2[i]) * 100, 4))
            k += 1

        FACTOR.append(round(FACTOR[4] + FACTOR[5] + FACTOR[6], 4))
    print(FACTOR)
    return FACTOR

# Результаты показателей
@app.route('/analiz/otchet/<inn>/<data_year1>/<data_year2>', methods=['POST', 'GET'])
def Anotchet(inn, data_year1, data_year2):
    # Check if user is loggedin
    if 'loggedin' in session:
        # Текущие время и дата
        d = datetime.now().date()

        t = datetime.now().time()

        data_year1 = datetime.strptime(data_year1, "%Y-%m-%d").date()
        data_year2 = datetime.strptime(data_year2, "%Y-%m-%d").date()

        conn = get_db_connection()
        cur = conn.cursor()

        # Получаем всю информацию о текущем пользователе
        cur.execute('SELECT * FROM users WHERE id_user = %s', [session['id']])
        acc = cur.fetchone()

        IMUSH = ["1. Внеоборотные активы", " в том числе: основные средства", " нематериальные активы",
                 "2. Оборотные активы", " в том числе: запасы", " дебиторская задолженность",
                 " денежные средства и краткосрочные финансовые вложения", "1. Собственный капитал",
                 "2. Долгосрочные обязательства", " в том числе: заемные средства", "3. Краткосрочные обязательства",
                 " в том числе: заемные средства", "Валюта баланса"]

        cur.execute("""
                   SELECT vn_aktivs.id, ob_aktivs.id, vn_aktivs.year, ob_aktivs.year, itog_vn, ostov_sredstva, 
                   nemater_akt, itog_ob, zapas, debitor_zadolg, 
                        deneg_sredstv, balans, finans_vlog, proch_obor_aktiv FROM balans_aktiv
	                    JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
	                    JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
	                    WHERE vn_aktivs.id_user = %s and ob_aktivs.id_user = %s
	                    and vn_aktivs.inn = %s and ob_aktivs.inn = %s
	                    and vn_aktivs.year >= %s and vn_aktivs.year <= %s
	                    and ob_aktivs.year >= %s and ob_aktivs.year <= %s
	                    ORDER BY vn_aktivs.year, ob_aktivs.year;
        """, (acc[0], acc[0], inn, inn, data_year1, data_year2, data_year1, data_year2, ))
        aktiv = cur.fetchall()

        cur.execute("""
                          SELECT kap_reserv.id, dolgosr_obzat.id, kratkosr_obzat.id, kap_reserv.year, dolgosr_obzat.year, 
                          kratkosr_obzat.year, 
                                itog_kap, itog_dolg, dolgosr_obzat.zaymn_sredstva, itog_krat, kratkosr_obzat.zaymn_sredstva,
                                balans, kap_reserv.yst_kap, dohod_bydysh_periodov, kredit_zadolg FROM balans_passiv
	                            JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
	                            JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
	                            JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
	                            WHERE kap_reserv.id_user = %s and dolgosr_obzat.id_user = %s and kratkosr_obzat.id_user = %s
	                            and kap_reserv.inn = %s and dolgosr_obzat.inn = %s and kratkosr_obzat.inn = %s
	                            and kap_reserv.year >= %s and kap_reserv.year <= %s
	                            and dolgosr_obzat.year >= %s and dolgosr_obzat.year <= %s
	                            and kratkosr_obzat.year >= %s and kratkosr_obzat.year <= %s
	                            ORDER BY kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year;
                """, (acc[0], acc[0], acc[0], inn, inn, inn, data_year1, data_year2, data_year1, data_year2, data_year1, data_year2, ))
        passiv = cur.fetchall()

        if len(aktiv) != len(passiv):
            return "Ошибка 1"

        for i in range(len(aktiv)):
            if aktiv[i][11] != passiv[i][11]:
                return "Ошибка! Сумма баланса активов и пассивов не равна! Проверьте значения на странице 'Просмотр'"

        YEARS = []
        for i in range(len(aktiv)):
            YEARS.append(aktiv[i][2])
        lYEARS = len(YEARS)
        lIMUSH = len(IMUSH)

        cur.execute("""
                           SELECT vn_aktivs.id, ob_aktivs.id, vn_aktivs.year, ob_aktivs.year, itog_vn, ostov_sredstva, nemater_akt, itog_ob, zapas, debitor_zadolg, 
                                deneg_sredstv, balans, finans_vlog FROM balans_aktiv
        	                    JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
        	                    JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
        	                    WHERE vn_aktivs.id_user = %s and ob_aktivs.id_user = %s
        	                    and vn_aktivs.inn = %s and ob_aktivs.inn = %s
        	                    and vn_aktivs.year = %s
        	                    and ob_aktivs.year = %s
        	                    ORDER BY vn_aktivs.year, ob_aktivs.year;
                """, (acc[0], acc[0], inn, inn, data_year1, data_year1,))
        nach_aktiv = cur.fetchone()

        cur.execute("""
                           SELECT vn_aktivs.id, ob_aktivs.id, vn_aktivs.year, ob_aktivs.year, itog_vn, ostov_sredstva, nemater_akt, itog_ob, zapas, debitor_zadolg, 
                                deneg_sredstv, balans, finans_vlog, proch_obor_aktiv, nalog_na_dob_st_po_pr_cen FROM balans_aktiv
        	                    JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
        	                    JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
        	                    WHERE vn_aktivs.id_user = %s and ob_aktivs.id_user = %s
        	                    and vn_aktivs.inn = %s and ob_aktivs.inn = %s
        	                    and vn_aktivs.year = %s
        	                    and ob_aktivs.year = %s
        	                    ORDER BY vn_aktivs.year, ob_aktivs.year;
                """, (acc[0], acc[0], inn, inn, data_year2, data_year2,))
        kon_aktiv = cur.fetchone()

        cur.execute("""
                                  SELECT kap_reserv.id, dolgosr_obzat.id, kratkosr_obzat.id, kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year, 
                                        itog_kap, itog_dolg, dolgosr_obzat.zaymn_sredstva, itog_krat, kratkosr_obzat.zaymn_sredstva,
                                        balans, kap_reserv.yst_kap, dohod_bydysh_periodov FROM balans_passiv
        	                            JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
        	                            JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
        	                            JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
        	                            WHERE kap_reserv.id_user = %s and dolgosr_obzat.id_user = %s and kratkosr_obzat.id_user = %s
        	                            and kap_reserv.inn = %s and dolgosr_obzat.inn = %s and kratkosr_obzat.inn = %s
        	                            and kap_reserv.year = %s 
        	                            and dolgosr_obzat.year = %s 
        	                            and kratkosr_obzat.year = %s
        	                            ORDER BY kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year;
                        """, (
        acc[0], acc[0], acc[0], inn, inn, inn, data_year1, data_year1, data_year1,))
        nach_passiv = cur.fetchone()


        cur.execute("""
                                  SELECT kap_reserv.id, dolgosr_obzat.id, kratkosr_obzat.id, kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year, 
                                        itog_kap, itog_dolg, dolgosr_obzat.zaymn_sredstva, itog_krat, kratkosr_obzat.zaymn_sredstva,
                                        balans, kap_reserv.yst_kap, dohod_bydysh_periodov, kredit_zadolg FROM balans_passiv
        	                            JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
        	                            JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
        	                            JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
        	                            WHERE kap_reserv.id_user = %s and dolgosr_obzat.id_user = %s and kratkosr_obzat.id_user = %s
        	                            and kap_reserv.inn = %s and dolgosr_obzat.inn = %s and kratkosr_obzat.inn = %s
        	                            and kap_reserv.year = %s 
        	                            and dolgosr_obzat.year = %s 
        	                            and kratkosr_obzat.year = %s
        	                            ORDER BY kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year;
                        """, (
        acc[0], acc[0], acc[0], inn, inn, inn, data_year2, data_year2, data_year2,))
        kon_passiv = cur.fetchone()

        PROCENT, IZM, lYEARS= Imush(IMUSH, aktiv, passiv, nach_aktiv, kon_aktiv, nach_passiv, kon_passiv)
        PRproch_ob = round(int(kon_aktiv[13] + kon_aktiv[10]) / int(kon_aktiv[11]) * 100, 2)
        ZaySob = round(IZM[9][1]/IZM[7][1], 2)
        KratDolg = round(IZM[10][1]/IZM[8][1], 2)
        data = [PROCENT[0][1], PRproch_ob, PROCENT[4][1], PROCENT[5][1]]

        # Вторая таблица
        STOIMCHIST = ["1. Чистые активы", "2. Уставной капитал", "3. Превышение чистых активов над уставным капиталом"]
        cur.execute("""
                                  SELECT kap_reserv.yst_kap, balans, kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year FROM balans_passiv
        	                            JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
        	                            JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
        	                            JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
        	                            WHERE kap_reserv.id_user = %s and dolgosr_obzat.id_user = %s and kratkosr_obzat.id_user = %s
        	                            and kap_reserv.inn = %s and dolgosr_obzat.inn = %s and kratkosr_obzat.inn = %s
        	                            and kap_reserv.year = %s 
        	                            and dolgosr_obzat.year = %s 
        	                            and kratkosr_obzat.year = %s
        	                            ORDER BY kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year;
                        """, (
        acc[0], acc[0], acc[0], inn, inn, inn, data_year1, data_year1, data_year1,))
        nach_yst = cur.fetchone()

        cur.execute("""
                                  SELECT kap_reserv.yst_kap, balans, kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year FROM balans_passiv
        	                            JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
        	                            JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
        	                            JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
        	                            WHERE kap_reserv.id_user = %s and dolgosr_obzat.id_user = %s and kratkosr_obzat.id_user = %s
        	                            and kap_reserv.inn = %s and dolgosr_obzat.inn = %s and kratkosr_obzat.inn = %s
        	                            and kap_reserv.year = %s 
        	                            and dolgosr_obzat.year = %s 
        	                            and kratkosr_obzat.year = %s
        	                            ORDER BY kap_reserv.year, dolgosr_obzat.year, kratkosr_obzat.year;
                        """, (
        acc[0], acc[0], acc[0], inn, inn, inn, data_year2, data_year2, data_year2,))
        kon_yst = cur.fetchone()
        CHIST = Stoimchist(STOIMCHIST, nach_yst, kon_yst, lYEARS, nach_aktiv, kon_aktiv, nach_passiv, kon_passiv, passiv)

        FINUST = ['1. Коэффициент автономности', '2. Коэффициент финансового левериджа', '3. Коэффициент обеспеченности собственными оборотными средствами',
                  '4. Индекс постоянного актива', '5. Коэффициент покрытия инвестиций', '6. Коэффициент маневренности собственного капитала',
                  '7. Коэффициент мобильности имущества', '8. Коэффициент мобильности оборотных средств', '9. Коэффициент обеспеченности запасов',
                  '10. Коэффициент краткосрочной задолженности']

        FIN = Finustoich(FINUST, aktiv, passiv, lYEARS)
        print(FIN)

        SOBOBOROTACT = ['СОС(1) (рассчитан без учета долгосрочных и краткосрочных пассивов)',
                  'СОС(2) (рассчитан с учетом долгосрочных пассивов; фактически равен чистому оборотному '
                  'капиталу, Net Working Capital)',
                  'СОС(3) (рассчитанные с учетом как долгосрочных пассивов, так и краткосрочной задолженности по кредитам и займам)']

        SobObAct, NSobObAct = SobOborotAct(SOBOBOROTACT,aktiv, passiv, lYEARS, nach_aktiv, kon_aktiv, nach_passiv, kon_passiv)
        print(SobObAct)

        KOEFLIKV = ['1. Коэффициент текущей (общей) ликвидности', '2. Коэффициент быстрой (промежуточной) ликвидности',
                    '3. Коэффициент абсолютной ликвидности']

        KOE = KOELIK(KOEFLIKV, aktiv, passiv, lYEARS)
        print(KOE)

        SOOTACTIV1 = ['A1. Высоколиквидные активы', 'А2. Быстрореализуемые активы', 'А3. Медленно реализуемые активы', 'А4. Труднореализуемые активы']
        SOOTACTIV2 = ['П1. Наиболее срочные обязательства', 'П2. Среднесрочные обязательства', 'П3. Долгосрочные обязательства',
                      'П4. Постоянные пассивы']

        SOOT = SootAct(SOOTACTIV1, SOOTACTIV2, kon_aktiv, kon_passiv)
        lSOOT = len(SOOT)


        if lYEARS <= 2:
            return render_template('analit_otchet.html', username=session['username'], acc=acc, inn=inn, aktiv=aktiv,
                                   passiv=passiv,
                                   YEARS=YEARS, lYEARS=lYEARS, IMUSH=IMUSH, lIMUSH=lIMUSH,
                                   PROCENT=PROCENT, IZM=IZM,
                                   data_year2=data_year2, CHIST=CHIST, STOIMCHIST=STOIMCHIST, data_year1=data_year1,
                                   FINUST=FINUST, FIN=FIN,
                                   SOBOBOROTACT=SOBOBOROTACT, SobObAct=SobObAct, NSobObAct=NSobObAct, KOEFLIKV=KOEFLIKV,
                                   KOE=KOE, SOOT=SOOT,
                                   lSOOT=lSOOT, data=data, ZaySob=ZaySob, KratDolg=KratDolg)
        # 2 часть
        cur.execute("""
                           SELECT fin_res.id, nalog_na_pribl.id, fin_res_rashchet.id, fin_res.year, fin_res.inn, vrychka, 
                           sebest_prodag, val_pr, kommerchesk_rashod, ypravl_rashod, pr_ot_prodag, 
                           dohod_ot_ychast_v_dr_org, procent_k_polych, procent_k_yplat, proch_dohod, proch_rashod, 
                           prib_do_nalog, nalog_na_pr, tek_nalog_na_pribl, otlog_nalog_na_pribl,izm_ot_nalog_ob,
                           izm_ot_nalog_act, proch, chist_pribl FROM fin_res_rashchet
                            JOIN fin_res ON (fin_res.id = fin_res_rashchet.id_fin_res)
        	                JOIN nalog_na_pribl ON (nalog_na_pribl.id = fin_res_rashchet.id_nalog_na_pribl)
        	                WHERE fin_res.id_user = %s and nalog_na_pribl.id_user = %s
        	                and fin_res.inn = %s and nalog_na_pribl.inn = %s
        	                and fin_res.year > %s and fin_res.year <= %s
        	                and nalog_na_pribl.year > %s and nalog_na_pribl.year <= %s
        	                ORDER BY fin_res.year, nalog_na_pribl.year;
                """, (acc[0], acc[0], inn, inn, data_year1, data_year2, data_year1, data_year2,))
        fin = cur.fetchall()

        YEARSFIN = []
        for i in range(len(fin)):
            YEARSFIN.append(fin[i][3])
        lYEARSFIN = len(YEARSFIN)

        if lYEARSFIN != lYEARS - 1:
            return render_template('analit_otchet.html', username=session['username'], acc=acc, inn=inn, aktiv=aktiv,
                                   passiv=passiv,
                                   YEARS=YEARS, lYEARS=lYEARS, IMUSH=IMUSH, lIMUSH=lIMUSH,
                                   PROCENT=PROCENT, IZM=IZM,
                                   data_year2=data_year2, CHIST=CHIST, STOIMCHIST=STOIMCHIST, data_year1=data_year1,
                                   FINUST=FINUST, FIN=FIN,
                                   SOBOBOROTACT=SOBOBOROTACT, SobObAct=SobObAct, NSobObAct=NSobObAct, KOEFLIKV=KOEFLIKV,
                                   KOE=KOE, SOOT=SOOT,
                                   lSOOT=lSOOT, lYEARSFIN=lYEARSFIN, data=data, ZaySob=ZaySob, KratDolg=KratDolg)

        OBZOR=['1. Выручка', '2. Расходы по обычным видам деятельности', '3. Прибыль (убыток) от продаж',
               '4. Прочие доходы и расходы, кроме процентов к уплате','5. EBIT ', '6. Проценты к уплате',
               '7. Налог на прибыль, изменение налоговых активов и прочее',
               '8. Чистая прибыль (убыток)', 'Справочно: Совокупный финансовый результат периода']

        OBZRESDEYTORG = Obzor(OBZOR, fin, lYEARSFIN)

        RENTABEL = ['1. Рентабельность продаж', '2. Рентабельность продаж по EBIT', '3. Рентабельность продаж по чистой прибыли',
                    'Cправочно: Прибыль от продаж на рубль, вложенный в производство и реализацию продукции', 'Коэффициент покрытия процентов к уплате (ICR)']

        RENT = AnalizRent(RENTABEL, fin, lYEARSFIN)

        RENTABEL2 = ['1. Рентабельность собственного капитала (ROE)', '2. Рентабельность активов (ROA)',
                     '3. Прибыль на задействованный капитал (ROCE)']

        RENT2 = AnalizRent2(RENTABEL2, fin, lYEARSFIN,  aktiv, passiv)

        OBORACHIV = ['1. Оборачиваемость оборотных средств', '2. Оборачиваемость запасов',
                     '3. Оборачиваемость дебиторской задолженности', '4. Оборачиваемость кредиторской задолженности',
                     '5. Оборачиваемость активов', '6. Оборачиваемость собственного капитала']

        OBR, SRactiv, OboAktiv = Oborach(OBORACHIV, fin, lYEARSFIN,  aktiv, passiv)

        FACTOR = FactornAnaliz(fin, lYEARSFIN,  aktiv, passiv, lYEARS)

        OBORACHIV = ['1. Оборачиваемость оборотных средств', '2. Оборачиваемость запасов',
                     '3. Оборачиваемость дебиторской задолженности', '4. Оборачиваемость кредиторской задолженности',
                     '5. Оборачиваемость активов', '6. Оборачиваемость собственного капитала']
        Reiting = []

        Reiting.append(round(2*FIN[2][0] + 0.1*KOE[0][0] + 0.08*OboAktiv[0] + 0.45*(RENT[0][0]/100) + (RENT2[0][0]/100), 2))
        Reiting.append(round(2 * FIN[2][lYEARS-1] + 0.1 * KOE[0][lYEARS-1] + 0.08 * OboAktiv[1] + 0.45 * (RENT[0][lYEARSFIN-1]/100) + (RENT2[0][lYEARSFIN-1]/100), 2))

        return render_template('analit_otchet.html', username=session['username'], acc=acc, inn=inn, aktiv=aktiv, passiv=passiv,
                               YEARS=YEARS, lYEARS=lYEARS, IMUSH=IMUSH, lIMUSH=lIMUSH,
                               PROCENT=PROCENT, IZM=IZM,
                               data_year2=data_year2, CHIST=CHIST, STOIMCHIST=STOIMCHIST, data_year1=data_year1, FINUST=FINUST, FIN=FIN,
                               SOBOBOROTACT=SOBOBOROTACT, SobObAct=SobObAct, NSobObAct=NSobObAct, KOEFLIKV=KOEFLIKV, KOE=KOE, SOOT=SOOT,
                               lSOOT=lSOOT, OBZRESDEYTORG=OBZRESDEYTORG, lYEARSFIN=lYEARSFIN, fin=fin, OBZOR=OBZOR, YEARSFIN=YEARSFIN,
                               RENTABEL=RENTABEL, RENT=RENT, RENTABEL2=RENTABEL2, RENT2=RENT2, OBORACHIV=OBORACHIV,
                               OBR=OBR, SRactiv=SRactiv, FACTOR=FACTOR, data=data, ZaySob=ZaySob, KratDolg=KratDolg, OboAktiv=OboAktiv,
                               Reiting=Reiting)

    return redirect(url_for('login'))


# Изменение
@app.route('/izmb/<par>/<id>', methods=['POST', 'GET'])
def Izm(par, id):
    # Check if user is loggedin

    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()

        # Получаем всю информацию о текущем пользователе
        cur.execute('SELECT * FROM users WHERE id_user = %s', [session['id']])
        acc = cur.fetchone()
        par = int(par)
        if request.method == "POST":
            if par == 0 or par == 1:

                inn = request.form['inn']
                pok1 = request.form['pok1']
                pok2 = request.form['pok2']
                pok3 = request.form['pok3']
                pok4 = request.form['pok4']
                pok5 = request.form['pok5']
                pok6 = request.form['pok6']
                pok7 = request.form['pok7']
                pok8 = request.form['pok8']
                pok9 = request.form['pok9']
                pok10 = request.form['pok10']
                pok11 = request.form['pok11']
                pok12 = request.form['pok12']
                pok13 = request.form['pok13']
                pok14 = request.form['pok14']
                pok15 = request.form['pok15']
                pok16 = request.form['pok16']
                pok17 = request.form['pok17']

                conn = get_db_connection()
                cur = conn.cursor()

                if par == 0:
                    cur.execute("""
                                        SELECT * FROM vn_aktivs WHERE vn_aktivs.id_user = %s and vn_aktivs.id = %s;
                             """, (acc[0], id,))
                    par_izm = cur.fetchone()

                    cur.execute("""
                                         SELECT * FROM ob_aktivs WHERE ob_aktivs.id_user = %s and ob_aktivs.year = %s and ob_aktivs.inn = %s;
                                         """, (acc[0], par_izm[3], par_izm[1],))
                    par_izm2 = cur.fetchone()

                    cur.execute(
                        """
                             UPDATE vn_aktivs SET inn = %s, nemater_akt = %s, res_issl_rasrab = %s,
                                nemater_poisk_akt = %s, mater_poisk_akt = %s, ostov_sredstva = %s,
                                dohod_vlog_v_mat = %s, fin_vlog = %s, otlog_nalog_aktiv = %s,
                                proch_vneob_akt = %s, avans_na_kap_str = %s, nezav_str = %s
                              WHERE id = %s;
                        """, (inn, pok1, pok2, pok3, pok4, pok5, pok6, pok7, pok8, pok9, pok10, pok11, id, ))
                    conn.commit()

                    cur.execute(
                        """
                             UPDATE ob_aktivs SET inn = %s, zapas = %s, nalog_na_dob_st_po_pr_cen = %s,
                                debitor_zadolg = %s, finans_vlog = %s, proch_obor_aktiv = %s,
                                deneg_sredstv = %s WHERE id = %s;
                        """, (inn, pok12, pok13, pok14, pok15, pok16, pok17, par_izm2[0]))
                    conn.commit()

                    itog_vn = int(pok1) + int(pok2) + int(pok3) + int(pok4) + int(pok5) + int(pok6) + int(pok7) + int(pok8) + int(pok9)
                    itog_ob = int(pok12) + int(pok13) + int(pok14) + int(pok15) + int(pok16) + int(pok17)
                    balans = itog_vn + itog_ob

                    print(itog_vn,' ', itog_ob, ' ',balans )

                    cur.execute(
                        """
                             UPDATE balans_aktiv SET itog_vn = %s, itog_ob = %s, balans = %s
                              WHERE id_vn_akt = %s and id_ob_akt = %s;
                        """, (itog_vn, itog_ob, balans, id, par_izm2[0],))
                    conn.commit()

                if par == 1:
                    cur.execute(""" SELECT * FROM ob_aktivs WHERE ob_aktivs.id_user = %s and ob_aktivs.id = %s; 
                                             """, (acc[0], id))
                    par_izm2 = cur.fetchone()

                    cur.execute(""" SELECT * FROM vn_aktivs WHERE vn_aktivs.id_user = %s and vn_aktivs.year = %s and vn_aktivs.inn = %s;
                                 """, (acc[0], par_izm2[3], par_izm2[1],))
                    par_izm = cur.fetchone()

                    print('Мб')
                    cur.execute(
                            """
                                 UPDATE vn_aktivs  SET inn = %s, nemater_akt = %s, res_issl_rasrab = %s,
                                    nemater_poisk_akt = %s, mater_poisk_akt = %s, ostov_sredstva = %s,
                                    dohod_vlog_v_mat = %s, fin_vlog = %s, otlog_nalog_aktiv = %s,
                                    proch_vneob_akt = %s, avans_na_kap_str = %s, nezav_str = %s
                                  WHERE id = %s;
                            """, (inn, pok1, pok2, pok3, pok4, pok5, pok6, pok7, pok8, pok9, pok10, pok11, par_izm[0],))
                    conn.commit()

                    cur.execute(
                            """
                                 UPDATE ob_aktivs SET inn = %s, zapas = %s, nalog_na_dob_st_po_pr_cen = %s,
                                    debitor_zadolg = %s, finans_vlog = %s, proch_obor_aktiv = %s,
                                    deneg_sredstv = %s WHERE id = %s;
                            """, (inn, pok12, pok13, pok14, pok15, pok16, pok17, par_izm2[0]))
                    conn.commit()

                    itog_vn = int(pok1) + int(pok2) + int(pok3) + int(pok4) + int(pok5) + int(pok6) + int(
                            pok7) + int(pok8) + int(pok9)
                    itog_ob = int(pok12) + int(pok13) + int(pok14) + int(pok15) + int(pok16) + int(pok17)
                    balans = itog_vn + itog_ob

                    print(itog_vn, ' ', itog_ob, ' ', balans)

                    cur.execute(
                            """
                                 UPDATE balans_aktiv SET itog_vn = %s, itog_ob = %s, balans = %s
                                  WHERE id_vn_akt = %s and id_ob_akt = %s;
                            """, (itog_vn, itog_ob, balans, par_izm[0], id,))
                    conn.commit()

            if par == 2 or par == 3 or par == 4:
                inn = request.form['inn2']
                pok1 = request.form['pok1p']
                pok2 = request.form['pok2p']
                pok3 = request.form['pok3p']
                pok4 = request.form['pok4p']
                pok5 = request.form['pok5p']
                pok6 = request.form['pok6p']
                pok7 = request.form['pok7p']
                pok8 = request.form['pok8p']
                pok9 = request.form['pok9p']
                pok10 = request.form['pok10p']
                pok11 = request.form['pok11p']
                pok12 = request.form['pok12p']
                pok13 = request.form['pok13p']
                pok14 = request.form['pok14p']
                pok15 = request.form['pok15p']

                conn = get_db_connection()
                cur = conn.cursor()

                if par == 2:
                    cur.execute(""" SELECT * FROM kap_reserv WHERE kap_reserv.id_user = %s and kap_reserv.id = %s; """
                                , (acc[0], id,))
                    kap = cur.fetchone()

                    cur.execute(""" SELECT * FROM balans_passiv WHERE id_kap = %s; """, (kap[0],))
                    bal = cur.fetchone()

                    cur.execute(
                        """
                             UPDATE kap_reserv SET inn = %s, yst_kap = %s, sob_akci = %s,
                                 pereocenka_vn_akt = %s, dobav_kap = %s, reserv_kap = %s,
                                 neraspred_prib = %s
                              WHERE id = %s;
                        """, (inn, pok1, pok2, pok3, pok4, pok5, pok6, id,))
                    conn.commit()

                    cur.execute(
                        """
                             UPDATE dolgosr_obzat SET inn = %s, zaymn_sredstva = %s, otl_nalog_ob = %s,
                               ocenoch_ob = %s, proch_ob = %s WHERE id = %s;
                        """, (inn, pok7, pok8, pok9, pok10, bal[3], ))
                    conn.commit()

                    cur.execute(
                        """
                             UPDATE kratkosr_obzat SET inn = %s, zaymn_sredstva = %s, kredit_zadolg = %s,
                               dohod_bydysh_periodov = %s, ocenoch_ob = %s, proch_ob = %s WHERE id = %s;
                        """, (inn, pok11, pok12, pok13, pok14, pok15, bal[2], ))
                    conn.commit()

                    itog_kap = int(pok1) + int(pok2) + int(pok3) + int(pok4) + int(pok5) + int(pok6)
                    itog_dolg = int(pok7) + int(pok8) + int(pok9) + int(pok10)
                    itog_krat = int(pok11) + int(pok12) + int(pok13) + int(pok14) + int(pok15)
                    balans = itog_kap + itog_dolg + itog_krat

                    cur.execute(
                        """
                             UPDATE balans_passiv SET itog_kap = %s, itog_krat = %s, itog_dolg = %s, balans = %s
                              WHERE id_kap = %s and id_krat = %s and id_dolg = %s;
                        """, (itog_kap, itog_krat, itog_dolg, balans, id, bal[2], bal[3]))
                    conn.commit()

                if par == 3:
                    cur.execute("""SELECT * FROM dolgosr_obzat WHERE dolgosr_obzat.id_user = %s and dolgosr_obzat.id = %s;
                                                    """, (acc[0], id,))
                    dolg = cur.fetchone()

                    cur.execute("""SELECT * FROM balans_passiv WHERE id_dolg = %s;
                                                        """, (dolg[0],))
                    bal = cur.fetchone()

                    cur.execute(
                        """
                             UPDATE kap_reserv SET inn = %s, yst_kap = %s, sob_akci = %s,
                                 pereocenka_vn_akt = %s, dobav_kap = %s, reserv_kap = %s,
                                 neraspred_prib = %s
                              WHERE id = %s;
                        """, (inn, pok1, pok2, pok3, pok4, pok5, pok6, bal[1],))
                    conn.commit()

                    cur.execute(
                        """
                             UPDATE dolgosr_obzat SET inn = %s, zaymn_sredstva = %s, otl_nalog_ob = %s,
                               ocenoch_ob = %s, proch_ob = %s WHERE id = %s;
                        """, (inn, pok7, pok8, pok9, pok10, id, ))
                    conn.commit()

                    cur.execute(
                        """
                             UPDATE kratkosr_obzat SET inn = %s, zaymn_sredstva = %s, kredit_zadolg = %s,
                               dohod_bydysh_periodov = %s, ocenoch_ob = %s, proch_ob = %s WHERE id = %s;
                        """, (inn, pok11, pok12, pok13, pok14, pok15, bal[2], ))
                    conn.commit()

                    itog_kap = int(pok1) + int(pok2) + int(pok3) + int(pok4) + int(pok5) + int(pok6)
                    itog_dolg = int(pok7) + int(pok8) + int(pok9) + int(pok10)
                    itog_krat = int(pok11) + int(pok12) + int(pok13) + int(pok14) + int(pok15)
                    balans = itog_kap + itog_dolg + itog_krat

                    cur.execute(
                        """
                             UPDATE balans_passiv SET itog_kap = %s, itog_krat = %s, itog_dolg = %s, balans = %s
                              WHERE id_kap = %s and id_krat = %s and id_dolg = %s;
                        """, (itog_kap, itog_krat, itog_dolg, balans, bal[1], bal[2], id, ))
                    conn.commit()

                if par == 4:
                    cur.execute(""" SELECT * FROM kratkosr_obzat WHERE kratkosr_obzat.id_user = %s and kratkosr_obzat.id = %s;
                                                        """, (acc[0], id,))
                    krat = cur.fetchone()

                    cur.execute(""" SELECT * FROM balans_passiv WHERE id_krat = %s; """, (krat[0],))
                    bal = cur.fetchone()

                    cur.execute(
                        """
                             UPDATE kap_reserv SET inn = %s, yst_kap = %s, sob_akci = %s,
                                 pereocenka_vn_akt = %s, dobav_kap = %s, reserv_kap = %s,
                                 neraspred_prib = %s
                              WHERE id = %s;
                        """, (inn, pok1, pok2, pok3, pok4, pok5, pok6, bal[1],))
                    conn.commit()

                    cur.execute(
                        """
                             UPDATE dolgosr_obzat SET inn = %s, zaymn_sredstva = %s, otl_nalog_ob = %s,
                               ocenoch_ob = %s, proch_ob = %s WHERE id = %s;
                        """, (inn, pok7, pok8, pok9, pok10, bal[3], ))
                    conn.commit()

                    cur.execute(
                        """
                             UPDATE kratkosr_obzat SET inn = %s, zaymn_sredstva = %s, kredit_zadolg = %s,
                               dohod_bydysh_periodov = %s, ocenoch_ob = %s, proch_ob = %s WHERE id = %s;
                        """, (inn, pok11, pok12, pok13, pok14, pok15, id, ))
                    conn.commit()

                    itog_kap = int(pok1) + int(pok2) + int(pok3) + int(pok4) + int(pok5) + int(pok6)
                    itog_dolg = int(pok7) + int(pok8) + int(pok9) + int(pok10)
                    itog_krat = int(pok11) + int(pok12) + int(pok13) + int(pok14) + int(pok15)
                    balans = itog_kap + itog_dolg + itog_krat
                    print(balans)
                    cur.execute(
                        """
                             UPDATE balans_passiv SET itog_kap = %s, itog_krat = %s, itog_dolg = %s, balans = %s
                              WHERE id_kap = %s and id_krat = %s and id_dolg = %s;
                        """, (itog_kap, itog_krat, itog_dolg, balans, bal[1], id, bal[3]), )
                    conn.commit()


            cur.execute('SELECT * FROM vn_aktivs WHERE id_user = %s ORDER BY year', [session['id']])
            vn_aktive = cur.fetchall()
            vn_aktive_len = len(vn_aktive)

            cur.execute('SELECT * FROM ob_aktivs WHERE id_user = %s ORDER BY year', [session['id']])
            ob_aktive = cur.fetchall()
            ob_aktive_len = len(ob_aktive)

            cur.execute("""
                                    SELECT balans_aktiv.id, balans_aktiv.id_vn_akt, balans_aktiv.id_ob_akt, itog_vn, itog_ob, balans FROM balans_aktiv 
                                        JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
                                        JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
                                        WHERE vn_aktivs.id_user = %s and ob_aktivs.id_user = %s 
                                        ORDER BY vn_aktivs.year, ob_aktivs.year;
                        """, (acc[0], acc[0],))
            balans_aktiv = cur.fetchall()

            cur.execute('SELECT * FROM kap_reserv WHERE id_user = %s ORDER BY year', [session['id']])
            kap_reserv = cur.fetchall()
            kap_reserv_len = len(kap_reserv)
            cur.execute('SELECT * FROM kratkosr_obzat WHERE id_user = %s ORDER BY year', [session['id']])
            kratkosr_obzat = cur.fetchall()
            kratkosr_obzat_len = len(kratkosr_obzat)
            cur.execute('SELECT * FROM dolgosr_obzat WHERE id_user = %s ORDER BY year', [session['id']])
            dolgosr_obzat = cur.fetchall()
            dolgosr_obzat_len = len(dolgosr_obzat)

            cur.execute("""
                                SELECT balans_passiv.id, balans_passiv.id_kap, balans_passiv.id_krat, id_dolg, itog_kap, itog_krat, itog_dolg, balans FROM balans_passiv
                                JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
                                JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
                                JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
                                WHERE kap_reserv.id_user = %s and kratkosr_obzat.id_user = %s and dolgosr_obzat.id_user = %s 
                                ORDER BY kap_reserv.year
                            """, (acc[0], acc[0], acc[0],))
            balans_passiv = cur.fetchall()

            cur.execute('SELECT * FROM fin_res WHERE id_user = %s ORDER BY year', [session['id']])
            fin_res = cur.fetchall()
            cur.execute('SELECT * FROM nalog_na_pribl WHERE id_user = %s ORDER BY year', [session['id']])
            nalog_na_prib = cur.fetchall()

            nalog_na_prib_len = len(nalog_na_prib)

            cur.execute("""
                                    SELECT fin_res_rashchet.id, id_nalog_na_pribl, id_fin_res, val_pr, pr_ot_prodag, prib_do_nalog, nalog_na_pr, chist_pribl FROM fin_res_rashchet 
                                    JOIN fin_res ON (fin_res.id = fin_res_rashchet.id_fin_res)
                                    JOIN nalog_na_pribl ON (nalog_na_pribl.id = fin_res_rashchet.id_nalog_na_pribl)
                                    WHERE fin_res.id_user = %s and nalog_na_pribl.id_user = %s 
                                    ORDER BY fin_res.year
                                """, (acc[0], acc[0],))
            fin_res_rashch = cur.fetchall()

            cur.close()
            conn.close()
            return render_template('prosmotr.html', username=session['username'], acc=acc, vn_aktive=vn_aktive,
                               vn_aktive_len=vn_aktive_len,
                               ob_aktive=ob_aktive, ob_aktive_len=ob_aktive_len,
                               balans_aktiv=balans_aktiv, kap_reserv=kap_reserv, kap_reserv_len=kap_reserv_len,
                               kratkosr_obzat=kratkosr_obzat, kratkosr_obzat_len=kratkosr_obzat_len,
                               dolgosr_obzat_len=dolgosr_obzat_len,
                               dolgosr_obzat=dolgosr_obzat, balans_passiv=balans_passiv, fin_res=fin_res,
                               nalog_na_prib=nalog_na_prib,
                               fin_res_rashch=fin_res_rashch, nalog_na_prib_len=nalog_na_prib_len)

        if int(par) == 0 or int(par) == 1:
            if int(par) == 0:
                cur.execute("""
                               SELECT * FROM vn_aktivs WHERE vn_aktivs.id_user = %s and vn_aktivs.id = %s;
                    """, (acc[0], id,))
                par_izm = cur.fetchone()

                cur.execute("""
                                SELECT * FROM ob_aktivs WHERE ob_aktivs.id_user = %s and ob_aktivs.year = %s and ob_aktivs.inn = %s;
                                """, (acc[0], par_izm[3], par_izm[1],))
                par_izm2 = cur.fetchone()

                date = datetime.strptime(str(par_izm[3]), "%Y-%m-%d").strftime("%d.%m.%Y")
            else:

                cur.execute("""
                                                SELECT * FROM ob_aktivs WHERE ob_aktivs.id_user = %s and ob_aktivs.id = %s; 
                                                """, (acc[0], id,))
                par_izm2 = cur.fetchone()

                cur.execute("""
                                                SELECT * FROM vn_aktivs WHERE vn_aktivs.id_user = %s and vn_aktivs.year = %s and vn_aktivs.inn = %s;
                                     """, (acc[0], par_izm2[3], par_izm2[1],))
                par_izm = cur.fetchone()

                date = datetime.strptime(str(par_izm2[3]), "%Y-%m-%d").strftime("%d.%m.%Y")
            return render_template('izm.html', username=session['username'], acc=acc, id=id, par=par, par_izm=par_izm, date=date, par_izm2=par_izm2)

        if int(par) == 2 or int(par) == 3 or int(par) == 4:
            kap = 0
            bal = 0
            date = 0
            krat = 0
            dolg = 0

            if int(par) == 2:
                cur.execute("""
                               SELECT * FROM kap_reserv WHERE kap_reserv.id_user = %s and kap_reserv.id = %s;
                    """, (acc[0], id,))
                kap = cur.fetchone()

                cur.execute("""
                                SELECT * FROM balans_passiv WHERE id_kap = %s;
                                    """, (kap[0],))
                bal = cur.fetchone()

                cur.execute("""
                                           SELECT * FROM dolgosr_obzat WHERE dolgosr_obzat.id_user = %s and dolgosr_obzat.id = %s;
                                """, (acc[0], bal[3],))
                dolg = cur.fetchone()

                cur.execute("""
                                           SELECT * FROM kratkosr_obzat WHERE kratkosr_obzat.id_user = %s and kratkosr_obzat.id = %s;
                                """, (acc[0],  bal[2],))
                krat = cur.fetchone()

                date = datetime.strptime(str(kap[3]), "%Y-%m-%d").strftime("%d.%m.%Y")
            if int(par) == 3:

                cur.execute("""
                                           SELECT * FROM dolgosr_obzat WHERE dolgosr_obzat.id_user = %s and dolgosr_obzat.id = %s;
                                """, (acc[0], id,))
                dolg = cur.fetchone()


                cur.execute("""
                                SELECT * FROM balans_passiv WHERE id_dolg = %s;
                                    """, (dolg[0],))
                bal = cur.fetchone()


                cur.execute("""
                               SELECT * FROM kap_reserv WHERE kap_reserv.id_user = %s and kap_reserv.id = %s;
                    """, (acc[0], bal[1],))
                kap = cur.fetchone()

                cur.execute("""
                                           SELECT * FROM kratkosr_obzat WHERE kratkosr_obzat.id_user = %s and kratkosr_obzat.id = %s;
                                """, (acc[0],  bal[2],))
                krat = cur.fetchone()

                date = datetime.strptime(str(dolg[3]), "%Y-%m-%d").strftime("%d.%m.%Y")
            if int(par) == 4:
                cur.execute("""
                                    SELECT * FROM kratkosr_obzat WHERE kratkosr_obzat.id_user = %s and kratkosr_obzat.id = %s;
                                    """, (acc[0], id,))
                krat = cur.fetchone()

                cur.execute("""
                                    SELECT * FROM balans_passiv WHERE id_krat = %s;
                                        """, (krat[0],))
                bal = cur.fetchone()

                cur.execute("""
                                   SELECT * FROM kap_reserv WHERE kap_reserv.id_user = %s and kap_reserv.id = %s;
                        """, (acc[0], bal[1],))
                kap = cur.fetchone()

                cur.execute("""
                                    SELECT * FROM dolgosr_obzat WHERE dolgosr_obzat.id_user = %s and dolgosr_obzat.id = %s;
                                    """, (acc[0], bal[3],))
                dolg = cur.fetchone()
                date = datetime.strptime(str(krat[3]), "%Y-%m-%d").strftime("%d.%m.%Y")
            return render_template('izm.html', username=session['username'], acc=acc, id=id, par=par, kap=kap, bal=bal,
                                   date=date, krat=krat, dolg=dolg)
    return redirect(url_for('login'))


# Удаление
@app.route('/ydal/<par>/<id>', methods=['POST', 'GET'])
def Ydal(par, id):
    # Check if user is loggedin
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()

        # Получаем всю информацию о текущем пользователе
        cur.execute('SELECT * FROM users WHERE id_user = %s', [session['id']])
        acc = cur.fetchone()
        par = int(par)

        if par == 0:
            cur.execute("""
                            SELECT * FROM balans_aktiv WHERE balans_aktiv.id_vn_akt = %s;
                            """, (id,))
            balans_aktiv = cur.fetchone()

            id2 = balans_aktiv[2]

            cur.execute(
                """
                     DELETE FROM balans_aktiv WHERE id_vn_akt = %s;
                """, (id,))
            conn.commit()

            cur.execute(
                """
                     DELETE FROM vn_aktivs WHERE id = %s;
                """, (id,))
            conn.commit()

            cur.execute(
                """
                     DELETE FROM ob_aktivs WHERE id = %s;
                """, (id2,))
            conn.commit()

        if par == 1:
            cur.execute("""
                            SELECT * FROM balans_aktiv WHERE balans_aktiv.id_ob_akt = %s;
                            """, (id,))
            balans_aktiv = cur.fetchone()

            id2 = balans_aktiv[2]

            cur.execute(
                """
                     DELETE FROM balans_aktiv WHERE id_ob_akt = %s;
                """, (id,))
            conn.commit()

            cur.execute(
                """
                     DELETE FROM ob_aktivs WHERE id = %s;
                """, (id,))
            conn.commit()

            cur.execute(
                """
                     DELETE FROM vn_aktivs WHERE id = %s;
                """, (id2,))
            conn.commit()

        if par == 2:
            cur.execute("""
                            SELECT * FROM balans_passiv WHERE balans_passiv.id_kap = %s;
                            """, (id,))
            balans_passiv = cur.fetchone()

            id2 = balans_passiv[2]
            id3 = balans_passiv[3]

            cur.execute(
                """
                     DELETE FROM balans_passiv WHERE id_kap = %s;
                """, (id,))
            conn.commit()

            cur.execute(
                """
                     DELETE FROM dolgosr_obzat WHERE id = %s;
                """, (id3,))
            conn.commit()

            cur.execute(
                """
                     DELETE FROM kratkosr_obzat WHERE id = %s;
                """, (id2,))
            conn.commit()

            cur.execute(
                """
                     DELETE FROM kap_reserv WHERE id = %s;
                """, (id,))
            conn.commit()

        if par == 3:
            cur.execute("""
                            SELECT * FROM balans_passiv WHERE balans_passiv.id_dolg = %s;
                            """, (id,))
            balans_passiv = cur.fetchone()

            id2 = balans_passiv[1]
            id3 = balans_passiv[2]

            cur.execute(
                """
                     DELETE FROM balans_passiv WHERE id_dolg = %s;
                """, (id,))
            conn.commit()

            cur.execute(
                """
                     DELETE FROM kap_reserv WHERE id = %s;
                """, (id2,))
            conn.commit()

            cur.execute(
                """
                     DELETE FROM kratkosr_obzat WHERE id = %s;
                """, (id3,))
            conn.commit()

            cur.execute(
                """
                     DELETE FROM dolgosr_obzat WHERE id = %s;
                """, (id,))
            conn.commit()

        if par == 4:
            cur.execute("""
                            SELECT * FROM balans_passiv WHERE balans_passiv.id_krat = %s;
                            """, (id,))
            balans_passiv = cur.fetchone()

            id2 = balans_passiv[1]
            id3 = balans_passiv[3]

            cur.execute(
                """
                     DELETE FROM balans_passiv WHERE id_krat = %s;
                """, (id,))
            conn.commit()

            cur.execute(
                """
                     DELETE FROM kap_reserv WHERE id = %s;
                """, (id2,))
            conn.commit()

            cur.execute(
                """
                     DELETE FROM dolgosr_obzat WHERE id = %s;
                """, (id3,))
            conn.commit()

            cur.execute(
                """
                     DELETE FROM kratkosr_obzat WHERE id = %s;
                """, (id,))
            conn.commit()

        cur.execute('SELECT * FROM vn_aktivs WHERE id_user = %s ORDER BY id', [session['id']])
        vn_aktive = cur.fetchall()
        vn_aktive_len = len(vn_aktive)

        cur.execute('SELECT * FROM ob_aktivs WHERE id_user = %s ORDER BY id', [session['id']])
        ob_aktive = cur.fetchall()
        ob_aktive_len = len(ob_aktive)

        cur.execute("""
                                    SELECT balans_aktiv.id, balans_aktiv.id_vn_akt, balans_aktiv.id_ob_akt, itog_vn, itog_ob, balans FROM balans_aktiv 
                                        JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
                                        JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
                                        WHERE vn_aktivs.id_user = %s and ob_aktivs.id_user = %s 
                                        ORDER BY id_vn_akt, id_ob_akt;
                        """, (acc[0], acc[0],))
        balans_aktiv = cur.fetchall()

        cur.execute('SELECT * FROM kap_reserv WHERE id_user = %s ORDER BY id', [session['id']])
        kap_reserv = cur.fetchall()
        kap_reserv_len = len(kap_reserv)
        cur.execute('SELECT * FROM kratkosr_obzat WHERE id_user = %s ORDER BY id', [session['id']])
        kratkosr_obzat = cur.fetchall()
        kratkosr_obzat_len = len(kratkosr_obzat)
        cur.execute('SELECT * FROM dolgosr_obzat WHERE id_user = %s ORDER BY id', [session['id']])
        dolgosr_obzat = cur.fetchall()
        dolgosr_obzat_len = len(dolgosr_obzat)

        cur.execute("""
                                SELECT balans_passiv.id, balans_passiv.id_kap, balans_passiv.id_krat, id_dolg, itog_kap, itog_krat, itog_dolg, balans FROM balans_passiv
                                JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
                                JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
                                JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
                                WHERE kap_reserv.id_user = %s and kratkosr_obzat.id_user = %s and dolgosr_obzat.id_user = %s 
                                ORDER BY kap_reserv.year
                            """, (acc[0], acc[0], acc[0],))
        balans_passiv = cur.fetchall()

        cur.execute('SELECT * FROM fin_res WHERE id_user = %s ORDER BY id', [session['id']])
        fin_res = cur.fetchall()
        cur.execute('SELECT * FROM nalog_na_pribl WHERE id_user = %s ORDER BY id', [session['id']])
        nalog_na_prib = cur.fetchall()

        nalog_na_prib_len = len(nalog_na_prib)

        cur.execute("""
                                    SELECT fin_res_rashchet.id, id_nalog_na_pribl, id_fin_res, val_pr, pr_ot_prodag, prib_do_nalog, nalog_na_pr, chist_pribl FROM fin_res_rashchet 
                                    JOIN fin_res ON (fin_res.id = fin_res_rashchet.id_fin_res)
                                    JOIN nalog_na_pribl ON (nalog_na_pribl.id = fin_res_rashchet.id_nalog_na_pribl)
                                    WHERE fin_res.id_user = %s and nalog_na_pribl.id_user = %s 
                                    ORDER BY fin_res.id
                                """, (acc[0], acc[0],))
        fin_res_rashch = cur.fetchall()

        cur.close()
        conn.close()
        return render_template('prosmotr.html', username=session['username'], acc=acc, vn_aktive=vn_aktive,
                               vn_aktive_len=vn_aktive_len,
                               ob_aktive=ob_aktive, ob_aktive_len=ob_aktive_len,
                               balans_aktiv=balans_aktiv, kap_reserv=kap_reserv, kap_reserv_len=kap_reserv_len,
                               kratkosr_obzat=kratkosr_obzat, kratkosr_obzat_len=kratkosr_obzat_len,
                               dolgosr_obzat_len=dolgosr_obzat_len,
                               dolgosr_obzat=dolgosr_obzat, balans_passiv=balans_passiv, fin_res=fin_res,
                               nalog_na_prib=nalog_na_prib,
                               fin_res_rashch=fin_res_rashch, nalog_na_prib_len=nalog_na_prib_len)

        # # if int(par) == 0 or int(par) == 1:
        # #     if int(par) == 0:
        # #         cur.execute("""
        # #                        SELECT * FROM vn_aktivs WHERE vn_aktivs.id_user = %s and vn_aktivs.id = %s;
        # #             """, (acc[0], id,))
        # #         par_izm = cur.fetchone()
        # #
        # #         cur.execute("""
        # #                         SELECT * FROM ob_aktivs WHERE ob_aktivs.id_user = %s and ob_aktivs.year = %s and ob_aktivs.inn = %s;
        # #                         """, (acc[0], par_izm[3], par_izm[1],))
        # #         par_izm2 = cur.fetchone()
        # #
        # #         date = datetime.strptime(str(par_izm[3]), "%Y-%m-%d").strftime("%d.%m.%Y")
        # #     else:
        # #
        # #         cur.execute("""
        # #                                         SELECT * FROM ob_aktivs WHERE ob_aktivs.id_user = %s and ob_aktivs.id = %s;
        # #                                         """, (acc[0], id,))
        # #         par_izm2 = cur.fetchone()
        # #
        # #         cur.execute("""
        # #                                         SELECT * FROM vn_aktivs WHERE vn_aktivs.id_user = %s and vn_aktivs.year = %s and vn_aktivs.inn = %s;
        # #                              """, (acc[0], par_izm2[3], par_izm2[1],))
        # #         par_izm = cur.fetchone()
        # #
        # #         date = datetime.strptime(str(par_izm2[3]), "%Y-%m-%d").strftime("%d.%m.%Y")
        # #     return render_template('izm.html', username=session['username'], acc=acc, id=id, par=par, par_izm=par_izm, date=date, par_izm2=par_izm2)
        #
        # if int(par) == 2 or int(par) == 3 or int(par) == 4:
        #     cur.execute("""
        #                        SELECT * FROM kap_reserv WHERE kap_reserv.id_user = %s and kap_reserv.id = %s;
        #             """, (acc[0], id,))
        #     par_izm = cur.fetchone()
        #
        #     cur.execute("""
        #                                    SELECT * FROM dolgosr_obzat WHERE dolgosr_obzat.id_user = %s and dolgosr_obzat.id = %s;
        #                         """, (acc[0], id,))
        #     par_izm2 = cur.fetchone()
        #
        #     cur.execute("""
        #                                    SELECT * FROM kratkosr_obzat WHERE kratkosr_obzat.id_user = %s and kratkosr_obzat.id = %s;
        #                         """, (acc[0], id,))
        #     par_izm3 = cur.fetchone()
        #
        #     return render_template('izm.html', username=session['username'], acc=acc, id=id, par=par, par_izm=par_izm, par_izm2=par_izm2, par_izm3=par_izm3 )

        # if int(par) == 5:
        #     cur.execute("""
        #                        SELECT * FROM fin_res WHERE fin_res.id_user = %s and fin_res.id = %s;
        #             """, (acc[0], id,))
        #     par_izm = cur.fetchone()
        #     return render_template('izm.html', username=session['username'], acc=acc, id=id, par=par, par_izm=par_izm)

    return redirect(url_for('login'))


# Изменение финансовых результатов
@app.route('/izm/<par>/<id>/<id_n>', methods=['POST', 'GET'])
def Izm2(par, id, id_n):
    # Check if user is loggedin
    id = int(id)
    id_n = int(id_n)

    print(id)
    print(id_n)
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()

        # Получаем всю информацию о текущем пользователе
        cur.execute('SELECT * FROM users WHERE id_user = %s', [session['id']])
        acc = cur.fetchone()
        par = int(par)
        if request.method == "POST":
            # date = request.form['date3']
            inn = request.form['inn3']
            pok1 = request.form['fin1']
            pok2 = request.form['fin2']
            pok3 = request.form['fin3']
            pok4 = request.form['fin4']
            pok5 = request.form['fin5']
            pok6 = request.form['fin6']
            pok7 = request.form['fin7']
            pok8 = request.form['fin8']
            pok9 = request.form['fin9']
            pok10 = request.form['fin10']
            pok11 = request.form['fin11']
            pok12 = request.form['fin12']
            pok13 = request.form['fin13']
            pok14 = request.form['fin14']

            # # Изменение формата дат с str на date
            # date = DT.datetime.strptime(date, '%d.%m.%Y').date()

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                    """
                    UPDATE fin_res SET inn = %s, vrychka = %s,
                    sebest_prodag = %s, kommerchesk_rashod = %s, ypravl_rashod = %s,
                    dohod_ot_ychast_v_dr_org = %s, procent_k_polych = %s, procent_k_yplat = %s,
                    proch_dohod = %s, proch_rashod = %s
                    WHERE id = %s;
                    """, (inn, pok1, pok2, pok3, pok4, pok5, pok6, pok7, pok8, pok9, id, ))
            conn.commit()

            cur.execute(
                    """
                    UPDATE nalog_na_pribl SET inn = %s, tek_nalog_na_pribl = %s,
                    otlog_nalog_na_pribl = %s, izm_ot_nalog_ob = %s, izm_ot_nalog_act = %s,
                    proch = %s
                    WHERE id = %s;
                    """, (inn, pok10, pok11, pok12, pok13, pok14, id_n,))
            conn.commit()

            val_pr = int(pok1) - int(pok2)
            pr_ot_prodag = val_pr - int(pok3) - int(pok4)
            prib_do_nalog = pr_ot_prodag + int(pok5) + int(pok6) - int(pok7) + int(pok8) - int(pok9)
            nalog_na_pr = int(pok10) - int(pok11)
            chist_pribl = prib_do_nalog - nalog_na_pr - int(pok12) - int(pok13) - int(pok14)

            cur.execute(
                    """
                    UPDATE fin_res_rashchet SET val_pr = %s,
                    pr_ot_prodag = %s, prib_do_nalog = %s, nalog_na_pr = %s,
                    chist_pribl = %s
                    WHERE id_nalog_na_pribl = %s and id_fin_res = %s;
                    """, (val_pr, pr_ot_prodag, prib_do_nalog, nalog_na_pr, chist_pribl, id_n, id, ))
            conn.commit()

            cur.execute('SELECT * FROM vn_aktivs WHERE id_user = %s ORDER BY id', [session['id']])
            vn_aktive = cur.fetchall()
            vn_aktive_len = len(vn_aktive)

            cur.execute('SELECT * FROM ob_aktivs WHERE id_user = %s ORDER BY id', [session['id']])
            ob_aktive = cur.fetchall()
            ob_aktive_len = len(ob_aktive)

            cur.execute("""
                                    SELECT balans_aktiv.id, balans_aktiv.id_vn_akt, balans_aktiv.id_ob_akt, itog_vn, itog_ob, balans FROM balans_aktiv 
                                        JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
                                        JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
                                        WHERE vn_aktivs.id_user = %s and ob_aktivs.id_user = %s 
                                        ORDER BY id_vn_akt, id_ob_akt;
                        """, (acc[0], acc[0],))
            balans_aktiv = cur.fetchall()

            cur.execute('SELECT * FROM kap_reserv WHERE id_user = %s ORDER BY id', [session['id']])
            kap_reserv = cur.fetchall()
            kap_reserv_len = len(kap_reserv)
            cur.execute('SELECT * FROM kratkosr_obzat WHERE id_user = %s ORDER BY id', [session['id']])
            kratkosr_obzat = cur.fetchall()
            kratkosr_obzat_len = len(kratkosr_obzat)
            cur.execute('SELECT * FROM dolgosr_obzat WHERE id_user = %s ORDER BY id', [session['id']])
            dolgosr_obzat = cur.fetchall()
            dolgosr_obzat_len = len(dolgosr_obzat)

            cur.execute("""
                                SELECT balans_passiv.id, balans_passiv.id_kap, balans_passiv.id_krat, id_dolg, itog_kap, itog_krat, itog_dolg, balans FROM balans_passiv
                                JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
                                JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
                                JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
                                WHERE kap_reserv.id_user = %s and kratkosr_obzat.id_user = %s and dolgosr_obzat.id_user = %s 
                                ORDER BY kap_reserv.year
                            """, (acc[0], acc[0], acc[0],))
            balans_passiv = cur.fetchall()

            cur.execute('SELECT * FROM fin_res WHERE id_user = %s ORDER BY id', [session['id']])
            fin_res = cur.fetchall()
            cur.execute('SELECT * FROM nalog_na_pribl WHERE id_user = %s ORDER BY id', [session['id']])
            nalog_na_prib = cur.fetchall()

            nalog_na_prib_len = len(nalog_na_prib)

            cur.execute("""
                                    SELECT fin_res_rashchet.id, id_nalog_na_pribl, id_fin_res, val_pr, pr_ot_prodag, prib_do_nalog, nalog_na_pr, chist_pribl FROM fin_res_rashchet 
                                    JOIN fin_res ON (fin_res.id = fin_res_rashchet.id_fin_res)
                                    JOIN nalog_na_pribl ON (nalog_na_pribl.id = fin_res_rashchet.id_nalog_na_pribl)
                                    WHERE fin_res.id_user = %s and nalog_na_pribl.id_user = %s 
                                    ORDER BY fin_res.id
                                """, (acc[0], acc[0],))
            fin_res_rashch = cur.fetchall()

            cur.close()
            conn.close()
            return render_template('prosmotr.html', username=session['username'], acc=acc, vn_aktive=vn_aktive,
                               vn_aktive_len=vn_aktive_len,
                               ob_aktive=ob_aktive, ob_aktive_len=ob_aktive_len,
                               balans_aktiv=balans_aktiv, kap_reserv=kap_reserv, kap_reserv_len=kap_reserv_len,
                               kratkosr_obzat=kratkosr_obzat, kratkosr_obzat_len=kratkosr_obzat_len,
                               dolgosr_obzat_len=dolgosr_obzat_len,
                               dolgosr_obzat=dolgosr_obzat, balans_passiv=balans_passiv, fin_res=fin_res,
                               nalog_na_prib=nalog_na_prib,
                               fin_res_rashch=fin_res_rashch, nalog_na_prib_len=nalog_na_prib_len)

        cur.execute("""
                    SELECT fin_res_rashchet.id, id_nalog_na_pribl, id_fin_res, vrychka, sebest_prodag, val_pr, 
                    kommerchesk_rashod, ypravl_rashod, pr_ot_prodag, dohod_ot_ychast_v_dr_org, procent_k_polych, procent_k_yplat, 
                    proch_dohod, proch_rashod, prib_do_nalog, nalog_na_pr, 
                    tek_nalog_na_pribl, otlog_nalog_na_pribl, izm_ot_nalog_ob, izm_ot_nalog_act, proch, 
                    chist_pribl, fin_res.inn, fin_res.year FROM fin_res_rashchet 
                    JOIN fin_res ON (fin_res.id = fin_res_rashchet.id_fin_res)
                    JOIN nalog_na_pribl ON (nalog_na_pribl.id = fin_res_rashchet.id_nalog_na_pribl)
                    WHERE fin_res.id_user = %s and nalog_na_pribl.id_user = %s
                    and fin_res.id = %s and nalog_na_pribl.id = %s
                """, (acc[0], acc[0], id, id_n))
        fin_res_rashch = cur.fetchone()
        print(fin_res_rashch)
        date = datetime.strptime(str(fin_res_rashch[23]), "%Y-%m-%d").strftime("%d.%m.%Y")

        return render_template('izm.html', username=session['username'], acc=acc, id=id, par=par, fin_res_rashch=fin_res_rashch, date=date)

    return redirect(url_for('login'))

# Удаление финансовых результатов
@app.route('/ydal/<par>/<id>/<id_n>', methods=['POST', 'GET'])
def Ydal2(par, id, id_n):
    # Check if user is loggedin
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()

        # Получаем всю информацию о текущем пользователе
        cur.execute('SELECT * FROM users WHERE id_user = %s', [session['id']])
        acc = cur.fetchone()
        par = int(par)

        cur.execute("""
                      SELECT * FROM fin_res_rashchet WHERE id_nalog_na_pribl = %s and id_fin_res = %s;
                    """, (id, id_n, ))
        fin_rasch = cur.fetchone()

        id_str = fin_rasch[0]

        cur.execute(
            """
                 DELETE FROM fin_res_rashchet WHERE id = %s;
            """, (id_str,))
        conn.commit()

        cur.execute(
            """
                 DELETE FROM fin_res WHERE id = %s;
            """, (id, ))
        conn.commit()

        cur.execute(
            """
                 DELETE FROM nalog_na_pribl WHERE id = %s;
            """, (id_n, ))
        conn.commit()

        cur.execute('SELECT * FROM vn_aktivs WHERE id_user = %s ORDER BY id', [session['id']])
        vn_aktive = cur.fetchall()
        vn_aktive_len = len(vn_aktive)

        cur.execute('SELECT * FROM ob_aktivs WHERE id_user = %s ORDER BY id', [session['id']])
        ob_aktive = cur.fetchall()
        ob_aktive_len = len(ob_aktive)

        cur.execute("""
                                    SELECT balans_aktiv.id, balans_aktiv.id_vn_akt, balans_aktiv.id_ob_akt, itog_vn, itog_ob, balans FROM balans_aktiv 
                                        JOIN vn_aktivs ON (vn_aktivs.id = balans_aktiv.id_vn_akt)
                                        JOIN ob_aktivs ON (ob_aktivs.id = balans_aktiv.id_ob_akt)
                                        WHERE vn_aktivs.id_user = %s and ob_aktivs.id_user = %s 
                                        ORDER BY id_vn_akt, id_ob_akt;
                        """, (acc[0], acc[0],))
        balans_aktiv = cur.fetchall()

        cur.execute('SELECT * FROM kap_reserv WHERE id_user = %s ORDER BY id', [session['id']])
        kap_reserv = cur.fetchall()
        kap_reserv_len = len(kap_reserv)
        cur.execute('SELECT * FROM kratkosr_obzat WHERE id_user = %s ORDER BY id', [session['id']])
        kratkosr_obzat = cur.fetchall()
        kratkosr_obzat_len = len(kratkosr_obzat)
        cur.execute('SELECT * FROM dolgosr_obzat WHERE id_user = %s ORDER BY id', [session['id']])
        dolgosr_obzat = cur.fetchall()
        dolgosr_obzat_len = len(dolgosr_obzat)

        cur.execute("""
                                SELECT balans_passiv.id, balans_passiv.id_kap, balans_passiv.id_krat, id_dolg, itog_kap, itog_krat, itog_dolg, balans FROM balans_passiv
                                JOIN kap_reserv ON (kap_reserv.id = balans_passiv.id_kap)
                                JOIN kratkosr_obzat ON (kratkosr_obzat.id = balans_passiv.id_krat)
                                JOIN dolgosr_obzat ON (dolgosr_obzat.id = balans_passiv.id_dolg)
                                WHERE kap_reserv.id_user = %s and kratkosr_obzat.id_user = %s and dolgosr_obzat.id_user = %s 
                                ORDER BY kap_reserv.year
                            """, (acc[0], acc[0], acc[0],))
        balans_passiv = cur.fetchall()

        cur.execute('SELECT * FROM fin_res WHERE id_user = %s ORDER BY id', [session['id']])
        fin_res = cur.fetchall()
        cur.execute('SELECT * FROM nalog_na_pribl WHERE id_user = %s ORDER BY id', [session['id']])
        nalog_na_prib = cur.fetchall()

        nalog_na_prib_len = len(nalog_na_prib)

        cur.execute("""
                                    SELECT fin_res_rashchet.id, id_nalog_na_pribl, id_fin_res, val_pr, pr_ot_prodag, prib_do_nalog, nalog_na_pr, chist_pribl FROM fin_res_rashchet 
                                    JOIN fin_res ON (fin_res.id = fin_res_rashchet.id_fin_res)
                                    JOIN nalog_na_pribl ON (nalog_na_pribl.id = fin_res_rashchet.id_nalog_na_pribl)
                                    WHERE fin_res.id_user = %s and nalog_na_pribl.id_user = %s 
                                    ORDER BY fin_res.id
                                """, (acc[0], acc[0],))
        fin_res_rashch = cur.fetchall()

        cur.close()
        conn.close()
        return render_template('prosmotr.html', username=session['username'], acc=acc, vn_aktive=vn_aktive,
                               vn_aktive_len=vn_aktive_len,
                               ob_aktive=ob_aktive, ob_aktive_len=ob_aktive_len,
                               balans_aktiv=balans_aktiv, kap_reserv=kap_reserv, kap_reserv_len=kap_reserv_len,
                               kratkosr_obzat=kratkosr_obzat, kratkosr_obzat_len=kratkosr_obzat_len,
                               dolgosr_obzat_len=dolgosr_obzat_len,
                               dolgosr_obzat=dolgosr_obzat, balans_passiv=balans_passiv, fin_res=fin_res,
                               nalog_na_prib=nalog_na_prib,
                               fin_res_rashch=fin_res_rashch, nalog_na_prib_len=nalog_na_prib_len)
    return redirect(url_for('login'))


# Прогноз
@app.route('/prognoz', methods=['POST', 'GET'])
def prognoz():

    # Check if user is loggedin
    if 'loggedin' in session:
        # Текущие время и дата
        d = datetime.now().date()
        t = datetime.now().time()

        conn = get_db_connection()
        cur = conn.cursor()
        res = []
        vosrast = []

        # Получаем всю информацию о текущем пользователе
        cur.execute('SELECT * FROM users WHERE id_user = %s', [session['id']])
        acc = cur.fetchone()

        return render_template('aktiv.html', username=session['username'], acc=acc)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Тест
@app.route('/test', methods=['POST', 'GET'])
def test():

    # Check if user is loggedin
    if 'loggedin' in session:
        # Текущие время и дата
        d = datetime.now().date()
        t = datetime.now().time()

        conn = get_db_connection()
        cur = conn.cursor()
        res = []
        vosrast = []

        # Получаем всю информацию о текущем пользователе
        cur.execute('SELECT * FROM users WHERE id_user = %s', [session['id']])
        acc = cur.fetchone()

        # # Проверка подписок (если прериум или vip)
        # if acc[16] == 2 or acc[16] == 3:
        #     # Отбираем запись о последней продажи подписки для пользователя
        #     cur.execute("""
        #                     SELECT * FROM prodag WHERE id_user = %s
        #                         ORDER BY date_prodag, time_prodag DESC
        #                         LIMIT 1;
        #                                 """,
        #                 ([session['id']]))
        #
        #     prod = cur.fetchone()

            # # Проверяем, прошел ли месяц с даты покупки подписки -> если да - меняем подписку пользователя на Стандарт
            # # и меняем ему макс кол-во лайков
            # if prod[1] + timedelta(days=30) < d:
            #
            #     cur.execute('SELECT * FROM subscription WHERE id_subscription = 1')
            #     pod = cur.fetchone()
            #
            #     cur.execute('UPDATE users SET id_subscription = %s, kol_like_po_podpisk = %s WHERE id_user = %s',
            #                 (pod[0], pod[4], acc[0]), )
            #     conn.commit()


        return render_template('test.html', username=session['username'], acc=acc)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)