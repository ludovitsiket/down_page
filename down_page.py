import urllib.request, sys, re, os, base64, difflib, requests, collections

def check_correct_url(url):
    if "http" not in url:
        url = "http://"+url
    return url

def help_syntax():
    print("""Syntax (GNU/Linux, macOS) : python down_page.py www.name_of_page.com local_directory_to_download """)
    print("""Syntax (Windows)          : python.exe down_page.py www.name_of_page.com local_directory_to_download """)
    print("""Skript vyzaduje nainstalovany python 3.x""")

def make_aimed_directory(directory):
    try:
        os.mkdir(directory)
    except:
        print("Nepodarilo sa vytvorit pozadovany adresar pre stiahnutie web stranky.")
        sys.exit()
         
def download_web_page_data(url):
    try:
        content = requests.get(url)
        content.encoding = 'utf-8'
        data = content.text
        return data
    except:
        print("Nie je mozne nacitat obsah web stranky.")
        sys.exit()

def save_web_page_content(data, downloaded_file):
    try:
        print("Stahujem web stranku.")
        with open(downloaded_file,"w") as local_page:
            local_page.write(data)
        print("Web stranka stiahnuta.")
        return local_page
    except:
        print("Vyskytla sa chyba pri stahovani web stranky.")
        sys.exit()

def compare_web_page_content(url,destination):
    print("Web stranka uz je stiahnuta. Porovnavam jej obsah s aktualnou online verziou. Cakajte prosim.")
    directory = os.path.dirname(destination)
    actual_content = download_web_page_data(url)
    with open(destination, "r") as local:
        data = local.read()  
    difference = difflib.ndiff(actual_content, data) 
    difference = (''.join(difference))
    difference = difference.replace(' ','')
    if (('$Date') or ('<script>') or ('getElements')) in difference:
        print("Obsah stiahnutej web stranky a jej online verzia sa zhoduju.")
    else:
        print("Doslo k zmene na web stranke.")
        save_web_page_content(actual_content, destination)
        download_images_from_web_page(directory, destination, url)

def find_images_on_page(data):  
    try:
        img = re.findall('img .*?src="(.*?)"',data)
        return img
    except:
        print("Nepodarilo sa najst obrazky na zadanej web stranke.")
        sys.exit()

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

def download_images_from_web_page(directory, data_from_web_page,url): 
    try:
        images = find_images_on_page(data_from_web_page)
        local_file,remote_file = stored_data(directory)
        print("Stahujem obrazky. Cakajte prosim.")
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
        print("Stahovanie obrazkov dokoncene.")
    except :
        print("Nedefinovana chyba pri stahovani obrazkov.")

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

def edit_page_for_offline_reading(text_str, local_url, remote_url):
    with open(text_str, 'r') as source_file:
        data = source_file.read()
        images = find_images_on_page(data)
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
            data = data.replace(key, value)  # k remote urls pridava https:// = chyba(?) 
        new_file.write(data)
    return new_file

def main():
    try:
        if len(sys.argv) > 3:
            sys.exit()
        else:
            directory_to_download=sys.argv[2]
            local_web_page="page.html"
            local_html = os.path.join(directory_to_download, local_web_page)
            web_page_url=check_correct_url(sys.argv[1])
            directory_presence = os.path.isdir(directory_to_download)
            local_url, remote_url = stored_data(directory_to_download)
            if directory_presence is not True:
                make_aimed_directory(directory_to_download)
                data_from_web_page = download_web_page_data(web_page_url)
                save_web_page_content(data_from_web_page, local_html)
                download_images_from_web_page(directory_to_download, data_from_web_page,web_page_url)
                local_url, remote_url = get_and_change_data_in_files(local_url, remote_url)
                edit_page_for_offline_reading(local_html, local_url, remote_url)
            else:
                local_img_list, remote_img_list = change_data_in_memory(local_url, remote_url) 
                edit_page_for_comparing(local_html, local_img_list, remote_img_list) 
                compare_web_page_content(web_page_url, local_html)
                edit_page_for_comparing(local_html, remote_img_list, local_img_list)
    except:
           help_syntax()

main()
