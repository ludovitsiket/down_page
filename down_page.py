import urllib.request, sys, re, os, base64, difflib, requests

def main():
    if True:
        directory_to_download=sys.argv[2]
        local_web_page="page.html"
        local_html = os.path.join(directory_to_download, local_web_page)
        web_page_url=check_correct_url(sys.argv[1])
        if os.path.isdir(directory_to_download) is not True:
            make_directory_for_download(directory_to_download)
            data_from_web_page = download_web_page_data(web_page_url)
            write_web_page_content_to_local_file(data_from_web_page, local_web_page,directory_to_download)
            download_images_from_web_page(directory_to_download, data_from_web_page,web_page_url)
            change_local_html(local_html,directory_to_download)
        else:
            compare_web_page_content(web_page_url,directory_to_download,local_web_page)
    else:
           help_syntax()

def check_correct_url(url):
    if "http" not in url:
        url = "http://"+url
    return url

def help_syntax():
    print("""Syntax (GNU/Linux, OS X) : python down_page.py http://www.name_of_page.com local_directory_to_download """)
    print("""Syntax (Windows)         : python.exe down_page.py http://www.name_of_page.com local_directory_to_download """)
    print("""Skript vyzaduje nainstalovany python 3.x""")

def make_directory_for_download(directory):
    try:
        os.mkdir(directory)
    except:
        print("Nepodarilo sa vytvorit pozadovany adresar pre stiahnutie web stranky.")
        sys.exit()
         
def download_web_page_data(url):
    try:
        r=requests.get(url)
        r.encoding = 'utf-8'
        data = r.text
        return data
    except:
        print("Nie je mozne nacitat obsah web stranky.")
        sys.exit()

def write_web_page_content_to_local_file(data, destination, directory):
    try:
        print("Stahujem web stranku.")
        downloaded_file=os.path.join(directory,destination)
        with open(downloaded_file,"w") as local_file:
            local_file.write(data)
        print("Web stranka stiahnuta.")
        return local_file
    except:
        print("Vyskytla sa chyba pri stahovani web stranky.")
        sys.exit()

def compare_web_page_content(url,directory,destination):
    try:
        print("Web stranka uz je stiahnuta. Porovnavam obsah web stranky s aktualnou online verziou.")
        actual_content=download_web_page_data(url)
        local_content=os.path.join(directory, destination)
        with open(local_content, "r") as local:
            data=local.read()
        diff = difflib.context_diff(actual_content.splitlines(), data.splitlines())
        diff = (''.join(diff))
        if not diff:
            print("Ziadne zmeny. Obsah stiahnutej web stranky a jej online verzia sa zhoduju.")
        else:
            print("Doslo k zmene na web stranke.")
            if "img" in diff:
                print("Zmena obrazku.")
            else:
                print("Zmena obsahu.")
            write_web_page_content_to_local_file(data, destination, directory)
            download_images_from_web_page(directory,actual_content,url)
    except:
        print("Nepodarilo sa porovnat obsah stiahnutej web stranky s online verziou.")
        sys.exit()

def find_images_on_page(data):
    try:
        img=re.findall('img .*?src="(.*?)"',data)
        return img
    except:
        print("Nepodarilo sa najst obrazky na zadanej web stranke.")
        sys.exit()

def join_path(directory, output_file):
    path=os.path.normpath(output_file)
    return os.path.join(directory,output_file)

def create_file_name(directory, picture):
    name=join_path(directory, picture).replace("/","")
    name=os.path.join(directory, name)
    return name

def check_picture_url(url, picture):
    if "http" in picture:
        picture=picture
    else:
        picture=(url+picture)
    return picture

def base64_picture_download(picture_url, local_picture):
    picture_read=urllib.request.urlopen(picture_url).read()
    picture_64_encode = base64.encodestring(picture_read)
    picture_64_decode = base64.decodestring(picture_64_encode)
    with open(local_picture, 'wb') as picture_result:
        picture_result.write(picture_64_decode)

def download_images_from_web_page(directory, data_from_web_page,url): 
    try:
        images=find_images_on_page(data_from_web_page)
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
    except :
        print("Nedefinovana chyba pri stahovani obrazkov.")

def stored_data(directory):
    file1 = os.path.join(directory, ".local_url_file")
    file2 = os.path.join(directory, ".remote_url_file")
    return (file1, file2)

def change_local_html(html_file, directory):
    input_file,output_file = stored_data(directory)
    with open(input_file, 'r') as input_data:
        data_to_local_page = input_data.readlines()
        with open(output_file, 'r') as output_data:
            data_from_local_page = output_data.readlines()
            with open(html_file, 'r') as result:
                print ('Upravujem stiahnutu web stranku pre offline citanie.')
                replaced_urls = replacing(result.read(), data_from_local_page, data_to_local_page)
                with open(html_file, 'w') as result:
                    result.write(replaced_urls)
          
def replacing(text_str, remote_url, local_url):
    stripped_remote_url = remote_url[:]
    stripped_local_url = local_url[:]
    if len(remote_url) == len(local_url):
        for img_urls in zip(stripped_remote_url, stripped_local_url):
            stripped_local_url = os.path.basename(str(stripped_local_url))
            print(stripped_local_url)
            text_str = text_str.replace(img_urls[0][:-1], img_urls[1][:-1])
    return text_str
          
def replacing_back(html_file, remote_url, local_url):
    return

main()
