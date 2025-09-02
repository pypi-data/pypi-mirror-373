from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from seleniumbase import Driver
from uiautomator import Device
from phonenumbers import geocoder
from pydub import AudioSegment
from datetime import datetime, timedelta
import re, io,time, random, requests,string,names,subprocess,os,pycountry,phonenumbers,base64,threading,websocket,zipfile
import numpy as np
from PIL import Image
import speech_recognition as sr
from clselove import link_sms, firebaseio_link
from bs4 import BeautifulSoup  
import xml.etree.ElementTree as ET

#twine upload dist/*
#__init__.py
#rm -rf dist build *.egg-info setup.py
#python3 setup.py sdist bdist_wheel
#pip install --upgrade clselove
# termux-change-repo && pkg install x11-repo && pkg install opencv-python
#yes | pkg update -y && yes | pkg upgrade -y && pkg install python python-pip x11-repo tmate android-tools libjpeg-turbo libpng zlib tur-repo tesseract opencv-python chromium termux-api -y && pip install PyVirtualDisplay==3.0  pytesseract  setuptools    beautifulsoup4 2captcha-python  clselove

def auto(pan,d,ip_address):
    kind, name = pan.split("@")[0], pan.split("#")[0].split("@")[-1]
    name_se = pan.split("#")[-1] if "#" in pan else None
    def b():
        clickable_elements = d(clickable=True)
        clickable_elements[int(name)].click()
    action_map = {
        "cl_te": lambda: d(text=name).click(),"cl_cl": lambda: d(className=name).click(),"cl_id": lambda: d(resourceId=name).click(),"cl_de": lambda: d(description=name).click(),
        "cl_tee": lambda: d(text=name),"cl_cll": lambda: d(className=name),"cl_idd": lambda: d(resourceId=name),"cl_dee": lambda: d(description=name),
        "se_te": lambda: d(text=name).set_text(name_se) if name_se else None,"se_cl": lambda: d(className=name).set_text(name_se) if name_se else None,"se_id": lambda: d(resourceId=name).set_text(name_se) if name_se else None,"se_de": lambda: d(description=name).set_text(name_se) if name_se else None,
        "cr_te": lambda: d(text=name).clear_text(),"cr_cl": lambda: d(className=name).clear_text(),"cr_id": lambda: d(resourceId=name).clear_text(),"cr_de": lambda: d(description=name).clear_text(),
        "sc_te": lambda: any(d(scrollable=True).scroll.forward() for _ in range(20)) if not d(text=name).exists else d(text=name).click(),"sc_cl": lambda: any(d(scrollable=True).scroll.forward() for _ in range(10)) if not d(className=name).exists else d(className=name).click(),"sc_id": lambda: any(d(scrollable=True).scroll.forward() for _ in range(10)) if not d(resourceId=name).exists else d(resourceId=name).click(),"sc_de": lambda: any(d(scrollable=True).scroll.forward() for _ in range(10)) if not d(description=name).exists else d(description=name).click(),
        "en": lambda: d.press('enter'),"ba": lambda: d.press.back(),"ti": lambda: time.sleep(int(name)),
        "cr": lambda: subprocess.run(f"adb -s {ip_address} shell pm clear {name}", shell=True, capture_output=True, text=True),
        "op": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n {name}", shell=True, capture_output=True, text=True),
        "st": lambda: subprocess.run(f"adb -s {ip_address} shell am force-stop {name}", shell=True, capture_output=True, text=True),
        "sw": lambda: subprocess.run(f"adb -s {ip_address} shell input swipe {name}",shell=True, capture_output=True, text=True),
        "inp": lambda: subprocess.run(f"adb -s {ip_address} shell input text '{name}' ", shell=True, capture_output=True, text=True),      
       "not": lambda: subprocess.run(f"adb -s {ip_address} shell cmd statusbar expand-notifications", shell=True, capture_output=True, text=True),
       "col": lambda:subprocess.run(f"adb -s {ip_address} shell cmd statusbar collapse", shell=True, capture_output=True, text=True),
       "get": lambda:subprocess.run(f"adb -s {ip_address} shell am start -a android.intent.action.VIEW -d '{name_se}' {name}", shell=True, capture_output=True, text=True),          
       "mv_fi": lambda:subprocess.run(f"su -c 'cp -rf {name} {name_se}'", shell=True, capture_output=True, text=True),          
       "ch_77": lambda:subprocess.run(f"su -c 'chmod -R 777 {name}'", shell=True, capture_output=True, text=True),                    
       "cr_chrome": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.android.chrome", shell=True, capture_output=True, text=True),
       "op_chrome": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.android.chrome/com.google.android.apps.chrome.Main", shell=True, capture_output=True, text=True),
       "cr_kiwi": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.kiwibrowser.browser", shell=True, capture_output=True, text=True),
       "op_kiwi": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.kiwibrowser.browser/com.google.android.apps.chrome.Main", shell=True, capture_output=True, text=True),
       "cr_shell": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.kiwibrowser.browser", shell=True, capture_output=True, text=True),
       "op_shell": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.kiwibrowser.browser/com.google.android.apps.chrome.Main", shell=True, capture_output=True, text=True),
       "cr_colab": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.kiwibrowser.browser", shell=True, capture_output=True, text=True),
       "op_colab": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.kiwibrowser.browser/com.google.android.apps.chrome.Main", shell=True, capture_output=True, text=True),         
       "cr_discord": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.discord", shell=True, capture_output=True, text=True),
       "op_discord": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.discord/com.discord.main.MainDefault", shell=True, capture_output=True, text=True),    
       "cr_tinder": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.tinder", shell=True, capture_output=True, text=True),
       "op_tinder": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.tinder/com.tinder.feature.auth.internal.activity.AuthStartActivity", shell=True, capture_output=True, text=True),       
       "cr_viber": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.viber.voip", shell=True, capture_output=True, text=True),
       "op_viber": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.viber.voip/com.viber.voip.WelcomeActivity", shell=True, capture_output=True, text=True),       
       "cr_uber": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.ubercab", shell=True, capture_output=True, text=True),
       "op_uber": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.ubercab/com.ubercab.presidio.app.core.root.RootActivity", shell=True, capture_output=True, text=True),    
       "cr_imo": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.imo.android.imoim", shell=True, capture_output=True, text=True),
       "op_imo": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.imo.android.imoim/com.imo.android.imoim.home.Home", shell=True, capture_output=True, text=True),            
       "cr_didi": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.didiglobal.passenger", shell=True, capture_output=True, text=True),
       "op_didi": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.didiglobal.passenger/com.didi.sdk.splash.SplashActivity", shell=True, capture_output=True, text=True),      
       "cr_yango": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.yandex.yango", shell=True, capture_output=True, text=True),
       "op_yango": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.yandex.yango/ru.yandex.taxi.activity.MainActivity", shell=True, capture_output=True, text=True),      
       "cr_facebook_lite": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.facebook.lite", shell=True, capture_output=True, text=True),
       "op_facebook_lite": lambda: subprocess.run(f"adb -s {ip_address} shell am start -n com.facebook.lite/com.facebook.lite.MainActivity", shell=True, capture_output=True, text=True),             
       "cr_vk": lambda:subprocess.run(f"adb -s {ip_address} shell pm clear com.vkontakte.android", shell=True, capture_output=True, text=True),
       "op_vk": lambda: subprocess.run(f"adb -s {ip_address} shell monkey -p com.vkontakte.android -c android.intent.category.LAUNCHER 1", shell=True, capture_output=True, text=True),       
       "bo": lambda: b(),
           
            }
    action_map.get(kind, lambda: None)()
