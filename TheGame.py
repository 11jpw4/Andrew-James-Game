import sys
import pygame
import numpy as np
from pygame.locals import *
from utilities.spritesheet import spritesheet # for loading the spritesheet
import os # for paths

DIMENSIONS=(40,40) 
SURFACE = pygame.display.set_mode((16*DIMENSIONS[0],16*DIMENSIONS[1])) # each tile is 16 pixels wide

#this is everything I could have ever asked for and more

FPS = 60
clock = pygame.time.Clock()
SURFACE.fill(pygame.Color('black'))

ss = spritesheet(os.path.join('spritesheet/roguelikeSheet_transparent.png'))
# Sprite is 16x16 pixels at location 0,0 in the file...
# Load  images into an array, their transparent bit is (255, 255, 255)
images = [ss.images_at([(17*j, 17*i, 16,16) for i in range(57)],colorkey=(255, 255, 255)) for j in range(36)]



def main():
    game_map=GameMap()
    print game_map
    game_loop(game_map)
    

class GameMap:
    ''' The map is stored as  a collection of 40 by 40 2d arrays
        each representing one layer of the game world.
    
    ----tile-legend----
    #-terrain 1...coord
    # 
    
    
    
    
    '''
    def __init__(self):
        self.background_layer= np.array([[(0,0)]*40]*40)   
        self.foreground_layer= np.array([[(14,5)]*40]*40)
    
    def draw_all(self):
        for i in range(DIMENSIONS[0]):
            for j in range(DIMENSIONS[1]):
                draw_image_to_coord(self.background_layer[i][j], (i,j))
                draw_image_to_coord(self.foreground_layer[i][j], (i,j))
    
def draw_image_to_coord(img_location, draw_location):
    '''Takes as input two tuple, this first being the location on the spritesheet of the image
    The second tuple is the coordinate of the location where the image should be blitted to on the screen
    both use 0,0 as the top left corner 
    '''
    blit_location=(draw_location[0]*16,draw_location[1]*16)
    SURFACE.blit(images[img_location[0]][img_location[1]], blit_location)


def game_loop(game_map):   
    #this function contain the main game loop
    game_map.draw_all()
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