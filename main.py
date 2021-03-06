"""Получение json и запись значений этого jsonb в базу."""
import json
import os
import sys
import psycopg2
import jsonschema


def default_json(file: str) -> dict:
    """Эта функция читает схему json."""
    base_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(base_dir, file)
    with open(file_path) as f:
        data = json.load(f)
        return data


def input_json(file: str) -> dict:
    """Эта функция читает json файл, который подается."""
    base_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(base_dir, file)
    if os.path.splitext(file_path)[1] == '.json':
        with open(file_path) as e:
            data = json.load(e)
            return data
    else:
        print('Это не json файл')
        sys.exit(0)


def validation_json(data: dict, data2: dict) -> str:
    """Эта функция валидирует поданный json со схемой."""
    try:
        jsonschema.validate(data, data2)
        return "Json валидный"
    except jsonschema.exceptions.ValidationError:
        return "Json невалидный"


def add_values(data: dict) -> tuple:
    """Функция возвращает values для таблиц goods и shops_goods."""
    goods = [data['id'], data['name'], data['package_params']['width'], data['package_params']['height']]
    shop_goods = [data['id']]
    for i in data['location_and_quantity']:
        shop_goods.append(i['location'])
        shop_goods.append(i['amount'])
    return tuple(goods), tuple(shop_goods)


def function_db() -> bool:
    """Подключение к БД и insert или update в таблицы."""
    try:
        conn = psycopg2.connect(dbname='postgres', user='postgres', host='localhost')
        c = conn.cursor()
        c.execute(
            """create table if not exists goods
                            (id int unique not null primary key, name varchar not null,
                            package_height float not null, package_width float not null);""")

        c.execute("""create table if not exists shops_goods
                            (id serial not null, id_good int unique not null references goods (id) unique,
                            location varchar not null, amount int not null);""")

        c.execute(f"""INSERT  INTO goods (id, name, package_width, package_height)
                            values {goods_items} ON CONFLICT(id) do update
                                set
                                name = excluded.name,
                                package_width = excluded.package_width,
                                package_height = excluded.package_height;""")

        c.execute(f"""INSERT  INTO shops_goods (id_good, location, amount) values {shops_items}
                            ON CONFLICT(id_good) do update
                            set
                            location = excluded.location,
                            amount = excluded.amount""")

        conn.commit()
        conn.close()
        print("Записи успешно добавились или обновились")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return False

    finally:
        return True


input_data = input_json('file.json')
schema = default_json('goods.schema.json')
goods_items, shops_items = add_values(input_data)

print(function_db())