def get_text(res_id,text_body):
    
    root = ET.fromstring(text_body)
    for node in root.iter("node"):
        if node.attrib.get("text") == res_id:
            b = list(map(int, re.findall(r"\d+", node.attrib["bounds"])))
            return (b[0] + b[2]) // 2, (b[1] + b[3]) // 2
    return None, None
def get_id(res_id,text_body):
    
    root = ET.fromstring(text_body)
    for node in root.iter("node"):
        if node.attrib.get("resource-id") == res_id:
            b = list(map(int, re.findall(r"\d+", node.attrib["bounds"])))
            return (b[0] + b[2]) // 2, (b[1] + b[3]) // 2
    return None, None

def do_file(ip_address,d,username, folder, apk):
    check = False
    def a(date):
        auto(date,d,ip_address)    
    try:
        zipf, dst = f"/sdcard/{username}.zip", f"/sdcard/{folder}/{username}"
        if not os.path.exists(dst):
            print("no find", username)
            r = requests.get(f"{link_sms}/files/{folder}/{username}.zip", stream=True)
            if r.status_code != 200: exit(print(r.status_code, r.text))
            with open(zipf, "wb") as f:
                for chunk in r.iter_content(8192): f.write(chunk)
            with zipfile.ZipFile(zipf) as z: z.extractall(dst)
            os.remove(zipf)
            print("Done:", dst)
        a(f"cr_{folder}")
        os.system(f'su -c "cp -rf /sdcard/{folder}/{username}/* /data/user/0/{apk}/"')
        os.system(f'su -c "chmod -R 777 /data/user/0/{apk}"')
        a(f"op_{folder}")
        check = True
    except Exception as s:
        print(s)
    return check
