import urllib.request, sys, re, os, base64, requests, collections
from time import localtime, strftime 

def check_correct_url(url):
    if "http" not in url:
        url = "http://"+url
    return url

def help_syntax():
    print('Skript vyzaduje nainstalovany python 3.x')
    print('Skript si url adresy nacita zo suboru. Kazda adresa musi byt na samostatnom riadku.')
    print('Syntax (GNU/Linux, macOS) : python down_page.py -f')
    print('Syntax (Windows)          : python.exe down_page.py -f')
    print('Bez parametru -f sa ako parameter pouzije 1 url adresa ktora sa ma stiahnut.')
    print('Syntax (GNU/Linux, macOS) : python down_page.py www.web_page.com')
    print('Syntax (Windows)          : python.exe down_page.py www.web_page.com')

def write_to_log(error, log_file):
    print(error)
    log(log_file)

def log(log_file):
    with open(log_file, "a+") as log:
        formated_date_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        log.write( "[  " + formated_date_time + "  ]" + "  :" + "  " + str(sys.exc_info()[0])+ str(sys.exc_info()[1]) + '\n' )

def make_aimed_directory(directory,log_file):
    try:
        os.mkdir(directory)
    except Exception as e:
        write_to_log(e, log_file)
         
def download_web_page_data(url,log_file):
    try:
        content = requests.get(url)
        content.encoding = 'utf-8'
        data = content.text
        return data
    except Exception as e:
        write_to_log(e, log_file)

def save_web_page_content(data, downloaded_file,log_file):
    try:
        with open(downloaded_file,"w") as local_page:
            local_page.write(data)
        return local_page
    except Exception as e:
        write_to_log(e, log_file)

def check_for_changes(destination, temporary_html):
    diff = []
    with open(destination, "r") as local, open(temporary_html, "r") as actual:
        for local_line, temp_line in zip(local, actual):
            if local_line != temp_line:
                if '<script' in temp_line or '</script>' in temp_line:
                    pass
                else:
                    diff.append(temp_line)
    return diff
        
def compare_web_page_content(url,destination,temporary_html,log_file):
    print("Web stranka uz je stiahnuta. Porovnavam jej obsah s aktualnou online verziou. Cakajte prosim.")
    directory = os.path.dirname(destination)
    actual_content = download_web_page_data(url,log_file)
    save_web_page_content(actual_content,temporary_html,log_file)
    diff = check_for_changes(destination, temporary_html)
    if len(diff) != 0:
        print('Doslo k zmenam na web stranke.\nBude stiahnuta jej aktualna verzia.')
        save_web_page_content(actual_content,destination,log_file)
    else:
        print('Ziadna zmena.')

def find_images_on_page(data,log_file):  
    try:
        img = re.findall('img .*?src="(.*?)"',data)
        return img
    except Exception as e:
        write_to_log(e, log_file)

def join_path(directory, output_file):
    path = os.path.normpath(output_file)
    return os.path.join(directory,output_file)

def create_file_name(directory, picture):
    if True:
        name = join_path(directory, picture).replace("/","")
        name = os.path.join(directory, name)
        name = name.replace(":","")
        return name
    else:
        print('Nie je mozne vytvorit meno obrazka.')

def check_picture_url(url, picture):
    if "http" in picture:
        picture = picture
    else:
        picture = (url+picture)
    return picture

def base64_picture_download(picture_url, local_picture):
    picture_read = urllib.request.urlopen(picture_url).read()
    picture_64_encode = base64.encodestring(picture_read)
    picture_64_decode = base64.decodestring(picture_64_encode)
    with open(local_picture, 'wb') as picture_result:
        picture_result.write(picture_64_decode)

def download_images_from_web_page(directory, data_from_web_page,url,log_file): 
    try:
        images = find_images_on_page(data_from_web_page,log_file)
        local_file,remote_file = stored_data(directory)
        with open(local_file, 'w') as local_urls:
            for image in images:
                image = check_picture_url(url, image)
                picture_name = create_file_name(directory, image)
                picture_name = os.path.basename(picture_name)
                local_urls.write(picture_name + '\n')
        with open(remote_file, 'w') as remote_urls:
            for image in images:
                remote_urls.write(image + '\n')
        for image in images:
            image = check_picture_url(url, image)
            picture_name = create_file_name(directory, image)
            try:
                if "base64" in image:
                    base64_picture_download(image, picture_name)
                else:
                    urllib.request.urlretrieve(image, picture_name)
            except (ValueError, urllib.error.URLError):
                pass
    except Exception as e:
        write_to_log(e, log_file)

