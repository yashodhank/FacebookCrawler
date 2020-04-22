from tkinter import *
from tkinter.messagebox import *
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
import json
import datetime


# 能輸入fb帳號密碼的功能
def login_fb(page_url, your_email, your_pw):
    options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_setting_values': {'notifications' : 2}}
    options.add_experimental_option('prefs', prefs)

    # 版权声明：本文为CSDN博主「测试小李」的原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接及本声明。
    # 原文链接：https://blog.csdn.net/andydufre/article/details/79204158
    driver = webdriver.Chrome(options = options, executable_path="chromedriver.exe")
    # driver.implicitly_wait(5)
    driver.get(page_url)
    count = 0

    for i in range(3):
        email = driver.find_element_by_id("email")
        email.send_keys(your_email)
        password = driver.find_element_by_id("pass")
        password.send_keys(your_pw)
        try:
            driver.find_element_by_id("u_0_2").click()
        except:
            driver.find_element_by_id("loginbutton").click()
        # 如果沒有成功登入則重新書入帳號密碼, 若成功登入則繼續下一步
        time.sleep(1)
        try:
            # 確認是否能找到email及 password標籤，若找地到代表沒有成功登入
            if driver.find_element_by_id("email") == e_mail.get() and driver.find_element_by_id("pass") == e_mail.get():
                driver.find_element_by_id("u_0_2").click()
            else:
                driver.find_element_by_id("email").clear()
                driver.find_element_by_id("pass").clear()
                count +=1
                print("登入失敗，嘗試重新登入: {}次".format(count))
        except:
            break
    return driver


def change_lang(driver):
    driver.execute_script("window.scrollTo(0,1000)")
    langs = driver.find_elements_by_class_name("_5f4c")
    for lang in langs:
        if lang.text == "English (US)":
            lang.click()
            button = WebDriverWait(driver, 5, 0.5).until(EC.element_to_be_clickable((By.CLASS_NAME, "layerConfirm")))
            button.click()


# 取得所有貼文的資訊
def get_posts(driver):
    soup = BeautifulSoup(driver.page_source, "html5lib")
    posts = soup.find_all("div", {"class":"_5pcr userContentWrapper"})
    return posts


def get_post_timeObj(post):
    timeString = post.find("abbr", "_5ptz")['title']
    timeObj = datetime.datetime.strptime(timeString, "%A, %B %d, %Y at %I:%M %p")
    return timeObj


# 其功能為抓取當下driver取得的畫面中的貼文日期，將日期由字串轉為日期物件，並放到一個串列儲存並返回
def get_post_time(driver):
    soup = BeautifulSoup(driver.page_source, "html5lib")
    posts_head = soup.find_all("div", "clearfix g_5ogezyw9k")
    post_dateObj_list = []
    for post in posts_head:
        post_dateObj = get_post_timeObj(post)
        post_dateObj_list.append(post_dateObj)
    return post_dateObj_list


def timeStr_to_timeOBj(string):
    timeObj = datetime.datetime.strptime(string, "%Y-%m-%d")
    return timeObj


# 功能為判斷driver取得的畫面中的貼文是否在所指定的時間中，若沒有則自動向下滾動取得更多貼文
def get_posts_of_period(driver, post_dateObj_list, start_date):
    # 將參數:起始日期、結束日期轉為日期物件
    start_dateObj = timeStr_to_timeOBj(start_date)
    current_post_dateObj_list = post_dateObj_list
    # 判斷 起訖日期是否在目前畫面中, 變數為布林
    while True:
        try:
            is_start_date_in_list = start_dateObj >= current_post_dateObj_list[-1]
            if is_start_date_in_list:
                break
            else:
                # execute_script 可讓網頁滾到最下面，得到更多貼文
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                current_post_dateObj_list = get_post_time(driver)
                time.sleep(2)
        except Exception as e:
            print(e)
            print("Trying to fix the error...")
            time.sleep(1)
            current_post_dateObj_list = get_post_time(driver)


def filter_post_of_period(posts, start_date, end_date):
    start_dateObj = timeStr_to_timeOBj(start_date)
    end_dateObj = timeStr_to_timeOBj(end_date)
    posts_of_period = []
    for post in posts:
        post_dateObj = get_post_timeObj(post)
        if (end_dateObj + datetime.timedelta(days=1)) > post_dateObj >= start_dateObj:  # end_dateObj + datetime.timedelta(days=1) 代表 end date 的一整天
            posts_of_period.append(post)
    return posts_of_period


def expand(driver, n):
    for i in range(n):
        print("第 {} 次展開".format(i+1))
        time.sleep(5)
        for i in driver.find_elements_by_class_name("_4ssp"):
            print(i.text)
            try:
                i.click()
                time.sleep(2)
            except ElementClickInterceptedException:
                #print(i.id, "is not clickable")
                driver.execute_script("arguments[0].click();", i)
                time.sleep(2)


