import collections
import os
import sys
import urllib.request
from time import localtime, strftime
from re import findall
from base64 import b64encode, b64decode
import requests


class Log():
    def __init__(self, error):
        self.error = error

    def check_correct_url(url):
        if "http" not in url:
            return ("http://" + url)

    def write_log(error, log_file):
        print(error)
        Log.log(log_file)

    def log(value):
        with open(value, "a+") as log:
            x = strftime("%Y-%m-%d %H:%M:%S", localtime())
            log.write("[  " + x + "  ]" + "  :" + "  " +
                      str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + '\n')


def help_syntax():
    print('Script need python 3.x')
    print('Syntax (GNU/Linux, macOS) : python3 down_page.py -f')
    print('Syntax (Windows): python.exe down_page.py -f')
    print('Without parameter -f is posible using one url adress')


def make_dir(directory, log):
    try:
        os.mkdir(directory)
    except Exception as e:
        Log.write_log(e, log)


def download_data(url, log):
    try:
        content = requests.get(url)
        content.encoding = 'utf-8'
        return content.text
    except Exception as e:
        Log.write_log(e, log)


def save_content(data, content, log):
    try:
        with open(content, "w") as local:
            local.write(data)
        return local
    except Exception as e:
        Log.write_log(e, log)


def check_for_changes(dest, temp):
    diff = []
    with open(dest, "r") as local, open(temp, "r") as actual:
        for local_line, temp_line in zip(local, actual):
            if local_line != temp_line:
                if '<script' in temp_line or '</script>' in temp_line:
                    pass
                else:
                    diff.append(temp_line)
    return diff


def compare_content(url, dest, temp, log):
    print("Web page is downloaded. Comparing with actual online version.")
    save_content(download_data(url, log), temp, log)
    if len(check_for_changes(dest, temp)) != 0:
        print('Offline web page is old.\nDownloading actual version.')
        save_content(download_data(url, log), dest, log)
    else:
        print('Without changes.')


def find_images(data, log):
    try:
        return findall('img .*?src="(.*?)"', data)
    except Exception as e:
        Log.write_log(e, log)


def join_path(directory, output_file):
    return os.path.join(directory, output_file)


def create_file_name(directory, pic):
    if True:
        return os.path.join(
            directory,
            join_path(
                directory,
                pic).replace(
                "/",
                "")).replace(
            ":",
            "")


def check_picture_url(url, pic):
    if "http" not in pic:
        return (url + pic)


def base64_pic_down(url, local_picture):
    pic_64_encode = b64encode(urllib.request.urlopen(url).read())
    with open(local_picture, 'wb') as picture:
        picture.write(b64decode(pic_64_encode))


def download_local(local_file, images, url, directory):
    with open(local_file, 'w') as local_urls:
        for image in images:
            image = check_picture_url(url, image)
            picture_name = create_file_name(directory, image)
            picture_name = os.path.basename(picture_name)
            local_urls.write(picture_name + '\n')


def download_remote(remote_file, images):
    with open(remote_file, 'w') as remote_urls:
        for image in images:
            remote_urls.write(image + '\n')


def check_b64(image, pic_name):
    try:
        if "base64" in image:
            base64_pic_down(image, pic_name)
        else:
            urllib.request.urlretrieve(image, pic_name)
    except (ValueError, urllib.error.URLError):
        pass


def download_images(directory, data, url, log):
    try:
        images = find_images(data, log)
        local_file, remote_file = stored_data(directory)
        download_local(local_file, images, url, directory)
        download_remote(remote_file, images)
        for image in images:
            image = check_picture_url(url, image)
            check_b64(image, create_file_name(directory, image))
    except Exception as e:
        Log.write_log(e, log)


def stored_data(directory):
    return os.path.join(
        directory, ".local_url_file"), os.path.join(
        directory, ".remote_url_file")


def read_data(file1, file2):
    with open(file1, 'r') as f_1, open(file2, 'r') as f_2:
        data1 = f_1.readlines()
        data2 = f_2.readlines()
    return data1, data2