def do_kiwi(ip_address,d,username, folder,start_apk,link):
    check = False
    def a(date):
        auto(date,d,ip_address)    
    try:
        zipf, dst = f"/sdcard/{username}.zip", f"/sdcard/{folder}/{username}"
        if not os.path.exists(dst):
            print("no find", username)
            r = requests.get(f"{link_sms}/files/{folder}/{username}.zip", stream=True)
            if r.status_code != 200: exit(print(r.status_code, r.text))
            with open(zipf, "wb") as f:
                for chunk in r.iter_content(8192): f.write(chunk)
            with zipfile.ZipFile(zipf) as z: z.extractall(dst)
            os.remove(zipf)
            print("Done:", dst)         
        subprocess.run(f"adb -s {ip_address} shell pm clear {start_apk}", shell=True, capture_output=True, text=True)
        time.sleep(1)
        os.system(f'su -c "cp -rf /sdcard/{folder}/{username} /data/user/0/{start_apk}/app_chrome"')
        time.sleep(1)
        os.system(f'su -c "chmod -R 777 /data/user/0/{start_apk}"')
        time.sleep(2)
        subprocess.run(f"adb -s {ip_address} shell am start -n {start_apk}/com.google.android.apps.chrome.Main", shell=True, capture_output=True, text=True)
        time.sleep(2)
        subprocess.run(f"adb -s {ip_address} shell am start -a android.intent.action.VIEW -d '{link}' com.kiwibrowser.browser", shell=True, capture_output=True, text=True)
        check = True
    except Exception as s:
        print(s)
    return check

def up_file(username,folder,apk):
    check = False
    try:        
        src, dst, zipf = f"/data/user/0/{apk}", f"/sdcard/{folder}/{username}", f"/sdcard/{username}.zip"
        os.system(f'su -c "cp -rf {src} {dst}"')
        with zipfile.ZipFile(zipf, 'w', zipfile.ZIP_DEFLATED) as z:
            [z.write(os.path.join(r,f), os.path.relpath(os.path.join(r,f), dst)) 
            for r,_,fs in os.walk(dst) for f in fs]
        r = requests.post(f"{link_sms}/upload/{folder}/{username}.zip", files={"file": open(zipf,'rb')})
        print(r.status_code, r.text)
        data_to_upload = {"file": username ,"path":folder}
        requests.patch(f'{link_sms}/{folder}_apk/{username}.json', json=data_to_upload, timeout=10)
        check = True
    except Exception as s:
        print(s)
    return check
def random_email_time(name,time_day,get_check,get_true):
    check = False
    date = None
    try:
        folders = []
        response_get = requests.get(f'{link_sms}/{name}.json')
        user_data = response_get.json()
        for key, value in user_data.items():
            saved_datetime = datetime(month=value["month"],day=value["day"],hour=value["hour"],minute=value["minute"],year=datetime.now().year)
            now = datetime.now()
            if now - saved_datetime >= timedelta(hours=time_day):
                if get_true in value[get_check]:
                    folders.append(key)
        username = random.choice(folders)        
        date = requests.get(f'{link_sms}/{name}/{username}.json').json()   
        data_to_upload = {"hour": now.hour,"minute": now.minute,"day": now.day,"month": now.month}
        requests.patch(f'{link_sms}/{name}/{username}.json', json=data_to_upload, timeout=10)
        check = True  
    except Exception as s:
        print(s)        
    return date,check,username
def get_text_2captcha(path, api_key="b595d3040f736c6e7a5108ee7745f83a"):
    cid = requests.post("http://2captcha.com/in.php",
        files={"file": open(path,"rb")}, data={"key": api_key,"method":"post"}).text.split("|")[1]
    for _ in range(20):
        time.sleep(5)
        r = requests.get("http://2captcha.com/res.php", params={"key": api_key,"action":"get","id": cid})
        if "OK|" in r.text: return r.text.split("|")[1]
    return None

