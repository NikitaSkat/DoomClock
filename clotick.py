import tkinter as tk

class CloTick:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
    def setup_window(self):
        # Делаем окно во весь экран
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        
        # Устанавливаем черный цвет и прозрачность 50%
        self.root.configure(background='black')
        self.root.attributes('-alpha', 0.5)
        
        # Фокус на окно для гарантированного захвата клавиш
        self.root.focus_force()
        
        # Выход по ЛКМ или Escape
        self.root.bind('<Button-1>', self.close_app)    # Левая кнопка мыши
        self.root.bind('<Escape>', self.close_app)      # Клавиша Escape
        self.root.bind('<Key>', self.check_escape)      # Все клавиши для проверки
        
        # Метка с инструкцией
        label = tk.Label(
            self.root, 
            text="Click LEFT mouse button or press ESC to exit", 
            fg='white', 
            bg='black',
            font=('Arial', 16)
        )
        label.place(relx=0.5, rely=0.5, anchor='center')
        
        print("CloTick started - use LEFT CLICK or ESC to exit")
        
    def check_escape(self, event):
        # Проверяем конкретно клавишу Escape
        if event.keysym == 'Escape':
            self.close_app()
        
    def close_app(self, event=None):
        print("Closing CloTick...")
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("Starting CloTick screensaver...")
    app = CloTick()
    app.run()
    print("CloTick closed successfully")
