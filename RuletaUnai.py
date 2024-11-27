import pygame
import math
import time
import random
import utils

pygame.init()

# Constantes
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BLUE = (0, 0, 255)
FONT_SIZE = 24
CENTER = (200, 200)
RADIUS = 150
BUTTON_RECT = pygame.Rect(125, 400, 150, 50)
NUMBERS = list(range(37))  

# Información inicial de los jugadores
players = {
    "Taronja": {"color": ORANGE, "chips": {5: 5, 10: 2, 20: 1, 50: 1, 100: 1}, "bets": {}},
    "Lila": {"color": PURPLE, "chips": {5: 5, 10: 2, 20: 1, 50: 1, 100: 1}, "bets": {}},
    "Blau": {"color": BLUE, "chips": {5: 5, 10: 2, 20: 1, 50: 1, 100: 1}, "bets": {}},
}

# Configuración de la pantalla
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Casino Roulette")

font = pygame.font.Font(None, FONT_SIZE)

# Variables del juego / arrastrar fichas
spinning = False
angle_offset = 0
spin_duration = 3
segments = len(NUMBERS)

dragging_chip = None
drag_offset = (0, 0)
dragging_player = None


def draw_roulette_wheel(surface, angle_offset):

    """ Función que dibuja la rueda de la ruleta."""

    for i, number in enumerate(NUMBERS):
        # Calcular los ángulos de inicio y fin del segmento
        angle = 2 * math.pi * i / segments + angle_offset
        next_angle = 2 * math.pi * (i + 1) / segments + angle_offset
        
        # Calcular las posiciones de los vértices del triángulo
        x1, y1 = CENTER[0] + RADIUS * math.cos(angle), CENTER[1] + RADIUS * math.sin(angle)
        x2, y2 = CENTER[0] + RADIUS * math.cos(next_angle), CENTER[1] + RADIUS * math.sin(next_angle)
        
        if number == 0:
            color = GREEN 
        elif number % 2 == 0:
            color = BLACK 
        else:
            color = RED  
        
        # Dibujar el segmento de la rueda
        pygame.draw.polygon(surface, color, [CENTER, (x1, y1), (x2, y2)])
        
        # Dibujar el número en la rueda
        text = font.render(str(number), True, WHITE if color != GREEN else BLACK)
        tx, ty = CENTER[0] + (RADIUS - 30) * math.cos((angle + next_angle) / 2), CENTER[1] + (RADIUS - 30) * math.sin((angle + next_angle) / 2)
        surface.blit(text, (tx - text.get_width() // 2, ty - text.get_height() // 2))


def draw_betting_table(surface):

    """Función que dibuja la mesa de apuestas"""

    table_x, table_y = 400, 50
    cell_width, cell_height = 50, 40
    for row in range(12):
        for col in range(3):
            number = row * 3 + col + 1
            if number <= 36:
                color = RED if number % 2 == 0 else BLACK
                rect = pygame.Rect(table_x + col * cell_width, table_y + row * cell_height, cell_width, cell_height)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, WHITE, rect, 1)
                text = font.render(str(number), True, WHITE)
                surface.blit(text, (rect.x + cell_width // 2 - text.get_width() // 2, rect.y + cell_height // 2 - text.get_height() // 2))

    zero_rect = pygame.Rect(table_x - cell_width, table_y, cell_width, cell_height * 2)
    pygame.draw.rect(surface, GREEN, zero_rect)
    pygame.draw.rect(surface, WHITE, zero_rect, 1)
    text = font.render("0", True, WHITE)
    surface.blit(text, (zero_rect.x + cell_width // 2 - text.get_width() // 2, zero_rect.y + cell_height - text.get_height() // 2))


def draw_pointer(surface):

    """Función para dibujar el puntero con borde negro"""

    tip = (200, 350)
    pygame.draw.polygon(surface, BLACK, [(tip[0], tip[1]), (tip[0] - 17, tip[1] + 24), (tip[0] + 17, tip[1] + 24)])
    pygame.draw.polygon(surface, YELLOW, [(tip[0], tip[1]), (tip[0] - 10, tip[1] + 20), (tip[0] + 10, tip[1] + 20)])


def get_winning_number(angle_offset):

    """Función para obtener el número ganador"""

    segment_angle = 2 * math.pi / segments
    normalized_angle = angle_offset % (2 * math.pi)
    winning_segment = int((-normalized_angle + math.pi / 2) // segment_angle) % segments
    return NUMBERS[winning_segment]


def draw_player_chips(surface, players, start_x, start_y, spacing):

    """Función para dibujar las fichas"""

    for j, (player, data) in enumerate(players.items()):
        color = data["color"]
        chips = data["chips"]

        # Dibujar fichas
        for i, (value, count) in enumerate(chips.items()):
            x = start_x + j * spacing  
            y = start_y + i * 60 

            # Dibujar círculo
            pygame.draw.circle(surface, color, (x, y), 17)
            pygame.draw.circle(surface, BLACK, (x, y), 17, 2) 

            # Mostrar el valor de la ficha dentro del círculo
            value_text = font.render(str(value), True, BLACK)
            surface.blit(value_text, (x - value_text.get_width() // 2, y - value_text.get_height() // 2))

            # Mostrar el número de fichas al lado
            count_text = font.render(f"x{count}", True, BLACK)
            surface.blit(count_text, (x + 25, y - count_text.get_height() // 2))


def is_chip_dropped_in_betting_area(mouse_pos):

    """Función para verificar si una ficha se ha soltado en una casilla"""

    table_x, table_y = 400, 50
    cell_width, cell_height = 50, 40
    for row in range(12):
        for col in range(3):
            number = row * 3 + col + 1
            if number <= 36:
                rect = pygame.Rect(table_x + col * cell_width, table_y + row * cell_height, cell_width, cell_height)
                if rect.collidepoint(mouse_pos):
                    return number  
                
    zero_rect = pygame.Rect(table_x - cell_width, table_y, cell_width, cell_height * 2)
    if zero_rect.collidepoint(mouse_pos):
        return 0  
    return None  


def process_bets(winning_number):

    """Función para procesar las apuestas después de cada giro"""

    for player, data in players.items():
        total_winnings = 0

        winnings_to_add = []

        # Revisar todas las apuestas del jugador
        for bet_number, bet_amount in data["bets"].items():
            if bet_number == winning_number:
                winnings = bet_amount * 2  
                total_winnings += winnings

                chip_values = [100, 50, 20, 10, 5]
                for chip in chip_values:
                    while winnings >= chip:
                        winnings_to_add.append(chip)
                        winnings -= chip


        # Actualizar las fichas del jugador
        for chip in winnings_to_add:
            if chip in data["chips"]:
                data["chips"][chip] += 1  
            else:
                data["chips"][chip] = 1 

        data["bets"] = {}
        print(f"{player} gana {total_winnings} y recibe las siguientes fichas: {winnings_to_add}")


# Bucle principal del juego
running = True
while running:
    screen.fill(WHITE)
    #utils.draw_grid(pygame, screen, 50)

    # Eventos mouse
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            # Verificar si se hizo clic sobre una ficha
            for player, data in players.items():
                for value, count in data["chips"].items():
                    x = 585 + list(players.keys()).index(player) * 80  
                    y = 100 + list(data["chips"].keys()).index(value) * 60  
                    chip_rect = pygame.Rect(x - 17, y - 17, 34, 34)
                    if chip_rect.collidepoint(event.pos) and count > 0:
                        dragging_chip = value
                        dragging_player = player
                        drag_offset = (event.pos[0] - x, event.pos[1] - y)

        elif event.type == pygame.MOUSEBUTTONUP and dragging_chip is not None:

            # Verificar si se soltó sobre la mesa de apuestas
            dropped_number = is_chip_dropped_in_betting_area(event.pos)
            if dropped_number is not None:

                # Actualizar apuestas
                print(f"{dragging_player} apuesta {dragging_chip} a {dropped_number}")
                if dropped_number not in players[dragging_player]["bets"]:
                    players[dragging_player]["bets"][dropped_number] = 0
                    
                players[dragging_player]["bets"][dropped_number] += dragging_chip
                players[dragging_player]["chips"][dragging_chip] -= 1  

            dragging_chip = None
            dragging_player = None


        # Giro de la ruleta
        if event.type == pygame.MOUSEBUTTONDOWN and BUTTON_RECT.collidepoint(event.pos) and not spinning:
            spinning = True
            spin_start_time = time.time()
            final_angle = random.uniform(0, 2 * math.pi)
            initial_angle = angle_offset
            angle_increment = (final_angle - initial_angle) / (spin_duration * 185)

    # Actualización de la animación de giro
    if spinning:
        elapsed_time = time.time() - spin_start_time
        if elapsed_time < spin_duration:
            angle_offset += angle_increment
        else:
            spinning = False
            selected_number = get_winning_number(angle_offset)
            print(f"El resultado es: {selected_number}")
            process_bets(selected_number) 


    # Dibujar elementos
    draw_roulette_wheel(screen, angle_offset)
    draw_betting_table(screen)
    draw_pointer(screen)
    draw_player_chips(screen, players, 585, 100, 80)
    pygame.draw.rect(screen, YELLOW, BUTTON_RECT)
    pygame.draw.rect(screen, BLACK, BUTTON_RECT, 2)
    button_text = font.render("Girar Ruleta", True, BLACK)
    screen.blit(button_text, (BUTTON_RECT.x + BUTTON_RECT.width // 2 - button_text.get_width() // 2, BUTTON_RECT.y + BUTTON_RECT.height // 2 - button_text.get_height() // 2))


    # Dibujar la ficha arrastrada
    if dragging_chip is not None:
        drag_pos = pygame.mouse.get_pos() 
        color = players[dragging_player]["color"]
        pygame.draw.circle(screen, color, drag_pos, 17)
        pygame.draw.circle(screen, BLACK, drag_pos, 17, 2)  
        value_text = font.render(str(dragging_chip), True, BLACK)
        screen.blit(value_text, (drag_pos[0] - value_text.get_width() // 2, drag_pos[1] - value_text.get_height() // 2))

    pygame.display.flip()

pygame.quit()
