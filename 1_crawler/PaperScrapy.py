import time

import requests
import csv
import os
from bs4 import BeautifulSoup
import re
from PIL import Image
from io import BytesIO
import threading
import shutil
from win32com.client import Dispatch


proxies = {
    'https': 'https://127.0.0.1:1080',
    'http': 'http://127.0.0.1:1080'
}

headers = {
    'ieee': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    },
}


def load_csv(file):
    data = []
    with open(file, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append([row[i] for i in range(4)])
    return data


def download_by_ieee(link):
    # return None
    print("Searching {}".format(link))
    try:
        res = requests.get(link,
                           headers=headers['ieee'])
        content = res.content.decode('utf-8')
        result = re.search(r'pdfUrl":"/stamp/stamp\.jsp\?tp=&arnumber=\d*"', content)
        if result is None:
            return None
        url = result.group()
        url = url[9:len(url) - 1]

        res = requests.get("https://ieeexplore.ieee.org{}".format(url),
                           headers=headers['ieee'])
        content = res.content.decode('utf-8')
        bs = BeautifulSoup(content, features="html.parser")
        iframe = bs.find('iframe')
        if iframe is None:
            return None
        url = iframe['src']
        return url
    except Exception as _:
        print('Connect Failed')
        return None


class DownloadChecker(threading.Thread):
    def __init__(self, pid, link):
        threading.Thread.__init__(self)
        self.t_name = "{}.pdf".format(pid)
        self.o_name = self.parse_name(link)

    @staticmethod
    def parse_name(link):
        res = re.search(r'/.*.pdf', link)
        if res is not None:
            return res.group()[1:]

    def run(self):
        while True:
            if os.path.isfile('./papers/{}'.format(self.o_name)):
                shutil.move('./papers/{}'.format(self.o_name), './papers/{}'.format(self.t_name))
                break
            time.sleep(5)


def download(pid, link):
    if link is None:
        print("No valid url")
        return
    print("Downloading {}".format(link))
    try:
        thunder = Dispatch('ThunderAgent.Agent64.1')
        thunder.AddTask(link, '{}.pdf'.format(pid))
        thunder.CommitTasks()
        checker = DownloadChecker(pid, link)
        checker.start()
    except Exception as _:
        print("Failed to download")
        return


waited = True


def download_paper(pid, d):
    cf, title, doi, link = d
    global waited
    if link.startswith("http://dx.doi.org/"):
        if not waited:
            time.sleep(30)
            waited = True
        url = download_by_ieee(link)
        waited = False
        if url is None:
            print("Not found!")
        else:
            download(pid, url)
    else:
        print("Not found!")
        pass


def main(file):
    csv_data = load_csv(file)
    count = len(csv_data)
    for i, d in enumerate(csv_data):
        print(i, ' / ', count)
        if os.path.isfile("./papers/{}.pdf".format(i)) or os.path.isfile("./papers/{}.pdf.xltd".format(i)):
            continue
            cmd = input("Paper {} {}\nwas downloaded. Re-download it? y/N:  ".format(i, d[1]))
            if cmd == 'y' or cmd == 'Y':
                download_paper(i, d)
        else:
            download_paper(i, d)


# def check(st_id, e_id):
#     for i in range(st_id, e_id):


if __name__ == "__main__":
    # main("test.csv")
    # check(0, 3101)
    main("list.csv")
    # download(2085, 'https://ieeexplore.ieee.org/ielx5/2945/6064926/06064992.pdf?tp=&arnumber=6064992&isnumber=6064926&ref=')
