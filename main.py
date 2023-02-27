import time
from datetime import date as Date
from datetime import datetime
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from threading import Thread
import json
LINK = "https://ais.usvisa-info.com/en-il/niv/users/sign_in"
jsonFileName = 'customers.json'
DataFromJasonFile = None
days_in_month = {'January': 31,
              'Febuary': 28,
              'March': 31,
              'April': 30,
              'May': 31,
              'June': 30,
              'July': 31,
              'August': 31,
              'September': 30,
              'October': 31,
              'November': 30,
              'December': 31}

def textSlice(text):
    day = None
    month = None
    year = None
    temp_text = str(text)
    temp_text = temp_text.split(":")[1]  ## get the string after : and cut the things before ## (num of day) (month) ,(year), (num)
    temp_text = temp_text.split(", ")##[(num of day) (month) , (year)]
    year = temp_text[1]
    day_month = temp_text[0].split(" ")
    day = day_month[1]
    month = monthToNum(day_month[2])
    date = [int(year), int(month), int(day)]
    return date

def monthToNum(month : str):
    months = {'January': 0,
              'Febuary': 1,
              'March': 2,
              'April': 3,
              'May': 4,
              'June': 5,
              'July': 6,
              'August': 7,
              'September': 8,
              'October': 9,
              'November': 10,
              'December': 11}
    return months[month]+1

def numToMonth(num : int):
    months = {'January': 0,
              'Febuary': 1,
              'March': 2,
              'April': 3,
              'May': 4,
              'June': 5,
              'July': 6,
              'August': 7,
              'September': 8,
              'October': 9,
              'November': 10,
              'December': 11}
    for k in months.keys():
        if months[k]+1 == num:
            return k
    return None

def selectConsular( consularName : str, driver : webdriver):
    ##page to loking for a early date
    Consular_Section_Location_id = "appointments_consulate_appointment_facility_id"
    try:
        Consular_Section_Location = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, Consular_Section_Location_id))
        )
    except:
        return -1

    Consular_Section_Location.click()
    select = Select(driver.find_element(By.ID, Consular_Section_Location_id))

    #options = {"tel aviv" : '97', "jerusalem": '96'}
    if consularName == "Tel Aviv" or consularName == "tel aviv":
        select.select_by_visible_text("Tel Aviv")
    if consularName == "Jerusalem" or consularName == "jerusalem":
        select.select_by_visible_text("Jerusalem")


def selectNewDate(dateOfTheAppointment : dict , driver : webdriver):
    '''open the calnder'''
    Xpath_calender = "//*[@id='appointments_consulate_appointment_date']"
    lable_calendar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, Xpath_calender))
    )
    time.sleep(6)
    lable_calendar.click()
    '''calender open'''
    date_can_chosen = None
    counter = calcRangeMonth(dateOfTheAppointment)
    while date_can_chosen == None and counter > 0:
        date_can_chosen = getDateFormCalander(driver)
        counter-=1
    if date_can_chosen == None:
        return None
    if dateOfTheAppointment['year'] >= date_can_chosen['year']:
        if dateOfTheAppointment['month'] >= date_can_chosen['month']:
            if dateOfTheAppointment['day'] > date_can_chosen['day']:
                return date_can_chosen
                selectHour(driver)
    return None
def calcRangeMonth(dateOfTheAppointment : dict) -> int:
    if Date.today().year < dateOfTheAppointment['year']:
        return 12 - int(Date.today().month) + dateOfTheAppointment['month']
    elif Date.today().year == dateOfTheAppointment['year']:
        return dateOfTheAppointment['month'] - Date.month
    return -1

def getDateFormCalander(driver : webdriver):
    calander_id = "ui-datepicker-div"
    calender = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, calander_id))
    )
    #calender = driver.find_element(By.ID, calander_id)

    Xpath_calander_left = "//*[@id='ui-datepicker-div']/div[1]"
    Xpath_calander_right = "//*[@id='ui-datepicker-div']/div[2]"
    calander_left = calender.find_element(By.XPATH, Xpath_calander_left)
    calander_right = calender.find_element(By.XPATH, Xpath_calander_right)

    table_days_left = calander_left.find_element(By.CLASS_NAME, "ui-datepicker-calendar")
    table_days_left = table_days_left.find_elements(By.CLASS_NAME, "ui-state-default")
    for day in table_days_left:
        if day.get_attribute('href') != None:
            Xpath_month_chosen = "//*[@id='ui-datepicker-div']/div[1]/div/div/span[1]"
            Xpath_year_chosen = "//*[@id='ui-datepicker-div']/div[1]/div/div/span[2]"
            year = driver.find_element(By.XPATH , Xpath_year_chosen)
            month = driver.find_element(By.XPATH, Xpath_month_chosen)
            date = [day.text, month.text, year.text]
            full_date_dict = {"year": int(date[2]), "month": int(monthToNum(date[1])), "day": int(date[0])}
            day.click()
            return full_date_dict
    next_month(calander_right)
    return None

