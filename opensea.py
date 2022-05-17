from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time


class OpenSea(object):
    def __init__(self):
        self.url = 'https://opensea.io/collection/catalog-lu-store'
        self.driver = webdriver.Chrome()
        self.href_url_list = []
        self.status = []

    def circulate_handle(self):

        rets = self.driver.find_elements(By.XPATH, '//div[@role="gridcell"]')
        for ret in rets:
            href_url = ret.find_element(By.XPATH, './div/article/a').get_attribute('href')
            self.href_url_list.append(href_url)
            # print(href_url)
            # print(href_url_list)
            # 打开新标签页
            js = "window.open('{}')".format(href_url)
            self.driver.execute_script(js)
            windows = self.driver.window_handles
            # 根据标签页句柄列表索引下标进行切换窗口
            self.driver.switch_to.window(windows[1])
            self.driver.find_element(By.XPATH, '//i[@value="refresh"]').click()

            text = "We've queued this item for an update! Check back in a minute..."
            # 设置显示等待
            ret = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="toasts"]/div/div')))

            try:
                if text in ret.text:
                    self.status.append('Queued')
                    # print(status)
                else:
                    self.status.append('Clicked')
                    # print(status)
            except:
                self.status.append('Error')

            self.driver.close()

            # 切换回主页面窗口
            self.driver.switch_to.window(windows[0])

    def parse(self):
        height = 0

        # 循环向下滑动
        while True:
            # scrollBy表示从当前的滚动条位置向下滚动一段距离
            js = 'window.scrollBy(0, 800)'
            self.driver.execute_script(js)
            time.sleep(2)
            # rets = self.driver.find_elements(By.XPATH, '//div[@role="gridcell"]')

            self.circulate_handle()

            check_height = self.driver.execute_script(
                "return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;")
            # print(check_height)
            # 判断滑动后距顶部的距离与滑动前距顶部的距离
            if check_height == height:
                break
            height = check_height

        return self.href_url_list, self.status

    def save(self, href_url_list, status):
        data = {
            'URL': href_url_list,
            'Status': status
        }
        df = pd.DataFrame(data)
        # 去除重复数据(URL)行
        df.drop_duplicates('URL', inplace=True)
        # 插入递增列
        df.insert(0, 'No', range(1, 1 + len(df)))
        df.to_excel('text.xlsx', index=False)

    def run(self):
        self.driver.get(self.url)
        href_url_list, status = self.parse()
        self.save(href_url_list, status)

        self.driver.quit()


if __name__ == '__main__':
    opensea = OpenSea()
    opensea.run()
