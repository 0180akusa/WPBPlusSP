import tkinter as tk
from tkinter import ttk, messagebox
import os
import requests
from bs4 import BeautifulSoup
import json
import re

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.grajapa.shueisha.co.jp/'
    }

def get_folder_name(N1):
    headers = get_headers()
    url = f"https://www.grajapa.shueisha.co.jp/plus/special/archives/{N1}/"
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    
    if response.status_code != 200:
        print(f"Failed to retrieve data from {url}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    special_intro = soup.find('div', class_='special-intro-number')
    if special_intro:
        items = special_intro.find_all('div', class_='special-intro-number__item')
        if len(items) >= 2:
            number = items[-2].text.strip()
            date = items[-1].text.strip()
            month, year = date.split(' / ')
            date = f"{year}.{month}"
        else:
            print("Not enough items found in special-intro-number")
            return None
    else:
        print("special-intro-number not found")
        return None
    
    script = soup.find('script', text=re.compile(r'let jsonString ='))
    if script:
        json_text = re.search(r'let jsonString =\s*\'(.*?)\';', script.string, re.DOTALL).group(1)
        json_data = json.loads(json_text)
        title = json_data.get('title', '')
    else:
        print("jsonString not found")
        return None
    
    return f"WPB SP+ {number} {date}{title}"

def create_folders(base_path, folder_name):
    F1_path = os.path.join(base_path, folder_name)
    if not os.path.exists(F1_path):
        os.makedirs(F1_path)
        print(f"Created main folder: {F1_path}")
    else:
        print(f"Main folder already exists: {F1_path}")
    
    subfolders = ['Chapter1', 'Chapter2', 'Chapter3', 'Chapter4', 'MOVIE']
    for subfolder in subfolders:
        subfolder_path = os.path.join(F1_path, subfolder)
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)
            print(f"Created subfolder: {subfolder_path}")
        else:
            print(f"Subfolder already exists: {subfolder_path}")
    
    return F1_path

def generate_image_urls(N1, name, chapter_limits):
    base_url = f"https://www.grajapa.shueisha.co.jp/plus/special/archives/{N1}/contents/images"
    urls = {1: [], 2: [], 3: [], 4: []}
    for chapter in range(1, 5):
        for i in range(1, chapter_limits[chapter-1] + 1):
            url = f"{base_url}/chapter{chapter}/{i:03d}-chapter{chapter}-{name}.jpg"
            urls[chapter].append(url)
    return urls

def save_urls_to_files(urls, base_path):
    for chapter, chapter_urls in urls.items():
        filename = os.path.join(base_path, f"Chapter{chapter}.txt")
        mode = 'a' if os.path.exists(filename) else 'w'
        with open(filename, mode, encoding='utf-8') as f:
            for url in chapter_urls:
                f.write(f"{url}\n")
        print(f"Saved {len(chapter_urls)} URLs to {filename}")

def generate_framework():
    # 获取输入值
    N1 = entry_N1.get()
    name = entry_name.get()
    chapter_limits = [
        int(entry_ch1.get()),
        int(entry_ch2.get()),
        int(entry_ch3.get()),
        int(entry_ch4.get())
    ]

    # 获取文件夹名称
    folder_name = get_folder_name(N1)
    if not folder_name:
        messagebox.showerror("错误", "无法获取文件夹名称，请检查N1值是否正确。")
        return

    # 创建文件夹
    base_path = "D:\\FFOutput"
    F1_path = create_folders(base_path, folder_name)

    # 生成URL并保存到文件
    urls = generate_image_urls(N1, name, chapter_limits)
    save_urls_to_files(urls, F1_path)

    messagebox.showinfo("成功", "URL生成完成！")

def validate_inputs():
    if not all([entry_N1.get(), entry_name.get(), entry_ch1.get(), entry_ch2.get(), entry_ch3.get(), entry_ch4.get()]):
        messagebox.showerror("错误", "请填写所有输入框。")
        return False
    return True

def on_generate():
    if validate_inputs():
        generate_framework()

# 创建主窗口
root = tk.Tk()
root.title("WPB SP+")
root.geometry("300x400")
root.resizable(False, False)

# 设置样式
style = ttk.Style()
style.theme_use('clam')
style.configure('TLabel', font=('Helvetica', 12))
style.configure('TEntry', font=('Helvetica', 12))
style.configure('TButton', font=('Helvetica', 12, 'bold'))

# 创建主框架
main_frame = ttk.Frame(root, padding="20 20 20 20")
main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# 创建并放置输入框和标签
ttk.Label(main_frame, text="archives").grid(row=0, column=0, sticky=tk.W, pady=5)
entry_N1 = ttk.Entry(main_frame, width=30)
entry_N1.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

ttk.Label(main_frame, text="name").grid(row=1, column=0, sticky=tk.W, pady=5)
entry_name = ttk.Entry(main_frame, width=30)
entry_name.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

ttk.Label(main_frame, text="Chapter1").grid(row=2, column=0, sticky=tk.W, pady=5)
entry_ch1 = ttk.Entry(main_frame, width=30)
entry_ch1.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

ttk.Label(main_frame, text="Chapter2").grid(row=3, column=0, sticky=tk.W, pady=5)
entry_ch2 = ttk.Entry(main_frame, width=30)
entry_ch2.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

ttk.Label(main_frame, text="Chapter3").grid(row=4, column=0, sticky=tk.W, pady=5)
entry_ch3 = ttk.Entry(main_frame, width=30)
entry_ch3.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)

ttk.Label(main_frame, text="Chapter4").grid(row=5, column=0, sticky=tk.W, pady=5)
entry_ch4 = ttk.Entry(main_frame, width=30)
entry_ch4.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)

# 创建并放置按钮
generate_button = ttk.Button(main_frame, text="RUN", command=on_generate)
generate_button.grid(row=6, column=0, columnspan=2, pady=20)

# 配置列的权重
main_frame.columnconfigure(1, weight=1)

# 启动主循环
root.mainloop()