import pygame
import random
import sys
import time
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 700, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("¡Grug escapa de las piedras!")

fondo = pygame.image.load("cueva.jpg")
nave_img = pygame.image.load("grug.png")
asteroide_img = pygame.image.load("piedra.png")
powerup_bomba_img = pygame.image.load("powerup_bomba.png")
powerup_velocidad_img = pygame.image.load("powerup_velocidad.png")
banana_img = pygame.image.load("banana.png")

fondo = pygame.transform.scale(fondo, (WIDTH, HEIGHT))
nave_img = pygame.transform.scale(nave_img, (60, 80))
asteroide_img = pygame.transform.scale(asteroide_img, (50, 50))
powerup_bomba_img = pygame.transform.scale(powerup_bomba_img, (40, 40))
powerup_velocidad_img = pygame.transform.scale(powerup_velocidad_img, (40, 40))
banana_img = pygame.transform.scale(banana_img, (40, 40))

RECORD_FILE = "record.txt"

def cargar_record():
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as f:
            try:
                return int(f.read())
            except:
                return 0
    return 0

def guardar_record(record):
    with open(RECORD_FILE, "w") as f:
        f.write(str(record))

record_maximo = cargar_record()

class Nave:
    def __init__(self):
        self.image = nave_img
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 85))  # Ahora Grug toca el suelo
        self.base_speed = 7
        self.speed_bonus = 0
        self.speed_boost_timer = 0

    @property
    def speed(self):
        if self.speed_boost_timer > 0:
            return 15
        return min(self.base_speed + self.speed_bonus, 15)

    def mover(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def dibujar(self, pantalla):
        pantalla.blit(self.image, self.rect)

class Asteroide:
    def __init__(self, speed_bonus):
        self.image = asteroide_img
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH - 50), -50))
        self.base_speed = random.randint(4, 8)
        self.speed_bonus = speed_bonus

    @property
    def speed(self):
        return min(self.base_speed + self.speed_bonus, 20)

    def mover(self):
        self.rect.y += self.speed

    def dibujar(self, pantalla):
        pantalla.blit(self.image, self.rect)

class PolvoAnimacion:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.tiempo = 0
        self.duracion = 30
        self.color = color

    def actualizar(self):
        self.tiempo += 1

    def dibujar(self, pantalla):
        if self.tiempo < self.duracion:
            radio = self.tiempo * 2
            alpha = max(255 - self.tiempo * 8, 0)
            polvo = pygame.Surface((radio*2, radio*2), pygame.SRCALPHA)
            pygame.draw.circle(polvo, (*self.color, alpha), (radio, radio), radio)
            pantalla.blit(polvo, (self.x - radio, self.y - radio))

class PowerUp:
    def __init__(self, tipo):
        self.tipo = tipo
        self.image = powerup_bomba_img if tipo == "bomba" else powerup_velocidad_img
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH - 50), -50))
        self.speed = 5

    def mover(self):
        self.rect.y += self.speed

    def dibujar(self, pantalla):
        pantalla.blit(self.image, self.rect)

class Banana:
    def __init__(self):
        self.image = banana_img
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH - 50), -50))
        self.speed = 4

    def mover(self):
        self.rect.y += self.speed

    def dibujar(self, pantalla):
        screen.blit(self.image, self.rect)

