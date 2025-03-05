import pygame
import random
import animation_algo.heap_sort_animation as heap_sort_animation
import animation_algo.merge_sort_animation as merge_sort_animation
import animation_algo.quick_sort_animation as quick_sort_animation
import animation_algo.radix_sort_animation as radix_sort_animation


# Initialize pygame
pygame.init()

# Window settings
WIDTH, HEIGHT = 1200, 600
BAR_WIDTH = 20
BAR_SPACING = 5
LEFT_MARGIN = 50
RIGHT_MARGIN = 50
NUM_BARS = (WIDTH - LEFT_MARGIN - RIGHT_MARGIN) // (BAR_WIDTH + BAR_SPACING)
FPS = 60
BOTTOM_MARGIN = 50

# Limit the range of generated numbers
MIN_VALUE = 10
MAX_VALUE = 200

# Pastel Colors
BACKGROUND_COLOR = (245, 245, 245)  # Very soft background
BAR_COLOR = (160, 216, 239)  # Pastel Sky Blue
COMPARE_COLOR = (255, 168, 168)  # Pastel Soft Red
SWAP_COLOR = (168, 230, 168)  # Pastel Soft Green
LINE_COLOR = (255, 102, 102)  # Soft Red Line
TEXT_COLOR = (120, 80, 80)  # Darker Brown-Red for better contrast
DISABLED_COLOR = (210, 210, 210)  # Soft Gray for disabled buttons

# Pastel Buttons
BUTTON_COLORS = {
    "Start Sorting": (178, 230, 212),  # Pastel Teal
    "Reset": (212, 212, 212),  # Pastel Gray
    "Pause/Resume": (255, 239, 161),  # Pastel Yellow
    "Quit": (255, 178, 168)  # Pastel Coral Red
}

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sorting Algorithm Visualization")

# Button settings
BUTTONS = [
    ("Start Sorting", 10, 10, 140, 30),
    ("Reset", 160, 10, 140, 30),
    ("Pause/Resume", 310, 10, 160, 30),
    ("Quit", 480, 10, 140, 30),
]

SORTING_ALGORITHMS = {
    "Bubble Sort": "bubble_sort",
    "Quick Sort (Standard)": "quick_sort",
    "Quick Sort (Optimized)": "optimized_quick_sort",
    "Merge Sort (Top-Down)": "merge_sort",
    "Merge Sort (Bottom-Up)": "bottom_up_merge_sort",
    "Heap Sort (Binary)": "heap_sort",
    "Heap Sort (Ternary)": "heap_sort_ternary",
    "Radix Sort (LSD)": "radix_sort",
    "Radix Sort (MSD)": "iterative_msd_radix_sort"
}
selected_algorithm = "Bubble Sort"  # Default selection
dropdown_open = False



# Generate random bars with a limit
def generate_array():
    return [random.randint(MIN_VALUE, MAX_VALUE) for _ in range(NUM_BARS)]


# Draw bars with numbers and spacing
def draw_array(array, highlight1=None, highlight2=None):
    screen.fill(BACKGROUND_COLOR)

    # Draw reference horizontal line
    pygame.draw.line(screen, LINE_COLOR, (LEFT_MARGIN, HEIGHT - BOTTOM_MARGIN), (WIDTH - RIGHT_MARGIN, HEIGHT - BOTTOM_MARGIN), 2)

    # Draw bars
    for index, value in enumerate(array):
        x_position = LEFT_MARGIN + index * (BAR_WIDTH + BAR_SPACING)
        color = BAR_COLOR

        if index == highlight1:
            color = COMPARE_COLOR
        elif index == highlight2:
            color = SWAP_COLOR

        pygame.draw.rect(screen, color, (x_position, HEIGHT - value - BOTTOM_MARGIN, BAR_WIDTH, value))
        draw_text(str(value), (x_position + 5, HEIGHT - 30), TEXT_COLOR, 14)

    # Draw buttons
    draw_buttons()
    pygame.display.update()


# Draw text on screen
def draw_text(text, position, color, size):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)


# Bubble Sort (generator-based animation)
def bubble_sort(array, draw_array, delay):
    global last_highlight1, last_highlight2
    n = len(array)
    for i in range(n):
        for j in range(n - i - 1):
            if paused:
                yield  # Pause execution if sorting is paused
            last_highlight1, last_highlight2 = j, j + 1  # Save last highlighted bars
            draw_array(array, last_highlight1, last_highlight2)
            pygame.time.delay(40)
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]
            yield  # Yield allows for better animation control
    last_highlight1, last_highlight2 = None, None  # Clear highlights after sorting is done
    draw_array(array)


# Event handling
def check_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            check_button_click(event.pos)


