import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from time import sleep


def getUrls(urls):
    elm = driver.find_element_by_xpath('/html/body/div/div[2]/table/tbody/tr/td[1]/form/div[4]/table/tbody')
    trs = elm.find_elements_by_class_name('column_odd')
    trs += elm.find_elements_by_class_name('column_even')
    for tr in trs:
        urls.append(tr.find_element_by_tag_name('a').get_attribute('href'))
    print(len(urls))
    return urls

try:
    opt = Options()

    opt.set_headless(False)
    opt.add_argument('--disable-gpu')

    DRIVER_PATH = '/Users/kazuki/Downloads/chromedriver'
    driver = webdriver.Chrome(executable_path=DRIVER_PATH, chrome_options=opt)
    driver.implicitly_wait(20)
    driver.get("https://alss-portal.gifu-u.ac.jp/")
    elm = driver.find_element_by_id('t01')

    # ログイン
    elm = driver.find_element_by_id('username_input')
    elm.send_keys('x3033171')
    elm = driver.find_element_by_id('password_input')
    elm.send_keys('Aass7722!')
    elm = driver.find_element_by_id('login_button')
    elm.click()
    driver.implicitly_wait(20)


    # シラバスにホバー
    actions = ActionChains(driver)
    actions.move_to_element(driver.find_element_by_xpath('//*[@id="nav"]/li[4]/a')).perform()

    # 講義から検索をクリック
    driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[6]/ul/li[4]/ul/li[1]/a').click()
    driver.implicitly_wait(20)

    # 開口所属：工学部 開口時期：前学期 で検索
    selector1 = Select(driver.find_element_by_xpath('/html/body/div/div[2]/table/tbody/tr/td[1]/form/div[3]/table[2]/tbody/tr[7]/td[3]/select'))
    selector1.select_by_value('30')
    selector2 = Select(driver.find_element_by_xpath('/html/body/div/div[2]/table/tbody/tr/td[1]/form/div[3]/table[2]/tbody/tr[9]/td[3]/select'))
    selector2.select_by_value('1')
    driver.find_element_by_xpath('/html/body/div/div[2]/table/tbody/tr/td[1]/form/div[3]/div[2]/div/table/tbody/tr/td/div/input').click()
    driver.implicitly_wait(20)

    # 表示件数を100件に
    selector3 = Select(driver.find_element_by_xpath('/html/body/div/div[2]/table/tbody/tr/td[1]/form/div[4]/table/tbody/tr[1]/td/div[2]/select'))
    selector3.select_by_value('100')
    driver.implicitly_wait(20)

    # urlを取得
    urls = []
    urls = getUrls(urls)
    elm = driver.find_element_by_xpath('/html/body/div/div[2]/table/tbody/tr/td[1]/form/div[4]/table/tbody/tr[1]/td/div[2]/span[2]')
    pages = elm.find_elements_by_tag_name('a')
    pages.pop(-1)
    while(True):
        elm = driver.find_element_by_xpath('/html/body/div/div[2]/table/tbody/tr/td[1]/form/div[4]/table/tbody/tr[1]/td/div[2]/span[2]')
        if elm.find_elements_by_partial_link_text('次の100件'):
            elm.find_element_by_partial_link_text('次の100件').click()
            urls = getUrls(urls)
        else:
            print('break')
            break

    with open('lecture_urls.tsv', 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(url + '\n')

    sleep(5)

except Exception as ex:
    print(ex)
finally:
    if 'driver' in vars() and driver is not None:
        driver.quit()