def get_post_infos(posts):
    posts_infos = []
    # 貼文資訊的串列含有 日期物件、貼文內容、按讚數
    for post in posts:
        # 用戶名
        username = [name for name in post.find("h5", "_7tae").stripped_strings][0] # 將標籤中的多個字串切成串列，第一個值必為用戶ID
        # 貼文時間
        post_time = post.find("abbr", "_5ptz")['title']
        try:
            content = post.find("div", "_5pbx").text
        except:
            content = 'https://www.facebook.com' + post.find("div", "mtm").a['href'].split('?', 2)[0]

        # 按讚數
        try:
            thumbsup = post.find("span", "_1n9k").a["aria-label"].split()[0].replace(",", "")
            if "K" in thumbsup:
                thumbsup = int(thumbsup.replace("K", "")) * 1000
            else:
                thumbsup = int(thumbsup)
        except:
            thumbsup = 0

        # 找出貼文中的留言樹及分享數
        # 留言數
        comments_and_shares_block = post.find("div", "_4vn1")
        try:
            amount_comments = comments_and_shares_block.find("a", "_3hg- _42ft").text.split(" ")[0]
            if "K" in amount_comments:
                amount_comments = float(amount_comments.replace("K", "")) * 1000
                amount_comments = round(amount_comments) # round() 去除小數
            else:
                amount_comments = int(amount_comments)
        except:
            amount_comments = 0

        # 分享數
        try:
            amount_shares = comments_and_shares_block.find("a", "_3rwx _42ft").text.split(" ")[0]
            if "K" in amount_shares:
                amount_shares = float(amount_shares.replace("K", "")) * 1000
                amount_shares = round(amount_shares) # round() 去除小數
            else:
                amount_shares = int(amount_shares)
        except:
            amount_shares = 0

        post_info = {
            "username": username,
            "time": post_time,
            "content": content,
            "thumbsup": thumbsup,
            "amount_comments": amount_comments,
            "amount_shares": amount_shares # round() 去除小數
        }
        posts_infos.append(post_info)
    return posts_infos


def filter_thumbsup_number(posts_infos, number):
    popular_posts = []
    for post in posts_infos:
        thumbsup_number = post["thumbsup"]
        try:
            if thumbsup_number >= number:
                popular_posts.append(post)
        except ValueError:
            print("Invalid post", post)
    print("超過 {} 個讚的貼文: {:d} 則".format(number, len(popular_posts)))
    return popular_posts


def save_json(data):
    if json_name.get() == "":
        print("未輸入JSON檔名，不會儲存資料")
    else:
        print("將抓到的資料儲存至 {} 中...".format(json_name.get()))
        f = open(json_name.get(), "w", encoding="utf-8")
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.close()


def collecting_comments(posts):
    posts_with_comments = []

    count_post_having_comments = 0
    for post in posts:
        post_time = post.find("abbr", "_5ptz")['title']
        # 貼文中的每一條留言
        comments_of_post = post.find_all("div", "_6qw3")
        if comments_of_post:
            try:
                post_message = post.find("div", "_5pbx").text
            except:
                post_message = 'https://www.facebook.com' + post.find("div", "mtm").a['href'].split('?', 2)[0]
            print("尋找 {} 中的留言...".format(post_message))

            # 將貼文中的所有留言以dict格式儲存
            post_comments = {}
            for cmt in comments_of_post:
                # 每條留言的留言者ID
                username = cmt.find("a", "_6qw4").text
                comments = []
                for i in range(3):
                    try:
                        comment = cmt.find("span", "_3l3x").text
                        comments.append(comment)
                        break
                    except Exception as e:
                        print(e)
                        print("Trying to fix the error...")
                if username in post_comments:
                    post_comments[username] += comments
                else:
                    post_comments[username] = comments
            count_post_having_comments += 1
        else:
            continue
        # 將所有貼文以串列的方式儲存
        posts_with_comments.append({
            "post message": post_message,
            "post time": post_time,
            "comments": post_comments
        })
    return posts_with_comments, count_post_having_comments


def show_comments_data():
    driver = login_fb(url.get(), e_mail.get(), password.get())
    # 將 Facebook地顯示語言換成英文
    change_lang(driver)
    # 如果是社團首頁則轉換成最近貼文先顯示
    for i in range(3):
        try:
            driver.find_element_by_link_text("NEW ACTIVITY").click()
            driver.find_elements_by_class_name("_54nc")[1].click()
            break
        except:
            continue
    # 如果是粉專首頁則轉換到貼文區
    if driver.find_elements_by_class_name("_2yau"):
        for area in driver.find_elements_by_class_name("_2yau"):
            if area.text == "Posts":
                area.click()
                break

    # 取的畫面中的貼文時間字串，將字串轉換成日期物件並放入一個串列
    post_time_object_list = get_post_time(driver)
    # 找出起始日期到結束日期的貼文
    get_posts_of_period(driver, post_time_object_list, start_date.get())
    # 展開留言中的更多留言、回覆
    expand(driver, 2)
    time.sleep(2)
    posts = get_posts(driver)
    posts_of_period = filter_post_of_period(posts, start_date.get(), end_date.get())
    posts_with_comments, count_post_having_comments = collecting_comments(posts_of_period)
    print("共有 {} 則有流言的貼文".format(count_post_having_comments))

    # 判斷是否有增加姓名條件
    if user_name.get() != "":
        posts_with_someone_coments = []
        for post in posts_with_comments:
            someone_comments = {}
            post_comments = post["comments"]
            if user_name.get() in post_comments:
                someone_comments[user_name.get()] = post_comments[user_name.get()]
                post["comments"] = someone_comments
                posts_with_someone_coments.append(post)
        posts_with_comments = posts_with_someone_coments
        if len(posts_with_comments) == 0:
            showinfo("重要訊息", "沒有任何{}的留言".format(user_name.get()))
        else:
            # 印出貼文
            print("找到含有 {} 流言的貼文：{} 則".format(user_name.get(), len(posts_with_comments)))
            for post in posts_with_comments:
                print(post, end="\n")
            # 儲存資料到json檔
            save_json(posts_with_comments)
    else:
        save_json(posts_with_comments)

    driver.quit()


