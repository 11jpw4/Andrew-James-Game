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
        #redraws the entire map, blitting over players
        for i in range(DIMENSIONS[0]):
            for j in range(DIMENSIONS[1]):
                draw_image_to_coord(self.background_layer[i][j], (i,j))
                draw_image_to_coord(self.foreground_layer[i][j], (i,j))
        
    def draw_tile(self,coordinate):
        #redraws the a single tile, blitting over players
        draw_image_to_coord(self.background_layer[coordinate[0]][coordinate[1]], coordinate)
        draw_image_to_coord(self.foreground_layer[coordinate[0]][coordinate[1]], coordinate)
    
    def is_passable(self,coordinate):
        #tests to see if the tile in question is passable
        return True
    
class Player:
    def __init__(self,location):
        self.location=location
        self.health=10
        self.item=0
    
    def move(self,direction,distance,game_map):
        #moves the player in the direction desired if possible
        #direction is a tuple either (1,0),(-1,0),(0,1) or (0,-1)
        for _ in range(distance):   
            
            if game_map.is_passable(add_coords(self.location,direction)):
                game_map.draw_tile(self,coordinate)
                self.location = add_coords(self.location,direction)
                self.draw_player()
            else:
                #break out of the loop if the player encounters an obstacle 
                break
                
    def draw_player(self):
        pass
        
        

def add_coords(coord1,coord2):
    # adds two tuples of coordinates together keeping in mind map wrapping, returns a tuple
    return ((coord1[0]+coord2[0])%DIMENSIONS[0],(coord1[1]+coord2[1])%DIMENSIONS[1])
        
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