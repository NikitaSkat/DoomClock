import pygame
import math
import random
from datetime import datetime
import sys
import os

# Инициализация Pygame
pygame.init()

# Получаем размеры основного экрана
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("DOOM Clock")

# Цвета
BLACK = (25, 0, 0)

# Автоматическое определение пути к шрифту
def get_font_path():
    # Если шрифт в той же папке что и exe
    if hasattr(sys, '_MEIPASS'):
        # Для pyinstaller bundle
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    font_path = os.path.join(base_path, 'doom2016left.ttf')
    if os.path.exists(font_path):
        return font_path
    
    # Пробуем разные возможные пути
    possible_paths = [
        os.path.join(base_path, 'doom2016left.ttf'),
        os.path.join(base_path, 'fonts', 'doom2016left.ttf'),
        os.path.join(os.getcwd(), 'doom2016left.ttf'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
            
    return None

# Загрузка шрифта
def load_font():
    font_path = get_font_path()
    
    if font_path:
        try:
            return pygame.font.Font(font_path, 650)
        except:
            pass
    
    # Fallback
    return pygame.font.SysFont("arial", 650, bold=True)

font = load_font()

# Переменные для анимаций
pulse_phase = 0.0
heat_wave_phase = 0.0
flame_pulse_phase = 0.0
wind_strength = 0.0
wind_direction = 1
wind_change_timer = 0
sparks = []
vortices = []
clock = pygame.time.Clock()
last_mouse_pos = pygame.mouse.get_pos()

# Переменные для глитч-эффекта
glitch_timer = 0
glitch_duration = 0
last_minute = -1

class Vortex:
    def __init__(self):
        self.x = random.randint(200, WIDTH - 200)
        self.y = random.randint(200, HEIGHT - 200)
        self.strength = random.uniform(0.5, 2.0)
        self.radius = random.randint(100, 300)
        self.life = random.randint(200, 400)
        self.max_life = self.life
        self.rotation_speed = random.uniform(0.02, 0.05)
        self.phase = random.uniform(0, math.pi * 2)
        
    def update(self):
        self.life -= 1
        self.phase += self.rotation_speed
        
    def get_force(self, x, y):
        dx = x - self.x
        dy = y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < self.radius and distance > 10:
            force = self.strength * (1 - distance / self.radius)
            angle = math.atan2(dy, dx) + math.pi/2
            pulse = 0.8 + 0.2 * math.sin(self.phase)
            
            return (
                math.cos(angle) * force * pulse,
                math.sin(angle) * force * pulse
            )
        return (0, 0)
        
    def is_dead(self):
        return self.life <= 0

class Spark:
    def __init__(self):
        # Разные точки появления - снизу, с краев, и немного сверху
        spawn_type = random.choice(['bottom', 'bottom', 'left_edge', 'right_edge', 'bottom_corner', 'top_falling'])
        
        if spawn_type == 'bottom':
            # Искры появляются по всей ширине снизу
            self.x = random.randint(100, WIDTH - 100)
            self.y = HEIGHT + random.randint(5, 40)
            self.falling = False
        elif spawn_type == 'left_edge':
            self.x = random.randint(-100, -20)
            self.y = random.randint(HEIGHT//2, HEIGHT + 100)
            self.falling = False
        elif spawn_type == 'right_edge':
            self.x = random.randint(WIDTH + 20, WIDTH + 100)
            self.y = random.randint(HEIGHT//2, HEIGHT + 100)
            self.falling = False
        elif spawn_type == 'bottom_corner':
            if random.choice([True, False]):
                self.x = random.randint(-50, 200)
            else:
                self.x = random.randint(WIDTH - 200, WIDTH + 50)
            self.y = HEIGHT + random.randint(10, 60)
            self.falling = False
        else:  # top_falling - падающие сверху искры
            self.x = random.randint(100, WIDTH - 100)
            self.y = random.randint(-50, 100)
            self.falling = True
        
        # Более плавные и медленные искры
        if self.falling:
            # Падающие искры - медленнее и с другим направлением
            self.speed_x = random.uniform(-0.8, 0.8)
            self.speed_y = random.uniform(2, 6)  # Падают вниз
            self.life = random.randint(30, 60)
            self.size = random.uniform(0.8, 2.0)
            self.brightness = random.uniform(0.6, 1.2)
        else:
            # Взлетающие искры
            self.speed_x = random.uniform(-1.8, 1.8)
            self.speed_y = random.uniform(-16, -10)
            self.life = random.randint(40, 80)
            self.size = random.uniform(1.2, 3.5)
            self.brightness = random.uniform(1.0, 1.8)
        
        self.max_life = self.life
        
        # Яркие желтые и оранжевые цвета
        color_choice = random.choice(['bright_yellow', 'golden', 'orange', 'hot_white', 'amber'])
        if color_choice == 'bright_yellow':
            self.base_color = (255, 255, 100)
        elif color_choice == 'golden':
            self.base_color = (255, 220, 80)
        elif color_choice == 'orange':
            self.base_color = (255, 180, 50)
        elif color_choice == 'hot_white':
            self.base_color = (255, 255, 180)
        else:  # amber
            self.base_color = (255, 200, 70)
        
        # Физические свойства - более плавные
        self.wind_affected = True
        self.wind_resistance = random.uniform(0.3, 0.7)
        self.vortex_affected = True
        self.flicker_speed = random.uniform(0.2, 0.4)
        self.flicker_phase = random.uniform(0, math.pi * 2)
        
    def update(self, wind_strength, wind_direction, vortices):
        # Ветер - более плавное влияние
        if wind_strength > 0.1:
            wind_force = wind_strength * wind_direction * self.wind_resistance * 0.8
            self.speed_x += wind_force * 0.1
        
        # Вихри - плавное закручивание
        for vortex in vortices:
            vx, vy = vortex.get_force(self.x, self.y)
            self.speed_x += vx * 0.4
            self.speed_y += vy * 0.4
        
        # Движение - более плавное
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Физика - медленнее замедление
        self.speed_x *= 0.998
        self.speed_y *= 0.999
        
        # Гравитация - по-разному для падающих и взлетающих
        if self.falling:
            gravity = -0.08  # Отрицательная гравитация для падающих (замедляет падение)
        else:
            gravity = 0.12   # Положительная для взлетающих (тянет вниз)
        
        self.speed_y += gravity
        
        # Плавное мерцание
        self.flicker_phase += self.flicker_speed
        flicker = 0.8 + 0.2 * math.sin(self.flicker_phase)
        
        self.life -= 1
        self.current_brightness = self.brightness * flicker
        
    def draw(self):
        life_ratio = self.life / self.max_life
        alpha = life_ratio * self.current_brightness
        
        current_color = (
            max(0, min(255, int(self.base_color[0] * alpha))),
            max(0, min(255, int(self.base_color[1] * alpha))),
            max(0, min(255, int(self.base_color[2] * alpha)))
        )
        
        # Простая яркая точка
        spark_size = max(1, int(self.size * life_ratio))
        pygame.draw.circle(screen, current_color, (int(self.x), int(self.y)), spark_size)
        
    def is_dead(self):
        # Искры могут улетать далеко за пределы экрана
        return (self.life <= 0 or 
                self.y < -200 or 
                self.y > HEIGHT + 200 or
                self.x < -200 or 
                self.x > WIDTH + 200)

def update_wind():
    global wind_strength, wind_direction, wind_change_timer
    
    wind_change_timer += 1
    
    if wind_change_timer > random.randint(100, 300):
        wind_strength = random.uniform(0.1, 1.0)
        wind_direction = random.choice([-1, 1])
        wind_change_timer = 0
    
    wind_strength += random.uniform(-0.02, 0.02)
    wind_strength = max(0.0, min(1.0, wind_strength))

def update_vortices():
    global vortices
    
    for vortex in vortices[:]:
        vortex.update()
        if vortex.is_dead():
            vortices.remove(vortex)
    
    if random.random() < 0.05:
        vortices.append(Vortex())

def update_glitch():
    global glitch_timer, glitch_duration, last_minute
    
    current_minute = datetime.now().minute
    
    # Проверяем смену минуты
    if current_minute != last_minute:
        last_minute = current_minute
        glitch_duration = 30  # 0.5 секунды при 60 FPS
        glitch_timer = glitch_duration
    
    # Обновляем таймер глитча
    if glitch_timer > 0:
        glitch_timer -= 1

def draw_gradient_background():
    global pulse_phase, heat_wave_phase, flame_pulse_phase
    
    pulse_phase += 0.02
    heat_wave_phase += 0.015
    flame_pulse_phase += 0.03
    
    # Несколько источников пульсации пламени
    flame_pulse1 = 0.5 + 0.5 * math.sin(flame_pulse_phase)
    flame_pulse2 = 0.5 + 0.5 * math.sin(flame_pulse_phase * 1.3 + 2)
    flame_pulse3 = 0.5 + 0.5 * math.sin(flame_pulse_phase * 0.7 + 4)
    
    # Рисуем градиент сразу на экран с шагом в 2 пикселя для производительности
    for y in range(0, HEIGHT, 2):
        progress = y / HEIGHT
        inverted_progress = 1.0 - progress  # 1 внизу, 0 вверху
        
        # Базовый цвет с плавным градиентом
        if progress < 0.1:
            base_r = int(15 * (progress / 0.1))
        elif progress < 0.4:
            factor = (progress - 0.1) / 0.3
            base_r = int(15 + 40 * factor)
        elif progress < 0.7:
            factor = (progress - 0.4) / 0.3
            base_r = int(55 + 50 * factor)
        else:
            factor = (progress - 0.7) / 0.3
            base_r = int(105 + 80 * factor)
        
        # Плавные тепловые волны
        heat_wave = math.sin(heat_wave_phase + y * 0.005) * 2
        
        # Яркие вспышки внизу
        flame_intensity = 0
        if inverted_progress > 0.7:
            flame_intensity += flame_pulse1 * math.pow(inverted_progress, 4) * 30
        if inverted_progress > 0.5:
            flame_intensity += flame_pulse2 * math.pow(inverted_progress, 3) * 20
        if inverted_progress > 0.3:
            flame_intensity += flame_pulse3 * math.pow(inverted_progress, 2) * 10
        
        # Боковые неоднородности
        side_variation = 0
        for x_pos in [0.3, 0.5, 0.7]:
            distance_to_flame = abs(x_pos - 0.5) * 2
            flame_strength = max(0, 1 - distance_to_flame)
            flame_wave = math.sin(heat_wave_phase * 0.8 + x_pos * 8 + y * 0.003)
            side_variation += flame_wave * flame_strength * 6 * inverted_progress
        
        final_r = base_r + int(heat_wave) + int(flame_intensity) + int(side_variation)
        final_r = min(220, max(10, final_r))
        
        g = int(final_r * 0.05)
        color = (final_r, g, 0)
        
        # Рисуем линию толщиной 2 пикселя
        pygame.draw.line(screen, color, (0, y), (WIDTH, y), 2)

def draw_text_with_glitch():
    current_time = datetime.now().strftime("%H:%M")
    
    # Создаём поверхность для текста
    text_surface = font.render(current_time, True, (255, 255, 255))
    text_width, text_height = text_surface.get_size()
    
    # Создаём градиентную поверхность
    gradient_surface = pygame.Surface((text_width, text_height), pygame.SRCALPHA)
    
    # Рисуем вертикальный градиент
    for y in range(text_height):
        progress = y / text_height
        
        if progress < 0.4:
            factor = progress / 0.4
            r = 255
            g = int(165 + (58 - 165) * factor)
            b = 0
        else:
            factor = (progress - 0.4) / 0.6
            r = int(255 + (139 - 255) * factor)
            g = int(58 * (1 - factor * 0.8))
            b = 0
        
        color = (r, g, b, 255)
        pygame.draw.line(gradient_surface, color, (0, y), (text_width, y))
    
    # Применяем текстовую маску
    gradient_surface.blit(text_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    # Глитч-эффект
    if glitch_timer > 0:
        glitch_intensity = glitch_timer / glitch_duration
        
        # Основной текст по центру
        text_rect = gradient_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
        screen.blit(gradient_surface, text_rect)
        
        # Глитч-эффекты
        if random.random() < glitch_intensity * 0.7:
            # Случайное смещение
            offset_x = random.randint(-int(20 * glitch_intensity), int(20 * glitch_intensity))
            offset_y = random.randint(-int(10 * glitch_intensity), int(10 * glitch_intensity))
            glitch_rect = gradient_surface.get_rect(center=(WIDTH//2 + offset_x, HEIGHT//2 - 100 + offset_y))
            
            # Глитч с другим цветом
            glitch_color = (255, 100, 100, int(150 * glitch_intensity))
            glitch_surface = gradient_surface.copy()
            glitch_surface.fill(glitch_color, special_flags=pygame.BLEND_RGB_ADD)
            screen.blit(glitch_surface, glitch_rect)
        
        # Дополнительные артефакты
        if random.random() < glitch_intensity * 0.3:
            # Горизонтальные линии-артефакты
            for i in range(random.randint(1, 3)):
                line_y = HEIGHT//2 - 100 + random.randint(-text_height//2, text_height//2)
                line_width = random.randint(10, int(100 * glitch_intensity))
                line_color = (255, 255, 255, int(200 * glitch_intensity))
                pygame.draw.line(screen, line_color, 
                               (WIDTH//2 - text_width//2, line_y),
                               (WIDTH//2 - text_width//2 + line_width, line_y),
                               random.randint(1, 3))
    else:
        # Обычная отрисовка без глитча
        text_rect = gradient_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
        screen.blit(gradient_surface, text_rect)

def main():
    global sparks, last_mouse_pos, wind_strength, wind_direction, vortices
    
    # Проверяем аргументы командной строки для режима заставки
    is_preview = False
    is_settings = False
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg.startswith('/p'):  # Preview mode
            is_preview = True
            # В режиме предпросмотра используем меньший размер
            preview_rect = pygame.Rect(0, 0, 800, 600)
            global screen, WIDTH, HEIGHT
            screen = pygame.display.set_mode((preview_rect.width, preview_rect.height))
            WIDTH, HEIGHT = preview_rect.width, preview_rect.height
        elif arg.startswith('/c'):  # Settings dialog
            is_settings = True
            # Показываем сообщение что настроек нет
            try:
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, 
                    "DOOM Clock Screensaver\n\nNo settings available.\n\nMove mouse or press any key to exit.", 
                    "DOOM Clock", 0)
            except:
                pass
            return
        elif arg.startswith('/s'):  # Fullscreen mode
            pass
    
    # Прячем курсор во всех режимах (кроме предпросмотра)
    if not is_preview:
        pygame.mouse.set_visible(False)
    
    running = True
    while running:
        current_mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                running = False
        
        # Проверяем движение мыши только если не в режиме предпросмотра
        if not is_preview:
            mouse_moved = (
                abs(current_mouse_pos[0] - last_mouse_pos[0]) > 5 or 
                abs(current_mouse_pos[1] - last_mouse_pos[1]) > 5
            )
            
            if mouse_moved:
                running = False
        
        last_mouse_pos = current_mouse_pos
        
        update_wind()
        update_vortices()
        update_glitch()
        
        screen.fill(BLACK)
        draw_gradient_background()
        
        for spark in sparks[:]:
            spark.update(wind_strength, wind_direction, vortices)
            spark.draw()
            if spark.is_dead():
                sparks.remove(spark)
        
        # Создаем новые искры
        for _ in range(random.randint(5, 12)):
            if random.random() < 0.6:
                sparks.append(Spark())
        
        # Рисуем текст с глитч-эффектом
        draw_text_with_glitch()
        
        pygame.display.flip()
        clock.tick(60)
    
    # Восстанавливаем видимость курсора при выходе
    pygame.mouse.set_visible(True)
    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # В скринсейвере не используем input(), просто выходим
        print(f"Error: {e}")
        sys.exit(1)