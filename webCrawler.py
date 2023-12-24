# author LYQ
# date 2021/1/20
import requests  # 用于请求目标网站
import random  # 用于生成随机数
from bs4 import BeautifulSoup  # 用于网页抓取数据的
import pandas  # 数据输出和存储
import threading  # 用于控制和管理线程
import time  # 用于定时睡眠
import os  # 用于文件操作处理


# 爬取表格并提取table标签内容
def get_table_html(web_name):
    url = 'https://finance.yahoo.com/quote/AAPL/history?p=' + web_name
    # 获取连接
    html = requests.get(url)
    # 设置连接对象的编码为'utf-8'
    html.encoding = 'utf-8'
    # 将获取的html代码文本，通过BeautifulSoup库来进行解析
    soup = BeautifulSoup(html.text, 'html.parser')
    # 若使用lxml HTML 解析器，记得安装lxml库
    # soup = BeautifulSoup(html.text, 'lxml')
    # find()方法找到<table>标签的dom节点
    table_element = soup.find('table', {'data-test': 'historical-prices'})
    # 返回table表格节点的内容
    return table_element


# 解析表格数据并以json格式存储
def save_data(table_element, filename):
    # 表头信息 find()方法找到<thead>标签的dom节点
    thead_data = table_element.find('thead', {'data-reactid': '34'})
    # 表格体信息 find()方法找到<tbody>标签的dom节点
    tbody_data = table_element.find('tbody', {'data-reactid': '50'})
    data = []
    for tr in tbody_data:
        row = []
        for td in tr.find_all('td'):
            # 将获取的到的<td>标签的内容进行格式化，取掉多余的符号
            row.append(td.text.replace(',', ''))
        data.append(row)
    column = []
    # 若你已知表头信息，完全可以手动创建
    # column = ['日期(Date)','开市价(Open)','最高价(High)','最低价(Low)','收市价(Close)','调整关闭量(Adj Close)','交易量(Volume)']
    for th in thead_data.find_all('th'):
        column.append(th.text.strip('*').replace(' ', '').replace(',', ''))
    # print(column)
    df = pandas.DataFrame(data[1:], columns=column)
    # 以json格式存储
    df.to_json(filename, indent=2, orient='index')
    return filename


# 将数据保存成json格式的文件
def save_json_file(f_name):
    # 获取表格数据
    table_element = get_table_html('AAPL')
    print('table_html 数据获取成功...')
    # 保存数据
    save_data(table_element, f_name)
    print('文件保存成功...')


running = True  # 线程running标识
interval = 15   # 时间间隔
is_change = False   # 判断文件状态是否改变的标识
rm_num = 5   # 删除标志


# 随机删除文件
def random_remove(filename):
    global rm_num
    status = random.randint(1, 5)   # 生成随机整数status
    print('status='+str(status))
    if status == rm_num:    # 若相等则删除，否则睡3s
        if os.path.exists(filename):
            os.remove(filename)   # 删除文件
        else:
            print('文件不存在！')
            time.sleep(3)   # 让线程睡3s
    else:
        print('时机未到，无法删除...')
        time.sleep(3)


def is_update(file):
    global is_change
    # 若存在则代表还未发生变化
    if os.path.exists(file):
        return is_change
    else:
        # 不存在则改变状态
        is_change = True
        return is_change


# 模拟线程   流程: 程序运行生成LYQ.json文件 ===》 进入while循环生成status整数
#                                                     ====》相等则删除并判断为文件状态已改变 延迟interval秒 重新生成;继续while循环，直到用户输入一个任意整数停止线程
#                                                     ====》不相等则一直重试直到，用户输入一个任意整数停止线程
def thread_begin():
    global running, interval
    name = 'LYQ.json'
    save_json_file(name)
    while running:
        # 尝试改变文件状态
        random_remove(name)
        if is_update(name):
            print(f'请稍等{interval}s,数据文件正重新生成... ')
            time.sleep(interval)
            save_json_file(name)
        print('文件已存在，状态未改变...')
        time.sleep(interval)


# 管理和控制线程方法
def control_thread():
    global running
    while running:
        num = abs(int(input('若想停止work线程，请输入任意整数停止')))   # 提示用户输入任意整数可停止work线程
        if num is not None:   # 若识别到num已被用户输入赋值，则停止线程
            running = False
            print('work: 啊我死了！')
        else:                # 否则提示
            print(f'请{interval}s后重试~~~')


# 主方法
def main():
    global running, interval
    # 控制线程
    control_th = threading.Thread(target=control_thread, name='control')
    # 工作线程
    work_th = threading.Thread(target=thread_begin, name='work')

    # 开启线程
    work_th.start()
    control_th.start()


if __name__ == "__main__":
    main()
