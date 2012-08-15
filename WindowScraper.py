
from Tkinter import *
from PIL import Image, ImageTk
from ttk import Frame, Button, Style


class WallScraper(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.initUI()
        
    def initUI(self):
        self.master.title("WallScraper! (alpha)")
        self.pack(fill=BOTH, expand=1)
        
        Style().configure("TFrame", background="#333")
        
        self.img = Image.open('bg.jpg')
        self.bg = ImageTk.PhotoImage(self.img)
        canvas = Canvas(self, width=self.img.size[0], height = self.img.size[1])
        canvas.create_image(5, 5, anchor = NW, image=self.bg)
        canvas.pack(fill=BOTH, expand=1)
        
        #Board selection
        wg_var = IntVar()
        h_var = IntVar()
        hr_var = IntVar()
        
        label = Label(self, text='Categories: ')
        label.pack(in_=canvas, anchor = NW, side = LEFT)
        
        wg_cb = Checkbutton(self, text="WG", variable = wg_var, onvalue = 1, offvalue = 0)
        wg_cb.select()
        wg_cb.pack(in_=canvas, anchor = NW, side = LEFT)
        
        h_cb = Checkbutton(self, text="H", variable = h_var, onvalue = 1, offvalue = 0)
        h_cb.select()
        h_cb.pack(in_=canvas, anchor = NW, side = LEFT)
        
        hr_cb = Checkbutton(self, text="HR", variable = hr_var, onvalue = 1, offvalue = 0)
        hr_cb.select()
        hr_cb.pack(in_= canvas, anchor = NW, side = LEFT)
        
        #NSFW Filter
        sfw_var = IntVar()
        sketchy_var = IntVar()
        nsfw_var = IntVar()
        
        label = Label(self, text='Purity Filter: ')
        label.pack(in_=canvas, anchor = NW, side = LEFT)
        
        sfw_cb = Checkbutton(self, text="SFW", variable = sfw_var, onvalue = 1, offvalue = 0)
        sfw_cb.select()
        sfw_cb.pack(in_=canvas, anchor = NW, side = LEFT)
        
        sketchy_cb = Checkbutton(self, text="Sketchy", variable = sketchy_var, onvalue = 1, offvalue = 0)
        sketchy_cb.select()
        sketchy_cb.pack(in_=canvas, anchor = NW, side = LEFT)
        
        nsfw_cb = Checkbutton(self, text="NSFW", variable = nsfw_var, onvalue = 1, offvalue = 0)
        nsfw_cb.select()
        nsfw_cb.pack(in_= canvas, anchor = NW, side = LEFT)
        
        #Sort Options
        sort_opt = ['Favorites', 'Date', 'Relevance']
        lb = Listbox(self)
        for i in sort_opt:
            lb.insert(END, i)
        
        lb.bind("<<ListboxSelect>>", self.onSelect)
        lb.pack(in_=canvas, anchor = NW, side = RIGHT)
        self.var = StringVar()
        self.label = Label(self, text = 0, textvariable=self.var)
        self.label.pack(in_=canvas, anchor=NW, side = RIGHT)
        
        
        
        closeButton = Button(self, text="Close", command=self.onClose)
        closeButton.pack(in_=canvas, anchor=SE,  side = RIGHT, padx = 5, pady = 5)
        
        
        
    def onSelect(self, val):
        sender = val.widget
        idx = sender.curselection()
        value = sender.get(idx)
        self.var.set(value)
    
    #When called, closes the window
    def onClose(self):
        self.quit()
        
        
def main():
    root = Tk()
    root.geometry("720x405+300+300")
    app = WallScraper(root)
    root.mainloop()
    


if __name__ == '__main__':
    main()