def menu_inicio(font):
    while True:
        screen.blit(fondo, (0, 0))
        titulo = font.render("\u00a1Grug escapa de las piedras!", True, (255, 255, 255))
        iniciar_txt = font.render("Presiona ENTER para iniciar", True, (255, 255, 255))
        salir_txt = font.render("Presiona ESC para salir", True, (255, 255, 255))
        screen.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(iniciar_txt, (WIDTH // 2 - iniciar_txt.get_width() // 2, HEIGHT // 2))
        screen.blit(salir_txt, (WIDTH // 2 - salir_txt.get_width() // 2, HEIGHT // 2 + 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            return
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

def game_loop():
    global record_maximo
    pygame.mixer.music.load("THE WORLD REVOLVING.mp3")
    pygame.mixer.music.play(-1)

    clock = pygame.time.Clock()
    nave = Nave()
    asteroides = []
    powerups = []
    bananas = []
    animaciones = []
    spawn_timer = 0
    spawn_interval = 30
    powerup_timer = 0
    banana_timer = 0
    font = pygame.font.SysFont(None, 40)
    game_over = False

    start_time = time.time()
    last_speedup_meteor = 0
    last_speedup_nave = 0
    last_spawn_update = 0
    meteor_speed_bonus = 0
    tiempo_final = 0
    banana_recogidas = 0
    inmune = False
    inmune_timer = 0
    inmune_duration = 5

    while True:
        screen.blit(fondo, (0, 0))
        pygame.draw.rect(screen, (80, 42, 42), (0, HEIGHT - 60, WIDTH, 60))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        current_time = time.time()
        tiempo_actual = int(current_time - start_time)

        if not game_over:
            nave.mover(keys)

            if nave.speed_boost_timer > 0:
                nave.speed_boost_timer -= 1

            if inmune:
                inmune_timer += 1/60
                if inmune_timer >= inmune_duration:
                    inmune = False
                    inmune_timer = 0

            if tiempo_actual - last_speedup_meteor >= 5:
                meteor_speed_bonus += 1
                last_speedup_meteor = tiempo_actual

            if tiempo_actual - last_speedup_nave >= 10:
                nave.speed_bonus += 1
                last_speedup_nave = tiempo_actual

            if tiempo_actual - last_spawn_update >= 5:
                spawn_interval = max(spawn_interval - 3, 10)
                last_spawn_update = tiempo_actual

            spawn_timer += 1
            if spawn_timer >= spawn_interval:
                asteroides.append(Asteroide(meteor_speed_bonus))
                spawn_timer = 0

            powerup_timer += 1
            if powerup_timer >= 600:
                tipo = random.choice(["bomba", "velocidad"])
                powerups.append(PowerUp(tipo))
                powerup_timer = 0

            banana_timer += 1
            if banana_timer >= 1200:
                bananas.append(Banana())
                banana_timer = 0

            for ast in asteroides[:]:
                ast.mover()
                ast.dibujar(screen)
                if ast.rect.top > HEIGHT:
                    asteroides.remove(ast)
                elif ast.rect.colliderect(nave.rect) and not inmune:
                    animaciones.append(PolvoAnimacion(nave.rect.centerx, nave.rect.centery, (128, 128, 128)))
                    game_over = True
                    tiempo_final = tiempo_actual
                    if tiempo_actual > record_maximo:
                        record_maximo = tiempo_actual
                        guardar_record(record_maximo)
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("Game Over - Super Mario World.mp3")
                    pygame.mixer.music.play()

            for p in powerups[:]:
                p.mover()
                p.dibujar(screen)
                if p.rect.top > HEIGHT:
                    powerups.remove(p)
                elif p.rect.colliderect(nave.rect):
                    if p.tipo == "bomba":
                        asteroides.clear()
                        animaciones.append(PolvoAnimacion(nave.rect.centerx, nave.rect.centery, (255, 255, 0)))
                    elif p.tipo == "velocidad":
                        nave.speed_boost_timer = 300
                    powerups.remove(p)

            for b in bananas[:]:
                b.mover()
                b.dibujar(screen)
                if b.rect.top > HEIGHT:
                    bananas.remove(b)
                elif b.rect.colliderect(nave.rect):
                    bananas.remove(b)
                    banana_recogidas += 1
                    inmune = True
                    inmune_timer = 0

            if banana_recogidas >= 5:
                texto_victoria = font.render("\u00a1GANASTE! Recolectaste 5 bananas", True, (0, 255, 0))
                screen.blit(texto_victoria, (WIDTH // 2 - texto_victoria.get_width() // 2, HEIGHT // 2))
                pygame.display.flip()
                pygame.time.wait(5000)
                return

            for a in animaciones[:]:
                a.actualizar()
                a.dibujar(screen)
                if a.tiempo >= a.duracion:
                    animaciones.remove(a)

            nave.dibujar(screen)

            tiempo_txt = font.render(f"Tiempo: {tiempo_actual} s", True, (255, 255, 255))
            record_txt = font.render(f"Record: {record_maximo} s", True, (255, 215, 0))
            inmunidad_txt = font.render(f"Inmune: {'S\u00cd' if inmune else 'NO'}", True, (0, 255, 255))
            bananas_txt = font.render(f"Bananas: {banana_recogidas}/5", True, (255, 255, 0))
            screen.blit(tiempo_txt, (10, 10))
            screen.blit(record_txt, (10, 50))
            screen.blit(inmunidad_txt, (10, 90))
            screen.blit(bananas_txt, (10, 130))

        else:
            texto1 = font.render("\u00a1GAME OVER! Presiona R para reiniciar", True, (255, 0, 0))
            texto2 = font.render(f"Aguantaste: {tiempo_final} segundos", True, (255, 255, 255))
            texto3 = font.render(f"Record: {record_maximo} segundos", True, (255, 215, 0))
            screen.blit(texto1, (WIDTH // 2 - texto1.get_width() // 2, HEIGHT // 2 - 60))
            screen.blit(texto2, (WIDTH // 2 - texto2.get_width() // 2, HEIGHT // 2 - 10))
            screen.blit(texto3, (WIDTH // 2 - texto3.get_width() // 2, HEIGHT // 2 + 40))
            if keys[pygame.K_r]:
                return

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    font_menu = pygame.font.SysFont(None, 70)
    while True:
        menu_inicio(font_menu)
        game_loop()