# Handle button clicks
def check_button_click(pos):
    global sorting, sort_generator, array, paused, sorting_done, last_highlight1, last_highlight2, selected_algorithm, dropdown_open

    x, y = pos
    dropdown_x, dropdown_y, dropdown_w, dropdown_h = 650, 10, 200, 30

    # Toggle dropdown open/close
    if dropdown_x <= x <= dropdown_x + dropdown_w and dropdown_y <= y <= dropdown_y + dropdown_h:
        dropdown_open = not dropdown_open
        return

    # Handle dropdown selection
    if dropdown_open:
        for i, algo in enumerate(SORTING_ALGORITHMS.keys()):
            option_y = dropdown_y + (i + 1) * dropdown_h
            if dropdown_x <= x <= dropdown_x + dropdown_w and option_y <= y <= option_y + dropdown_h:
                selected_algorithm = algo
                dropdown_open = False
                return

    # Handle button clicks
    if 10 <= x <= 150 and 10 <= y <= 40 and not sorting and not sorting_done:  # Start Sorting
        sorting = True
        algorithm_function = SORTING_ALGORITHMS[selected_algorithm]

        SORTING_MODULES = {
            "quick_sort_animation": quick_sort_animation,
            "merge_sort_animation": merge_sort_animation,
            "heap_sort_animation": heap_sort_animation,
            "radix_sort_animation": radix_sort_animation,
        }

        for module_name, module in SORTING_MODULES.items():
            if hasattr(module, algorithm_function):
                sort_generator = getattr(module, algorithm_function)(array, draw_array, 40)  # Pass draw_array & delay
                break



    elif 160 <= x <= 300 and 10 <= y <= 40 and not sorting:  # Reset
        array = generate_array()
        sorting = False
        sorting_done = False
        sort_generator = None
        last_highlight1, last_highlight2 = None, None  # Clear highlights on reset
        draw_array(array)
    elif 310 <= x <= 470 and 10 <= y <= 40 and sorting:  # Pause/Resume
        paused = not paused
        if paused:
            draw_array(array, last_highlight1, last_highlight2)  # Keep colors on pause
    elif 480 <= x <= 620 and 10 <= y <= 40:  # Quit
        pygame.quit()
        exit()



# Draw buttons with dynamic pastel colors
def draw_buttons():
    font = pygame.font.Font(None, 30)

    for text, x, y, w, h in BUTTONS:
        color = BUTTON_COLORS[text]
        if sorting or sorting_done:  # Disable Start Sorting and Reset while sorting
            if text in ("Start Sorting", "Reset"):
                pygame.draw.rect(screen, DISABLED_COLOR, (x, y, w, h), border_radius=10)
                text_surface = font.render(text, True, (100, 100, 100))  # Darker text for disabled buttons
            else:
                pygame.draw.rect(screen, color, (x, y, w, h), border_radius=10)
                text_surface = font.render(text, True, (0, 0, 0))
        else:
            pygame.draw.rect(screen, color, (x, y, w, h), border_radius=10)
            text_surface = font.render(text, True, (0, 0, 0))

        screen.blit(text_surface, (x + 10, y + 5))

    # Draw dropdown menu
    dropdown_x, dropdown_y, dropdown_w, dropdown_h = 650, 10, 200, 30
    pygame.draw.rect(screen, (230, 230, 230), (dropdown_x, dropdown_y, dropdown_w, dropdown_h), border_radius=10)
    dropdown_text = font.render(selected_algorithm, True, (0, 0, 0))
    screen.blit(dropdown_text, (dropdown_x + 10, dropdown_y + 5))

    # Draw dropdown options if open
    if dropdown_open:
        for i, algo in enumerate(SORTING_ALGORITHMS.keys()):
            option_y = dropdown_y + (i + 1) * dropdown_h
            pygame.draw.rect(screen, (245, 245, 245), (dropdown_x, option_y, dropdown_w, dropdown_h), border_radius=10)
            option_text = font.render(algo, True, (0, 0, 0))
            screen.blit(option_text, (dropdown_x + 10, option_y + 5))


# Main loop
array = generate_array()
sorting = False
sorting_done = False
paused = False
sort_generator = None
last_highlight1, last_highlight2 = None, None

clock = pygame.time.Clock()

while True:
    check_events()
    draw_array(array, last_highlight1, last_highlight2)  # Keep last highlights visible

    if sorting and sort_generator:
        try:
            if not paused:
                next(sort_generator)  # Step through the generator
        except StopIteration:
            sorting = False
            sorting_done = True  # Sorting is done, must reset before sorting again

    pygame.display.update()
    clock.tick(FPS)
