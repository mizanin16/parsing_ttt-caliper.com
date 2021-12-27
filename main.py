import os.path

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time


def get_html():
    """
    Открытие сайта со всем списком товаров, скроллинг до конца страницы
    :return: Возвращается проскроленная страница
    """
    site = 'https://www.ttt-caliper.com/urunler'
    EXE_PATH = 'chromedriver.exe'
    driver = webdriver.Chrome(executable_path=EXE_PATH)
    driver.get(site)
    SCROLL_PAUSE_TIME = 3

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return driver.page_source


def open_site():
    """
    Открытие сайта и получение списка, состоящего из словарей с данными заголовка,
    ссылкой на изображение и ссылкой на товар
    :return:
    """
    list_items = []
    site_URI = 'https://www.ttt-caliper.com/'
    html_text = get_html()
    soup = BeautifulSoup(html_text, 'lxml')
    ads = soup.find_all('img', class_="img-responsive center-block")
    for i in range(0, ads.__len__()):
        attrs = ads[i].attrs
        title = attrs['title'].strip()
        try:
            # Преобразование с list в set и обратно, для исключения повторов
            href_img = site_URI + attrs['src'].strip()
            href_site = soup.find('a', class_="veris", id=i + 1)
            href_next_site = href_site['href']
            next_current_site = site_URI + href_next_site
            dict_item = {'title': title, 'href_img': href_img, 'next_current_site': next_current_site}
            list_items.append(dict_item)
        except Exception:
            continue
        list_items = list(set(list_items))
        iter_list_items(list_items)


def iter_list_items(list_items):
    """
    Создание и запись в файл из общего списка
    :param list_items: Список всех товаров
    :return:
    """
    for item in list_items:
        if check_double(item["title"]):
            csv_create()
            write_to_csv(f'\nНаименование товара: ; {item["title"]}\n\n')
            write_to_csv(f'Ссылка на изображение: ; {item["href_img"]} \n\n')
            write_to_csv(f'Ссылка на страницу товара: ; {item["next_current_site"]}\n\n')
            load_list(item['next_current_site'])


def main():
    open_site()


def load_list(name_site):
    """
    Открываем конкретный товар и получаем параметры
    :param name_site: Ссылка на товар
    :return:
    """
    EXE_PATH = 'chromedriver.exe'
    driver = webdriver.Chrome(executable_path=EXE_PATH)
    driver.get(name_site)
    h2 = driver.find_elements_by_xpath('//tr//td')
    try:
        button_all = driver.find_elements_by_xpath("//a[@href='javascript:void(0);']")
        for button_more in button_all:
            if button_more.text == 'More':
                button_more.click()
        h2 = driver.find_elements_by_xpath('//tr//td')
    except BaseException:
        pass
    label_brand = h2[5].text
    label_model = h2[6].text
    label_sub_model = h2[7].text
    label_sub_ref = h2[8].text
    i = 9
    write_to_csv(f'Brand: ;Model: ; Sub model: ; OEM Ref.:\n')
    write_to_csv(f'{label_brand};{label_model};{label_sub_model};{label_sub_ref}\n')
    if 'Close' in h2[0].text[:h2[0].text.find("Vehicle Brand")]:
        while True:
            label_brand = h2[i].text
            label_model = h2[i + 1].text
            label_sub_model = h2[i + 2].text
            label_sub_ref = h2[i + 3].text
            write_to_csv(f'{label_brand};{label_model};{label_sub_model};{label_sub_ref}\n')
            if 'Close' in h2[i + 5].text:
                i = i + 5
                break
            elif len(h2) < i + 5:
                break
            else:
                i = i + 4
    write_to_csv(f'\nVehicle Brand: ; Model: ; OEM Ref.:\n')
    position_products = True
    position_content = True
    while 'Vehicle Brand' != h2[i].text:
        i = i + 1
    else:
        i = i + 3
    if len(h2) < i + 1:
        return
    while h2[i].text != 'Product':
        label_veh_brand = h2[i].text
        label_veh_model = h2[i + 1].text
        label_veh_ref = h2[i + 2].text
        write_to_csv(f'{label_veh_brand};{label_veh_model};{label_veh_ref}\n')
        i = i + 3
        if len(h2) < (i + 4):
            break
        else:
            if h2[i + 4].text == 'Close':
                break

    while len(h2) > i + 1:
        if h2[i].text == 'Product' and h2[i + 1].text == ':':
            # Прикрепить 'Related products' с родительского узла
            if position_products:
                write_to_csv('\nRelated products\n')
                # worksheet.write(f'A{k - 2}', 'Related products')
                # print(f'A{k - 2}', 'Related products')
                position_products = False
                write_to_csv(f'Product: ; OEM Ref.: \n')
            name_product = h2[i + 2].text
            oem_product = h2[i + 5].text
            write_to_csv(f'{name_product};{oem_product}\n')
            i = i + 6
        elif h2[i + 1].text == 'TTT No':
            if position_content:
                write_to_csv('\nContent\n')
                write_to_csv('content_ttn_no ;content_product ;content_pcs\n')
                position_content = False
                i = i + 3
            if len(h2) < (i + 4):
                break
            content_ttn_no = h2[i + 1].text
            content_product = h2[i + 2].text
            content_pcs = h2[i + 3].text
            write_to_csv(f'{content_ttn_no};{content_product};{content_pcs}\n\n')
            i = i + 3
        else:
            i = i + 1


def write_to_csv(text):
    i = 0
    while os.path.exists(f'path\out{i}.csv'):
        i = i + 1
    with open(f'path\out{i - 1}.csv', 'a+', encoding='utf-16') as f:
        f.write(text)


def check_double(title):
    dirs_path = os.listdir('path')
    for file in dirs_path:
        if r'path\out' in title:
            return True
        if title in file:
            return False
    return True


def csv_create():
    """
    Создаю файл. Если не существет следующий с значением i записую в него
    :return:
    """
    i = 0
    while os.path.exists(f'path\out{i}.csv'):
        i = i + 1
    else:
        file = open(f'path\out{i}.csv', 'w')
        file.close()


def check_host(text: str) -> bool:
    file = open(f'host.log', 'r')
    datafiles = file.readlines()
    for datafile in datafiles:
        if text in datafile:
            return True
        else:
            continue
    return False


def to_host(text: str):
    file = open(f'host.log', 'a+')
    file.write(text)
    file.write('\n')
    file.close()


if __name__ == '__main__':
    main()
