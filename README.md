# Приложение для ведения бюджета на python c использованием GUI библиотеки Tkinter и базы данных SQLite

## Задание

1. Добавить поддержку горячих клавиш;
2. Сделать более удобный интерфейс;
3. Добавить календарь, чтобы привязывать расходы к дате;
4. Добавить проверку на пустые значения названий и сумм;
5. Добавить поддержку категорий расходов;
6. Посчитать, сколько уже потрачено в этом месяце и на что ушло больше всего;
7. Сделать лимиты трат и настроить уведомления о них.

Преобразование в .EXE:

pyinstaller --noconfirm --onedir --windowed --icon "buss-icon.ico" --name "Buss db" --hidden-import "babel" --collect-submodules "babel"  "class_db.py"
