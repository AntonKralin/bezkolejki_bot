import time
import smtplib
from email.message import EmailMessage

from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from playsound3 import playsound


main_url = 'https://uw.bezkolejki.eu/ouw'
address = 'kralin.dart@gmail.com'


def click_checkbox(driver):
    try:
        captcha_frame = driver.find_element(
            By.XPATH,
            "//iframe[contains(@src, 'hcaptcha.com')]"
        )
        driver.execute_script("arguments[0].click();", captcha_frame)
        captcha_frame.click()
    except Exception as ex:
        print('checkbox:', ex)


def select_first_time_from_dropdown(driver):
    try:
        time_select = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "selectTime"))
            )
        time_select = driver.find_element(By.ID, "selectTime")
        WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "selectTime"))
            )
        select = Select(time_select)
        options = select.options

        if len(options) == 0:
            print("❌ Нет доступных опций")
            return False

        # Исключаем первую пустую опцию если есть
        start_index = 0
        if options[0].text.strip() == "":
            start_index = 1

        if start_index >= len(options):
            print("❌ Нет доступных времен после фильтрации")
            return False

        select.select_by_index(start_index)
        selected_value = select.first_selected_option.text
        playsound('AITheme0.mp3', block=False)
        send_email(address=address, text='')
        print(f"Текущее выбранное значение: {selected_value}")
        # click_checkbox(driver)

    except Exception as e:
        print(f"❌ Ошибка при выборе времени: {e}")
        return False, None


def check_calendar(driver):
    # календарь
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "span.vc-day-content"))
    )
    available_dates = driver.find_elements(
        By.CSS_SELECTOR,
        "span.vc-day-content:not(.is-disabled)"
    )
    print(f"Найдено доступных дат: {len(available_dates)}")

    # Выводим информацию о каждой доступной дате
    for i, date_element in enumerate(available_dates, 1):
        try:
            # Получаем текст даты (число)
            day_number = date_element.text

            # Получаем полную дату из атрибута aria-label
            aria_label = date_element.get_attribute("aria-label")

            # Получаем дополнительные классы (если есть)
            classes = date_element.get_attribute("class")

            print(f"{i}. Дата: {day_number}, Полная дата: {aria_label}, Классы: {classes}")
            parent_element = driver.execute_script("return arguments[0].parentNode;", date_element)
            parent_element.click()
            select_first_time_from_dropdown(driver)

        except Exception as e:
            print(f"Ошибка при получении данных элемента {i}: {e}")


def go_to_calendar(driver):
    try:
        try:
            # Ждем появления кнопки Karta Polaka
            karta_polaka_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, 
                "//button[contains(@class, 'operation-button') and contains(text(), 'Karta Polaka')]"))
            )

            # Проверяем, активна ли кнопка
            if "active" in karta_polaka_button.get_attribute("class"):
                print("Кнопка Karta Polaka уже активна (выбрана)")
            else:
                # Если не активна, кликаем на нее
                karta_polaka_button.click()
                time.sleep(1)

        except TimeoutException:
            print("Не удалось найти кнопку Karta Polaka")

        # 2. Найти и нажать кнопку "Dalej"
        try:
            # Ждем появления кнопки Dalej
            dalej_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                    "//button[contains(@class, 'footer-btn') and contains(text(), 'Dalej')]"))
            )

            # Прокручиваем к кнопке для надежности
            driver.execute_script("arguments[0].scrollIntoView(true);", dalej_button)
            time.sleep(0.5)

            # Нажимаем кнопку
            dalej_button.click()
            print("Нажали кнопку Dalej")

        except TimeoutException:
            print("Не удалось найти кнопку Dalej")

    except Exception as e:
        print(f"Произошла ошибка: {e}")


def start_parsing():
    try:
        driver = wd.Firefox()
        driver.maximize_window()
        driver.get(main_url)

        go_to_calendar(driver)

        while True:
            check_calendar(driver)
            next_month = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div.vc-arrow.is-right"))
                )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_month)
            next_month.click()
            check_calendar(driver)
            prev_month = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div.vc-arrow.is-left"))
                )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", prev_month)
            prev_month.click()
            time.sleep(1)

    except Exception as ex:
        print(ex)
        driver.quit()


def send_email(address, text):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465
    sender_email = 'tktat6@gmail.com'
    sender_password = 'kbzg wmpr swlp yuau'
    subject = 'Visa'

    msg = EmailMessage()
    msg.set_content(text)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = address

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email sent successfully!")

    except smtplib.SMTPException as e:
        print(f"Error: unable to send email. {e}")


if __name__ == '__main__':
    start_parsing()
