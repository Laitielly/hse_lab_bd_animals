import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msg

import sqlalchemy.exc
from sqlalchemy import create_engine

# engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
#
# cursor = engine.connect()

# engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/logs")
#
# cursor_2 = engine_2.connect()

current_login = ''


class LoginFrame(tk.Frame):

    def login_user(self):
        if not msg.askyesno("Точно?", "Вы уверены, что хотите авторизоваться?"):
            return
        queue_create = f"""
            SELECT get_pass_right('{self.login_entry.get()}');
            """
        if list(self.cursor_2.execute(queue_create))[0][0] is not None:
            res = list(self.cursor_2.execute(queue_create))[0][0].replace('(', '').replace(')', '').split(',')
        else:
            msg.showerror('Ошибка', "Неверные логин или пароль")
            return
        if self.login_entry.get() == res[0] and self.passwd_entry.get() == res[1]:
            [child.destroy() for child in self.master.winfo_children()]
            self.cursor_2.close()
            main_frame = MainFrame(self.master)
            self.pack_forget()
            main_frame.pack(fill=tk.BOTH)
            return
        msg.showerror("Ошибка!", "Логин или пароль неверные")

    def reg_user(self):
        if not msg.askyesno("Точно?", "Вы уверены, что хотите зарегистрироваться?"):
            return

        login = self.login_entry.get()
        password = self.passwd_entry.get()
        queue_create = f"""
                    SELECT get_pass_right('{self.login_entry.get()}');
                    """
        if list(self.cursor_2.execute(queue_create))[0][0] is not None or \
                self.login_entry.get() == '':
            msg.showerror('Ошибка', "Уже есть пользователь с таким логином или введено пустое поле")
            return
        else:
            queue_get_login = f'''
                                    Begin;
                                    CALL uplogins('{login}', '{password}');
                                    Commit;
                                    '''
            self.cursor_2.execute(queue_get_login)
        return

    def __init__(self, parent):
        super().__init__(parent)

        self.engine_2 = create_engine("postgresql+psycopg2://creator:bkppasswd@localhost:5432/logs")
        self.cursor_2 = self.engine_2.connect()

        self.config(bg='#6FE7DD')
        self.hello_lb = tk.Label(self, text="Добрый день! Вы находитесь перед входом в базу данных \"Скотобаза\"",
                                 bg='#6FE7DD', font=('GothamPro', 14))
        self.hello_lb.pack(side=tk.TOP, pady=15)
        self.login_lb = tk.Label(self, text="Ваш логин:", bg='#6FE7DD', font=('GothamPro', 14))
        self.login_lb.pack(side=tk.TOP)
        self.login_entry = tk.Entry(self)
        # self.login_entry.insert(0, self.USER)
        self.login_entry.pack()
        self.passwd_lb = tk.Label(self, text="Пароль:", bg='#6FE7DD', font=('GothamPro', 14))
        self.passwd_lb.pack(side=tk.TOP)
        self.passwd_entry = tk.Entry(self, show='*')
        # self.passwd_entry.insert(0, self.PASSWORD)
        self.passwd_entry.pack()
        self.login_btn = tk.Button(self, text="Авторизация")
        self.login_btn.config(command=self.login_user)
        self.login_btn.pack(pady=5)
        self.reg_btn = tk.Button(self, text="Регистрация")
        self.reg_btn.config(command=self.reg_user)
        self.reg_btn.pack(pady=5)
        # or like this
        # self.login_btn["command"] = login_user


class MainFrame(tk.Frame):
    query_check = f'''
        SELECT check_db('animals');
    '''
    query_delete_db = f'''
        SELECT drop_db('animals');
    '''
    query_create_db = f'''
        SELECT create_db('animals');
    '''
    query_grant_role = f'''
        Begin;
        CALL create_role_client();
        Commit;
    '''

    def delete_db(self):
        if not msg.askyesno("Точно?", "Вы уверены, что хотите удалить БД?"):
            return
        flag = list(self.cursor_2.execute(MainFrame.query_check))[0][0]
        if flag:
            self.cursor_2.execute(MainFrame.query_delete_db)
            msg.showinfo('Успех', 'БД успешно удалена!')
        else:
            msg.showerror('Ошибка', 'БД уже удалена!')
            return
        return

    def create_db(self):
        if not msg.askyesno("Точно?", "Вы уверены, что хотите создать БД?"):
            return
        flag = list(self.cursor_2.execute(MainFrame.query_check))[0][0]
        if flag:
            msg.showerror('Ошибка', 'БД уже создана!')
            return
        else:
            self.cursor_2.execute(MainFrame.query_create_db)
            msg.showinfo('Успех', 'БД успешно создана!')
            engine = create_engine("postgresql+psycopg2://creator:bkppasswd@localhost:5432/animals")
            cursor = engine.connect()

            cursor.execute(self.query_grant_role)
            cursor.close()
        return

    def change_tables(self):
        flag = list(self.cursor_2.execute(MainFrame.query_check))[0][0]
        if flag:
            self.cursor_2.close()
            [child.destroy() for child in self.master.winfo_children()]
            main_frame = ChangingTables(self.master)
            self.pack_forget()
            main_frame.pack(fill=tk.BOTH)
        else:
            msg.showinfo('Замечание', 'Сначала создайте БД!')
            return
        return

    def __init__(self, parent):
        super().__init__(parent)

        self.engine_2 = create_engine("postgresql+psycopg2://creator:bkppasswd@localhost:5432/logs")
        self.cursor_2 = self.engine_2.connect()

        self.config(bg="#6FE7DD")

        self.change_tables = tk.Button(self, text='Работать с данными',
                                       command=self.change_tables, font=('SolomonSans', 15))
        self.change_tables.grid(row=1, column=0, rowspan=2, stick='wens', padx=10, pady=10)

        self.delete_db = tk.Button(self, text='Удалить базу данных',
                                   font=('SolomonSans', 15), command=self.delete_db)
        self.delete_db.grid(row=1, column=1, rowspan=2, stick='wens', padx=10, pady=10)

        self.create_db = tk.Button(self, text='Создать базу данных',
                                   font=('SolomonSans', 15), command=self.create_db)
        self.create_db.grid(row=1, column=2, rowspan=2, stick='wens', padx=10, pady=10)

        self.grid_columnconfigure(0, minsize=233)
        self.grid_columnconfigure(1, minsize=233)
        self.grid_columnconfigure(2, minsize=234)

        self.grid_rowconfigure(0, minsize=55)
        self.grid_rowconfigure(1, minsize=55)
        self.grid_rowconfigure(2, minsize=55)
        self.grid_rowconfigure(3, minsize=55)


