# подключаем библиотеку для работы с базой данных
from datetime import date
import sqlite3
from tkinter import END, Button, Entry, Label, Listbox, Scrollbar, StringVar, Tk, messagebox
from tkcalendar import DateEntry
from dateutil.relativedelta import relativedelta

# создаём класс для работы с базой данных
class DB:
    # конструктор класса
    def __init__(self):
        # соединяемся с файлом базы данных
        self.conn = sqlite3.connect("mybooks.db")
        # создаём курсор для виртуального управления базой данных
        self.cur = self.conn.cursor()
        # если нужной нам таблицы в базе нет — создаём её
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS buy (id INTEGER PRIMARY KEY, product TEXT, price TEXT, comment TEXT, date DATE, category TEXT, limits INTEGER)")
        # сохраняем сделанные изменения в базе
        self.conn.commit()

        # деструктор класса
    def __del__(self):
        # отключаемся от базы при завершении работы
        self.conn.close()

        # просмотр всех записей
    def view(self):
        # выбираем все записи о покупках
        self.cur.execute("SELECT * FROM buy")
        # собираем все найденные записи в колонку со строками
        rows = self.cur.fetchall()
        # возвращаем сроки с записями расходов
        return rows

    # добавляем новую запись
    def insert(self, product, price, comment, date, category, limit):
        if not product or not price:
            messagebox.showerror('Ошибка', 'Поля товар и цена должны быть заполнены.')
            raise ValueError('Ошибка','Поля товар и цена не заполнены.')
        # формируем запрос с добавлением новой записи в БД
        self.cur.execute("INSERT INTO buy VALUES (NULL,?,?,?,?,?,?)", (product, price, comment, date, category, limit))
        # сохраняем изменения
        self.conn.commit()
        

    # обновляем информацию о покупке
    def update(self, id, product, price):
        # формируем запрос на обновление записи в БД
        self.cur.execute("UPDATE buy SET product=?, price=? WHERE id=?", (product, price, id,))
        # сохраняем изменения 
        self.conn.commit()

    # удаляем запись
    def delete(self, id):
        # формируем запрос на удаление выделенной записи по внутреннему порядковому номеру
        self.cur.execute("DELETE FROM buy WHERE id=?", (id,))
        # сохраняем изменения
        self.conn.commit()

    # ищем запись по названию покупки
    def search(self, product=""):
        # формируем запрос на поиск по точному совпадению
        self.cur.execute("SELECT * FROM buy WHERE product=?", (product,))
        # формируем полученные строки и возвращаем их как ответ
        rows = self.cur.fetchall()
        return rows
    
    # считаем траты в месяце
    def get_monthly_expenses(self):
        today = date.today()
        start_date = date(today.year, today.month, 1)
        end_date = start_date + relativedelta(months=1, days=-1)
        # формируем запрос на сумму по категориям от начала до конца месяца
        self.cur.execute(
            "SELECT category, SUM(CAST(price AS FLOAT)) AS total_spent "
            "FROM buy "
            "WHERE date BETWEEN ? AND ? "
            "GROUP BY category "
            "ORDER BY total_spent DESC",
            (start_date, end_date))
        rows = self.cur.fetchall()
        return rows
    
    # метод выборки лимита по категории из таблицы
    def get_limit(self):
        today = date.today().strftime('%Y-%m-%d')
        db.cur.execute("SELECT SUM(price) FROM buy WHERE date=? GROUP BY date", (today,))
        total_spent_today = db.cur.fetchone()
        if total_spent_today:
            total_spent_today = float(total_spent_today[0])
            db.cur.execute("SELECT limits FROM buy")
            daily_limit = db.cur.fetchone()
            if daily_limit and total_spent_today > float(daily_limit[0]):
                messagebox.showwarning("Превышение лимита", f"Дневной лимит в {daily_limit[0]} превышен! Сегодня потрачено {total_spent_today}.")
                return
# создаём экземпляр базы данных на основе класса
db = DB()

window = Tk()
# создаём надписи для полей ввода и размещаем их по сетке
l1 = Label(window, text="Название")
l1.grid(row=0, column=0)

l2 = Label(window, text="Стоимость")
l2.grid(row=2, column=2)

l3 = Label(window, text="Комментарий")
l3.grid(row=1, column=0)

l4 = Label(window, text="Дата")
l4.grid(row=0, column=2)

l5 = Label(window, text="Категории")
l5.grid(row=2, column=0)

l6 = Label(window, text="Лимит")
l6.grid(row=1, column=2)

# создаём поле ввода названия покупки, говорим, что это будут строковые переменные и размещаем их тоже по сетке
product_text = StringVar()
e1 = Entry(window, textvariable=product_text)
e1.grid(row=0, column=1)

# то же самое для комментариев и цен
price_text = StringVar()
e2 = Entry(window, textvariable=price_text)
e2.grid(row=2, column=3)

comment_text = StringVar()
e3 = Entry(window, textvariable=comment_text)
e3.grid(row=1, column=1)

# создаем поле для ввода даты
date_entry = DateEntry()
e4 = DateEntry(window, textvariable=date_entry)
e4.grid(row=0, column=3)

# создаем поле для ввода категории
category_text = StringVar()
e5 = Entry(window, textvariable=category_text)
e5.grid(row=2, column=1)

# создаем поле для ввода лимита
limit_text = StringVar()
e6 = Entry(window, textvariable=limit_text)
e6.grid(row=1, column=3)