def stored_data(directory):
    file1 = os.path.join(directory, ".local_url_file")
    file2 = os.path.join(directory, ".remote_url_file")
    return (file1, file2)

def read_data(file1, file2):
    with open(file1, 'r') as subor1, open(file2, 'r') as subor2:
        data1 = subor1.readlines()
        data2 = subor2.readlines()
    return (data1, data2)

def change_data_between_files(data):
    value1 = list(data.keys())
    value2 = list(data.values())
    return (value1, value2)

def write_data_per_line(aimed_file, data):
    with open(aimed_file, 'w') as subor:
        for line in data:
            subor.write(line)
    return subor

def get_and_change_data_in_files(file1, file2):
    result1, result2 = change_data_in_memory(file1, file2)
    write_data_per_line(file1, result1)
    write_data_per_line(file2, result2)
    return (file1, file2)

def change_data_in_memory(file1, file2):
    data1, data2 = read_data(file1, file2)
    dictionary = collections.OrderedDict(zip(data1, data2))
    inverted_dict = collections.OrderedDict(zip(dictionary.values(), dictionary.keys()))
    result1, result2 = change_data_between_files(inverted_dict)
    return (result1, result2)

def find_and_replace_data(remote_url):
    with open(remote_url, 'r') as new_img_urls:
        new_img = new_img_urls.readlines()
    return new_img

def edit_page_for_offline_reading(text_str, local_url, remote_url,log_file):
    with open(text_str, 'r') as source_file:
        data = source_file.read()
        images = find_images_on_page(data,log_file)
        new_img_urls = find_and_replace_data(remote_url)
        dictionary = collections.OrderedDict(zip(images, new_img_urls))
        for key,value in dictionary.items():
            data = data.replace(key, value) 
    with open(text_str, 'w') as new_file:
        new_file.write(data)
    return new_file

def edit_page_for_comparing(text_str, local_data, remote_data):
    with open(text_str, 'r') as source_file:
        data = source_file.read()
    images = local_data
    new_img_urls = remote_data
    dictionary = collections.OrderedDict(zip(images, new_img_urls))
    with open(text_str, 'w') as new_file:
        for key,value in dictionary.items():
            data = data.replace(key, value) 
        new_file.write(data)
    return new_file

def formated_url(url):
    part = url.replace('/','')
    remove_http = 'http:'
    remove_www = 'www'
    http = len(remove_http)
    www = len(remove_www)
    part2 = part[http:]
    formated_url = part2[www:].replace('.','', 1)
    return formated_url

def count_lines(file_name):
    with open(file_name) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def read_urls_from_file(urls_file):
    addr = []
    i = 0
    number_of_lines = count_lines(urls_file)
    with open(urls_file, 'r') as urls:
        while i < number_of_lines:
            address = urls.readline()
            address = address.replace('\n','')
            addr.append(address)
            i += 1
    return addr

def main():
    if len(sys.argv) != 2:
        help_syntax()
        sys.exit()
    else:
        addr = []
        log_file = 'log_down_page.txt'
        urls_file = 'urls.txt'
        if sys.argv[1] == '-f':
            addr = read_urls_from_file(urls_file)
        else:
            addr.append(sys.argv[1])
        for item in addr:
            local_web_page="page.html"
            web_page_url=check_correct_url(item)
            directory_to_download = formated_url(web_page_url)
            local_html = os.path.join(directory_to_download, local_web_page)
            temporary_web_page=".temp.html"
            temporary_html = os.path.join(directory_to_download, temporary_web_page)
            directory_presence = os.path.isdir(directory_to_download)
            local_url, remote_url = stored_data(directory_to_download)
            if directory_presence is not True:
                make_aimed_directory(directory_to_download,log_file)
                data_from_web_page = download_web_page_data(web_page_url,log_file)
                print("Stahujem web stranku",item)
                save_web_page_content(data_from_web_page, local_html,log_file)
                print("Stahujem obrazky. Cakajte prosim.")
                download_images_from_web_page(directory_to_download, data_from_web_page,web_page_url,log_file)
                local_url, remote_url = get_and_change_data_in_files(local_url, remote_url)
                edit_page_for_offline_reading(local_html, local_url, remote_url,log_file)
                print('Hotovo.')
            else:
                local_img_list, remote_img_list = change_data_in_memory(local_url, remote_url) 
                edit_page_for_comparing(local_html, local_img_list, remote_img_list) 
                compare_web_page_content(web_page_url, local_html,temporary_html,log_file)
                edit_page_for_comparing(local_html, remote_img_list, local_img_list)
                print('Hotovo.')

main()
