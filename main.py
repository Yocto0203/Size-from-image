import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import cv2
import numpy as np

class Application(tk.Frame):
    def __init__(self, master=None):
        # GUI 初期設定
        super().__init__(master)
        self.master.geometry("800x600")
        master.title("マイアプリ")
        
        #フィールド設定
        self.imgPath = ""
        self.isWriting = False
        self.mene_mode = -1
        # 線の情報
        self.line_colour = ["blue", "red", "red", "red"]
        self.measure_start = [[] for i in range(10)]
        self.measure_end = [[] for i in range(10)]
        self.measure_line = [None for i in range(10)]
        self.master_width = [1 for i in range(10)]
        self.base_length = 0.
        self.line_dist = [None for i in range(10)]
        
        self.line_ans = [None for i in range(10)]
        
        
        # メニューの作成
        self.create_menu()
        # ツールバーの作成
        self.create_tool_bar()
        # ステータスバーの作成
        self.create_status_bar()
        # サイドパネル
        self.create_side_panel()
        
        self.canvas = tk.Canvas(self.master, background="#8FB9CF")
        self.canvas.pack(expand=True,  fill=tk.BOTH)
        
        #マウスイベント
        self.canvas.bind('<ButtonPress-1>', self.mouse_left_press)
        self.canvas.bind('<B1-Motion>', self.mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.stop_pickup)
        
        
    def create_menu(self):
        #メニューの作成
        menu_bar = tk.Menu(self)
 
        file_menu = tk.Menu(menu_bar, tearoff = tk.OFF)
        menu_bar.add_cascade(label="ファイル", menu = file_menu) 

        file_menu.add_command(label = "開く", command = self.button_load_img_click, accelerator = "Ctrl+O")
        file_menu.add_separator() # セパレータ
        file_menu.add_command(label = "終了", command = self.master.destroy)

        # 親のメニューに設定
        self.master.config(menu = menu_bar)
        
    def create_tool_bar(self):
        frame_tool_bar = tk.Frame(self.master, borderwidth = 2, relief = tk.SUNKEN)
        
        button0 = tk.Button(frame_tool_bar, text = "LOCK", width = 6, command=lambda:self.menu_button_clicked(-1))
        button1 = tk.Button(frame_tool_bar, text = "基準線", width = 6, command=lambda:self.menu_button_clicked(0))
        button2 = tk.Button(frame_tool_bar, text = "測定1", width = 6, command=lambda:self.menu_button_clicked(1))
        button3 = tk.Button(frame_tool_bar, text = "測定2", width = 6, command=lambda:self.menu_button_clicked(2))
        button4 = tk.Button(frame_tool_bar, text = "測定3", width = 6, command=lambda:self.menu_button_clicked(3))
        self.menu_button_list = [button1, button2, button3, button4]
        
        button0.pack(side = tk.LEFT)
        button1.pack(side = tk.LEFT)
        button2.pack(side = tk.LEFT)
        button3.pack(side = tk.LEFT)
        button4.pack(side = tk.LEFT)

        frame_tool_bar.pack(fill = tk.X)

    def create_status_bar(self):
        frame_status_bar = tk.Frame(self.master, borderwidth = 2, relief = tk.SUNKEN)

        self.label1 = tk.Label(frame_status_bar, text = "image path :")
        self.label2 = tk.Label(frame_status_bar, text = "mode : Lock")

        self.label1.pack(side = tk.LEFT)
        self.label2.pack(side = tk.RIGHT)

        frame_status_bar.pack(side = tk.BOTTOM, fill = tk.X)

    def create_side_panel(self):
        side_panel = tk.Frame(self.master, borderwidth = 2, relief = tk.SUNKEN)

        button1 = tk.Button(side_panel, text = "更新", width = 15, command=self.show_img)
        button2 = tk.Button(side_panel, text = "線の削除", width = 15, command=self.del_line)
        button3 = tk.Button(side_panel, text = "すべて削除", width = 15, command=lambda:self.del_line(1))
        button4 = tk.Button(side_panel, text = "適用", width = 10, command=self.apply)
        
        label0 = tk.Label(side_panel, text = "")
        label1 = tk.Label(side_panel, text = "線の太さ")
        label3 = tk.Label(side_panel, text = "線の色")
        label2 = tk.Label(side_panel, text = "基準線の大きさ")
        
        measurelabel1 = tk.Label(side_panel, text = "測定1 : ")
        measurelabel2 = tk.Label(side_panel, text = "測定2 : ")
        measurelabel3 = tk.Label(side_panel, text = "測定2 : ")
        self.measurelabel_list = [None, measurelabel1, measurelabel2, measurelabel3]
        
        self.alert_label = tk.Label(side_panel, text = "", foreground='#ff0000')
        
        self.sptxt1 = tk.StringVar()
        sp1 = tk.Spinbox(side_panel,textvariable=self.sptxt1,from_=1,to=15,increment=1, width=15)
        
        self.enttxt1 = tk.StringVar()
        entey1 = tk.Entry(side_panel, textvariable=self.enttxt1, width=15)
        
        self.cbtxt1 = tk.StringVar()
        cb = ttk.Combobox(side_panel, textvariable=self.cbtxt1, values=["km", "m", "mm"], width=5)
        cb.set("mm")
        
        self.cbtxt2 = tk.StringVar()
        cb2 = ttk.Combobox(side_panel, textvariable=self.cbtxt2, values=["blue", "red", 'green', 'blue', 'cyan', 'yellow', 'magenta', 'white', 'black',], width=5)

        button1.pack()
        button2.pack()
        button3.pack()
        
        label0.pack()
        label1.pack()
        
        sp1.pack()
        
        label3.pack()
        cb2.pack()
        
        label2.pack(pady = (20, 0))
        entey1.pack(anchor=tk.E, padx=(0,10))
        cb.pack(anchor=tk.E, padx=(0,10), pady = (0, 20))
        
        button4.pack(pady = (0, 20)) #適応
        
        measurelabel1.pack(anchor=tk.W)
        measurelabel2.pack(anchor=tk.W)
        measurelabel3.pack(anchor=tk.W)
        
        self.alert_label.pack()
        
        side_panel.pack(side=tk.RIGHT, fill = tk.Y)
        
        #イベント
        cb.bind("<<ComboboxSelected>>",self.combo_selected)
    
    def button_load_img_click(self):
        #ファイルダイアログを開く
        fTyp = [("画像ファイル", "*")]
        iDir = os.path.abspath(os.path.dirname(__file__))
        path = tk.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)
        #読み込んだ画像パスを保存
        self.imgPath = path
        self.label1["text"] = f"image path : {path}"
        
        #画像表示
        if path:
            self.show_img()
    
    def show_img(self):
        global image_tk
        
        #画像を取得
        n = np.fromfile(self.imgPath, np.uint8)
        image_bgr = cv2.imdecode(n, cv2.IMREAD_COLOR)
        #画像がキャンバス内に入るように修正
        canvas_width = self.canvas.winfo_width() #キャンバスサイズを入手
        canvas_height = self.canvas.winfo_height()
        height, width, channels = image_bgr.shape[:3] #画像サイズを入手
        
        height_ratio = canvas_height/height #縮小倍率を求める
        width_ratio = canvas_width/width
        
        if height_ratio < width_ratio: #縮小(or拡大)する
            image_bgr = cv2.resize(image_bgr, None, None, height_ratio, height_ratio)
        else:
            image_bgr = cv2.resize(image_bgr, None, None, width_ratio, width_ratio)
        
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB) # imreadはBGRなのでRGBに変換
        image_pil = Image.fromarray(image_rgb) # RGBからPILフォーマットへ変換
        image_tk  = ImageTk.PhotoImage(image_pil) # ImageTkフォーマットへ変換
        self.canvas.create_image(0, 0, image=image_tk, anchor=tk.NW) # ImageTk 画像配置
    
    def mouse_left_press(self, event): #左クリックされたとき
        if self.mene_mode != -1:
            self.measure_start[self.mene_mode] = [event.x, event.y]
    
    def mouse_drag(self, event):
        #線の設定
        if self.mene_mode != -1:
            c = self.line_colour[self.mene_mode]
        else:
            c = "Red"
        
        if self.mene_mode != -1: #線の書き込み
            if self.measure_line[self.mene_mode]:
                self.canvas.delete(self.measure_line[self.mene_mode])
            self.measure_end[self.mene_mode] = [event.x, event.y]
            self.measure_line[self.mene_mode] = self.canvas.create_line(self.measure_start[self.mene_mode][0], 
                                                                            self.measure_start[self.mene_mode][1],
                                                                            self.measure_end[self.mene_mode][0], 
                                                                            self.measure_end[self.mene_mode][1], 
                                                                            fill = c, width = self.master_width[self.mene_mode])
    def del_line(self, arg=0):
        if self.mene_mode != -1:
            if arg==1:
                for i in self.measure_line:
                    self.canvas.delete(i)
                for i, j in enumerate(self.measurelabel_list[1:]):
                    j["text"] = f"測定{i+1} : None"
            elif self.measure_line[self.mene_mode]:
                self.canvas.delete(self.measure_line[self.mene_mode])
                self.measurelabel_list[self.mene_mode]["text"] = f"測定{self.mene_mode} : None"
    
    def menu_button_clicked(self, id):
        self.mene_mode = id
        if id == 0:
            self.label2["text"] = "mode : Line Base (write)"
        elif id != -1:
            self.label2["text"] = f"mode : Line {id} (write)"
        else:
            self.label2["text"] = "mode : Lock"
        
        #押されたボタンの色変更
        for i, button in enumerate(self.menu_button_list):
            if i == id:
                button.config(bg='grey')
            else:
                button.config(bg="#f0f0f0")
        
        #
        self.sptxt1.set(self.master_width[id])
        self.cbtxt2.set(self.line_colour[id])
        pass
    
    def stop_pickup(self, e):
        if self.mene_mode != -1:
            self.line_dist[self.mene_mode] = ((self.measure_end[self.mene_mode][0] - self.measure_start[self.mene_mode][0])**2 
                                              + (self.measure_end[self.mene_mode][1] - self.measure_start[self.mene_mode][1])**2)**0.5
        self.calc_dist()
        
    def calc_dist(self):
        unit_times = 1000 if self.cbtxt1.get()=="mm" else 1 if self.cbtxt1.get()=="m" else 0.001
        for i in range(1,4):
            if self.line_dist[i] != None and self.line_dist[0] != None:
                dist = self.line_dist[i]/self.line_dist[0]*self.base_length
                self.measurelabel_list[i]["text"] = f"測定{i} : {round(dist*unit_times, 2)} [{self.cbtxt1.get()}]"
            else:
                self.measurelabel_list[i]["text"] = f"測定{i} : None"
        if self.base_length == None or self.base_length == 0:
            self.alert_label["text"] = "\n注意:基準の大きさが\n設定されていません"
        else:
            self.alert_label["text"] = ""
        
    def combo_selected(self, e):
        #基準の修正
        unit = self.cbtxt1.get()
        dist = 0.
        
        try:
            if float(self.enttxt1.get()) < 0:
                raise ValueError("Invalid value")
            if unit == "mm":
                dist = float(self.enttxt1.get())*(1/1000)
            elif unit == "m":
                dist = float(self.enttxt1.get())*(1)
            elif unit == "km":
                dist = float(self.enttxt1.get())*(1000)
        except ValueError:
            self.enttxt1.set("ERROR")
        
    def apply(self):
        #線の幅の適応
        if self.mene_mode != -1:
            self.master_width[self.mene_mode] = int(self.sptxt1.get())
            self.line_colour[self.mene_mode] = self.cbtxt2.get()
        #基準の適応
        unit = self.cbtxt1.get()
        dist = 0.
        
        try:
            if float(self.enttxt1.get()) < 0:
                raise ValueError("Invalid value")
            if unit == "mm":
                dist = float(self.enttxt1.get())*(1/1000)
            elif unit == "m":
                dist = float(self.enttxt1.get())*(1)
            elif unit == "km":
                dist = float(self.enttxt1.get())*(1000)
        except ValueError:
            self.enttxt1.set("ERROR")
        
        self.base_length = dist
        self.calc_dist()
        
if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    # mainloop
    app.mainloop()