class ChangingTables(tk.Frame):

    def back(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = MainFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def clear_all_tables(self):
        if not msg.askyesno("Точно?", "Вы уверены, что хотите очистить все таблицы?"):
            return
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()

        query_delete_all = f'''
            Begin;
            CALL clear_all_tables();
            Commit; 
        '''

        cursor.execute(query_delete_all)
        msg.showinfo('Уведомление', 'Все таблицы очищены!')
        cursor.close()
        return

    def show_tables_pets(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = TablesPetsFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def show_tables_cust(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = TablesCustFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def show_tables_shops(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = TablesShopsFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def show_tables_purchases(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = TablesPurchasesFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def insert_tables_pets(self):
        query_get_shops = '''
                                                    SELECT print_table(NULL::shop);
                                                '''
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")

        cursor = engine.connect()
        try:
            if list(cursor.execute(query_get_shops))[0][0]:
                [child.destroy() for child in self.master.winfo_children()]
                main_frame = InsertPetsFrame(self.master)
                self.pack_forget()
                main_frame.pack(fill=tk.BOTH)
        except IndexError:
            msg.showerror('Ошибка', 'Добавить животное можно лишь при наличии магазинов.')
        cursor.close()
        return

    def insert_tables_cust(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = InsertCustFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def insert_tables_shops(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = InsertShopsFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def insert_tables_purchases(self):
        query_get_buyers = '''
                 SELECT print_table(NULL::buyer);
        '''
        query_get_stamp = '''
                 SELECT print_table(NULL::animals);
        '''
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        try:
            if list(cursor.execute(query_get_buyers))[0][0] and list(cursor.execute(query_get_stamp))[0][0]:
                [child.destroy() for child in self.master.winfo_children()]
                main_frame = InsertPurchasesFrame(self.master)
                self.pack_forget()
                main_frame.pack(fill=tk.BOTH)
        except IndexError:
            msg.showerror('Ошибка', 'Добавить покупку можно лишь при наличии покупателей и животного.')
        cursor.close()
        return

    def delete_pets(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = DeletePetsFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def delete_cust(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = DeleteCustFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def delete_shops(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = DeleteShopsFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def delete_purchases(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = DeletePurchasesFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def change_pets(self):
        query_get_animals = '''
                                                                    SELECT print_table(NULL::animals);
                                                                '''
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")

        cursor = engine.connect()
        try:
            if list(cursor.execute(query_get_animals))[0][0]:
                [child.destroy() for child in self.master.winfo_children()]
                main_frame = ChangePetsFrame(self.master)
                self.pack_forget()
                main_frame.pack(fill=tk.BOTH)
        except IndexError:
            msg.showerror('Ошибка',
                          'Чтобы изменять что-то ненужное, надо сначала добавить что-то ненужное, а у нас данных нет!')
        cursor.close()
        return

    def change_cust(self):
        query_get_cust = '''
                                                                                   SELECT print_table(NULL::buyer);
                                                                               '''
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")

        cursor = engine.connect()
        try:
            if list(cursor.execute(query_get_cust))[0][0]:
                [child.destroy() for child in self.master.winfo_children()]
                main_frame = ChangeCustFrame(self.master)
                self.pack_forget()
                main_frame.pack(fill=tk.BOTH)
        except IndexError:
            msg.showerror('Ошибка',
                          'Чтобы изменять что-то ненужное, надо сначала добавить что-то ненужное, а у нас данных нет!')
        cursor.close()
        return

    def change_shop(self):
        query_get_shops = '''
                                              SELECT print_table(NULL::shop);
                                 '''
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")

        cursor = engine.connect()
        try:
            if list(cursor.execute(query_get_shops))[0][0]:
                [child.destroy() for child in self.master.winfo_children()]
                main_frame = ChangeShopsFrame(self.master)
                self.pack_forget()
                main_frame.pack(fill=tk.BOTH)
        except IndexError:
            msg.showerror('Ошибка',
                          'Чтобы изменять что-то ненужное, надо сначала добавить что-то ненужное, а у нас данных нет!')
        cursor.close()
        return

    def change_purchases(self):
        query_get_purchase = '''
                                                      SELECT print_table(NULL::purchase);
                                         '''
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")

        cursor = engine.connect()
        try:
            if list(cursor.execute(query_get_purchase))[0][0]:
                [child.destroy() for child in self.master.winfo_children()]
                main_frame = ChangePurchasesFrame(self.master)
                self.pack_forget()
                main_frame.pack(fill=tk.BOTH)
        except IndexError:
            msg.showerror('Ошибка',
                          'Чтобы изменять что-то ненужное, надо сначала добавить что-то ненужное, а у нас данных нет!')
        cursor.close()
        return

    def find_something(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = FindFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def __init__(self, parent):
        super().__init__(parent)
        # ЖИВОТНЫЕ

        self.master.geometry('700x220')
        self.config(bg="#6FE7DD")
        self.pets = tk.Label(self, text='Животные', bg='#6FE7DD', font=('GothamPro', 10))
        self.pets.grid(row=0, column=0, stick='wens')
        self.show_pets = tk.Button(self, text='Показать животных',
                                   font=('SolomonSans', 10),
                                   command=self.show_tables_pets)
        self.show_pets.grid(row=1, column=0, stick='wens')
        self.add_pet = tk.Button(self, text='Добавить животное',
                                 font=('SolomonSans', 10),
                                 command=self.insert_tables_pets)
        self.add_pet.grid(row=2, column=0, stick='wens')
        self.delete_pet = tk.Button(self, text='Удалить данные', font=('SolomonSans', 10),
                                    command=self.delete_pets)  # дописать команду потом
        self.delete_pet.grid(row=3, column=0, stick='wens')
        self.change_data_pets = tk.Button(self, text='Поменять данные',
                                          font=('SolomonSans', 10),
                                          command=self.change_pets)  # дописать команду потом
        self.change_data_pets.grid(row=4, column=0, stick='wens')
        self.back = tk.Button(self, text='Вернуться', command=self.back,
                              font=('SolomonSans', 10))
        self.back.grid(row=5, column=0, stick='wens')
        # ПОКУПАТЕЛИ

        self.cust = tk.Label(self, text='Покупатели', bg='#6FE7DD', font=('GothamPro', 10))
        self.cust.grid(row=0, column=1, stick='wens')
        self.show_cust = tk.Button(self, text='Показать покупателей',
                                   font=('SolomonSans', 10),
                                   command=self.show_tables_cust)
        self.show_cust.grid(row=1, column=1, stick='wens')
        self.add_cust = tk.Button(self, text='Добавить покупателя',
                                  font=('SolomonSans', 10),
                                  command=self.insert_tables_cust)  # дописать команду потом
        self.add_cust.grid(row=2, column=1, stick='wens')
        self.delete_cust = tk.Button(self, text='Удалить данные',
                                     font=('SolomonSans', 10),
                                     command=self.delete_cust)  # дописать команду потом
        self.delete_cust.grid(row=3, column=1, stick='wens')
        self.change_data_cust = tk.Button(self, text='Поменять данные',
                                          font=('SolomonSans', 10),
                                          command=self.change_cust)  # дописать команду потом
        self.change_data_cust.grid(row=4, column=1, stick='wens')
        self.delete_all = tk.Button(self, text='Очистить все таблицы',
                                    font=('SolomonSans', 10),
                                    command=self.clear_all_tables)
        self.delete_all.grid(row=5, column=1, stick='wens')
        # МАГАЗИНЫ

        self.shops = tk.Label(self, text='Магазины', bg='#6FE7DD', font=('GothamPro', 10))
        self.shops.grid(row=0, column=2, stick='wens')
        self.show_cust = tk.Button(self, text='Показать магазины',
                                   font=('SolomonSans', 10),
                                   command=self.show_tables_shops)  # дописать команду потом
        self.show_cust.grid(row=1, column=2, stick='wens')
        self.add_shops = tk.Button(self, text='Добавить магазин',
                                   font=('SolomonSans', 10),
                                   command=self.insert_tables_shops)  # дописать команду потом
        self.add_shops.grid(row=2, column=2, stick='wens')
        self.delete_shops = tk.Button(self, text='Удалить данные',
                                      font=('SolomonSans', 10),
                                      command=self.delete_shops)  # дописать команду потом
        self.delete_shops.grid(row=3, column=2, stick='wens')
        self.change_data_shops = tk.Button(self, text='Поменять данные',
                                           font=('SolomonSans', 10),
                                           command=self.change_shop)  # дописать команду потом
        self.change_data_shops.grid(row=4, column=2, stick='wens')
        self.find_something_btn = tk.Button(self, text='Найти что-нибудь',
                                            font=('SolomonSans', 10),
                                            command=self.find_something)
        self.find_something_btn.grid(row=5, column=2, stick='wens')
        # ПОКУПКИ

        self.purchase = tk.Label(self, text='Данные покупок', bg='#6FE7DD', font=('GothamPro', 10))
        self.purchase.grid(row=0, column=3, stick='wens')
        self.show_purchase = tk.Button(self, text='Показать покупки',
                                       font=('SolomonSans', 10),
                                       command=self.show_tables_purchases)  # дописать команду потом
        self.show_purchase.grid(row=1, column=3, stick='wens')
        self.add_purchase = tk.Button(self, text='Добавить покупку',
                                      font=('SolomonSans', 10),
                                      command=self.insert_tables_purchases)  # дописать команду потом
        self.add_purchase.grid(row=2, column=3, stick='wens')
        self.delete_purchase = tk.Button(self, text='Удалить данные',
                                         font=('SolomonSans', 10),
                                         command=self.delete_purchases)  # дописать команду потом
        self.delete_purchase.grid(row=3, column=3, stick='wens')
        self.change_data_purchase = tk.Button(self, text='Поменять данные',
                                              font=('SolomonSans', 10),
                                              command=self.change_purchases)  # дописать команду потом
        self.change_data_purchase.grid(row=4, column=3, stick='wens')

        self.grid_columnconfigure(0, minsize=175)
        self.grid_columnconfigure(1, minsize=175)
        self.grid_columnconfigure(2, minsize=175)
        self.grid_columnconfigure(3, minsize=175)

        self.grid_rowconfigure(0, minsize=37)
        self.grid_rowconfigure(1, minsize=37)
        self.grid_rowconfigure(2, minsize=37)
        self.grid_rowconfigure(3, minsize=37)
        self.grid_rowconfigure(4, minsize=37)
        self.grid_rowconfigure(5, minsize=37)


class TablesPetsFrame(tk.Frame):

    def back(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def __init__(self, parent):
        super().__init__(parent)

        self.engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        self.cursor_2 = self.engine_2.connect()

        self.config(bg="#6FE7DD")
        self.master.geometry('800x250')
        self.animals = []

        self.query_get_table = '''
            SELECT print_table(NULL::animals);
        '''

        try:
            if list(self.cursor_2.execute(self.query_get_table))[0][0]:
                for i in range(0, 100):
                    try:
                        self.animals.append(
                            list(self.cursor_2.execute(self.query_get_table))[i][0].replace('(', '').replace(')',
                                                                                                             '').split(
                                ','))
                    except IndexError:
                        break
                # определяем столбцы
                self.columns = ("Чип", "Вид", "Порода", "Возраст", "Окрас", 'Пол', "Стоимость", "Куплено",
                                "Айди магазина")

                self.tree = ttk.Treeview(columns=self.columns, show="headings")
                self.tree.pack()

                # определяем заголовки
                self.tree.heading("Чип", text="Чип", anchor=W)
                self.tree.heading("Вид", text="Вид", anchor=W)
                self.tree.heading("Порода", text="Порода", anchor=W)
                self.tree.heading("Возраст", text="Возраст", anchor=W)
                self.tree.heading("Окрас", text="Окрас", anchor=W)
                self.tree.heading("Пол", text="Пол", anchor=W)
                self.tree.heading("Стоимость", text="Стоимость", anchor=W)
                self.tree.heading("Куплено", text="Куплено", anchor=W)
                self.tree.heading("Айди магазина", text="ID магазина", anchor=W)

                self.tree.column("#1", stretch=NO, width=50)
                self.tree.column("#2", stretch=NO, width=50)
                self.tree.column("#3", stretch=NO, width=100)
                self.tree.column("#4", stretch=NO, width=100)
                self.tree.column("#5", stretch=NO, width=100)
                self.tree.column("#6", stretch=NO, width=100)
                self.tree.column("#7", stretch=NO, width=100)
                self.tree.column("#8", stretch=NO, width=100)
                self.tree.column("#9", stretch=NO, width=100)

                for i in self.animals:
                    self.tree.insert("", END, values=i)
        except IndexError:
            self.label = tk.Label(self, text='Здесь не на что смотреть...')
            self.label.pack()

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.pack()
        self.cursor_2.close()


class TablesCustFrame(tk.Frame):

    def back(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def __init__(self, parent):
        super().__init__(parent)

        self.engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        self.cursor_2 = self.engine_2.connect()

        self.config(bg="#6FE7DD")
        self.master.geometry('700x250')
        self.buyer = []

        self.query_get_table = '''
                    SELECT print_table(NULL::buyer);
                '''

        try:
            if list(self.cursor_2.execute(self.query_get_table))[0][0]:
                for i in range(0, 100):
                    try:
                        self.buyer.append(
                            list(self.cursor_2.execute(self.query_get_table))[i][0].replace('(', '').replace(')',
                                                                                                             '').split(
                                ','))
                    except IndexError:
                        break
                # определяем столбцы
                self.columns = ("Паспорт", "Имя", "Телефон", "Скидка")

                self.tree = ttk.Treeview(columns=self.columns, show="headings")
                self.tree.pack()

                # определяем заголовки
                self.tree.heading("Паспорт", text="Пасспорт", anchor=W)
                self.tree.heading("Имя", text="Имя", anchor=W)
                self.tree.heading("Телефон", text="Телефон", anchor=W)
                self.tree.heading("Скидка", text="Скидка", anchor=W)

                self.tree.column("#1", stretch=NO, width=200)
                self.tree.column("#2", stretch=NO, width=200)
                self.tree.column("#3", stretch=NO, width=200)
                self.tree.column("#4", stretch=NO, width=100)

                for i in self.buyer:
                    self.tree.insert("", END, values=i)
        except IndexError:
            self.label = tk.Label(self, text='Здесь не на что смотреть...')
            self.label.pack()

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.pack()
        self.cursor_2.close()


class TablesShopsFrame(tk.Frame):

    def back(self):
        self.cursor_2.close()
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def __init__(self, parent):
        super().__init__(parent)

        self.engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        self.cursor_2 = self.engine_2.connect()

        self.config(bg="#6FE7DD")
        self.master.geometry('700x250')
        self.shop = []

        self.query_get_table = '''
                            SELECT print_table(NULL::shop);
                        '''

        try:
            if list(self.cursor_2.execute(self.query_get_table))[0][0]:
                for i in range(0, 100):
                    try:
                        self.shop.append(
                            list(self.cursor_2.execute(self.query_get_table))[i][0].replace('(', '').replace(')',
                                                                                                             '').split(
                                ','))
                    except IndexError:
                        break
                    # определяем столбцы
                self.columns = ("ID", "Название", "Район", "Телефон")

                self.tree = ttk.Treeview(columns=self.columns, show="headings")
                self.tree.pack()

                # определяем заголовки
                self.tree.heading("ID", text="ID", anchor=W)
                self.tree.heading("Название", text="Название", anchor=W)
                self.tree.heading("Район", text="Район", anchor=W)
                self.tree.heading("Телефон", text="Телефон", anchor=W)

                self.tree.column("#1", stretch=NO, width=100)
                self.tree.column("#2", stretch=NO, width=200)
                self.tree.column("#3", stretch=NO, width=200)
                self.tree.column("#4", stretch=NO, width=200)

                for i in self.shop:
                    self.tree.insert("", END, values=i)
        except IndexError:
            self.label = tk.Label(self, text='Здесь не на что смотреть...')
            self.label.pack()

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.pack()
        self.cursor_2.close()


class TablesPurchasesFrame(tk.Frame):

    def back(self):
        self.cursor_2.close()
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def __init__(self, parent):
        super().__init__(parent)

        self.engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        self.cursor_2 = self.engine_2.connect()

        self.config(bg="#6FE7DD")
        self.master.geometry('700x250')
        self.purchase = []

        self.query_get_table = '''
                                    SELECT print_table(NULL::purchase);
                                '''

        try:
            if list(self.cursor_2.execute(self.query_get_table))[0][0]:
                for i in range(0, len(list(self.cursor_2.execute(self.query_get_table))) + 1):
                    try:
                        self.purchase.append(
                            list(self.cursor_2.execute(self.query_get_table))[i][0].replace('(', '').replace(')',
                                                                                                             '').split(
                                ','))
                    except IndexError:
                        break
                    # определяем столбцы
                self.columns = ("ID", "Дата", "Стоимость", "Чип", "ID покупателя")

                self.tree = ttk.Treeview(columns=self.columns, show="headings")
                self.tree.pack()

                # определяем заголовки
                self.tree.heading("ID", text="ID", anchor=W)
                self.tree.heading("Дата", text="Дата", anchor=W)
                self.tree.heading("Стоимость", text="Стоимость", anchor=W)
                self.tree.heading("Чип", text="Чип", anchor=W)
                self.tree.heading("ID покупателя", text="ID покупателя", anchor=W)

                self.tree.column("#1", stretch=NO, width=100)
                self.tree.column("#2", stretch=NO, width=200)
                self.tree.column("#3", stretch=NO, width=100)
                self.tree.column("#4", stretch=NO, width=100)
                self.tree.column("#5", stretch=NO, width=200)

                for i in self.purchase:
                    self.tree.insert("", END, values=i)
        except IndexError:
            self.label = tk.Label(self, text='Здесь не на что смотреть...')
            self.label.pack()

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.pack()
        self.cursor_2.close()


class InsertPetsFrame(tk.Frame):

    def back(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def submit(self, chip, vid, breed, age, color, sex, price, idshop):
        queue_insert = f'''
        Begin;
        SELECT insert_animal({chip}, '{vid}', '{breed}', {age}, '{color}', '{sex}', {price}, {idshop});
        Commit;
        '''
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        try:
            cursor.execute(queue_insert)
        except sqlalchemy.exc.IntegrityError:
            msg.showerror('Ошибка', 'Такой ID уже есть!')
            cursor.close()
            return
        cursor.close()

        msg.showinfo('Уведомление', 'Вы добавили животное!')
        return

    def __init__(self, parent):
        super().__init__(parent)
        self.config(bg="#6FE7DD")
        self.master.geometry('1170x220')

        self.label = tk.Label(self, text='Введите данные для добавления животного в таблицу', bg="#6FE7DD")
        self.label.grid(row=0, column=2, columnspan=4)

        self.engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        self.cursor_2 = self.engine_2.connect()

        self.shops = []

        self.query_get_shops = '''
                                            SELECT print_table(NULL::shop);
                                        '''

        for i in range(0, 100):
            try:
                self.shops.append(
                    list(self.cursor_2.execute(self.query_get_shops))[i][0].replace('(', '').replace(')',
                                                                                                     '').split(
                        ',')[0])
            except IndexError:
                break
        self.combo_id = ttk.Combobox(self, value=self.shops)
        self.combo_id.current(0)
        self.combo_id.grid(row=2, column=7, rowspan=2, stick='news', padx=5, pady=5)

        self.chip = tk.Label(self, text='Чип', bg="#6FE7DD")
        self.chip.grid(row=1, column=0)
        self.vid = tk.Label(self, text='Вид', bg="#6FE7DD")
        self.vid.grid(row=1, column=1)
        self.breed = tk.Label(self, text='Порода', bg="#6FE7DD")
        self.breed.grid(row=1, column=2)
        self.age = tk.Label(self, text='Возраст', bg="#6FE7DD")
        self.age.grid(row=1, column=3)
        self.color = tk.Label(self, text='Окрас', bg="#6FE7DD")
        self.color.grid(row=1, column=4)
        self.sex = tk.Label(self, text='Пол', bg="#6FE7DD")
        self.sex.grid(row=1, column=5)
        self.price = tk.Label(self, text='Стоимость', bg="#6FE7DD")
        self.price.grid(row=1, column=6)
        self.idshop = tk.Label(self, text='ID магазина', bg="#6FE7DD")
        self.idshop.grid(row=1, column=7)

        self.chip_entry = tk.Entry(self)
        self.chip_entry.grid(row=2, column=0, rowspan=2, stick='news', padx=5, pady=5)
        self.vid_entry = tk.Entry(self)
        self.vid_entry.grid(row=2, column=1, rowspan=2, stick='news', padx=5, pady=5)
        self.breed_entry = tk.Entry(self)
        self.breed_entry.grid(row=2, column=2, rowspan=2, stick='news', padx=5, pady=5)
        self.age_entry = tk.Entry(self)
        self.age_entry.grid(row=2, column=3, rowspan=2, stick='news', padx=5, pady=5)
        self.color_entry = tk.Entry(self)
        self.color_entry.grid(row=2, column=4, rowspan=2, stick='news', padx=5, pady=5)
        self.sex_entry = tk.Entry(self)
        self.sex_entry.grid(row=2, column=5, rowspan=2, stick='news', padx=5, pady=5)
        self.price_entry = tk.Entry(self)
        self.price_entry.grid(row=2, column=6, rowspan=2, stick='news', padx=5, pady=5)

        self.add_btn = tk.Button(self, text='Добавить', font=('SolomonSans', 10),
                                 command=lambda: self.submit(int(self.chip_entry.get()), self.vid_entry.get(),
                                                             self.breed_entry.get(), int(self.age_entry.get()),
                                                             self.color_entry.get(), self.sex_entry.get(),
                                                             int(self.price_entry.get()),
                                                             int(self.combo_id.get())))
        self.add_btn.grid(row=4, column=2, columnspan=4)

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.grid(row=5, column=2, columnspan=4)

        self.grid_columnconfigure(0, minsize=88)
        self.grid_columnconfigure(1, minsize=88)
        self.grid_columnconfigure(2, minsize=88)
        self.grid_columnconfigure(3, minsize=88)
        self.grid_columnconfigure(4, minsize=88)
        self.grid_columnconfigure(5, minsize=88)
        self.grid_columnconfigure(6, minsize=88)
        self.grid_columnconfigure(7, minsize=88)
        self.grid_columnconfigure(8, minsize=88)

        self.grid_rowconfigure(0, minsize=37)
        self.grid_rowconfigure(1, minsize=37)
        self.grid_rowconfigure(2, minsize=37)
        self.grid_rowconfigure(3, minsize=37)
        self.grid_rowconfigure(4, minsize=37)
        self.grid_rowconfigure(5, minsize=37)


class InsertCustFrame(tk.Frame):

    def back(self):
        self.cursor_2.close()
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def submit(self, passport, name, phone, discount):
        queue_insert = f'''
        Begin;
        SELECT insert_buyer({passport}, '{name}', {phone}, {discount});
        Commit;
        '''
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        try:
            cursor.execute(queue_insert)
        except sqlalchemy.exc.IntegrityError:
            msg.showerror('Ошибка', 'Такой ID уже есть!')
            cursor.close()
            return
        cursor.close()

        msg.showinfo('Уведомление', 'Вы добавили покупателя!')
        return

    def __init__(self, parent):
        super().__init__(parent)
        self.config(bg="#6FE7DD")
        self.master.geometry('700x220')

        self.engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        self.cursor_2 = self.engine_2.connect()

        self.label = tk.Label(self, text='Введите данные для добавления покупателя в таблицу', bg="#6FE7DD")
        self.label.grid(row=0, column=1, columnspan=2)

        self.passport = tk.Label(self, text='Паспорт', bg="#6FE7DD")
        self.passport.grid(row=1, column=0)
        self.name = tk.Label(self, text='Имя', bg="#6FE7DD")
        self.name.grid(row=1, column=1)
        self.phone = tk.Label(self, text='Телефон', bg="#6FE7DD")
        self.phone.grid(row=1, column=2)
        self.discount = tk.Label(self, text='Скидка', bg="#6FE7DD")
        self.discount.grid(row=1, column=3)

        self.passport_entry = tk.Entry(self)
        self.passport_entry.grid(row=2, column=0, rowspan=2, stick='news', padx=5, pady=5)
        self.name_entry = tk.Entry(self)
        self.name_entry.grid(row=2, column=1, rowspan=2, stick='news', padx=5, pady=5)
        self.phone_entry = tk.Entry(self)
        self.phone_entry.grid(row=2, column=2, rowspan=2, stick='news', padx=5, pady=5)
        self.discount_entry = tk.Entry(self)
        self.discount_entry.grid(row=2, column=3, rowspan=2, stick='news', padx=5, pady=5)

        self.add_btn = tk.Button(self, text='Добавить', font=('SolomonSans', 10),
                                 command=lambda: self.submit(int(self.passport_entry.get()), self.name_entry.get(),
                                                             int(self.phone_entry.get()),
                                                             int(self.discount_entry.get())))
        self.add_btn.grid(row=4, column=1, columnspan=2)

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.grid(row=5, column=1, columnspan=2)

        self.grid_columnconfigure(0, minsize=175)
        self.grid_columnconfigure(1, minsize=175)
        self.grid_columnconfigure(2, minsize=175)
        self.grid_columnconfigure(3, minsize=175)

        self.grid_rowconfigure(0, minsize=37)
        self.grid_rowconfigure(1, minsize=37)
        self.grid_rowconfigure(2, minsize=37)
        self.grid_rowconfigure(3, minsize=37)
        self.grid_rowconfigure(4, minsize=37)
        self.grid_rowconfigure(5, minsize=37)


class InsertShopsFrame(tk.Frame):

    def back(self):
        self.cursor_2.close()
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def submit(self, shop_id, name, district, phone):
        queue_insert = f'''
        Begin;
        SELECT insert_shop({shop_id}, '{name}', '{district}', {phone});
        Commit;
        '''
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        try:
            cursor.execute(queue_insert)
        except sqlalchemy.exc.IntegrityError:
            msg.showerror('Ошибка', 'Такой ID уже есть!')
            cursor.close()
            return
        cursor.close()

        msg.showinfo('Уведомление', 'Вы добавили магазин!')
        return

    def __init__(self, parent):
        super().__init__(parent)
        self.config(bg="#6FE7DD")
        self.master.geometry('700x220')

        self.engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        self.cursor_2 = self.engine_2.connect()

        self.label = tk.Label(self, text='Введите данные для добавления магазина в таблицу', bg="#6FE7DD")
        self.label.grid(row=0, column=1, columnspan=2)

        self.shop_id = tk.Label(self, text='ID магазина', bg="#6FE7DD")
        self.shop_id.grid(row=1, column=0)
        self.name = tk.Label(self, text='Имя', bg="#6FE7DD")
        self.name.grid(row=1, column=1)
        self.district = tk.Label(self, text='Район', bg="#6FE7DD")
        self.district.grid(row=1, column=2)
        self.phone = tk.Label(self, text='Телефон', bg="#6FE7DD")
        self.phone.grid(row=1, column=3)

        self.shop_id_entry = tk.Entry(self)
        self.shop_id_entry.grid(row=2, column=0, rowspan=2, stick='news', padx=5, pady=5)
        self.name_entry = tk.Entry(self)
        self.name_entry.grid(row=2, column=1, rowspan=2, stick='news', padx=5, pady=5)
        self.district_entry = tk.Entry(self)
        self.district_entry.grid(row=2, column=2, rowspan=2, stick='news', padx=5, pady=5)
        self.phone_entry = tk.Entry(self)
        self.phone_entry.grid(row=2, column=3, rowspan=2, stick='news', padx=5, pady=5)

        self.add_btn = tk.Button(self, text='Добавить', font=('SolomonSans', 10),
                                 command=lambda: self.submit(int(self.shop_id_entry.get()), self.name_entry.get(),
                                                             self.district_entry.get(), int(self.phone_entry.get())))
        self.add_btn.grid(row=4, column=1, columnspan=2)

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.grid(row=5, column=1, columnspan=2)

        self.grid_columnconfigure(0, minsize=175)
        self.grid_columnconfigure(1, minsize=175)
        self.grid_columnconfigure(2, minsize=175)
        self.grid_columnconfigure(3, minsize=175)

        self.grid_rowconfigure(0, minsize=37)
        self.grid_rowconfigure(1, minsize=37)
        self.grid_rowconfigure(2, minsize=37)
        self.grid_rowconfigure(3, minsize=37)
        self.grid_rowconfigure(4, minsize=37)
        self.grid_rowconfigure(5, minsize=37)


class InsertPurchasesFrame(tk.Frame):

    def back(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def submit(self, purchase_id, date, chip, cust_id):
        queue_insert = f'''
        Begin;
        SELECT insert_purchase({purchase_id}, '{date}', {chip}, {cust_id});
        Commit;
        '''
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        try:
            cursor.execute(queue_insert)
        except sqlalchemy.exc.IntegrityError:
            msg.showerror('Ошибка', 'Перепроверьте ID!')
            cursor.close()
            return
        cursor.close()

        msg.showinfo('Уведомление', 'Вы добавили покупку!')
        return

    def __init__(self, parent):
        super().__init__(parent)
        self.config(bg="#6FE7DD")
        self.master.geometry('826x220')

        self.label = tk.Label(self, text='Введите данные для добавления покупки в таблицу', bg="#6FE7DD")
        self.label.grid(row=0, column=2, columnspan=2)

        self.query_get_buyers = '''
                         SELECT print_table(NULL::buyer);
                '''
        self.query_get_stamp = '''
                         SELECT print_table(NULL::animals);
                '''
        self.engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        self.cursor = self.engine.connect()

        self.buyers = []
        self.stamps = []

        for i in range(0, 100):
            try:
                self.buyers.append(
                    list(self.cursor.execute(self.query_get_buyers))[i][0].replace('(', '').replace(')',
                                                                                                    '').split(
                        ',')[0])
                self.stamps.append(
                    list(self.cursor.execute(self.query_get_stamp))[i][0].replace('(', '').replace(')',
                                                                                                   '').split(
                        ',')[0])
            except IndexError:
                break

        self.combo_stamp = ttk.Combobox(self, value=self.stamps)
        self.combo_stamp.current(0)
        self.combo_stamp.grid(row=2, column=2, rowspan=2, stick='news', padx=5, pady=5)

        self.combo_buyer = ttk.Combobox(self, value=self.buyers)
        self.combo_buyer.current(0)
        self.combo_buyer.grid(row=2, column=3, rowspan=2, stick='news', padx=5, pady=5)

        self.purchase_id = tk.Label(self, text='ID покупки', bg="#6FE7DD")
        self.purchase_id.grid(row=1, column=0)
        self.date = tk.Label(self, text='Дата', bg="#6FE7DD")
        self.date.grid(row=1, column=1)
        self.chip = tk.Label(self, text='Чип животного', bg="#6FE7DD")
        self.chip.grid(row=1, column=2)
        self.cust_id = tk.Label(self, text='ID покупателя', bg="#6FE7DD")
        self.cust_id.grid(row=1, column=3)

        self.purchase_id_entry = tk.Entry(self)
        self.purchase_id_entry.grid(row=2, column=0, rowspan=2, stick='news', padx=5, pady=5)
        self.date_entry = tk.Entry(self)
        self.date_entry.grid(row=2, column=1, rowspan=2, stick='news', padx=5, pady=5)

        self.add_btn = tk.Button(self, text='Добавить', font=('SolomonSans', 10),
                                 command=lambda: self.submit(int(self.purchase_id_entry.get()), self.date_entry.get(),
                                                             int(self.combo_stamp.get()),
                                                             int(self.combo_buyer.get())))
        self.add_btn.grid(row=4, column=2, columnspan=2)

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.grid(row=5, column=2, columnspan=2)

        self.grid_columnconfigure(0, minsize=117)
        self.grid_columnconfigure(1, minsize=117)
        self.grid_columnconfigure(2, minsize=117)
        self.grid_columnconfigure(3, minsize=117)
        self.grid_columnconfigure(4, minsize=117)
        self.grid_columnconfigure(5, minsize=117)

        self.grid_rowconfigure(0, minsize=37)
        self.grid_rowconfigure(1, minsize=37)
        self.grid_rowconfigure(2, minsize=37)
        self.grid_rowconfigure(3, minsize=37)
        self.grid_rowconfigure(4, minsize=37)
        self.grid_rowconfigure(5, minsize=37)


class DeletePetsFrame(tk.Frame):

    def back(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def delete_table(self):
        engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor_2 = engine_2.connect()
        query_delete_table = '''
            Begin;
            select clear_table(NULL::animals);
            Commit;
        '''
        cursor_2.execute(query_delete_table)
        msg.showinfo('Уведомление', 'Таблица очищена! Больше очищать здесь нечего, возвращаем в основное меню')
        cursor_2.close()
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)

    def delete_row(self, numb):
        engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor_2 = engine_2.connect()
        query_delete_table = f'''
                    Begin;
                    select delete_row('animals', 'stamp', {numb});
                    Commit;
                '''
        cursor_2.execute(query_delete_table)
        msg.showinfo('Уведомление', 'Успешно удалено!')
        cursor_2.close()
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = DeletePetsFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)

    def __init__(self, parent):
        super().__init__(parent)
        self.config(bg="#6FE7DD")
        self.master.geometry('790x228')
        self.engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        self.cursor_2 = self.engine_2.connect()

        self.query_get_id = '''
            SELECT print_table(NULL::animals);
        '''

        self.id_list = []

        try:
            if list(self.cursor_2.execute(self.query_get_id))[0][0]:
                for i in range(0, 100):
                    try:
                        self.id_list.append(
                            list(self.cursor_2.execute(self.query_get_id))[i][0].replace('(', '').replace(')',
                                                                                                          '').split(
                                ',')[0])
                    except IndexError:
                        break
                self.combo_id = ttk.Combobox(self, value=self.id_list)
                self.combo_id.current(0)
                self.combo_id.grid(row=2, column=0)

                self.delete_row_btn = tk.Button(self, text='Подтвердить',
                                                command=lambda: self.delete_row(self.combo_id.get()),
                                                font=('SolomonSans', 10))
                self.delete_row_btn.grid(row=2, column=0, rowspan=2)
        except IndexError:
            self.warning = tk.Label(self, text='Нет животных!', bg='red')
            self.warning.grid(row=2, column=0)

        self.label = tk.Label(self, text='Выберите данные для удаления', bg="#6FE7DD", font=('GothamPro', 15))
        self.label.grid(row=0, column=1)

        self.delete_id = tk.Label(self, text='Удалить животное по ID', bg="#6FE7DD", font=('GothamPro', 10))
        self.delete_id.grid(row=1, column=0)

        self.delete_table_btn = tk.Button(self, text='Очистить таблицу \'Животные\'',
                                          command=self.delete_table,
                                          font=('SolomonSans', 10))
        self.delete_table_btn.grid(row=1, column=2, rowspan=2)

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.grid(row=5, column=1)

        self.grid_columnconfigure(0, minsize=233)
        self.grid_columnconfigure(1, minsize=233)
        self.grid_columnconfigure(2, minsize=233)

        self.grid_rowconfigure(0, minsize=40)
        self.grid_rowconfigure(1, minsize=40)
        self.grid_rowconfigure(2, minsize=40)
        self.grid_rowconfigure(3, minsize=40)
        self.grid_rowconfigure(4, minsize=40)

        self.cursor_2.close()


class DeleteCustFrame(tk.Frame):

    def back(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def delete_table(self):
        engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor_2 = engine_2.connect()
        query_delete_table = '''
            Begin;
            select clear_table(NULL::buyer);
            Commit;
        '''
        cursor_2.execute(query_delete_table)
        msg.showinfo('Уведомление', 'Таблица очищена! Больше очищать здесь нечего, возвращаем в основное меню')
        cursor_2.close()
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)

    def delete_row(self, numb):
        engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor_2 = engine_2.connect()
        query_delete_table = f'''
                    Begin;
                    select delete_row('buyer', 'pasport', {numb});
                    Commit;
                '''
        cursor_2.execute(query_delete_table)
        msg.showinfo('Уведомление', 'Успешно удалено!')
        cursor_2.close()
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = DeleteCustFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)

    def delete_by_phone(self, phone):
        engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor_2 = engine_2.connect()
        query_delete_table = f'''
                              Begin;
                              select delete_buyer_by_phone({phone});
                              Commit;
                            '''
        cursor_2.execute(query_delete_table)
        msg.showinfo('Уведомление', 'Успешно удалено!')
        cursor_2.close()
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = DeleteCustFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)

    def __init__(self, parent):
        super().__init__(parent)
        self.config(bg="#6FE7DD")
        self.master.geometry('790x228')
        self.engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        self.cursor_2 = self.engine_2.connect()

        self.query_get_id = '''
            SELECT print_table(NULL::buyer);
        '''

        self.id_list = []
        self.phone_list = []

        try:
            if list(self.cursor_2.execute(self.query_get_id))[0][0]:
                for i in range(0, 100):
                    try:
                        self.id_list.append(
                            list(self.cursor_2.execute(self.query_get_id))[i][0].replace('(', '').replace(')',
                                                                                                          '').split(
                                ',')[0])
                    except IndexError:
                        break
                self.combo_id = ttk.Combobox(self, value=self.id_list)
                self.combo_id.current(0)
                self.combo_id.grid(row=2, column=0)

                self.delete_row_btn = tk.Button(self, text='Подтвердить',
                                                command=lambda: self.delete_row(self.combo_id.get()),
                                                font=('SolomonSans', 10))
                self.delete_row_btn.grid(row=3, column=0, rowspan=2)

                for i in range(0, 100):
                    try:
                        self.phone_list.append(
                            list(self.cursor_2.execute(self.query_get_id))[i][0].replace('(', '').replace(')',
                                                                                                          '').split(
                                ',')[2])
                    except IndexError:
                        break
                self.combo_phone = ttk.Combobox(self, value=self.phone_list)
                self.combo_phone.current(0)
                self.combo_phone.grid(row=2, column=1)

                self.delete_by_phone_btn = tk.Button(self, text='Подтвердить',
                                                     command=lambda: self.delete_by_phone(self.combo_phone.get()),
                                                     font=('SolomonSans', 10))
                self.delete_by_phone_btn.grid(row=3, column=1, rowspan=2)
        except IndexError:
            self.warning = tk.Label(self, text='Нет покупателей!', bg='red')
            self.warning.grid(row=2, column=0, columnspan=2, stick='wens')

        self.label = tk.Label(self, text='Выберите данные для удаления', bg="#6FE7DD", font=('GothamPro', 15))
        self.label.grid(row=0, column=1)

        self.delete_id = tk.Label(self, text='Удалить покупателя по паспорту', bg="#6FE7DD", font=('GothamPro', 10))
        self.delete_id.grid(row=1, column=0)

        self.delete_id = tk.Label(self, text='Удалить покупателя по номеру телефона', bg="#6FE7DD",
                                  font=('GothamPro', 10))
        self.delete_id.grid(row=1, column=1)

        self.delete_table_btn = tk.Button(self, text='Очистить таблицу \'Покупатели\'',
                                          command=self.delete_table,
                                          font=('SolomonSans', 10))
        self.delete_table_btn.grid(row=1, column=2, rowspan=2)

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.grid(row=5, column=1)

        self.grid_columnconfigure(0, minsize=233)
        self.grid_columnconfigure(1, minsize=233)
        self.grid_columnconfigure(2, minsize=233)

        self.grid_rowconfigure(0, minsize=40)
        self.grid_rowconfigure(1, minsize=40)
        self.grid_rowconfigure(2, minsize=40)
        self.grid_rowconfigure(3, minsize=40)
        self.grid_rowconfigure(4, minsize=40)

        self.cursor_2.close()


class DeleteShopsFrame(tk.Frame):

    def back(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def delete_table(self):
        engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor_2 = engine_2.connect()
        query_delete_table = '''
            Begin;
            select clear_table(NULL::shop);
            Commit;
        '''
        cursor_2.execute(query_delete_table)
        msg.showinfo('Уведомление', 'Таблица очищена! Больше очищать здесь нечего, возвращаем в основное меню')
        cursor_2.close()
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)

    def delete_row(self, numb):
        engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor_2 = engine_2.connect()
        query_delete_table = f'''
                    Begin;
                    select delete_row('shop', 'id', {numb});
                    Commit;
                '''
        cursor_2.execute(query_delete_table)
        msg.showinfo('Уведомление', 'Успешно удалено!')
        cursor_2.close()
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = DeleteShopsFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)

    def replace_bounds(self, stroke):
        lr = []
        coord = []
        for i, j in enumerate(stroke, 0):
            if j == '{' or j == '}':
                coord.append(i)

        st = stroke.split()
        name = ''
        dist = ''
        if len(coord) == 2:
            name = st[0]
            dist = stroke[coord[0] + 2:coord[1] - 1]

        else:
            name = stroke[coord[0] + 2:coord[1] - 1]
            dist = stroke[coord[2] + 2:coord[3] - 1]

        return name, dist

    def delete_shop_by_location(self, district, name):
        engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor_2 = engine_2.connect()
        query_delete_table = f'''
                            Begin;
                            select delete_shop_by_location('{district}', '{name}');
                            Commit;
                        '''
        cursor_2.execute(query_delete_table)
        print(district, name)
        print()
        msg.showinfo('Уведомление', 'Успешно удалено!')
        cursor_2.close()
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = DeleteShopsFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)

    def __init__(self, parent):
        super().__init__(parent)
        self.config(bg="#6FE7DD")
        self.master.geometry('790x228')
        self.engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        self.cursor_2 = self.engine_2.connect()

        self.query_get_id = '''
            SELECT print_table(NULL::shop);
        '''

        self.id_list = []
        self.district_name_list = []

        try:
            if list(self.cursor_2.execute(self.query_get_id))[0][0]:
                for i in range(0, 100):
                    try:
                        self.id_list.append(
                            list(self.cursor_2.execute(self.query_get_id))[i][0].replace('(', '').replace(')',
                                                                                                          '').split(
                                ',')[0])
                    except IndexError:
                        break
                self.combo_id = ttk.Combobox(self, value=self.id_list)
                self.combo_id.current(0)
                self.combo_id.grid(row=2, column=0)

                self.delete_row_btn = tk.Button(self, text='Подтвердить',
                                                command=lambda: self.delete_row(self.combo_id.get()),
                                                font=('SolomonSans', 10))
                self.delete_row_btn.grid(row=3, column=0, rowspan=2)
                for i in range(0, 100):
                    try:
                        self.district_name_list.append(
                            list(self.cursor_2.execute(self.query_get_id))[i][0].replace('(', '').replace(')',
                                                                                                          '').split(
                                ',')[1:3])
                    except IndexError:
                        break
                self.combo_district_name = ttk.Combobox(self, value=self.district_name_list)
                self.combo_district_name.current(0)
                self.combo_district_name.grid(row=2, column=1)

                self.delete_shop_by_location_btn = tk.Button(self, text='Подтвердить',
                                                             command=lambda: self.delete_shop_by_location(
                                                                 self.replace_bounds(self.combo_district_name.get())[1],
                                                                 self.replace_bounds(self.combo_district_name.get())[0]),
                                                             font=('SolomonSans', 10))
                self.delete_shop_by_location_btn.grid(row=3, column=1, rowspan=2)
        except IndexError:
            self.warning = tk.Label(self, text='Нет магазинов!', bg='red')
            self.warning.grid(row=2, column=0, columnspan=2)

        self.label = tk.Label(self, text='Выберите данные для удаления', bg="#6FE7DD", font=('GothamPro', 15))
        self.label.grid(row=0, column=1)

        self.delete_id = tk.Label(self, text='Удалить магазин по ID', bg="#6FE7DD", font=('GothamPro', 10))
        self.delete_id.grid(row=1, column=0)

        self.delete_id = tk.Label(self, text='Удалить магазин по имени и району', bg="#6FE7DD", font=('GothamPro', 10))
        self.delete_id.grid(row=1, column=1)

        self.delete_table_btn = tk.Button(self, text='Очистить таблицу \'Магазины\'',
                                          command=self.delete_table,
                                          font=('SolomonSans', 10))
        self.delete_table_btn.grid(row=1, column=2, rowspan=2)

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.grid(row=5, column=1)

        self.grid_columnconfigure(0, minsize=233)
        self.grid_columnconfigure(1, minsize=233)
        self.grid_columnconfigure(2, minsize=233)

        self.grid_rowconfigure(0, minsize=40)
        self.grid_rowconfigure(1, minsize=40)
        self.grid_rowconfigure(2, minsize=40)
        self.grid_rowconfigure(3, minsize=40)
        self.grid_rowconfigure(4, minsize=40)

        self.cursor_2.close()


class DeletePurchasesFrame(tk.Frame):

    def back(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def delete_table(self):
        engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor_2 = engine_2.connect()
        query_delete_table = '''
            Begin;
            select clear_table(NULL::purchase);
            Commit;
        '''
        cursor_2.execute(query_delete_table)
        msg.showinfo('Уведомление', 'Таблица очищена! Больше очищать здесь нечего, возвращаем в основное меню')
        cursor_2.close()
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def delete_row(self, numb):
        engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor_2 = engine_2.connect()
        query_delete_table = f'''
                    Begin;
                    select delete_row('purchase', 'id', {numb});
                    Commit;
                '''
        cursor_2.execute(query_delete_table)
        msg.showinfo('Уведомление', 'Успешно удалено!')
        cursor_2.close()
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = DeletePurchasesFrame(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def delete_purchase_ps(self, phone, stamp):
        engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor_2 = engine_2.connect()
        query_delete_table_test = f'''
                                    Begin;
                                    select delete_purchase_by_stamp_phone({phone}, {stamp});
                                '''
        query_delete_table = f'''
                            Commit;
                        '''
        if list(cursor_2.execute(query_delete_table_test))[0][0]:
            cursor_2.execute(query_delete_table)
            msg.showinfo('Уведомление', 'Успешно удалено!')
            cursor_2.close()
            [child.destroy() for child in self.master.winfo_children()]
            main_frame = DeletePurchasesFrame(self.master)
            self.pack_forget()
            main_frame.pack(fill=tk.BOTH)
            return
        else:
            msg.showerror('Ошибка', 'Такого покупателя с таким животным нет!')
            return

    def __init__(self, parent):
        super().__init__(parent)
        self.config(bg="#6FE7DD")
        self.master.geometry('880x228')
        self.engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        self.cursor_2 = self.engine_2.connect()

        self.query_get_id_purchase = '''
            SELECT print_table(NULL::purchase);
        '''
        self.query_get_phone_cust = '''
            SELECT print_table(NULL::buyer);
        '''
        self.query_get_stamp_pets = '''
            SELECT print_table(NULL::animals);
        '''

        self.id_list = []
        self.stamp_list = []
        self.phone_list = []

        try:
            if list(self.cursor_2.execute(self.query_get_id_purchase))[0][0]:
                for i in range(0, 100):
                    try:
                        self.id_list.append(
                            list(self.cursor_2.execute(self.query_get_id_purchase))[i][0].replace('(', '').replace(')',
                                                                                                                   '').split(
                                ',')[0])
                    except IndexError:
                        break
                self.combo_id = ttk.Combobox(self, value=self.id_list)
                self.combo_id.current(0)
                self.combo_id.grid(row=2, column=0)

                self.delete_row_btn = tk.Button(self, text='Подтвердить',
                                                command=lambda: self.delete_row(self.combo_id.get()),
                                                font=('SolomonSans', 10))
                self.delete_row_btn.grid(row=3, column=0, rowspan=2)
        except IndexError:
            self.warning = tk.Label(self, text='Нет покупок!', bg='red')
            self.warning.grid(row=2, column=0)

        try:
            if list(self.cursor_2.execute(self.query_get_phone_cust))[0][0] and \
                    list(self.cursor_2.execute(self.query_get_stamp_pets))[0][0] and \
                    list(self.cursor_2.execute(self.query_get_id_purchase))[0][0]:
                for i in range(0, 100):
                    try:
                        self.phone_list.append(
                            list(self.cursor_2.execute(self.query_get_phone_cust))[i][0].replace('(', '').replace(')',
                                                                                                                  '').split(
                                ',')[2])
                    except IndexError:
                        break
                for i in range(0, 100):
                    try:
                        self.stamp_list.append(
                            list(self.cursor_2.execute(self.query_get_stamp_pets))[i][0].replace('(', '').replace(')',
                                                                                                                  '').split(
                                ',')[0])
                    except IndexError:
                        break
                self.combo_phone = ttk.Combobox(self, value=self.phone_list)
                self.combo_phone.current(0)
                self.combo_phone.grid(row=2, column=1, stick='wens')

                self.combo_stamp = ttk.Combobox(self, value=self.stamp_list)
                self.combo_stamp.current(0)
                self.combo_stamp.grid(row=2, column=2, stick='wens')

                self.delete_purchase_phone_stamp_btn = tk.Button(self, text='Удалить',
                                                                 command=lambda: self.delete_purchase_ps(
                                                                     self.combo_phone.get(), self.combo_stamp.get()),
                                                                 font=('SolomonSans', 10))
                self.delete_purchase_phone_stamp_btn.grid(row=3, column=1, columnspan=2)
        except IndexError:
            self.warning = tk.Label(self, text='Недостаточно данных!', bg='red')
            self.warning.grid(row=2, column=1, columnspan=2)

        self.label = tk.Label(self, text='Выберите данные для удаления', bg="#6FE7DD", font=('GothamPro', 15))
        self.label.grid(row=0, column=1)

        self.delete_id = tk.Label(self, text='Удалить покупку по ID', bg="#6FE7DD", font=('GothamPro', 10))
        self.delete_id.grid(row=1, column=0)

        self.delete_purchase_phone_stamp = tk.Label(self, text='Удалить покупку по номеру телефона и чипу',
                                                    bg="#6FE7DD", font=('GothamPro', 10))
        self.delete_purchase_phone_stamp.grid(row=1, column=1, columnspan=2)

        self.delete_table_btn = tk.Button(self, text='Очистить таблицу \'Магазины\'',
                                          command=self.delete_table,
                                          font=('SolomonSans', 10))
        self.delete_table_btn.grid(row=2, column=3, rowspan=2)

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.grid(row=5, column=1)

        self.grid_columnconfigure(0, minsize=175)
        self.grid_columnconfigure(1, minsize=175)
        self.grid_columnconfigure(2, minsize=175)
        self.grid_columnconfigure(3, minsize=175)

        self.grid_rowconfigure(0, minsize=40)
        self.grid_rowconfigure(1, minsize=40)
        self.grid_rowconfigure(2, minsize=40)
        self.grid_rowconfigure(3, minsize=40)
        self.grid_rowconfigure(4, minsize=40)

        self.cursor_2.close()


class ChangePetsFrame(tk.Frame):

    def back(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def submit(self, chip, new_chip, vid, breed, age, color, sex, price, idshop):
        queue_insert = f'''
        Begin;
        SELECT update_animal_by_stamp({chip}, {new_chip}, '{vid}', '{breed}', {age}, '{color}',
         '{sex}', {price}, {idshop});
        Commit;
        '''
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        cursor.execute(queue_insert)
        cursor.close()

        msg.showinfo('Уведомление', 'Вы изменили данные животного!')
        return

    def __init__(self, parent):
        super().__init__(parent)
        self.config(bg="#6FE7DD")
        self.master.geometry('1330x220')
        self.engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        self.cursor_2 = self.engine_2.connect()

        self.label = tk.Label(self, text='Введите данные для изменения животного', bg="#6FE7DD")
        self.label.grid(row=0, column=2, columnspan=4)

        self.query_get_stamps = '''
                    SELECT print_table(NULL::animals);
                '''
        self.query_get_shops = '''
                      SELECT print_table(NULL::shop);
                  '''
        self.shops = []
        self.stamps = []

        for i in range(0, 100):
            try:
                self.stamps.append(
                    list(self.cursor_2.execute(self.query_get_stamps))[i][0].replace('(', '').replace(')',
                                                                                                      '').split(
                        ',')[0])
                self.shops.append(
                    list(self.cursor_2.execute(self.query_get_shops))[i][0].replace('(', '').replace(')',
                                                                                                     '').split(
                        ',')[0])
            except IndexError:
                break

        self.combo_stamp = ttk.Combobox(self, value=self.stamps)
        self.combo_stamp.current(0)
        self.combo_stamp.grid(row=2, column=0, rowspan=2, stick='news', padx=5, pady=5)

        self.combo_shop = ttk.Combobox(self, value=self.shops)
        self.combo_shop.current(0)
        self.combo_shop.grid(row=2, column=8, rowspan=2, stick='news', padx=5, pady=5)

        self.chip_old = tk.Label(self, text='Старый чип', bg="#6FE7DD")
        self.chip_old.grid(row=1, column=0)
        self.chip = tk.Label(self, text='Новый чип', bg="#6FE7DD")
        self.chip.grid(row=1, column=1)
        self.vid = tk.Label(self, text='Вид', bg="#6FE7DD")
        self.vid.grid(row=1, column=2)
        self.breed = tk.Label(self, text='Порода', bg="#6FE7DD")
        self.breed.grid(row=1, column=3)
        self.age = tk.Label(self, text='Возраст', bg="#6FE7DD")
        self.age.grid(row=1, column=4)
        self.color = tk.Label(self, text='Окрас', bg="#6FE7DD")
        self.color.grid(row=1, column=5)
        self.sex = tk.Label(self, text='Пол', bg="#6FE7DD")
        self.sex.grid(row=1, column=6)
        self.price = tk.Label(self, text='Стоимость', bg="#6FE7DD")
        self.price.grid(row=1, column=7)
        self.idshop = tk.Label(self, text='ID магазина', bg="#6FE7DD")
        self.idshop.grid(row=1, column=8)

        self.chip_entry = tk.Entry(self)
        self.chip_entry.grid(row=2, column=1, rowspan=2, stick='news', padx=5, pady=5)
        self.vid_entry = tk.Entry(self)
        self.vid_entry.grid(row=2, column=2, rowspan=2, stick='news', padx=5, pady=5)
        self.breed_entry = tk.Entry(self)
        self.breed_entry.grid(row=2, column=3, rowspan=2, stick='news', padx=5, pady=5)
        self.age_entry = tk.Entry(self)
        self.age_entry.grid(row=2, column=4, rowspan=2, stick='news', padx=5, pady=5)
        self.color_entry = tk.Entry(self)
        self.color_entry.grid(row=2, column=5, rowspan=2, stick='news', padx=5, pady=5)
        self.sex_entry = tk.Entry(self)
        self.sex_entry.grid(row=2, column=6, rowspan=2, stick='news', padx=5, pady=5)
        self.price_entry = tk.Entry(self)
        self.price_entry.grid(row=2, column=7, rowspan=2, stick='news', padx=5, pady=5)

        self.add_btn = tk.Button(self, text='Изменить', font=('SolomonSans', 10),
                                 command=lambda: self.submit(int(self.combo_stamp.get()), self.chip_entry.get(),
                                                             self.vid_entry.get(),
                                                             self.breed_entry.get(), int(self.age_entry.get()),
                                                             self.color_entry.get(), self.sex_entry.get(),
                                                             int(self.price_entry.get()),
                                                             int(self.combo_shop.get())))
        self.add_btn.grid(row=4, column=2, columnspan=4)

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.grid(row=5, column=1)

        self.grid_columnconfigure(0, minsize=88)
        self.grid_columnconfigure(1, minsize=88)
        self.grid_columnconfigure(2, minsize=88)
        self.grid_columnconfigure(3, minsize=88)
        self.grid_columnconfigure(4, minsize=88)
        self.grid_columnconfigure(5, minsize=88)
        self.grid_columnconfigure(6, minsize=88)
        self.grid_columnconfigure(7, minsize=88)
        self.grid_columnconfigure(8, minsize=88)
        self.grid_columnconfigure(9, minsize=88)

        self.grid_rowconfigure(0, minsize=37)
        self.grid_rowconfigure(1, minsize=37)
        self.grid_rowconfigure(2, minsize=37)
        self.grid_rowconfigure(3, minsize=37)
        self.grid_rowconfigure(4, minsize=37)
        self.grid_rowconfigure(5, minsize=37)


class ChangeCustFrame(tk.Frame):

    def back(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def submit(self, passport, new_passport, name, phone, discount):
        queue_insert = f'''
        Begin;
        SELECT update_buyer_by_passport({passport}, {new_passport}, '{name}', {phone}, {discount});
        Commit;
        '''
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        cursor.execute(queue_insert)
        cursor.close()

        msg.showinfo('Уведомление', 'Вы изменили покупателя!')
        return

    def __init__(self, parent):
        super().__init__(parent)
        self.config(bg="#6FE7DD")
        self.master.geometry('800x220')

        self.engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        self.cursor_2 = self.engine_2.connect()

        self.label = tk.Label(self, text='Введите данные для изменения покупателя', bg="#6FE7DD")
        self.label.grid(row=0, column=1, columnspan=2)

        self.query_get_buyer = '''
                              SELECT print_table(NULL::buyer);
                          '''
        self.buyers = []

        for i in range(0, 100):
            try:
                self.buyers.append(
                    list(self.cursor_2.execute(self.query_get_buyer))[i][0].replace('(', '').replace(')',
                                                                                                     '').split(
                        ',')[0])
            except IndexError:
                break
        self.combo_pass = ttk.Combobox(self, value=self.buyers)
        self.combo_pass.current(0)
        self.combo_pass.grid(row=2, column=0, rowspan=2, stick='news', padx=5, pady=5)

        self.passport_old = tk.Label(self, text='Паспорт', bg="#6FE7DD")
        self.passport_old.grid(row=1, column=0)
        self.passport = tk.Label(self, text='Паспорт', bg="#6FE7DD")
        self.passport.grid(row=1, column=1)
        self.name = tk.Label(self, text='Имя', bg="#6FE7DD")
        self.name.grid(row=1, column=2)
        self.phone = tk.Label(self, text='Телефон', bg="#6FE7DD")
        self.phone.grid(row=1, column=3)
        self.discount = tk.Label(self, text='Скидка', bg="#6FE7DD")
        self.discount.grid(row=1, column=4)

        self.passport_entry = tk.Entry(self)
        self.passport_entry.grid(row=2, column=1, rowspan=2, stick='news', padx=5, pady=5)
        self.name_entry = tk.Entry(self)
        self.name_entry.grid(row=2, column=2, rowspan=2, stick='news', padx=5, pady=5)
        self.phone_entry = tk.Entry(self)
        self.phone_entry.grid(row=2, column=3, rowspan=2, stick='news', padx=5, pady=5)
        self.discount_entry = tk.Entry(self)
        self.discount_entry.grid(row=2, column=4, rowspan=2, stick='news', padx=5, pady=5)

        self.add_btn = tk.Button(self, text='Изменить', font=('SolomonSans', 10),
                                 command=lambda: self.submit(self.combo_pass.get(),
                                                             int(self.passport_entry.get()),
                                                             self.name_entry.get(),
                                                             int(self.phone_entry.get()),
                                                             int(self.discount_entry.get())))
        self.add_btn.grid(row=4, column=1, columnspan=2)

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.grid(row=5, column=1, columnspan=2)

        self.grid_columnconfigure(0, minsize=160)
        self.grid_columnconfigure(1, minsize=160)
        self.grid_columnconfigure(2, minsize=160)
        self.grid_columnconfigure(3, minsize=160)
        self.grid_columnconfigure(4, minsize=160)

        self.grid_rowconfigure(0, minsize=37)
        self.grid_rowconfigure(1, minsize=37)
        self.grid_rowconfigure(2, minsize=37)
        self.grid_rowconfigure(3, minsize=37)
        self.grid_rowconfigure(4, minsize=37)
        self.grid_rowconfigure(5, minsize=37)


class ChangeShopsFrame(tk.Frame):
    def back(self):
        self.cursor_2.close()
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def submit(self, shop_id, new_shop_id, name, district, phone):
        queue_insert = f'''
        Begin;
        SELECT update_shop_by_id({shop_id}, {new_shop_id}, '{name}', '{district}', {phone});
        Commit;
        '''
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        cursor.execute(queue_insert)
        cursor.close()

        msg.showinfo('Уведомление', 'Вы изменили магазин!')
        return

    def __init__(self, parent):
        super().__init__(parent)
        self.config(bg="#6FE7DD")
        self.master.geometry('800x220')

        self.engine_2 = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        self.cursor_2 = self.engine_2.connect()

        self.label = tk.Label(self, text='Введите данные для изменения магазина', bg="#6FE7DD")
        self.label.grid(row=0, column=1, columnspan=2)

        self.query_get_shop = '''
                                      SELECT print_table(NULL::shop);
                                  '''
        self.shops = []

        for i in range(0, 100):
            try:
                self.shops.append(
                    list(self.cursor_2.execute(self.query_get_shop))[i][0].replace('(', '').replace(')',
                                                                                                    '').split(
                        ',')[0])
            except IndexError:
                break
        self.combo_shop = ttk.Combobox(self, value=self.shops)
        self.combo_shop.current(0)
        self.combo_shop.grid(row=2, column=0, rowspan=2, stick='news', padx=5, pady=5)

        self.shop_id = tk.Label(self, text='ID магазина', bg="#6FE7DD")
        self.shop_id.grid(row=1, column=0)
        self.shop_id = tk.Label(self, text='Новый ID магазина', bg="#6FE7DD")
        self.shop_id.grid(row=1, column=1)
        self.name = tk.Label(self, text='Имя', bg="#6FE7DD")
        self.name.grid(row=1, column=2)
        self.district = tk.Label(self, text='Район', bg="#6FE7DD")
        self.district.grid(row=1, column=3)
        self.phone = tk.Label(self, text='Телефон', bg="#6FE7DD")
        self.phone.grid(row=1, column=4)

        self.shop_id_entry = tk.Entry(self)
        self.shop_id_entry.grid(row=2, column=1, rowspan=2, stick='news', padx=5, pady=5)
        self.name_entry = tk.Entry(self)
        self.name_entry.grid(row=2, column=2, rowspan=2, stick='news', padx=5, pady=5)
        self.district_entry = tk.Entry(self)
        self.district_entry.grid(row=2, column=3, rowspan=2, stick='news', padx=5, pady=5)
        self.phone_entry = tk.Entry(self)
        self.phone_entry.grid(row=2, column=4, rowspan=2, stick='news', padx=5, pady=5)

        self.add_btn = tk.Button(self, text='Изменить', font=('SolomonSans', 10),
                                 command=lambda: self.submit(self.combo_shop.get(),
                                                             int(self.shop_id_entry.get()), self.name_entry.get(),
                                                             self.district_entry.get(), int(self.phone_entry.get())))
        self.add_btn.grid(row=4, column=1, columnspan=2)

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.grid(row=5, column=1, columnspan=2)

        self.grid_columnconfigure(0, minsize=160)
        self.grid_columnconfigure(1, minsize=160)
        self.grid_columnconfigure(2, minsize=160)
        self.grid_columnconfigure(3, minsize=160)
        self.grid_columnconfigure(4, minsize=160)

        self.grid_rowconfigure(0, minsize=37)
        self.grid_rowconfigure(1, minsize=37)
        self.grid_rowconfigure(2, minsize=37)
        self.grid_rowconfigure(3, minsize=37)
        self.grid_rowconfigure(4, minsize=37)
        self.grid_rowconfigure(5, minsize=37)


class ChangePurchasesFrame(tk.Frame):

    def back(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def submit(self, purchase_id, new_purchase_id, date):
        queue_insert = f'''
        Begin;
        SELECT update_purchase_by_id({purchase_id}, {new_purchase_id}, '{date}');
        Commit;
        '''
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        cursor.execute(queue_insert)
        cursor.close()

        msg.showinfo('Уведомление', 'Вы изменили покупку!')
        return

    def __init__(self, parent):
        super().__init__(parent)
        self.config(bg="#6FE7DD")
        self.master.geometry('826x220')

        self.label = tk.Label(self, text='Введите данные для изменения покупки', bg="#6FE7DD")
        self.label.grid(row=0, column=2, columnspan=2)

        self.query_get_id = '''
                         SELECT print_table(NULL::purchase);
                '''
        self.engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        self.cursor = self.engine.connect()

        self.purchases_id = []
        for i in range(0, 100):
            try:
                self.purchases_id.append(
                    list(self.cursor.execute(self.query_get_id))[i][0].replace('(', '').replace(')',
                                                                                                '').split(
                        ',')[0])
            except IndexError:
                break
        self.combo_stamp = ttk.Combobox(self, value=self.purchases_id)
        self.combo_stamp.current(0)
        self.combo_stamp.grid(row=2, column=0, rowspan=2, stick='news', padx=5, pady=5)

        self.purchase_id = tk.Label(self, text='ID покупки', bg="#6FE7DD")
        self.purchase_id.grid(row=1, column=0)
        self.date = tk.Label(self, text='Новый ID покупки', bg="#6FE7DD")
        self.date.grid(row=1, column=1)
        self.price = tk.Label(self, text='Дата', bg="#6FE7DD")
        self.price.grid(row=1, column=2)

        self.purchase_id_entry = tk.Entry(self)
        self.purchase_id_entry.grid(row=2, column=1, rowspan=2, stick='news', padx=5, pady=5)
        self.date_entry = tk.Entry(self)
        self.date_entry.grid(row=2, column=2, rowspan=2, stick='news', padx=5, pady=5)

        self.add_btn = tk.Button(self, text='Изменить', font=('SolomonSans', 10),
                                 command=lambda: self.submit(self.combo_stamp.get(),
                                                             int(self.purchase_id_entry.get()),
                                                             self.date_entry.get()))
        self.add_btn.grid(row=4, column=1, columnspan=2)

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.grid(row=5, column=1, columnspan=2)

        self.grid_columnconfigure(0, minsize=250)
        self.grid_columnconfigure(1, minsize=250)
        self.grid_columnconfigure(2, minsize=250)

        self.grid_rowconfigure(0, minsize=37)
        self.grid_rowconfigure(1, minsize=37)
        self.grid_rowconfigure(2, minsize=37)
        self.grid_rowconfigure(3, minsize=37)
        self.grid_rowconfigure(4, minsize=37)
        self.grid_rowconfigure(5, minsize=37)


class FindFrame(tk.Frame):

    def back(self):
        [child.destroy() for child in self.master.winfo_children()]
        main_frame = ChangingTables(self.master)
        self.pack_forget()
        main_frame.pack(fill=tk.BOTH)
        return

    def find_phen(self, species, breed, color):
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        query_get_phen = f'''
                                 SELECT find_animal_by_phenotype('{species}', '{breed}', '{color}');
                        '''
        animals = []
        try:
            if list(cursor.execute(query_get_phen))[0][0] and species != '' and breed != '' and color != '':
                for i in range(0, 100):
                    try:
                        animals.append(
                            list(cursor.execute(query_get_phen))[i][0].replace('(', '').replace(')', '').split(','))
                    except IndexError:
                        break
                win = tk.Toplevel()
                win.wm_title("Результаты")
                columns = ("Чип", "Вид", "Порода", "Окрас", "Пол", 'Возраст', "Куплено", "ID магазина",
                           "Название магазина", "Район магазина", "Телефон магазина")

                tree = ttk.Treeview(win, columns=columns, show="headings")
                tree.pack()

                # Определяем заголовки
                tree.heading("Чип", text="Чип", anchor=W)
                tree.heading("Вид", text="Вид", anchor=W)
                tree.heading("Порода", text="Порода", anchor=W)
                tree.heading("Окрас", text="Окрас", anchor=W)
                tree.heading("Пол", text="Пол", anchor=W)
                tree.heading("Возраст", text="Возраст", anchor=W)
                tree.heading("Куплено", text="Куплено", anchor=W)
                tree.heading("ID магазина", text="ID магазина", anchor=W)
                tree.heading("Название магазина", text="Название магазина", anchor=W)
                tree.heading("Район магазина", text="Район магазина", anchor=W)
                tree.heading("Телефон магазина", text="Телефон магазина", anchor=W)

                tree.column("#1", stretch=NO, width=50)
                tree.column("#2", stretch=NO, width=50)
                tree.column("#3", stretch=NO, width=100)
                tree.column("#4", stretch=NO, width=100)
                tree.column("#5", stretch=NO, width=100)
                tree.column("#6", stretch=NO, width=100)
                tree.column("#7", stretch=NO, width=100)
                tree.column("#8", stretch=NO, width=100)
                tree.column("#9", stretch=NO, width=100)
                tree.column("#10", stretch=NO, width=100)
                tree.column("#11", stretch=NO, width=100)

                for i in animals:
                    tree.insert("", END, values=i)
                btn_exit = tk.Button(win, text='Выход', comman=win.destroy)
                btn_exit.pack()
        except IndexError:
            msg.showinfo('Пусто', 'Ничего не найдено!')
            return

    def find_district_name(self, district, name):
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        query_get_shops = f'''
                                 SELECT find_shop_by_location_name('{district}', '{name}');
                        '''
        shops = []
        try:
            if district != '' and name != '' and list(cursor.execute(query_get_shops))[0][0]:
                for i in range(0, 100):
                    try:
                        shops.append(
                            list(cursor.execute(query_get_shops))[i][0].replace('(', '').replace(')', '').split(','))
                    except IndexError:
                        break
                win = tk.Toplevel()
                win.wm_title("Результаты")
                columns = ("ID", "Название", "Район", "Телефон")

                tree = ttk.Treeview(win, columns=columns, show="headings")
                tree.pack()

                # Определяем заголовки
                tree.heading("ID", text="ID", anchor=W)
                tree.heading("Название", text="Название", anchor=W)
                tree.heading("Район", text="Район", anchor=W)
                tree.heading("Телефон", text="Телефон", anchor=W)

                tree.column("#1", stretch=NO, width=200)
                tree.column("#2", stretch=NO, width=200)
                tree.column("#3", stretch=NO, width=200)
                tree.column("#4", stretch=NO, width=200)

                for i in shops:
                    tree.insert("", END, values=i)
                btn_exit = tk.Button(win, text='Выход', comman=win.destroy)
                btn_exit.pack()
            else:
                msg.showinfo('Пусто', 'Ничего не найдено!')
                return
        except IndexError:
            msg.showinfo('Пусто', 'Ничего не найдено!')
            return

    def find_phone(self, phone):
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        query_get_buyer = f'''
                                 SELECT find_buyer_by_phone({phone});
                        '''
        buyers = []
        try:
            if phone != '' and list(cursor.execute(query_get_buyer))[0][0]:
                for i in range(0, 100):
                    try:
                        buyers.append(
                            list(cursor.execute(query_get_buyer))[i][0].replace('(', '').replace(')', '').split(','))
                    except IndexError:
                        break
                win = tk.Toplevel()
                win.wm_title("Результаты")
                columns = ("Паспорт", "Имя", "Телефон", "Скидка")

                tree = ttk.Treeview(win, columns=columns, show="headings")
                tree.pack()

                # Определяем заголовки
                tree.heading("Паспорт", text="Паспорт", anchor=W)
                tree.heading("Имя", text="Имя", anchor=W)
                tree.heading("Телефон", text="Телефон", anchor=W)
                tree.heading("Скидка", text="Скидка", anchor=W)

                tree.column("#1", stretch=NO, width=200)
                tree.column("#2", stretch=NO, width=200)
                tree.column("#3", stretch=NO, width=200)
                tree.column("#4", stretch=NO, width=200)

                for i in buyers:
                    tree.insert("", END, values=i)
                btn_exit = tk.Button(win, text='Выход', comman=win.destroy)
                btn_exit.pack()
            else:
                msg.showinfo('Пусто', 'Ничего не найдено!')
                return
        except IndexError:
            msg.showinfo('Пусто', 'Ничего не найдено!')
            return

    def find_buyer_by_passport(self, passport):
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        query_get_buyer = f'''
                                    SELECT find_buyer_by_passport({passport});
                           '''
        buyers = []
        try:
            if passport != '' and list(cursor.execute(query_get_buyer))[0][0]:
                for i in range(0, 100):
                    try:
                        buyers.append(
                            list(cursor.execute(query_get_buyer))[i][0].replace('(', '').replace(')', '').split(','))
                    except IndexError:
                        break
                win = tk.Toplevel()
                win.wm_title("Результаты")
                columns = ("Паспорт", "Имя", "Телефон", "ID покупки", "Дата покупки", "Стоимость", "Чип", "ID магазина")

                tree = ttk.Treeview(win, columns=columns, show="headings")
                tree.pack()

                # Определяем заголовки
                tree.heading("Паспорт", text="Паспорт", anchor=W)
                tree.heading("Имя", text="Имя", anchor=W)
                tree.heading("Телефон", text="Телефон", anchor=W)
                tree.heading("ID покупки", text="ID покупки", anchor=W)
                tree.heading("Дата покупки", text="Дата покупки", anchor=W)
                tree.heading("Стоимость", text="Стоимость", anchor=W)
                tree.heading("Чип", text="Чип", anchor=W)
                tree.heading("ID магазина", text="ID магазина", anchor=W)

                tree.column("#1", stretch=NO, width=100)
                tree.column("#2", stretch=NO, width=100)
                tree.column("#3", stretch=NO, width=100)
                tree.column("#4", stretch=NO, width=100)
                tree.column("#5", stretch=NO, width=100)
                tree.column("#6", stretch=NO, width=100)
                tree.column("#7", stretch=NO, width=100)
                tree.column("#8", stretch=NO, width=100)

                for i in buyers:
                    tree.insert("", END, values=i)
                btn_exit = tk.Button(win, text='Выход', comman=win.destroy)
                btn_exit.pack()
            else:
                msg.showinfo('Пусто', 'Ничего не найдено!')
                return
        except IndexError:
            msg.showinfo('Пусто', 'Ничего не найдено!')
            return

    def find_purchase_by_stamp(self, stamp):
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        query_get_purchase = f'''
                                 SELECT find_purchase_by_stamp({stamp});
                        '''
        purchases = []
        try:
            if stamp != '' and list(cursor.execute(query_get_purchase))[0][0]:
                for i in range(0, 100):
                    try:
                        purchases.append(
                            list(cursor.execute(query_get_purchase))[i][0].replace('(', '').replace(')', '').split(','))
                    except IndexError:
                        break
                win = tk.Toplevel()
                win.wm_title("Результаты")
                columns = ("Дата покупки", "Стоимость", "ID магазина", "ID покупателя")

                tree = ttk.Treeview(win, columns=columns, show="headings")
                tree.pack()

                # Определяем заголовки
                tree.heading("Дата покупки", text="Дата покупки", anchor=W)
                tree.heading("Стоимость", text="Стоимость", anchor=W)
                tree.heading("ID магазина", text="ID магазина", anchor=W)
                tree.heading("ID покупателя", text="ID покупателя", anchor=W)

                tree.column("#1", stretch=NO, width=200)
                tree.column("#2", stretch=NO, width=200)
                tree.column("#3", stretch=NO, width=200)
                tree.column("#4", stretch=NO, width=200)

                for i in purchases:
                    tree.insert("", END, values=i)
                btn_exit = tk.Button(win, text='Выход', comman=win.destroy)
                btn_exit.pack()
            else:
                msg.showinfo('Пусто', 'Ничего не найдено!')
                return
        except IndexError:
            msg.showinfo('Пусто', 'Ничего не найдено!')
            return

    def find_not_bought(self):
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        query_get_purchase = f'''
                                 SELECT find_not_bought(false);
                        '''
        purchases = []
        try:
            if list(cursor.execute(query_get_purchase))[0][0]:
                for i in range(0, 100):
                    try:
                        purchases.append(
                            list(cursor.execute(query_get_purchase))[i][0].replace('(', '').replace(')', '').split(','))
                    except IndexError:
                        break
                win = tk.Toplevel()
                win.wm_title("Результаты")
                columns = ("Чип", "Вид", "Порода", "Возраст", "Окрас", "Пол", "ID магазина")

                tree = ttk.Treeview(win, columns=columns, show="headings")
                tree.pack()

                # Определяем заголовки
                tree.heading("Чип", text="Чип", anchor=W)
                tree.heading("Вид", text="Вид", anchor=W)
                tree.heading("Порода", text="Порода", anchor=W)
                tree.heading("Возраст", text="Возраст", anchor=W)
                tree.heading("Окрас", text="Окрас", anchor=W)
                tree.heading("Пол", text="Пол", anchor=W)
                tree.heading("ID магазина", text="ID магазина", anchor=W)

                tree.column("#1", stretch=NO, width=200)
                tree.column("#2", stretch=NO, width=200)
                tree.column("#3", stretch=NO, width=200)
                tree.column("#4", stretch=NO, width=200)
                tree.column("#5", stretch=NO, width=200)
                tree.column("#6", stretch=NO, width=200)
                tree.column("#7", stretch=NO, width=200)

                for i in purchases:
                    tree.insert("", END, values=i)
                btn_exit = tk.Button(win, text='Выход', comman=win.destroy)
                btn_exit.pack()
            else:
                msg.showinfo('Пусто', 'Ничего не найдено!')
                return
        except IndexError:
            msg.showinfo('Пусто', 'Ничего не найдено!')
            return

    def find_bought(self):
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        query_get_purchase = f'''
                                 SELECT find_not_bought(true);
                        '''
        purchases = []
        try:
            if list(cursor.execute(query_get_purchase))[0][0]:
                for i in range(0, 100):
                    try:
                        purchases.append(
                            list(cursor.execute(query_get_purchase))[i][0].replace('(', '').replace(')', '').split(','))
                    except IndexError:
                        break
                win = tk.Toplevel()
                win.wm_title("Результаты")
                columns = ("Чип", "Вид", "Порода", "Возраст", "Окрас", "Пол", "ID магазина")

                tree = ttk.Treeview(win, columns=columns, show="headings")
                tree.pack()

                # Определяем заголовки
                tree.heading("Чип", text="Чип", anchor=W)
                tree.heading("Вид", text="Вид", anchor=W)
                tree.heading("Порода", text="Порода", anchor=W)
                tree.heading("Возраст", text="Возраст", anchor=W)
                tree.heading("Окрас", text="Окрас", anchor=W)
                tree.heading("Пол", text="Пол", anchor=W)
                tree.heading("ID магазина", text="ID магазина", anchor=W)

                tree.column("#1", stretch=NO, width=200)
                tree.column("#2", stretch=NO, width=200)
                tree.column("#3", stretch=NO, width=200)
                tree.column("#4", stretch=NO, width=200)
                tree.column("#5", stretch=NO, width=200)
                tree.column("#6", stretch=NO, width=200)
                tree.column("#7", stretch=NO, width=200)

                for i in purchases:
                    tree.insert("", END, values=i)
                btn_exit = tk.Button(win, text='Выход', comman=win.destroy)
                btn_exit.pack()
            else:
                msg.showinfo('Пусто', 'Ничего не найдено!')
                return
        except IndexError:
            msg.showinfo('Пусто', 'Ничего не найдено!')
            return

    def super_poisk(self, table_name, number):
        engine = create_engine("postgresql+psycopg2://client:client@localhost:5432/animals")
        cursor = engine.connect()
        try:
            if table_name == 'Животные':
                result = []
                query_super = f'''
                                                 SELECT find_with_id(NULL::animals, 'stamp', {number});
                                        '''
                if number != '' and list(cursor.execute(query_super))[0][0]:
                    for i in range(0, 100):
                        try:
                            result.append(
                                list(cursor.execute(query_super))[i][0].replace('(', '').replace(')', '').split(','))
                        except IndexError:
                            break
                            # определяем столбцы
                    win = tk.Toplevel()
                    win.wm_title("Результаты")
                    columns = ("Чип", "Вид", "Порода", "Возраст", "Окрас", 'Пол', "Стоимость", "Куплено",
                               "Айди магазина")

                    tree = ttk.Treeview(win, columns=columns, show="headings")
                    tree.pack()

                    tree.heading("Чип", text="Чип", anchor=W)
                    tree.heading("Вид", text="Вид", anchor=W)
                    tree.heading("Порода", text="Порода", anchor=W)
                    tree.heading("Возраст", text="Возраст", anchor=W)
                    tree.heading("Окрас", text="Окрас", anchor=W)
                    tree.heading("Пол", text="Пол", anchor=W)
                    tree.heading("Стоимость", text="Стоимость", anchor=W)
                    tree.heading("Куплено", text="Куплено", anchor=W)
                    tree.heading("Айди магазина", text="ID магазина", anchor=W)

                    tree.column("#1", stretch=NO, width=50)
                    tree.column("#2", stretch=NO, width=50)
                    tree.column("#3", stretch=NO, width=100)
                    tree.column("#4", stretch=NO, width=100)
                    tree.column("#5", stretch=NO, width=100)
                    tree.column("#6", stretch=NO, width=100)
                    tree.column("#7", stretch=NO, width=100)
                    tree.column("#8", stretch=NO, width=100)
                    tree.column("#9", stretch=NO, width=100)

                    for i in result:
                        tree.insert("", END, values=i)
                    btn_exit = tk.Button(win, text='Выход', comman=win.destroy)
                    btn_exit.pack()
                else:
                    msg.showinfo('Пусто', 'Ничего не найдено!')
                    return
            elif table_name == 'Покупатели':
                result = []
                query_super = f'''
                                    SELECT find_with_id(NULL::buyer, 'pasport', {number});
                '''
                if number != '' and list(cursor.execute(query_super))[0][0]:
                    for i in range(0, 100):
                        try:
                            result.append(
                                list(cursor.execute(query_super))[i][0].replace('(', '').replace(')', '').split(','))
                        except IndexError:
                            break
                    # определяем столбцы
                    win = tk.Toplevel()
                    win.wm_title("Результаты")
                    columns = ("Паспорт", "Имя", "Телефон", "Скидка")

                    tree = ttk.Treeview(win, columns=columns, show="headings")
                    tree.pack()

                    tree.heading("Паспорт", text="Пасспорт", anchor=W)
                    tree.heading("Имя", text="Имя", anchor=W)
                    tree.heading("Телефон", text="Телефон", anchor=W)
                    tree.heading("Скидка", text="Скидка", anchor=W)

                    tree.column("#1", stretch=NO, width=200)
                    tree.column("#2", stretch=NO, width=200)
                    tree.column("#3", stretch=NO, width=200)
                    tree.column("#4", stretch=NO, width=100)

                    for i in result:
                        tree.insert("", END, values=i)
                    btn_exit = tk.Button(win, text='Выход', comman=win.destroy)
                    btn_exit.pack()
                else:
                    msg.showinfo('Пусто', 'Ничего не найдено!')
                    return
            elif table_name == 'Магазины':
                result = []
                query_super = f'''
                                            SELECT find_with_id(NULL::shop, 'id', {number});
                                    '''
                if number != '' and list(cursor.execute(query_super))[0][0]:
                    for i in range(0, 100):
                        try:
                            result.append(
                                list(cursor.execute(query_super))[i][0].replace('(', '').replace(')', '').split(','))
                        except IndexError:
                            break
                    win = tk.Toplevel()
                    win.wm_title("Результаты")
                    columns = ("ID", "Название", "Район", "Телефон")

                    tree = ttk.Treeview(win, columns=columns, show="headings")
                    tree.pack()

                    tree.heading("ID", text="ID", anchor=W)
                    tree.heading("Название", text="Название", anchor=W)
                    tree.heading("Район", text="Район", anchor=W)
                    tree.heading("Телефон", text="Телефон", anchor=W)

                    tree.column("#1", stretch=NO, width=100)
                    tree.column("#2", stretch=NO, width=200)
                    tree.column("#3", stretch=NO, width=200)
                    tree.column("#4", stretch=NO, width=200)

                    for i in result:
                        tree.insert("", END, values=i)
                    btn_exit = tk.Button(win, text='Выход', comman=win.destroy)
                    btn_exit.pack()

                else:
                    msg.showinfo('Пусто', 'Ничего не найдено!')
                    return
            elif table_name == 'Покупки':
                result = []
                query_super = f'''
                                            SELECT find_with_id(NULL::purchase, 'id', {number});
                                        '''
                if number != '' and list(cursor.execute(query_super))[0][0]:
                    for i in range(0, 100):
                        try:
                            result.append(
                                list(cursor.execute(query_super))[i][0].replace('(', '').replace(')', '').split(','))
                        except IndexError:
                            break
                    win = tk.Toplevel()
                    win.wm_title("Результаты")
                    columns = ("ID", "Дата", "Стоимость", "Чип", "ID покупателя")

                    tree = ttk.Treeview(win, columns=columns, show="headings")
                    tree.pack()

                    tree.heading("ID", text="ID", anchor=W)
                    tree.heading("Дата", text="Дата", anchor=W)
                    tree.heading("Стоимость", text="Стоимость", anchor=W)
                    tree.heading("Чип", text="Чип", anchor=W)
                    tree.heading("ID покупателя", text="ID покупателя", anchor=W)

                    tree.column("#1", stretch=NO, width=100)
                    tree.column("#2", stretch=NO, width=200)
                    tree.column("#3", stretch=NO, width=100)
                    tree.column("#4", stretch=NO, width=100)
                    tree.column("#5", stretch=NO, width=200)

                    for i in result:
                        tree.insert("", END, values=i)
                    btn_exit = tk.Button(win, text='Выход', comman=win.destroy)
                    btn_exit.pack()

                else:
                    msg.showinfo('Пусто', 'Ничего не найдено!')
                    return
        except IndexError:
            msg.showinfo('Пусто', 'Ничего не найдено!')
            return

    def __init__(self, parent):
        super().__init__(parent)
        self.config(bg="#6FE7DD")
        self.master.geometry('1050x350')

        self.label = tk.Label(self, text='Выберите данные для поиска', bg="#6FE7DD")
        self.label.grid(row=0, column=2, columnspan=2)

        self.label_phenotype = tk.Label(self, text='''Поиск животного
         по фенотипу''', bg="#6FE7DD", justify=tk.CENTER)
        self.label_phenotype.grid(row=1, column=0)
        self.label_phenotype1 = tk.Label(self, text='''Введите вид''', bg="#6FE7DD", justify=tk.CENTER)
        self.label_phenotype1.grid(row=2, column=0)
        self.entry_phenotype = tk.Entry(self)
        self.entry_phenotype.grid(row=3, column=0)
        self.label_phenotype2 = tk.Label(self, text='''Введите породу''', bg="#6FE7DD", justify=tk.CENTER)
        self.label_phenotype2.grid(row=4, column=0)
        self.entry_phenotype1 = tk.Entry(self)
        self.entry_phenotype1.grid(row=5, column=0)
        self.label_phenotype2 = tk.Label(self, text='''Введите окрас''', bg="#6FE7DD", justify=tk.CENTER)
        self.label_phenotype2.grid(row=6, column=0)
        self.entry_phenotype2 = tk.Entry(self)
        self.entry_phenotype2.grid(row=7, column=0)
        self.phenotype_btn = tk.Button(self, text='Найти', font=('SolomonSans', 10),
                                       command=lambda: self.find_phen(self.entry_phenotype.get(),
                                                                      self.entry_phenotype1.get(),
                                                                      self.entry_phenotype2.get()))
        self.phenotype_btn.grid(row=8, column=0)

        self.label_phone = tk.Label(self, text='''Поиск покупателя
         по телефону''', bg="#6FE7DD", justify=tk.CENTER)
        self.label_phone.grid(row=1, column=1)
        self.entry_phone = tk.Entry(self)
        self.entry_phone.grid(row=2, column=1)
        self.phone_btn = tk.Button(self, text='Найти', font=('SolomonSans', 10),
                                   command=lambda: self.find_phone(self.entry_phone.get()))
        self.phone_btn.grid(row=3, column=1)

        self.label_district_name = tk.Label(self, text='''Поиск магазина 
        по району и названию''', bg="#6FE7DD", justify=tk.CENTER)
        self.label_district_name.grid(row=1, column=2)
        self.label_district = tk.Label(self, text='''Введите район''', bg="#6FE7DD", justify=tk.CENTER)
        self.label_district.grid(row=2, column=2)
        self.entry_district = tk.Entry(self)
        self.entry_district.grid(row=3, column=2)
        self.label_name = tk.Label(self, text='''Введите название''', bg="#6FE7DD", justify=tk.CENTER)
        self.label_name.grid(row=4, column=2)
        self.entry_name = tk.Entry(self)
        self.entry_name.grid(row=5, column=2)
        self.district_name_btn = tk.Button(self, text='Найти', font=('SolomonSans', 10),
                                           command=lambda: self.find_district_name(self.entry_district.get(),
                                                                                   self.entry_name.get()))
        self.district_name_btn.grid(row=6, column=2)

        self.label_passport = tk.Label(self, text='''Поиск покупателя 
        по паспорту''', bg="#6FE7DD", justify=tk.CENTER)
        self.label_passport.grid(row=1, column=3)
        self.label_passport1 = tk.Label(self, text='''Введите цифры паспорта''', bg="#6FE7DD", justify=tk.CENTER)
        self.label_passport1.grid(row=2, column=3)
        self.entry_passport = tk.Entry(self)
        self.entry_passport.grid(row=3, column=3)
        self.passport_btn = tk.Button(self, text='Найти', font=('SolomonSans', 10),
                                      command=lambda: self.find_buyer_by_passport(self.entry_passport.get()))
        self.passport_btn.grid(row=4, column=3)

        self.label_stamp = tk.Label(self, text='''Поиск покупки 
        по чипу''', bg="#6FE7DD", justify=tk.CENTER)
        self.label_stamp.grid(row=1, column=4)
        self.label_stamp1 = tk.Label(self, text='''Введите номер чипа''', bg="#6FE7DD", justify=tk.CENTER)
        self.label_stamp1.grid(row=2, column=4)
        self.entry_stamp = tk.Entry(self)
        self.entry_stamp.grid(row=3, column=4)
        self.stamp_btn = tk.Button(self, text='Найти', font=('SolomonSans', 10),
                                   command=lambda: self.find_purchase_by_stamp(self.entry_stamp.get()))
        self.stamp_btn.grid(row=4, column=4)

        self.label_taken = tk.Label(self, text='''Найти ещё не 
        купленных животных''', bg="#6FE7DD", justify=tk.CENTER)
        self.label_taken.grid(row=1, column=5)
        self.taken_btn = tk.Button(self, text='Найти', font=('SolomonSans', 10),
                                   command=self.find_not_bought)
        self.taken_btn.grid(row=2, column=5)

        self.label_taken = tk.Label(self, text='''Найти купленных животных''', bg="#6FE7DD", justify=tk.CENTER)
        self.label_taken.grid(row=3, column=5)
        self.taken_btn = tk.Button(self, text='Найти', font=('SolomonSans', 10),
                                   command=self.find_bought)
        self.taken_btn.grid(row=4, column=5)

        self.label_super = tk.Label(self, text='''Особо мощный поиск''', bg="#6FE7DD", justify=tk.CENTER)
        self.label_super.grid(row=1, column=6)
        self.ids = ['Животные', 'Покупатели', 'Магазины', 'Покупки']
        self.label_super1 = tk.Label(self, text='''Введите id или номер чипа''', bg="#6FE7DD", justify=tk.CENTER)
        self.label_super1.grid(row=3, column=6)
        self.entry_super = tk.Entry(self)
        self.entry_super.grid(row=4, column=6)
        self.combo_super = ttk.Combobox(self, value=self.ids)
        self.combo_super.current(0)
        self.combo_super.grid(row=2, column=6)
        self.super_btn = tk.Button(self, text='Найти', font=('SolomonSans', 10),
                                   command=lambda: self.super_poisk(self.combo_super.get(), self.entry_super.get()))
        self.super_btn.grid(row=5, column=6)

        self.back = tk.Button(self, text='Вернуться', command=self.back, font=('SolomonSans', 10))
        self.back.grid(row=9, column=1, columnspan=2)

        self.grid_columnconfigure(0, minsize=100)
        self.grid_columnconfigure(1, minsize=100)
        self.grid_columnconfigure(2, minsize=100)
        self.grid_columnconfigure(3, minsize=100)
        self.grid_columnconfigure(4, minsize=100)
        self.grid_columnconfigure(5, minsize=100)
        self.grid_columnconfigure(6, minsize=100)

        self.grid_rowconfigure(0, minsize=35)
        self.grid_rowconfigure(1, minsize=35)
        self.grid_rowconfigure(2, minsize=35)
        self.grid_rowconfigure(3, minsize=35)
        self.grid_rowconfigure(4, minsize=35)
        self.grid_rowconfigure(5, minsize=35)
        self.grid_rowconfigure(6, minsize=35)
        self.grid_rowconfigure(7, minsize=35)
        self.grid_rowconfigure(8, minsize=35)
        self.grid_rowconfigure(9, minsize=35)


root = tk.Tk()
root.geometry("700x220+100+100")

login_frame = LoginFrame(root)
login_frame.pack()

root.mainloop()
