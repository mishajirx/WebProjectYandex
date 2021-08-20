# "Sweetland" REST API Service #

## IDEA ##

"SweetLand" is a delivery service, where you can make orders, deliver orders,
earn money, control couriers and etc.. Your possibilities depends on your status (User, Courier, Admin).
You can all this actions with UI or you can use API.


## RULES ##

#### User Types:
1. Courier
2. Admin
3. User
#### User's opportunities:
1. Order something(/orders)
2. Send VC to become courier
#### Admin's opportunities:
1. Hire couriers (/couriers)
#### Courier's opportunities:
1. Take orders (/orders/assign)
2. Change info about itself (/courier/<courier_id>)
3. Complete orders (orders/complete)
4. Get info about itself (/couriers/<couriers_id>)



## How to move folder with repository to your own computer ##
1. Press button "fork" in repository https://github.com/mishajirx/YandexBackend
2. Go to the CMD
3. Go to the folder you need
4. Use command "git clone  https://github.com/<YourName>/YandexBackend"

## How to install neccessary libraries ##
#### To install libraries you need: ####
0. All actions needed to be done in the CMD
1. Go to the project catalog
2. Use  "pip install -r requirements.txt"
#### Example ####
$ pip install -r requirements.txt
## How to run web app ##
To run the app you just need to use this command
"python3 main.py (или sudo python main.py)"
#### Example #### 
$ python3 main.py

## How to test the service ##
To test service you need to:
1. Run web app
2. Press ctrl+z. Use the "bg" command. It will move proccess to the background
3. Use command  "pytest-3 test.py -x -s"
4. Type 'y'
#### Example: ####
$ python3 main.py
$ ^Z
$ bg
$ pytest-3 test.py -x -s

## How to make web app autostarting ##
Чтобы сделать так, чтобы сервер запускался при старте 
системы нужно зайти в консоль и ввести следующие команды:
If you want to service automatically run while your system starting you need to do these actions
1. Use command "crontab -e"
2. В открывшемся файле в последней строке набрать:
2. Type this in the file you just opened
   @reboot python3 /path_to_the_project/main.py