def change_data_between_files(data):
    return list(data.keys()), list(data.values())


def write_data_per_line(some_file, data):
    with open(some_file, 'w') as f:
        for line in data:
            f.write(line)
    return f


def change_files_data(file1, file2):
    result1, result2 = change_data(file1, file2)
    write_data_per_line(file1, result1)
    write_data_per_line(file2, result2)
    return file1, file2


def change_data(file1, file2):
    data1, data2 = read_data(file1, file2)
    dic = collections.OrderedDict(zip(data1, data2))
    new = collections.OrderedDict(zip(dic.values(), dic.keys()))
    result1, result2 = change_data_between_files(new)
    return result1, result2


def find_and_replace_data(remote_url):
    with open(remote_url, 'r') as url:
        return url.readlines()


def offline_page(text_str, remote_url, log_file):
    with open(text_str, 'r') as f:
        data = f.read()
        new_img_urls = find_and_replace_data(remote_url)
        dic = collections.OrderedDict(
            zip(find_images(data, log_file), new_img_urls))
        for key, value in dic.items():
            data = data.replace(key, value)
    with open(text_str, 'w') as new_file:
        return new_file.write(data)


def comparing_content(text_str, local_data, remote_data):
    with open(text_str, 'r') as f:
        data = f.read()
    dictionary = collections.OrderedDict(zip(local_data, remote_data))
    with open(text_str, 'w') as new_file:
        for key, value in dictionary.items():
            data = data.replace(key, value)
        return new_file.write(data)


def formated_url(url):
    http = len('http:')
    www = len('www')
    return url.replace('/', '')[http:][www:].replace('.', '', 1)


def count_lines(file_name):
    with open(file_name) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def read_urls(some_file, number, result):
    i = 0
    with open(some_file, 'r') as f:
        while i < number:
            result.append(f.readline().replace('\n', ''))
            i += 1
    return result


def url_from_file(some_file):
    address = []
    return read_urls(some_file, count_lines(some_file), address)


def files():
    file_1 = 'log_down_page.txt'
    file_2 = 'urls.txt'
    file_3 = "page.html"
    file_4 = ".temp.html"
    return file_1, file_2, file_3, file_4


def argument_control():
    if len(sys.argv) != 2:
        help_syntax()
        sys.exit()
    else:
        addr = []
        log_file, urls_file, local_web_page, temporary_web_page = files()
        if sys.argv[1] == '-f':
            addr = url_from_file(urls_file)
        else:
            addr.append(sys.argv[1])
    return log_file, urls_file, local_web_page, temporary_web_page, addr


def save_page(url, log, l_html, directory, l_url, r_url, item):
    try:
        print("Downloading web page", item)
        save_content(download_data(url, log), l_html, log)
        download_images(directory, download_data(url, log), url, log)
        l_url, remote_url = change_files_data(l_url, r_url)
        offline_page(l_html, r_url, log)
    except FileNotFoundError as e:
        print(e)


def compare(l_url, r_url, web_page_url, l_html, tmp, log):
    l_img_list, r_img_list = change_data(l_url, r_url)
    comparing_content(l_html, l_img_list, r_img_list)
    compare_content(web_page_url, l_html, tmp, log)
    comparing_content(l_html, r_img_list, l_img_list)


def main():
    log, urls_file, l_page, tmp, addr = argument_control()
    for item in addr:
        url = Log.check_correct_url(item)
        directory = formated_url(Log.check_correct_url(item))
        l_html = os.path.join(directory, l_page)
        temp_html = os.path.join(directory, tmp)
        dir_exist = os.path.isdir(directory)
        l_url, r_url = stored_data(directory)
        if dir_exist is not True:
            make_dir(directory, log)
            save_page(url, log, l_html, directory, l_url, r_url, item)
        else:
            compare(l_url, r_url, url, l_html, temp_html, log)
        print('Finish.')


main()
