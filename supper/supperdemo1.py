from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver import ActionChains
import requests
from PIL import Image
import os
from io import BytesIO
import cv2
import numpy as np

browser = webdriver.Chrome()

def star_browser(url):

    # url = 'https://www.chaoxing.com/'
    browser.get(url)
    browser.maximize_window()
    sleep(2)


def login(userid,pwd):
    browser.find_element(By.XPATH, '//*[text()="登录"]').click()
    sleep(1)
    browser.find_element(By.XPATH, '//*[@placeholder="请输入手机号"]').send_keys(userid)
    browser.find_element(By.XPATH, '//input[@id="lPassword"]').send_keys(pwd)
    browser.find_element(By.XPATH, '//*[@class="wall-sub-btn"]').click()
    sleep(5)
    # 处理滑块验证码
def screenshot():
    # 定位背景图
    bg_img = browser.find_element(By.XPATH, '//*[@class="yidun_bg-img"]')
    # 定位滑块
    fo_img = browser.find_element(By.XPATH, '//*[@class="yidun_jigsaw"]')
    #下载滑块图片
    # print(target_img.get_attribute('src'))
    bg_dowm = Image.open(BytesIO(requests.get(bg_img.get_attribute('src')).content))
    bg_dowm.save('tar_bg.jpg')
    fo_dowm = Image.open(BytesIO(requests.get(fo_img.get_attribute('src')).content))
    fo_dowm.save('tar_fo.png')
    img_jpg = cv2.imread('tar_bg.jpg')
    img_png = cv2.imread('tar_fo.png')

    # 截取全图
    # browser.save_screenshot('full.png')
    # 截取背景图
    # print(target_img.location)
    # print(target_img.size)
    # left = target_img.location['x']
    # top = target_img.location['y']
    # right = target_img.location['x'] + target_img.size['width']
    # bottom = target_img.location['y'] + target_img.size['height']
    # photo = Image.open('full.png')
    # photo = photo.crop((left,top,right,bottom))
    # photo.save('bg_before.png')
    # bg = cv2.imread('tar_bg.png')
    # 截取按钮图片
    # left = tarplate_img.location['x']
    # top = tarplate_img.location['y']
    # right = tarplate_img.location['x'] + tarplate_img.size['width']
    # bottom = tarplate_img.location['y'] + tarplate_img.size['height']
    # photo = Image.open('full.png')
    # photo = photo.crop((left, top, right, bottom))
    # photo.save('fo_before.png')
    # fo = cv2.imread('tar_fo.png')
    # 对图片进行灰度处理
    fo = cv2.cvtColor(img_png, cv2.COLOR_BGR2GRAY)
    bg = cv2.cvtColor(img_jpg, cv2.COLOR_BGR2GRAY)
    # 去掉滑块黑色部分
    # fo = fo[fo.any(1)]  # 0表示黑色，1表示高亮部分
    # 匹配->cv图像匹配算法， 匹配出划片图片在背景图的位置
    result = cv2.matchTemplate(bg, fo, cv2.TM_CCORR_NORMED)  # match匹配,Template模板;精度高，速度慢的方法
    index_max = np.argmax(result)
    # 反着推最大值的二维位置，和opencv是相反的
    x, y = np.unravel_index(index_max, result.shape)
    print(index_max,result.shape)
    action = ActionChains(browser)
    # 鼠标左键按下不放
    action.click_and_hold(fo_img).perform()
    action.drag_and_drop_by_offset(fo_img, xoffset=x + 10, yoffset=0).perform()
    sleep(1)
    # 通过当前滑块图片是否存在判断是否跳出循环
    # get_element_null(loc1).is_displayed()
    # print('第%s次进行滑动验证码校验' % n, '\n')
    # n = n + 1
    # sleep(1)

    print("login succeeeded!")

if __name__ == '__main__':
    url = 'https://www.zhihuishu.com/'
    userid = '18316478347'
    pwd = '101867Qaz'

    star_browser(url)
    login(userid,pwd)
    # sleep(2)
    screenshot()
