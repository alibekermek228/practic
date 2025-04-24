import psycopg2
import csv
from psycopg2 import connect



# Подключение к базе данных
conn = psycopg2.connect(
    host="localhost",
    database="phonebook",
    user="postgres",
    password="postgres",
    port="5432"
)
cur = conn.cursor()

# Создание таблицы
def create_table():
    cur.execute('''
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL
        )
    ''')
    conn.commit()



# Вставка записи вручную
def insert_from_console():
    name = input("Введите имя: ")
    phone = input("Введите номер: ")
    cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()
    print("Запись добавлена!")

# Загрузка из CSV
def insert_from_csv():
    file_path = input("Укажите путь к CSV-файлу: ")
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            cur.execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (row[0], row[1]))
    conn.commit()
    print("CSV-записи успешно загружены!")

# Обновление номера по имени
def update_entry():
    name = input("Введите имя: ")
    new_phone = input("Введите новый номер: ")
    cur.execute("UPDATE phonebook SET phone = %s WHERE name = %s", (new_phone, name))
    conn.commit()
    print("Запись обновлена!")

# Поиск по шаблону
def query_phonebook():
    query_type = input("Фильтр по name/phone: ")
    value = input("Введите значение: ")
    query = f"SELECT * FROM phonebook WHERE {query_type} ILIKE %s"
    cur.execute(query, ('%' + value + '%',))
    rows = cur.fetchall()
    for row in rows:
        print(row)

# Удаление по имени или номеру
def delete_data():
    by = input("Удалить по name/phone: ")
    value = input("Введите значение: ")
    cur.execute(f"DELETE FROM phonebook WHERE {by} = %s", (value,))
    conn.commit()
    print("Запись удалена!")

# ---------- Использование процедур/функций из PostgreSQL ----------

def search_by_pattern(pattern):
    cur.execute("SELECT * FROM search_by_pattern(%s)", (pattern,))
    results = cur.fetchall()
    print("Результаты поиска:")
    for row in results:
        print(row)

def insert_or_update_user(name, phone):
    cur.execute("CALL insert_or_update_user(%s, %s)", (name, phone))
    conn.commit()
    print(f"Пользователь {name} вставлен/обновлён.")

def bulk_insert_users():
    n = int(input("Сколько пользователей вставить? "))
    users = []
    for _ in range(n):
        name = input("Имя: ")
        phone = input("Телефон: ")
        users.append((name, phone))
    cur.execute("CALL bulk_insert_users(%s)", (users,))
    conn.commit()
    print("Множественная вставка завершена.")

def get_page(limit, offset):
    cur.execute("SELECT * FROM get_phonebook_page(%s, %s)", (limit, offset))
    rows = cur.fetchall()
    for row in rows:
        print(row)

def delete_user(by, value):
    cur.execute("CALL delete_by_name_or_phone(%s, %s)", (by, value))
    conn.commit()
    print("Удалено.")

# Главное меню
def main():
    create_table()
    while True:
        print("\nМеню:")
        print("1 - Добавить запись вручную")
        print("2 - Загрузить из CSV")
        print("3 - Обновить запись")
        print("4 - Поиск по фильтру")
        print("5 - Удалить запись вручную")
        print("6 - Поиск по шаблону (функция)")
        print("7 - Вставить/обновить 1 пользователя (процедура)")
        print("8 - Массовая вставка (процедура)")
        print("9 - Пагинация (функция)")
        print("10 - Удалить по name/phone (процедура)")
        print("0 - Выход")

        choice = input("Выбор: ")
        if choice == '1':
            insert_from_console()
        elif choice == '2':
            insert_from_csv()
        elif choice == '3':
            update_entry()
        elif choice == '4':
            query_phonebook()
        elif choice == '5':
            delete_data()
        elif choice == '6':
            pattern = input("Введите шаблон: ")
            search_by_pattern(pattern)
        elif choice == '7':
            name = input("Имя: ")
            phone = input("Телефон: ")
            insert_or_update_user(name, phone)
        elif choice == '8':
            bulk_insert_users()
        elif choice == '9':
            limit = int(input("Лимит: "))
            offset = int(input("Смещение: "))
            get_page(limit, offset)
        elif choice == '10':
            by = input("Удалить по name/phone: ")
            value = input("Введите значение: ")
            delete_user(by, value)
        elif choice == '0':
            break
        else:
            print("Неверный выбор!")

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