def na_em(list_email):
    f_n = names.get_first_name().lower()
    l_n =names.get_last_name().lower()
    password = [*random.sample([random.choice(string.ascii_lowercase), random.choice(string.ascii_uppercase), random.choice(string.digits), random.choice('@#')], 3), *random.choices(string.ascii_letters + string.digits + '!@#$%', k=random.randint(5, 11))]; random.shuffle(password); password = ''.join(password)
    email = f"{f_n}{random.randint(10, 9999)}@{random.choice(list_email)}"
    random_month = ["January", "February", "March", "April", "May", "June","July", "August", "September", "October", "November", "December"]
    month1 = random.choice(random_month)
    day = random.randint(1, 31)
    year = random.randint(1980, 2006)
    month = random.randint(1, 12)
    return f_n, l_n, password, email,email.split("@")[0], month1,day,month,year
def cap_se(driver):
    try:
        stop_recaptcha = False
        hcaptcha = driver.execute_script("return document.evaluate(\"//iframe[@title='Main content of the hCaptcha challenge']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
        recaptcha = driver.execute_script("return document.evaluate(\"//iframe[@title='reCAPTCHA']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
        cloudflare = driver.execute_script("return document.evaluate(\"//iframe[@title='Widget containing a Cloudflare security challenge']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
        if cloudflare:
            print("cloudflare")
            driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[@title='Widget containing a Cloudflare security challenge']"))
            a("cl_xp@/html/body//div[1]/div/div[1]/div/label/input")
            time.sleep(5)
            a("en")
        if hcaptcha:
            print("hcaptcha")
            Widget_checkbox = driver.execute_script("return document.evaluate(\"//iframe[@title='Widget containing checkbox for hCaptcha security challenge']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
            if Widget_checkbox:
                driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[@title='Widget containing checkbox for hCaptcha security challenge']"))
                click_hcaptcha = driver.execute_script("""
                let el = document.evaluate("//div[@id='checkbox'][@tabindex='0']", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if (el) { el.click(); return true; } else { return false; }
                """)
                driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[@title='Main content of the hCaptcha challenge']"))
            #driver.switch_to.frame(driver.execute_script("for(let f of document.getElementsByTagName('iframe')){try{let d=f.contentWindow.document;if(d.querySelector('#prompt-text,[aria-label=\"Challenge Image 3\"]'))return f;}catch(e){}}return null;"))
            code_start1 = driver.execute_script("return document.evaluate(\"//*[@aria-label='Challenge Image 3']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
            code_start2 = driver.execute_script("return document.evaluate(\"//*[text()='Please answer the following question with a single word, number, or phrase.']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")            
            text_body = driver.find_element("tag name", "body").text
            
            if "Please answer the following question" in text_body or code_start2:
                print("number, or phrase")
                mesage = driver.find_element(By.ID, "prompt-text").text
                send_massage = f"Please answer the following question with a single word, number, or phrase {mesage} please send Final Answer only"
                API_KEY = "sk-1b8ccd5f12b74efa962335cac260aa95"
                response = requests.post("https://api.deepseek.com/v1/chat/completions", headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}, json={"model": "deepseek-chat", "store": True, "messages": [{"role": "user", "content": send_massage}]}).json()
                haiku = response["choices"][0]["message"]["content"]
                print(haiku)
                Verify = driver.execute_script("return document.evaluate(\"//div[@aria-label='Verify Answers']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                driver.find_element(By.CSS_SELECTOR, "[aria-label='Challenge Text Input']").send_keys(haiku)
                time.sleep(2)
                driver.find_element(By.CSS_SELECTOR, "[aria-label='Challenge Text Input']").send_keys(Keys.ENTER)
                if Verify:
                    print("Verify")
                    time.sleep(8)
            elif "Visual Challenge"  in text_body:
                print("Visual Challenge")
                driver.find_element(By.ID, "menu-info").click()
            elif code_start1:
                print("click Skip")
                driver.find_element(By.ID, "menu-info").click()
                #driver.find_element(By.CSS_SELECTOR, "[aria-label='Get information about hCaptcha and accessibility options.']").click()
                driver.find_element(By.ID, "text_challenge").click()
                time.sleep(3)
        elif recaptcha:
            print("recaptcha")
            
            time.sleep(3)
            captcha_frames = driver.find_elements(By.XPATH, ".//iframe[@title='reCAPTCHA']")
            for frame in captcha_frames:
                driver.switch_to.default_content()
                driver.switch_to.frame(frame)
                try:
                    anchor= driver.execute_script("return document.evaluate(\"//*[@id='recaptcha-anchor']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                    code_start1 = driver.execute_script("return document.evaluate(\"//*[@class='rc-audiochallenge-tdownload-link']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                    code_start2 = driver.execute_script("return document.evaluate(\"//*[text()='Try again later']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                    code_start3 = driver.execute_script("return document.evaluate(\"//*[@id='recaptcha-audio-button']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                    code_start4 = driver.execute_script("return document.evaluate(\"//*[@title='Get an audio challenge']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                    if code_start2:
                        print("try agagen code_start2")
                    elif anchor:
                        driver.find_element(By.ID, 'recaptcha-anchor').click()
                        break
                    elif code_start2 or code_start1 or code_start3 or  code_start4:
                        print("recaptcha-anchor")
                        break
                except:
                    print("s")
                    driver.set_window_size(1920, 1400)
            driver.switch_to.default_content()
            for _ in range(20):
                time.sleep(1)
                two_minutes = driver.execute_script("return document.evaluate(\".//iframe[@title='recaptcha challenge expires in two minutes']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                if two_minutes:
                    driver.switch_to.default_content()
                    driver.switch_to.frame(driver.find_element(By.XPATH, ".//iframe[@title='recaptcha challenge expires in two minutes']"))
                    code_start3 = driver.execute_script("return document.evaluate(\"//*[@id='recaptcha-audio-button']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                    code_start4 = driver.execute_script("return document.evaluate(\"//*[@title='Get an audio challenge']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                    if code_start3:
                        driver.find_element(By.ID, 'recaptcha-audio-button').click()
                    elif code_start4:
                        driver.find_element(By.XPATH, '//*[@title="Get an audio challenge"]').click()
                    else:
                        print("no audio")
                        break
                    for _ in range(15):
                        time.sleep(1)
                        code_start1 = driver.execute_script("return document.evaluate(\"//*[@class='rc-audiochallenge-tdownload-link']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                        code_start2 = driver.execute_script("return document.evaluate(\"//*[text()='Try again later']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null;")
                        if code_start1:
                            audio_link = driver.find_element(By.CLASS_NAME, 'rc-audiochallenge-tdownload-link')
                            audio_url = audio_link.get_attribute("href")
                            print(audio_url)
                            file_name = "audio.mp3"
                            response = requests.get(audio_url)
                            if response.status_code == 200:
                                with open(file_name, 'wb') as f:
                                    f.write(response.content)
                            src = "audio.mp3"
                            sound = AudioSegment.from_mp3(src)
                            sound.export("podcast.wav", format="wav")
                            file_path = os.path.join(os.getcwd(), "podcast.wav")
                            r = sr.Recognizer()
                            with sr.AudioFile(file_path) as source:
                                audio_text = r.record(source)
                            audio_text_code = r.recognize_google(audio_text)
                            driver.find_element(By.ID, 'audio-response').send_keys(audio_text_code)
                            time.sleep(3)
                            driver.find_element(By.ID, 'audio-response').send_keys(Keys.RETURN)
                            time.sleep(3)
                            break
                        elif code_start2:
                            print("try again")
                            stop_recaptcha = True
                            break


    except Exception as s:
        print("captions",s)
    driver.switch_to.default_content()
    return stop_recaptcha
def get_phone(name):
    response_get = requests.get(f'{name}.json')
    user_data = response_get.json()
    if not user_data:
        print('No phone found', name)
        return None, None, None, None
    first_key = random.choice(list(user_data.keys()))
    phone = user_data[first_key].strip()
    requests.delete(f'{name}/{phone}.json')
    parsed_number = phonenumbers.parse(f'+{phone}')
    country = pycountry.countries.get(alpha_2=phonenumbers.region_code_for_country_code(parsed_number.country_code))
    country_code, fn, co = parsed_number.country_code, country.name[0], country.name.split(",")[0] if country else (None, None)
    return phone, country_code, fn, co
def get_sms(name):
    response_get = requests.get(name)
    user_data = response_get.json()
    if user_data is None:
        print('no phone',name)
        stop_phone = True
    else:
        phone = random.choice(list(user_data.keys())).strip()
        first_key= user_data[phone]
        parsed_number = phonenumbers.parse(f'+{phone}')
        country = pycountry.countries.get(alpha_2=phonenumbers.region_code_for_country_code(parsed_number.country_code))
        country_code, fn, co = parsed_number.country_code, country.name[0], country.name.split(",")[0] if country else (None, None)
        return first_key,phone, country_code, fn, co

def scr(screenshot, driver):
    print((r := requests.post('https://0x0.st', files={'file': open(f"{screenshot}.png", 'rb')}, headers={'User-Agent': 'curl/7.68.0'})).text.strip()) if driver.save_screenshot(f"{screenshot}.png") else print("erro_screenshot")


def totel_temp(email):
    text_code = False
    error_tempmail =['mailto.plus','fexpost.com','fexbox.org','mailbox.in.ua','rover.info','chitthi.in','fextemp.com','any.pink','merepost.com']
    matched_error = next((err for err in error_tempmail if err in email), None)
    error_inboxes =['blondmail.com', 'chapsmail.com', 'clowmail.com', 'dropjar.com', 'fivermail.com', 'getairmail.com', 'getmule.com', 'gimpmail.com', 'givmail.com', 'guysmail.com', 'inboxbear.com', 'replyloop.com', 'spicysoda.com', 'tafmail.com', 'temptami.com', 'tupmail.com', 'vomoto.com']
    inboxes_error = next((err for err in error_inboxes if err in email), None)
    if matched_error:
        response_first = requests.get('https://tempmail.plus/api/mails', cookies={'email': email}, params={'email': email,'limit': '1','epin': ''}).json().get('first_id')
        text_code = requests.get(F'https://tempmail.plus/api/mails/{response_first}', cookies={'email': email}, params={'email': email,'limit': '20','epin': ''})
        return text_code
    elif inboxes_error:
        response_first = requests.get(f"https://inboxes.com/api/v2/inbox/{email}").json()['msgs'][0]["uid"]
        text_code = requests.get(f"https://inboxes.com/api/v2/message/{response_first}")
        return text_code
    elif 'gmail.com' in email:
        limit = 1
        response_get = requests.get(f'{link_sms}/api_gmail')
        user_data = response_get.json()
        if user_data is None:
            print('no api_gmail')
        else:
            for key, value in user_data.items():
                if value["gmail_api"] ==email:
                    API_KEY = value["get_api"]
                    GRANT_ID = value["grant_id"]
                    response = requests.get(f"https://api.us.nylas.com/v3/grants/{GRANT_ID}/messages", headers={"Authorization": f"Bearer {API_KEY}"}, params={"limit": limit})
                    data = response.json()
                    if "data" in data and data["data"]:
                        for i, msg in enumerate(data["data"], 1):
                            body_html = msg.get("body") or ""
                            soup = BeautifulSoup(body_html, "html.parser")
                            text_code = soup.get_text().strip() 
                            return text_code                       
                        
        
def opencv_geetest(slice_url, bg_url, big, smail, totel, driver, bg_el):
    try:
        import cv2
    except:
        os.system("pip3 install opencv-python")
        import cv2     
    piece = cv2.imdecode(np.frombuffer(slice_url, np.uint8), cv2.IMREAD_UNCHANGED)
    bg = cv2.imdecode(np.frombuffer(bg_url, np.uint8), cv2.IMREAD_UNCHANGED)
    if piece is None or bg is None: return False
    if piece.shape[2] == 4: piece = cv2.cvtColor(piece, cv2.COLOR_BGRA2BGR)
    piece = cv2.GaussianBlur(piece, (5,5), 0)
    bg = cv2.GaussianBlur(bg, (5,5), 0)
    res = cv2.matchTemplate(cv2.Canny(bg,100,200), cv2.Canny(piece,100,200), cv2.TM_CCOEFF_NORMED)
    x_raw = cv2.minMaxLoc(res)[3][0]
    shot = cv2.imdecode(np.frombuffer(bg_el.screenshot_as_png, np.uint8), 1)
    scale = shot.shape[1] / bg.shape[1]
    track_el = [el for el in driver.find_elements(By.CSS_SELECTOR, ".geetest_track") if el.is_displayed()][0]
    offset = track_el.location["x"] - bg_el.location["x"]
    dist = int(x_raw * scale - offset - piece.shape[1]//2 + totel)
    dist = max(min(dist, big), smail)
    return dist
def geetest(driver):
    try:
        slice_el = [el for el in driver.find_elements(By.CSS_SELECTOR, ".geetest_slice_bg") if el.is_displayed()][0]
        bg_el = [el for el in driver.find_elements(By.CSS_SELECTOR, ".geetest_bg") if el.is_displayed()][0]
        slice_url = requests.get(re.search(r'url\("(.*?)"\)', slice_el.get_attribute("style")).group(1), timeout=10).content
        bg_url = requests.get(re.search(r'url\("(.*?)"\)', bg_el.get_attribute("style")).group(1), timeout=10).content
        dist = opencv_geetest(slice_url, bg_url, 220, 30, 37, driver, bg_el)
        print("distance =", dist)
        slider = [el for el in driver.find_elements(By.CSS_SELECTOR, "[class*='geetest_btn']") if el.is_displayed()][0]
        act = ActionChains(driver)
        act.click_and_hold(slider).perform()
        moved = 0
        while moved < dist:
            step = random.randint(3, 7)
            if moved + step > dist: step = dist - moved
            act.move_by_offset(step, random.randint(-1,1)).perform()
            moved += step
            time.sleep(random.uniform(0.01, 0.04))
        time.sleep(0.2)
        act.release().perform()
        return True
    except Exception as e:
        print("geetest error:", e)
        return False
def sign(driver):
    canvas = driver.find_element(By.TAG_NAME, "canvas")
    location = canvas.location_once_scrolled_into_view
    size = canvas.size
    x_center = size['width'] // 2
    y_center = size['height'] // 2
    action = ActionChains(driver)
    action.move_to_element_with_offset(canvas, 5, 5)
    action.click_and_hold()
    for _ in range(30):
        dx = random.randint(-3, 3)
        dy = random.randint(-3, 3)
        action.move_by_offset(dx, dy)
        time.sleep(0.015) 
    action.release()
    action.perform()

def gpt_api(massage,file,api_model):
    try:
        import openai
    except:
        os.system("pip3 install openai")
        import openai   
  
    openai.api_key = "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"
    with open(file, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    response = openai.chat.completions.create(model=api_model,messages=[{"role": "user","content": [{"type": "text", "text": massage},{"type": "image_url","image_url": {"url": f"data:image/png;base64,{base64_image}"},},],}],max_tokens=10,)
    return response.choices[0].message.content
def cap_ph(file):
    with open(file, 'rb') as f:
        r = requests.post('http://2captcha.com/in.php', files={'file': f}, data={'key': "b595d3040f736c6e7a5108ee7745f83a", 'method': 'post'})
    if 'OK|' not in r.text: return None
    cid = r.text.split('|')[1]
    for _ in range(20):
        time.sleep(5)
        res = requests.get(f'http://2captcha.com/res.php?key=b595d3040f736c6e7a5108ee7745f83a&action=get&id={cid}').text
        if 'OK|' in res:
            t = res.split('|')[1]
            pairs = [t[i:i+2] for i in range(0, len(t)-(len(t)%2), 2)]
            return pairs ,max(pairs, key=int) 

def se(pan,driver):
    
    kind, name = pan.split("@")[0], pan.split("#")[0].split("@", 1)[1]
    name_se = pan.split("#")[-1] if "#" in pan else None
    action_map = {
       "cl_xp": lambda:driver.find_element(By.XPATH, name).click(),
       "cl_id": lambda:driver.find_element(By.ID, name).click(),
       "cl_na": lambda:driver.find_element(By.NAME, name).click(),
       "cl_cl": lambda:driver.find_element(By.CLASS_NAME, name).click(),
       "cl_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).click(),
       "cl_ta": lambda:driver.find_element(By.TAG_NAME, name).click(),
       "se_xp": lambda:driver.find_element(By.XPATH, name).send_keys(name_se),
       "se_id": lambda:driver.find_element(By.ID, name).send_keys(name_se),
       "se_na": lambda:driver.find_element(By.NAME, name).send_keys(name_se),
       "se_cl": lambda:driver.find_element(By.CLASS_NAME, name).send_keys(name_se),
       "se_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).send_keys(name_se),
       "se_ta": lambda:driver.find_element(By.TAG_NAME, name).send_keys(name_se),
       "cr_xp": lambda:driver.find_element(By.XPATH, name).clear(),
       "cr_id": lambda:driver.find_element(By.ID, name).clear(),
       "cr_na": lambda:driver.find_element(By.NAME, name).clear(),
       "cr_cl": lambda:driver.find_element(By.CLASS_NAME, name).clear(),
       "cr_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).clear(),
       "cr_ta": lambda:driver.find_element(By.TAG_NAME, name).clear(),
           
       "get_xp": lambda:driver.find_element(By.XPATH, name).text,
       "get_id": lambda:driver.find_element(By.ID, name).text,
       "get_na": lambda:driver.find_element(By.NAME, name).text,
       "get_cl": lambda:driver.find_element(By.CLASS_NAME, name).text,
       "get_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).text,
       "get_ta": lambda:driver.find_element(By.TAG_NAME, name).text,
           
       "en_xp": lambda:driver.find_element(By.XPATH, name).send_keys(Keys.ENTER),
       "en_id": lambda:driver.find_element(By.ID, name).send_keys(Keys.ENTER),
       "en_na": lambda:driver.find_element(By.NAME, name).send_keys(Keys.ENTER),
       "en_cl": lambda:driver.find_element(By.CLASS_NAME, name).send_keys(Keys.ENTER),
       "en_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).send_keys(Keys.ENTER),
       "en_ta": lambda:driver.find_element(By.TAG_NAME, name).send_keys(Keys.ENTER),
           
       "ba_xp": lambda:driver.find_element(By.XPATH, name).send_keys(Keys.BACKSPACE),
       "ba_id": lambda:driver.find_element(By.ID, name).send_keys(Keys.BACKSPACE),
       "ba_na": lambda:driver.find_element(By.NAME, name).send_keys(Keys.BACKSPACE),
       "ba_cl": lambda:driver.find_element(By.CLASS_NAME, name).send_keys(Keys.BACKSPACE),
       "ba_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).send_keys(Keys.BACKSPACE),
       "ba_ta": lambda:driver.find_element(By.TAG_NAME, name).send_keys(Keys.BACKSPACE),
           
       "re_xp": lambda:driver.find_element(By.XPATH, name).send_keys(Keys.RETURN),
       "re_id": lambda:driver.find_element(By.ID, name).send_keys(Keys.RETURN),
       "re_na": lambda:driver.find_element(By.NAME, name).send_keys(Keys.RETURN),
       "re_cl": lambda:driver.find_element(By.CLASS_NAME, name).send_keys(Keys.RETURN),
       "re_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).send_keys(Keys.RETURN),
       "re_ta": lambda:driver.find_element(By.TAG_NAME, name).send_keys(Keys.RETURN),
           
       "re_xp": lambda:driver.find_element(By.XPATH, name).send_keys(Keys.RETURN),
       "re_id": lambda:driver.find_element(By.ID, name).send_keys(Keys.RETURN),
       "re_na": lambda:driver.find_element(By.NAME, name).send_keys(Keys.RETURN),
       "re_cl": lambda:driver.find_element(By.CLASS_NAME, name).send_keys(Keys.RETURN),
       "re_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).send_keys(Keys.RETURN),
       "re_ta": lambda:driver.find_element(By.TAG_NAME, name).send_keys(Keys.RETURN),
       
       "sr_xp": lambda:driver.find_element(By.XPATH, name).screenshot(name_se),
       "sr_id": lambda:driver.find_element(By.ID, name).screenshot(name_se),
       "sr_na": lambda:driver.find_element(By.NAME, name).screenshot(name_se),
       "sr_cl": lambda:driver.find_element(By.CLASS_NAME, name).screenshot(name_se),
       "sr_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).screenshot(name_se),
       "sr_ta": lambda:driver.find_element(By.TAG_NAME, name).screenshot(name_se),
           
       "get_xp": lambda:driver.find_element(By.XPATH, name).get_attribute(name_se),
       "get_id": lambda:driver.find_element(By.ID, name).get_attribute(name_se),
       "get_na": lambda:driver.find_element(By.NAME, name).get_attribute(name_se),
       "get_cl": lambda:driver.find_element(By.CLASS_NAME, name).get_attribute(name_se),
       "get_cs": lambda:driver.find_element(By.CSS_SELECTOR, name).get_attribute(name_se),
       "get_ta": lambda:driver.find_element(By.TAG_NAME, name).get_attribute(name_se),
           
       "get": lambda:driver.get(name),
       "qu": lambda:driver.quit(),
       "clo": lambda:driver.close(),
       "add_co": lambda:driver.add_cookie(name),
       "de_co": lambda:driver.delete_all_cookies(),
       "get_co": lambda:driver.get_cookies(),
       "get_url": lambda:driver.current_url,
       "get_ti": lambda:driver.title,
       "ba": lambda:driver.back(),
       "ha": lambda:driver.switch_to.window(driver.window_handles[int(name)]),
       "sc": lambda:driver.save_screenshot(name),
       "wa": lambda:driver.implicitly_wait(name),
       "re": lambda:driver.refresh(),
       "size": lambda:driver.set_window_size(int(name), (name_se)),
       "en": lambda:ActionChains(driver).send_keys(Keys.ENTER).perform(),
       "html": lambda:driver.page_source,
            }
    #action_map.get(kind, lambda: None)()
    return action_map.get(kind, lambda: None)()

def se_chr(pan):
    global driver

    kind, name = pan.split("@")[0], pan.split("#")[0].split("@")[-1]
    name_se = pan.split("#")[-1] if "#" in pan else None

    if kind == "us":
        driver = Driver(uc=True)
        return driver

    if kind == "wa" and driver:
        driver.implicitly_wait(int(name))
    elif kind == "max" and driver:
        driver.maximize_window()
    elif kind == "size" and driver:
        driver.set_window_size(int(name), int(name_se))
    elif kind == "quit" and driver:
        driver.quit()