def show_post_data():
    # 登入fb
    driver = login_fb(url.get(), e_mail.get(), password.get())
    # 將 Facebook地顯示語言換成英文
    change_lang(driver)
    # 如果是社團首頁則轉換成最近貼文先顯示
    for i in range(3):
        try:
            time.sleep(1)
            driver.find_element_by_link_text("NEW ACTIVITY").click()
            driver.find_elements_by_class_name("_54nc")[1].click()
            time.sleep(2)
            break
        except:
            continue
    # 如果是粉專首頁則轉換到貼文區
    if driver.find_elements_by_class_name("_2yau"):
        for area in driver.find_elements_by_class_name("_2yau"):
            if area.text == "Posts":
                area.click()
                break
    # 取的畫面中的貼文時間字串，將字串轉換成日期物件並放入一個串列
    post_time_object_list = get_post_time(driver)
    # 找出起始日期到結束日期的貼文
    time.sleep(2)
    get_posts_of_period(driver, post_time_object_list, start_date.get())
    posts = get_posts(driver)
    posts_of_period = filter_post_of_period(posts, start_date.get(), end_date.get())
    posts_infos = get_post_infos(posts_of_period)

    # 判斷是否有輸入按讚數條件
    if thumbsup_number.get() > 0:
        posts_infos = filter_thumbsup_number(posts_infos, thumbsup_number.get())
    # 判斷是否有輸入姓名條件
    if user_name.get() != "":
        posts_infos = [post for post in posts_infos if post["username"] == user_name.get()]

    if len(posts_infos) == 0:
        showinfo("重要訊息", "沒有符合條件的貼文")
    else:
        # 印出貼文
        print("找到符合條件的貼文：{} 則".format(len(posts_infos)))
        for post in posts_infos:
            print(post, end="\n")
        # 儲存資料到json檔
        save_json(posts_infos)

    driver.quit()

if __name__ == '__main__':
    # 建立Tk物件, 設定視窗大小
    window = Tk()
    window.title("Facebook爬蟲程式")
    window.geometry("600x200")
    window.maxsize(900,500)

    # 輸入值變數
    e_mail = StringVar()
    password = StringVar()
    url = StringVar()
    user_name = StringVar()
    start_date = StringVar()
    end_date = StringVar()
    thumbsup_number = IntVar()
    json_name = StringVar()

    # 標籤元件設定
    email_label = Label(window, text="帳號:").grid(row=0, column=0, sticky=E)
    password_label = Label(window, text="密碼:").grid(row=0, column=2, sticky=E)
    url_label = Label(window, text="網址:").grid(row=1, sticky=E)
    setting_label = Label(window, text="條件設定:").grid(row=3,sticky=W)
    username_label = Label(window, text="姓名:").grid(row=4, sticky=E)
    start_date_label= Label(window, text="日期:從").grid(row=5, sticky=E)
    end_date_label= Label(window, text="至").grid(row=5, column=2, sticky=W+E+S+N)
    thumbsup_number_label = Label(window, text="按讚數:").grid(row=6, sticky=W)
    save_json_name_label = Label(window, text="檔名:").grid(row=7, column=0, sticky=W)

    # 輸入欄元件設定
    input_email = Entry(window, textvariable=e_mail).grid(row=0, column=1, sticky=W)
    input_password = Entry(window, textvariable=password, show="*").grid(row=0, column=3, sticky=W)
    input_url = Entry(window, width=70, textvariable=url).grid(row=1, column=1, columnspan=50, sticky=W)
    input_username = Entry(window, textvariable=user_name).grid(row=4, column=1, sticky=W)
    input_startdate = Entry(window, textvariable=start_date).grid(row=5, column=1, sticky=W)
    input_enddate = Entry(window, textvariable=end_date).grid(row=5, column=3, sticky=W)
    input_thumbsup_number = Entry(window, textvariable=thumbsup_number).grid(row=6, column=1, sticky=W)
    input_json_name = Entry(window, textvariable=json_name).grid(row=7, column=1, sticky=W)

    #按鈕元件設定，觸發程式執行
    button1 = Button(window, text="尋找貼文", command=show_post_data).grid(row=8, column=1)
    button2 = Button(window, text="尋找留言", command=show_comments_data).grid(row=8, column=3)


    window.mainloop()
