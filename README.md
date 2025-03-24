# FastAPI-Homework

Команды:

POST http://localhost:8000/register/ - Регистрация пользователя

POST http://localhost:8000/token/ - Авторизация (получение токена)

POST http://localhost:8000/tasks/ - Создание задачи
Body:
  {
    "title": "Новая задача",
    "description": "Описание задачи",
    "status": "в ожидании",
    "priority": 3
  }

GET http://localhost:8000/tasks/?sort_by=priority&sort_order=desc&search=срочно&limit=5 - Получение задач с сортировкой/поиском

GET http://localhost:8000/tasks/top/?limit=3 - Получение топ-N задач по приоритету

GET http://localhost:8000/tasks/1 - Получение топ-N задач по приоритету

GET http://localhost:8000/tasks/1 - Получение конкретной задачи

PUT http://localhost:8000/tasks/1 - Обновление задачи

DELETE http://localhost:8000/tasks/1 - Удаление задачи

Примеры использования:

![IMAGE 2025-03-24 21:33:06](https://github.com/user-attachments/assets/f640cf5c-64e0-4baa-9283-f96796005c20)

![IMAGE 2025-03-24 21:33:15](https://github.com/user-attachments/assets/0093bc60-c37b-4ee1-9ec9-a9035364514d)

![IMAGE 2025-03-24 21:33:21](https://github.com/user-attachments/assets/b54d95ab-4f86-4322-a2c9-ca03a16a079e)

![IMAGE 2025-03-24 21:33:30](https://github.com/user-attachments/assets/7f0335dc-4820-49e3-acf5-9aa3ef00c1ad)

![IMAGE 2025-03-24 21:33:36](https://github.com/user-attachments/assets/8b9e12bc-4472-4e6f-9c13-da9bfe37a6e7)

![IMAGE 2025-03-24 21:33:48](https://github.com/user-attachments/assets/9f9d55ae-601b-4305-a68f-5529e5bd040b)

![IMAGE 2025-03-24 21:33:54](https://github.com/user-attachments/assets/38414280-c015-4f5e-a82e-607cb3b44b8a)

![IMAGE 2025-03-24 21:33:59](https://github.com/user-attachments/assets/e7dc9612-c1a5-4614-bad4-7fe2db6bf8ad)

![IMAGE 2025-03-24 21:34:09](https://github.com/user-attachments/assets/47fa71cc-07df-48c7-ac03-5a164ceb28cd)

![IMAGE 2025-03-24 21:34:15](https://github.com/user-attachments/assets/5f8fd126-b169-4448-8469-be26d8b24ace)

![IMAGE 2025-03-24 21:34:22](https://github.com/user-attachments/assets/5c097b09-77c7-447a-aeeb-913b275734c2)

![IMAGE 2025-03-24 21:34:28](https://github.com/user-attachments/assets/383ef21e-4f23-424b-97ef-c67b07480b39)

![IMAGE 2025-03-24 21:34:34](https://github.com/user-attachments/assets/aea6a89e-3375-495d-bf47-c4f1119a5b5c)

![IMAGE 2025-03-24 21:34:41](https://github.com/user-attachments/assets/e7561808-3242-4b6d-8ba1-59e062d73a7f)
