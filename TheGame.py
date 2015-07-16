import sys
import pygame
from pygame.locals import *
import spritesheet

SURFACE = pygame.display.set_mode((640,640))

#this is everything I could have ever asked for and more

FPS = 60
clock = pygame.time.Clock()
SURFACE.fill(pygame.Color('black'))

ss = spritesheet.spritesheet('sprite test/Spritesheet/roguelikeSheet_transparent.png')
# Sprite is 16x16 pixels at location 0,0 in the file...
# Load  images into an array, their transparent bit is (255, 255, 255)
images = [ss.images_at([(17*i, 17*j, 16,16) for i in range(50)],colorkey=(255, 255, 255)) for j in range(36)]



def main():
    game_loop()

def draw_image_to_coord(img_location, draw_location):
    '''Takes as input two tuple, this first being the location on the spritesheet of the image
    The second tuple is the coordinate of the location where the image should be blitted to on the screen
    both use 0,0 as the top left corner 
    '''
    blit_location=(draw_location[0]*16,draw_location[1]*16)
    SURFACE.blit(images[img_location[0]][img_location[1]], blit_location)


def game_loop():   
    #this function contain the main game loop
    
    while True:
    # this is the main game loop
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
        
        
        

        pygame.display.flip() # this draws all the updates to the screen
        clock.tick(FPS) 
    
if __name__ == "__main__":
    main()