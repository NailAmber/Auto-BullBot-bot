import json

# Чтение данных из файлов
async def proceed_data():
    with open('./data/raw_numbers.txt', 'r') as phones_file, \
            open('./data/raw_api_id.txt', 'r') as ids_file, \
            open('./data/raw_api_hash.txt', 'r') as hashes_file:

        phones = phones_file.read().splitlines()
        ids = ids_file.read().splitlines()
        hashes = hashes_file.read().splitlines()

    # Создание словаря
    data = {phone: [int(id_), hash_]
            for phone, id_, hash_ in zip(phones, ids, hashes)}

    # Запись словаря в JSON файл
    with open('output.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    print("Данные успешно сохранены в out.json")
