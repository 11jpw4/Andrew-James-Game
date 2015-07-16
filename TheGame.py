import sys
import pygame
import numpy as np
from pygame.locals import *
from utilities.spritesheet import spritesheet # for loading the spritesheet
import os # for paths


'''
    -RULES-
    TBD
    
    -CONTROLS- 
    PLAYER1 arrow keys
    PLAYER2 WASD
     
'''

DIMENSIONS=(40,40) 
SURFACE = pygame.display.set_mode((16*DIMENSIONS[0],16*DIMENSIONS[1]+32)) # each tile is 16 pixels wide additionally two tiles are used for the HUD at the bottom

#this is everything I could have ever asked for and more

FPS = 30
clock = pygame.time.Clock()
SURFACE.fill(pygame.Color('black'))

ss = spritesheet(os.path.join('spritesheet/roguelikeSheet_transparent.png'))
char_ss = spritesheet(os.path.join('spritesheet/roguelikeChar_transparent.png'))
# Sprite is 16x16 pixels at location 0,0 in the file...
# Load  images into an array, their transparent bit is (255, 255, 255)
images = [ss.images_at([(17*j, 17*i, 16,16) for i in range(36)],colorkey=(255, 255, 255)) for j in range(57)]
char_images = [char_ss.images_at([(17*j, 17*i, 16,16) for i in range(12)],colorkey=(255, 255, 255)) for j in range(54)]



def main():
    game_map=GameMap()
    
    player1=Player(location=(2,2),appearance=(0,0,0,0,0,0),id=1)
    player2=Player(location=(10,30),appearance=(2,0,0,0,0,0),id=2)
    players=[player1,player2]
    
    status_bar=StatusBar(player1.health,player2.health)
    game_loop(game_map,players,status_bar)
    

class GameMap:
    ''' The map is stored as  a collection of 40 by 40 2d arrays
        each representing one layer of the game world.
    
    ----tile-legend----
    #(-1,-1) is an empty foreground tile
    
     
    '''
    def __init__(self):
        self.background_layer= np.array([[(5,0)]*40]*40)   
        self.foreground_layer= np.array([[(-1,-1)]*40]*40)
        self.interactive_layer= np.array([[((-1,-1),ss)]*40]*40) #interactive layer also specifies spritesheet
        listTrees = [(3,3),(7,5),(11,9),(33,29),(18,22),(32,22)]
        listWater = [(5,34),(6,34),(7,34),(5,33),(6,33),(7,33),(5,32),(6,32),(7,32)]
        listWaterUpEdge = [(5,31),(6,31),(7,31)]
        listWaterDownEdge = [(5,35),(6,35),(7,35)]
        listWaterLeftEdge = [(4,32),(4,33),(4,34)]
        listWaterRightEdge = [(8,32),(8,33),(8,34)]
        for i,j in listTrees:
        	self.foreground_layer[i][j]=(13,9)
        for i,j in listWater:
        	self.foreground_layer[i][j]=(3,1)
        for i,j in listWaterUpEdge:
        	self.foreground_layer[i][j]=(3,0)
        for i,j in listWaterDownEdge:
        	self.foreground_layer[i][j]=(3,2)
        for i,j in listWaterLeftEdge:
        	self.foreground_layer[i][j]=(2,1)
        for i,j in listWaterRightEdge:
        	self.foreground_layer[i][j]=(4,1)
        #Edges
        self.foreground_layer[4][31]=(2,0)
        self.foreground_layer[8][31]=(4,0)
        self.foreground_layer[4][35]=(2,2)
        self.foreground_layer[8][35]=(4,2)









    
    def draw_all(self):
        #redraws the entire map, blitting over players
        for i in range(DIMENSIONS[0]):
            for j in range(DIMENSIONS[1]):
                self.draw_tile((i,j))
        
    def draw_tile(self,coordinate):
        #redraws the a single tile, blitting over players
        draw_image_to_coord(self.background_layer[coordinate], coordinate)
        if self.foreground_layer[coordinate][0] != -1: draw_image_to_coord (self.foreground_layer[coordinate[0]][coordinate[1]], coordinate)
        if self.interactive_layer[coordinate][0][0] != -1: draw_image_to_coord (self.foreground_layer[coordinate][0], coordinate,images_list=self.foreground_layer[coordinate][1])
    
    def is_passable(self,coordinate):
        #tests to see if the tile in question is passable
        listImpassable = [(13,9), (3,1), (3,0), (3,2), (2,1), (4,1), (2,0), (4,0), (2,2), (4,2)]
        if tuple(self.foreground_layer[coordinate[0]][coordinate[1]]) in listImpassable :
        	return False
        return True
    