def next_month(calander_right : webdriver):
    Xpath_icon_next_month = "//*[@id='ui-datepicker-div']/div[2]/div/a/span"
    icon_next = calander_right.find_element(By.XPATH, Xpath_icon_next_month)
    icon_next.click()

def enter_user(driver : webdriver, email : str, password : str):
    try:
        textfildMail = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "user_email"))
        )
        textfildMail.send_keys(email)
        textFildPassword = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "user_password"))
        )
        textFildPassword.send_keys(password)

        cheakBox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='sign_in_form']/div[3]/label/div"))
        )
        cheakBox.click()

        signIn = "//*[@id='sign_in_form']/p[1]/input"
        signInButton = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, signIn))
        )
        signInButton.click()
    except:
        return -1

def getCurrentAppointmentDate(driver : webdriver) -> dict:
    try:
        continueButtonXPath = "//*[@id='main']/div[2]/div[3]/div[1]/div/div[1]/div[1]/div[2]/ul/li/a"


        continueButton = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, continueButtonXPath))
        )
        if len(continueButton) == 0:
            raise Exception("Driver not find button")

        dataXPath = "//*[@id='main']/div[2]/div[3]/div[1]/div/div[1]/div[2]/p[1]"
        data = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, dataXPath))
        )

        full_date_lst = textSlice(data.text)
        full_date_dict = {"year": full_date_lst[0], "month": full_date_lst[1], "day": full_date_lst[2]}
        continueButton[0].click()
        return full_date_dict
    except:
        return None

def selectHour(driver : webdriver):
    hour_lable_id = "appointments_consulate_appointment_time"

    hour_lable = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, hour_lable_id))
    )

    hour_lable.click()
    select = Select(driver.find_element(By.ID, hour_lable_id))
    select.select_by_index(1)
    hour_lable.click()

def allActions(driver : webdriver ,mail : str , password : str, consular_name : str):
    driver.get(LINK)
    time.sleep(5)
    ## log in page
    if enter_user(driver, mail, password) == -1:
        print("The login page did not load")
        return None
    time.sleep(5)
    ##page of user with his information
    full_date_dict = getCurrentAppointmentDate(driver)
    if full_date_dict == None:
        print("The information page did not load")
        return None
    time.sleep(5)
    ##page of change information user.. appointment etc..
    try:
        Reschedule_Appointment = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "fa-calendar-minus"))
        )
        Reschedule_Appointment[0].click()

        ##looking for early date
        Reschedule_Appointment_link = "https://ais.usvisa-info.com/en-il/niv/schedule/44493741/appointment"
        driver.get(Reschedule_Appointment_link)
    except:
        print("Selecting a new appointment did not work")
        return None
    time.sleep(5)
    try:
        selectConsular(consular_name, driver)
    except:
        print(f"The embassy {consular_name} has no available dates")
        return None
    time.sleep(5)
    try:
        new_date = selectNewDate(full_date_dict, driver)
    except:
        return None
    while new_date != None:
        pass

def main(*args, **kwargs):
    driver = webdriver.Chrome(ChromeDriverManager().install())

    if len(args) > 0:
        while allActions(driver, args[1], args[2], args[3]) == None:
            now = datetime.now()
            print(f"The software did not find an earlier date for {args[0]} {now.strftime('%H:%M:%S')}\n")
            driver.quit()
            time.sleep(60*3)  ## 3 min
            driver = webdriver.Chrome(ChromeDriverManager().install())

    elif len(kwargs) > 0:
        while allActions(driver,kwargs['mail'], kwargs['password'] , kwargs['consular']) == None:
            now = datetime.now()
            print(f"The software did not find an earlier date for {kwargs['user full name']} {now.strftime('%H:%M:%S')}\n")
            driver.quit()
            time.sleep(60*3)  ## 3 min
            driver = webdriver.Chrome(ChromeDriverManager().install())

if __name__ == '__main__':
    with open('customers.json') as f:
        DataFromJasonFile = json.load(f)
    count = 0
    for customer in DataFromJasonFile['customers']:
        kwargs = {'user full name': f'HODAIA BEN HAIM{count}', 'mail' : customer['mail'] , 'password' : customer['password'], 'consular': customer['consular']}
        new_thread = Thread(target=main, kwargs=kwargs)
        new_thread.start()
        time.sleep(10)
        count+=1
