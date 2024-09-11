import pygame as py
import pygame_widgets as pyw
from pygame_widgets.slider import Slider
import random
import concurrent.futures

from Boid import Boid, CELS_PER_AXIS, AVG_SIZE, set_max_force, set_max_speed, set_resolution
from Text import Text

def print_matriz(matriz: list)->None:
    print("\n\n")
    for fila in matriz:
        print("[ ", end="")
        for element in fila:
            print("[", end="")
            for e in element:
                print(str(e), end="")
            print("]", end=" ")
        print("]")

def main() -> None:
    # ================ DEFAULT VALUES ================
    REFERENCE_FPS = 1200
    BLUE: tuple = (27, 78, 207)
    RED: tuple = (232, 57, 51)
    GREEN: tuple = (72, 232, 51)
    PURPLE: tuple = (202, 67, 230)

    COLORS: list[tuple] = [BLUE, RED, GREEN, PURPLE]
    # ================ BASE ================
    py.init()
    infoObject = py.display.Info()
    set_resolution(infoObject.current_w, infoObject.current_h)
    SCREEN_WIDTH = infoObject.current_w; SCREEN_HEIGHT = infoObject.current_h
    CEL_GAP_X = SCREEN_WIDTH/CELS_PER_AXIS; CEL_GAP_Y = SCREEN_HEIGHT/CELS_PER_AXIS
    #SCREEN_WIDTH = 1400; SCREEN_HEIGHT = 700
    SCREEN = py.display.set_mode((infoObject.current_w, infoObject.current_h)) #, py.FULLSCREEN
    #SCREEN = py.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #, py.FULLSCREEN
    py.display.set_caption('Py Boid simulation')
    CLOCK = py.time.Clock()

    text_size: int = 15
    text_offSet: int = 10
    slider_sizeX: int = 50
    slider_sizeY: int = 10
    slider_offSetX: int = 75
    slider_offSetY: int = 25
    text_font = py.font.SysFont("Arial", text_size)

    def draw_text(textToRender: Text) -> None:
        img = text_font.render(str(textToRender), True, textToRender.text_col)
        SCREEN.blit(img, textToRender.pos)

    AlignmentText = Text("Alignment (1)",True, 10, SCREEN_HEIGHT - text_size*1 - text_offSet)
    CohesionText = Text("Cohesion (2)",True, 10, SCREEN_HEIGHT - text_size*2 - text_offSet)
    SeparationText = Text("Separation (3)",True, 10, SCREEN_HEIGHT - text_size*3 - text_offSet)
    FPSText = Text("FPS", 60,10, text_size*0 + text_offSet)
    BOIDSText = Text("BOIDS", 0,10, text_size*1 + text_offSet)
    BOIDSInfo1Text = Text("Add (Click / Scroll)",None,10, text_size*2 + text_offSet)
    BOIDSInfo2Text = Text("Remove (Q)",None,10, text_size*3 + text_offSet)
    BOIDSInfo3Text = Text("Rotate (R)",None,10, text_size*4 + text_offSet)
    BOIDSInfo4Text = Text("Random (T)",None,10, text_size*5 + text_offSet)


    FORCESlider = Slider(SCREEN,
                    SCREEN_WIDTH - slider_offSetX,
                    SCREEN_HEIGHT - slider_offSetY, slider_sizeX, slider_sizeY,
                    min=0, max=10, step=0.5, initial=1, handleColour=BLUE)
    FORCEText = Text("FORCE", 100,
                     SCREEN_WIDTH - slider_offSetX - text_offSet,
                     SCREEN_HEIGHT - slider_offSetY*2)

    SPEEDSlider = Slider(SCREEN,
                         SCREEN_WIDTH - slider_offSetX*2,
                         SCREEN_HEIGHT - slider_offSetY, slider_sizeX, slider_sizeY,
                         min=0.01, max=500, step=5, initial=200, handleColour=BLUE)
    SPEEDText = Text("SPEED", 100,
                     SCREEN_WIDTH - slider_offSetX*2 - text_offSet,
                     SCREEN_HEIGHT - slider_offSetY * 2)

    SIMULATIONSlider = Slider(SCREEN,
                         int(SCREEN_WIDTH - slider_offSetX * 3.5),
                         SCREEN_HEIGHT - slider_offSetY, slider_sizeX, slider_sizeY,
                         min=0.001, max=5, step=0.5, initial=1, handleColour=BLUE)
    SIMULATIONText = Text("SIMULATION X", 100,
                     SCREEN_WIDTH - slider_offSetX * 3.75,
                     SCREEN_HEIGHT - slider_offSetY * 2)

    TEXTS = [AlignmentText,CohesionText,SeparationText,FPSText, BOIDSText,
             FORCEText, SPEEDText,SIMULATIONText, BOIDSInfo1Text, BOIDSInfo2Text, BOIDSInfo3Text, BOIDSInfo4Text]


    # ================ COMPONENTS ================
    BOIDS_MATRIX = []

    for i,_ in enumerate(range(CELS_PER_AXIS)):
        BOIDS_MATRIX.append([])
        for _ in range(CELS_PER_AXIS):
            BOIDS_MATRIX[i].append([])

    BOIDS: list[Boid] = []

    def add_boid(x: float = None, y: float = None):
        if x is None: x = random.uniform(0, SCREEN_WIDTH)
        if y is None: y = random.uniform(0, SCREEN_HEIGHT)

        newBoid: Boid = Boid(x=x, y=y, size=AVG_SIZE, color=random.choice(COLORS), matrix=BOIDS_MATRIX)
        newBoid.switch_alignment(bool(AlignmentText.get_value()))
        newBoid.switch_cohesion(bool(CohesionText.get_value()))
        newBoid.switch_separation(bool(SeparationText.get_value()))

        BOIDSText.set_value(int(BOIDSText.get_value()) + 1)
        BOIDS.append(newBoid)

    def remove_boid():
        if int(BOIDSText.get_value()) <= 0: return
        BOIDSText.set_value(int(BOIDSText.get_value()) -1)
        boid = BOIDS.pop(random.randrange(0,len(BOIDS)))
        boid.remove_from_matrix()

    for x in range(100):
        add_boid()

    # ================ RUNNING LOOP ================
    RUNNING_GAME: bool = True
    #with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
    while RUNNING_GAME:
        #print_matriz(BOIDS_MATRIX)
        # ================ BASE ================
        SCREEN.fill((0,0,0))
        deltaTime = CLOCK.tick(REFERENCE_FPS) / 1000.0 * SIMULATIONSlider.getValue()
        if deltaTime == 0: continue
        FPSText.set_value(round(1/deltaTime, 2))

        # ================ SHOW CELLS ================
        for i in range(1, CELS_PER_AXIS):
            pointX = i * CEL_GAP_X
            for j in range(1, CELS_PER_AXIS):
                pointY = j * CEL_GAP_Y
                py.draw.circle(SCREEN, BLUE, (pointX, pointY), 1)
        # ================ COMPONENTS ================
        '''futures = [executor.submit(process_boid, boid, SCREEN, deltaTime) for boid in BOIDS]
        # Wait for all the boids
        concurrent.futures.wait(futures)'''
        for boid in BOIDS:
            boid.draw(SCREEN)
            boid.boid_movement(deltaTime)

        for text in TEXTS:
            draw_text(text)

        # ================ KEYS ================
        key = py.key.get_pressed()
        if key[py.K_q]:
            remove_boid()
        if key[py.K_r]:
            for boid in BOIDS:
                boid.change_velocity_direction(250*deltaTime)
        if key[py.K_t]:
            for boid in BOIDS:
                boid.change_velocity_direction(random.uniform(-50,50))
        if key[py.K_a]:
            for boid in BOIDS:
                boid.move_left(deltaTime=deltaTime)
        if key[py.K_d]:
            for boid in BOIDS:
                boid.move_right(deltaTime=deltaTime)
        if key[py.K_w]:
            for boid in BOIDS:
                boid.move_up(deltaTime=deltaTime)
        if key[py.K_s]:
            for boid in BOIDS:
                boid.move_down(deltaTime=deltaTime)

        # ================ EVENT HANDLER LOOP ================
        events = py.event.get()
        for event in events:
            if event.type == py.QUIT: RUNNING_GAME = False; break
            elif event.type == py.MOUSEBUTTONUP:
                pos = py.mouse.get_pos()
                add_boid(pos[0], pos[1])

            elif event.type == py.KEYUP:
                if event.key == py.K_ESCAPE: RUNNING_GAME = False; break
                if event.key == py.K_1:
                    AlignmentText.set_value(not bool(AlignmentText.get_value()))
                    for boid in BOIDS:
                        boid.switch_alignment(bool(AlignmentText.get_value()))
                if event.key == py.K_2:
                    CohesionText.set_value(not bool(CohesionText.get_value()))
                    for boid in BOIDS:
                        boid.switch_cohesion(bool(CohesionText.get_value()))
                if event.key == py.K_3:
                    SeparationText.set_value(not bool(SeparationText.get_value()))
                    for boid in BOIDS:
                        boid.switch_separation(bool(SeparationText.get_value()))

        # ================ SLIDER PARAMS ================
        set_max_force(FORCESlider.getValue())
        FORCEText.set_value(FORCESlider.getValue()*100)

        set_max_speed(SPEEDSlider.getValue())
        SPEEDText.set_value(SPEEDSlider.getValue())

        SIMULATIONText.set_value(round(SIMULATIONSlider.getValue(),2))

        pyw.update(events)
        py.display.update()
    py.quit()


if __name__ == '__main__':
    main()