class Player:
    def __init__(self,location,appearance,id):
        self.location=location
        self.appearance= appearance
        ''' appearance is a length 6 tuple
            body type : 0-3
            pant type : 0-9  4 and 9 are for dresses
            shirt type: guhhh
            hair type: 
            beard type:
        '''
        self.health=10
        self.id= id
        self.item=[]
    
    def move(self,direction,distance,game_map,players):
        #moves the player in the direction desired if possible
        #direction is a tuple either (1,0),(-1,0),(0,1) or (0,-1)
        for _ in range(distance):   
            destination=add_coords(self.location,direction)
            if game_map.is_passable(destination) and  players[not(self.id-1)].location!=destination: #check to see if movement is valid
                game_map.draw_tile(self.location)
                self.location = add_coords(self.location,direction)
            else:
                #break out of the loop if the player encounters an obstacle 
                break
                
    def draw_player(self):
        #draw the player and all their items        
        draw_image_to_coord((0, self.appearance[0]), self.location, images_list=char_images) # draw the body
    
    def interact(self,game_map):
        #interact with the map
        for direction in [(i,j) for i in range(-1,2) for j in range(-1,2)]:
        
            object= game_map.interactive_layer[add_coords(self.location,direction)]
            if object == (5,5): #example
                self.item+=5
                
        
class StatusBar:
    def __init__(self,player1_hp,player2_hp):
        self.player1_hp=player1_hp
        self.player2_hp=player2_hp
        
    def draw_all(self):
        # updates the status bar at the bottom of the screen
        for i in range(40): #paint a background
            draw_image_to_coord((45,26), (i,40))
            draw_image_to_coord((45,26), (i,41))
        
        # player1  ----------------------------------------      
        if self.player1_hp > 0 :
            draw_image_to_coord((33,27), (5,41))
        else: 
            draw_image_to_coord((33,28), (5,41))
        for i in range(1,10):
            if self.player1_hp > i:
                draw_image_to_coord((31,27), (5+i,41))
            else:
                draw_image_to_coord((31,28), (5+i,41))
        if self.player1_hp == 10 :
            draw_image_to_coord((34,27), (15,41))
        else: 
            draw_image_to_coord((34,28), (15,41))
            
            
        # player2  ----------------------------------------      
        if self.player2_hp > 0 :
            draw_image_to_coord((34,29), (34,41))
        else: 
            draw_image_to_coord((34,30), (34,41))
        for i in range(1,10):
            if self.player2_hp > i:
                draw_image_to_coord((31,29), (34-i,41))
            else:
                draw_image_to_coord((31,30), (34-i,41))
        if self.player2_hp == 10 :
            draw_image_to_coord((33,29), (24,41))
        else: 
            draw_image_to_coord((33,30), (24,41))
        
        

def add_coords(coord1,coord2):
    # adds two tuples of coordinates together keeping in mind map wrapping, returns a tuple
    return ((coord1[0]+coord2[0])%DIMENSIONS[0],(coord1[1]+coord2[1])%DIMENSIONS[1])
        
def draw_image_to_coord(img_location, draw_location, images_list=images):
    '''Takes as input two tuple, this first being the location on the spritesheet of the image
    The second tuple is the coordinate of the location where the image should be blitted to on the screen
    both use 0,0 as the top left corner 
    '''
    blit_location=(draw_location[0]*16,draw_location[1]*16)
    SURFACE.blit(images_list[img_location[0]][img_location[1]], blit_location)


def game_loop(game_map,players,status_bar):   
    #this function contain the main game loop
    game_map.draw_all()
    status_bar.draw_all()
    while True:
    # this is the main game loop
        
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
        
        keys = pygame.key.get_pressed()  #checking pressed keys
        
        if keys[pygame.K_UP] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_DOWN]:
            #player1's movement 
            if keys[pygame.K_UP]: direction= (0,-1)
            elif keys[pygame.K_DOWN]: direction= (0,1)
            elif keys[pygame.K_RIGHT]: direction= (1,0)
            elif keys[pygame.K_LEFT]: direction= (-1,0)
            players[0].move(direction,1,game_map,players)
            
            
        if keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_s] or keys[pygame.K_w]:
            #player2's movement 
            if keys[pygame.K_w]: direction= (0,-1)
            elif keys[pygame.K_s]: direction= (0,1)
            elif keys[pygame.K_d]: direction= (1,0)
            elif keys[pygame.K_a]: direction= (-1,0)
            players[1].move(direction,1,game_map,players)
            
        
        for player in players: 
            #redraw the players each frame
            player.draw_player()
        
        pygame.display.flip() # this draws all the updates to the screen
        clock.tick(FPS) 
    
if __name__ == "__main__":
    main()