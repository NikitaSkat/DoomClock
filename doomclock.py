import tkinter as tk
import time

class CloTick:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
    def setup_window(self):
        # Делаем окно во весь экран
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        
        # Устанавливаем черный цвет и прозрачность 50%
        self.root.configure(background='black')
        self.root.attributes('-alpha', 0.5)
        
        # Выход по клику мыши или любой клавише
        self.root.bind('<Button-1>', self.close_app)  # Левая кнопка мыши
        self.root.bind('<Key>', self.close_app)       # Любая клавиша
        
        # Метка с инструкцией (опционально)
        label = tk.Label(
            self.root, 
            text="Click or press any key to exit", 
            fg='white', 
            bg='black',
            font=('Arial', 16)
        )
        label.place(relx=0.5, rely=0.9, anchor='center')
        
    def close_app(self, event=None):
        self.root.destroy()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    print("Starting CloTick screensaver...")
    app = CloTick()
    app.run()
    print("CloTick closed")