# создаём список, где появятся наши покупки, и сразу определяем его размеры в окне
list1 = Listbox(window, height=25, width=65)
list1.grid(row=3, column=0, rowspan=6, columnspan=2)

# на всякий случай добавим сбоку скролл, чтобы можно было быстро прокручивать длинные списки
sb1 = Scrollbar(window)
sb1.grid(row=2, column=2, rowspan=6)

# привязываем скролл к списку
list1.configure(yscrollcommand=sb1.set)
sb1.configure(command=list1.yview)

# обработчик нажатия на кнопку «Посмотреть всё»
def view_command(*args):
    # очищаем список в приложении
    list1.delete(0, END)
    # проходим все записи в БД
    for row in db.view():
        # и сразу добавляем их на экран
        list1.insert(END, row)

# обработчик нажатия на кнопку «Поиск»
def search_command(*args):
    # очищаем список в приложении
    list1.delete(0, END)
    # находим все записи по названию покупки
    for row in db.search(product_text.get()):
        # и добавляем их в список в приложение
        list1.insert(END, row)

# обработчик нажатия на кнопку «Добавить»
def add_command(*args):
    if not product_text.get or not price_text.get:
        return
    # добавляем запись в БД
    db.insert(product_text.get(), price_text.get(), comment_text.get(), date_entry.get_date(), category_text.get(), limit_text.get())
    # уведомление о превышении лимита
    limit = db.get_limit()
    if limit and float(price_text.get()) > limit:
        messagebox.askyesno("Превышен лимит", f"Расходы на '{category_text.get()}' превышают лимит, указанный в {limit:.2f}. Вы хотите продолжить?")
        return
    # обновляем общий список в приложении
    view_command()

# обработчик нажатия на кнопку «Обновить»
def update_command(*args):
    # обновляем данные в БД о выделенной записи
    db.update(selected_tuple[0], product_text.get(), price_text.get(), date_entry.get_date(), category_text.get(), limit_text.get())
    # обновляем общий список расходов в приложении
    view_command()

# обработчик нажатия на кнопку «Удалить»
def delete_command(*args):
    # удаляем запись из базы данных по индексу выделенного элемента
    db.delete(selected_tuple[0])
    # обновляем общий список расходов в приложении
    view_command()

# отображение расходов за месяц 
def show_monthly_expenses(*args):
    expenses = db.get_monthly_expenses()
    total_spent = sum(expense[1] for expense in expenses)

    message = "Расходы за месяц:\n\n"
    for expense in expenses:
        message += f"{expense[0]}: {expense[1]:.2f}\n"
    message += f"\nОбщая сумма: {total_spent:.2f}"

    messagebox.showinfo("Расходы за месяц", message)

# обрабатываем закрытие окна
def on_closing(*args):
    # показываем диалоговое окно с кнопкой
    if messagebox.askokcancel("", "Закрыть программу?"):
        # удаляем окно и освобождаем память
        window.destroy()

# сообщаем системе о том, что делать, когда окно закрывается
window.protocol("WM_DELETE_WINDOW", on_closing)

# заполняем поля ввода значениями выделенной позиции в общем списке
def get_selected_row(event):
    # будем обращаться к глобальной переменной
    global selected_tuple
    # получаем позицию выделенной записи в списке
    index = list1.curselection()[0]  # this is the id of the selected tuple
    # получаем значение выделенной записи
    selected_tuple = list1.get(index)
    # удаляем то, что было раньше в поле ввода
    e1.delete(0, END)
    # и добавляем туда текущее значение названия покупки
    e1.insert(END, selected_tuple[1])
    # делаем то же самое с другими полями
    e2.delete(0, END)
    e2.insert(END, selected_tuple[2])
    e3.delete(0, END)
    e3.insert(END, selected_tuple[3])
    e4.delete(0, END)
    e4.insert(END, selected_tuple[4])
    e5.delete(0, END)
    e5.insert(END, selected_tuple[5])
    e6.delete(0, END)
    e6.insert(END, selected_tuple[6])

# привязываем выбор любого элемента списка к запуску функции выбора
list1.bind('<<ListboxSelect>>', get_selected_row)

# создаём кнопки действий и привязываем их к своим функциям
# кнопки размещаем тоже по сетке
b1 = Button(window, text="Посмотреть все", width=12, command=view_command)
b1.grid(row=3, column=3)  # size of the button

b2 = Button(window, text="Поиск", width=12, command=search_command)
b2.grid(row=4, column=3)

b3 = Button(window, text="Добавить", width=12, command=add_command)
b3.grid(row=5, column=3)

b4 = Button(window, text="Обновить", width=12, command=update_command)
b4.grid(row=6, column=3)

b5 = Button(window, text="Удалить", width=12, command=delete_command)
b5.grid(row=7, column=3)

b6 = Button(window, text="Закрыть", width=12, command=on_closing)
b6.grid(row=8, column=3)

b7 = Button(window, text="Расходы", width=12, command=show_monthly_expenses)
b7.grid(row=8, column=2)

# создаём поддержку горячих клавиш
window.bind_all("<Control-v>", view_command)
window.bind_all("<Control-a>", add_command)
window.bind_all("<Control-u>", update_command)
window.bind_all("<Control-d>", delete_command)
window.bind_all("<Control-c>", on_closing)

window.mainloop()








