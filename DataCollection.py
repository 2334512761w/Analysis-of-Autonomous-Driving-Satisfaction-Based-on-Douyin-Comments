import datetime
import csv
from DrissionPage import ChromiumPage

def save_comments_to_csv(comments, writer):
    for comment in comments:
        text = comment['text']
        nickname = comment['user']['nickname']
        create_time = datetime.datetime.fromtimestamp(comment['create_time']).strftime('%Y-%m-%d %H:%M:%S')
        digg_count = comment['digg_count']
        writer.writerow({'昵称': nickname, '点赞数': digg_count, '时间': create_time, '评论': text})
        print({'昵称': nickname, '点赞数': digg_count, '时间': create_time, '评论': text})

def main():
    with open('data.csv', mode='w', encoding='utf-8', newline='') as f:
        csv_writer = csv.DictWriter(f, fieldnames=['昵称', '点赞数', '时间', '评论'])
        csv_writer.writeheader()

        driver = ChromiumPage()
        driver.listen.start('aweme/v1/web/comment/list/')
        driver.get('https://www.douyin.com/user/self?from_tab_name=main&modal_id=7391356199146409266&showTab=like')
        # driver.get('https://v.douyin.com/ijUsDWgh/')

        for page in range(500):
            print(f'正在采集第{page + 1}页的数据内容')
            driver.scroll.to_bottom()
            resp = driver.listen.wait()
            json_data = resp.response.body
            save_comments_to_csv(json_data.get('comments', []), csv_writer)

if __name__ == '__main__':
    main()