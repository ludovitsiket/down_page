import urllib.request, sys, re, os, base64, difflib, requests, collections

def main():
    if True:
        directory_to_download=sys.argv[2]
        local_web_page="page.html"
        local_html = os.path.join(directory_to_download, local_web_page)
        web_page_url=check_correct_url(sys.argv[1])
        directory_presence = os.path.isdir(directory_to_download)
        if directory_presence is not True:
            make_aimed_directory(directory_to_download)
            data_from_web_page = download_web_page_data(web_page_url)
            save_web_page_content(data_from_web_page, local_web_page,directory_to_download)
            download_images_from_web_page(directory_to_download, data_from_web_page,web_page_url)
            edit_page_for_offline_reading(local_web_page, directory_to_download)
        else:
            compare_web_page_content(web_page_url,directory_to_download,local_web_page)
    else:
           help_syntax()

def check_correct_url(url):
    if "http" not in url:
        url = "http://"+url
    return url

def help_syntax():
    print("""Syntax (GNU/Linux, macOS) : python down_page.py http://www.name_of_page.com local_directory_to_download """)
    print("""Syntax (Windows)         : python.exe down_page.py http://www.name_of_page.com local_directory_to_download """)
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

def save_web_page_content(data, destination, directory):
    try:
        print("Stahujem web stranku.")
        downloaded_file = os.path.join(directory,destination)
        with open(downloaded_file,"w") as local_page:
            local_page.write(data)
        print("Web stranka stiahnuta.")
        return local_page
    except:
        print("Vyskytla sa chyba pri stahovani web stranky.")
        sys.exit()

def compare_web_page_content(url,directory,destination):
    try:
        print("Web stranka uz je stiahnuta. Porovnavam obsah web stranky s aktualnou online verziou.")
        actual_content = download_web_page_data(url)
        local_content = os.path.join(directory, destination)
        with open(local_content, "r") as local:
            data = local.read()
        difference = difflib.context_diff(actual_content.splitlines(), data.splitlines())
        difference = (''.join(difference))
        if not difference:
            print("Ziadne zmeny. Obsah stiahnutej web stranky a jej online verzia sa zhoduju.")
        else:
            print("Doslo k zmene na web stranke.")
            if "img" in difference:
                print("Zmena obrazku.")
            else:
                print("Zmena obsahu.")
            save_web_page_content(data, destination, directory)
            download_images_from_web_page(directory,actual_content,url)
    except:
        print("Nepodarilo sa porovnat obsah stiahnutej web stranky s online verziou.")
        sys.exit()

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
    try:
        name = join_path(directory, picture).replace("/","")
        name = os.path.join(directory, name)
        return name
    except:
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
        hidden_file,origin_file = stored_data(directory)
        print("Stahujem obrazky. Cakajte prosim.")
        with open(hidden_file, 'w') as hidden:
            with open(origin_file, 'w') as origin:
                for image in images:
                    image = check_picture_url(url, image)
                    picture_name=create_file_name(directory, image)
                    hidden.write(picture_name + '\n')
                    origin.write(image + '\n')
                    try:
                        if "base64" in image:
                            base64_picture_download(image, picture_name)
                        else:
                            urllib.request.urlretrieve(image, picture_name)
                    except (ValueError, urllib.error.URLError):
                        pass
        print("Stahovanie obrazkov dokoncene.")
        format_input_file(hidden_file)
    except :
        print("Nedefinovana chyba pri stahovani obrazkov.")

def format_input_file(local_file):
    print('Formatovanie lokalnych url adries obrazkov.')
    try:
        read_and_cut_data(local_file)
        print('Formatovanie dokoncene.')
    except:
        print('Formatovanie url adries obrazkov zlyhalo.')

def read_and_cut_data(data):
    cut_string = []
    with open(data, 'r') as data_file:
        for line in data_file:
            content = data_file.readline()
            cut_string.append(content)
    with open(data, 'w') as data_file:
        for line in cut_string:
            line = os.path.basename(line)
            data_file.write(line)
    return data_file

def stored_data(directory):
    file1 = os.path.join(directory, ".local_url_file")
    file2 = os.path.join(directory, ".remote_url_file")
    return (file1, file2)

def edit_page_for_offline_reading(text_str, directory):
    local_url, remote_url = stored_data(directory)
    text_str = os.path.join(directory, text_str)
    get_and_change_data_in_files(local_url, remote_url)
    with open(text_str, 'r') as source_file:
        data = source_file.read()
        images = find_images_on_page(data)
        new_img_urls = find_and_replace_data(remote_url)
        dictionary = collections.OrderedDict(zip(images, new_img_urls))

def find_and_replace_data(remote_url):
    with open(remote_url, 'r') as new_img_urls:
        new_img = new_img_urls.readlines()
    return new_img

def get_and_change_data_in_files(file1, file2):
    delta, data1, data2 = count_difference(file1, file2)
    if delta == 0:
        pass
    else:
        if len(data1) < len(data2):
            adding_blank_lines(file1, delta)
        else:
            adding_blank_lines(file2, delta)
    dictionary = collections.OrderedDict(zip(data1, data2))
    inverted_dict = collections.OrderedDict(zip(dictionary.values(), dictionary.keys()))
    result1, result2 = change_data_between_files(inverted_dict)
    write_data_per_line(file1, result1)
    write_data_per_line(file2, result2)
    print('Hotovo.')

def count_difference(file1, file2):
    with open(file1, 'r') as subor1:
        data1 = subor1.readlines()
    with open(file2, 'r') as subor2:
        data2 = subor2.readlines()
    difference = abs(len(data1)-len(data2))
    return (difference, data1, data2)

def adding_blank_lines(short_file, delta):
    with open(short_file, 'a+') as result_file:
        blank_lines = abs(delta)
        result_file.write(blank_lines *'\n')
    return result_file

def change_data_between_files(data):
    value1 = list(data.keys())
    value2 = list(data.values())
    return (value1, value2)

def write_data_per_line(aimed_file, data):
    with open(aimed_file, 'w') as subor:
        for line in data:
            subor.write(line)
    return subor

main()
