# "Сласти от всех напастей" REST API Сервис #
## Перенос папки с репозиторием к себе на компьютер ##
1. Нажмите кнопку fork в репозитории https://github.com/mishajirx/YandexBackend
2. Перейдите в командную строку
3. Перейдите подходящую вам папку
4. вбейте команду git clone  https://github.com/<YourName>/YandexBackend

## Установка нужного обеспечения ##
#### Для скачивания необходимых библиотек нужно: ####
0. Все действие ниже указанные выполнять в терминале
1. Перейти в командной строке в каталог с проектом
2. выполнить pip install -r requirements.txt
#### Пример ####
$ pip install -r requirements.txt
## Запуск приложения ##
Для запуска приложения нужно просто выполнить в консоли
python3 main.py (или sudo python main.py)
#### Пример #### 
$ python3 main.py

## Запуск Тестов ##
Для запуска тестов нужно:
1. Повторить пункты из раздела "Запуск приложения"
2. Нажать ctrl+z. Выполнить bg
3. выполнить pytest-3 test.py -x -s
4. ввести 'y'
#### Пример: ####
$ sudo python3 main.py
$ ^Z
& bg
$ pytest-3 test.py -x -s

## Автозапуск ##
Чтобы сделать так, чтобы сервер запускался при старте 
системы нужно зайти в консоль и ввести следующие команды:
1. crontab -e
2. В открывшемся файле в последней строке набрать:
   @reboot python3 /path_to_the_project/main.py

## Дополнительно
#### Виды пользователей:
1. Курьер
2. Админ
3. Бот
#### Возможности бота:
1. Сделать заказ(/orders)
2. Кинуть заявку на становление курьером
#### Возможности админа:
1. Подтверждать заявки на становление курьером (/couriers)
#### Возможности курьера:
1. Принять заказы (/orders/assign)
2. Изменить свои параметры (/courier/<courier_id>)
3. Выполнить заказ (orders/complete)
4. Получить информацию о себе (/couriers/<couriers_id>)