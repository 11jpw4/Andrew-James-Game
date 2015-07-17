import sys
import pygame
import numpy as np
from pygame.locals import *
from utilities.spritesheet import spritesheet # for loading the spritesheet
import os # for paths
import random


'''
    -RULES-
    TBD
    
    -CONTROLS- 
    PLAYER1 arrow keys
    PLAYER2 WASD
     
'''

DIMENSIONS=(40,40) 
DEBUG=True
SURFACE = pygame.display.set_mode((16*DIMENSIONS[0],16*DIMENSIONS[1]+32)) # each tile is 16 pixels wide additionally two tiles are used for the HUD at the bottom

#this is everything I could have ever asked for and more
pygame.init()
myfont = pygame.font.SysFont("monospace", 10)
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
    
    status_bar=StatusBar(players)
    game_loop(game_map,players,status_bar)
    

class GameMap:
    ''' The map is stored as  a collection of 40 by 40 2d arrays
        each representing one layer of the game world.
    
    ----tile-legend----
    #(-1,-1) is an empty foreground tile
    
     
    '''
    def __init__(self):
        self.background_layer= np.array([[(5,0)]*40]*40)   
        self.background_layer2= np.array([[(0,5)]*40]*40)   
        self.foreground_layer= np.array([[(-1,-1)]*40]*40)
        self.interactive_layer= np.array([[((-1,-1),0)]*40]*40) #interactive layer also specifies spritesheet
        
        self.interactive_layer[20][20]=((47,1),1)

        self.interactive_layer[33][11]=((36,3),1)
        
        #trees, bushes and grasses
        list_trees = [(3,3),(7,5),(11,9),(33,29),(18,22),(32,22)]
        list_cacti = [(27,1),(31,7),(33,4),(37,15),(33,13)]
        list_cacti2 = [(27,5),(35,8)]
        list_cacti3 = [(31,11),(38,6)]
        list_bushes = [(22,38), (24,38), (2,30), (26,24)]
        list_grass1 = [(15,15),(24,18),(16,36),(24,11)]
        list_grass2 = [(22,17),(32,37),(36,21),(4,28),(5,12)]
        list_tall_dg_tree_base=[(4,17),(30,32),(26,31)]
        list_tall_dg_tree_top=[add_coords(x,(0,-1)) for x in list_tall_dg_tree_base]

        
        # water tiles
        list_water = [(5,34),(6,34),(7,34),(5,33),(6,33),(7,33),(5,32),(6,32),(7,32)] +[(15,8),(16,8),(17,8),(17,7),(10,7)]+[(17,8+i) for i in range(4)]
        list_water_up_edge = [(5,31),(6,31),(7,31)] + [(12+i,7) for i in range(4)]+[(10,6)]
        list_water_down_edge = [(5,35),(6,35),(7,35)] +[(11,8),(12,8),(13,8),(15,9),(10,8),(19,14)]
        list_water_left_edge = [(4,32),(4,33),(4,34)] +[(17,i)for i in range(1,6)]+[(9,7),(16,10),(16,11)]
        list_water_right_edge = [(8,32),(8,33),(8,34)]+[(18,i)for i in range(2,12)]+[(19,0)]
        list_water_top_right_land_tiny=[(11,7),(18,12),(19,13)]
        list_water_bot_right_land_tiny=[(18,1)]
        list_water_top_left_land_tiny=[(16,7),(17,6),(18,0)]
        list_water_bot_left_land_tiny=[(14,8),(16,9),(17,12),(18,13)]
        list_water_bot_left_land_big=[(14,9),(9,8),(16,12),(17,13),(18,14)]
        list_water_bot_right_land_big=[(19,1),(20,14)]
        list_water_top_left_land_big=[(16,6),(17,0),(9,6)]
        list_water_top_right_land_big=[(11,6),(19,12),(20,13)]
        #desert corner
       	desert_count = 20
        list_desert_tiles=[]
        while desert_count <= 40:
            list_desert_tiles += [(desert_count+i,0+i) for i in range(14-(desert_count-25))]
            desert_count = desert_count + 1
        list_desert_tiles += [(39,0+i) for i in range(20)]    
        for i,j in list_desert_tiles:
        	self.background_layer[i][j]=(8,22)
        	
        desert_bottom_left=[(19+i,i) for i in range(1,21)]
        for i,j in desert_bottom_left:
        	self.background_layer2[i][j]=(7,23)
        
        for i,j in list_trees:
        	self.foreground_layer[i][j]=(13,9)
        for i,j in list_grass1:
        	self.foreground_layer[i][j]=(22,10)
        for i,j in list_grass2:
        	self.foreground_layer[i][j]=(22,11)
        for i,j in list_tall_dg_tree_base:
        	self.foreground_layer[i][j]=(15,11)
        for i,j in list_tall_dg_tree_top:
        	self.foreground_layer[i][j]=(15,10)
        for i,j in list_bushes:
        	self.foreground_layer[i][j]=(24,10)
        for i,j in list_cacti:
        	self.foreground_layer[i][j]=(22,9)
        for i,j in list_cacti2:
        	self.foreground_layer[i][j]=(26,10)
        for i,j in list_cacti3:
        	self.foreground_layer[i][j]=(26,11)

        for i,j in list_water:
        	self.background_layer[i][j]=(3,1)
        for i,j in list_water_up_edge:
        	self.background_layer[i][j]=(3,0)
        for i,j in list_water_down_edge:
        	self.background_layer[i][j]=(3,2)
        for i,j in list_water_left_edge:
        	self.background_layer[i][j]=(2,1)
        for i,j in list_water_right_edge:
        	self.background_layer[i][j]=(4,1)
        for i,j in list_water_top_right_land_tiny:
        	self.background_layer[i][j]=(0,2)
        for i,j in list_water_bot_left_land_tiny:
        	self.background_layer[i][j]=(1,1)
        for i,j in list_water_bot_right_land_tiny:
        	self.background_layer[i][j]=(0,1)
        for i,j in list_water_top_left_land_tiny:
        	self.background_layer[i][j]=(1,2)
        for i,j in list_water_bot_left_land_big:
        	self.background_layer[i][j]=(2,2)
        for i,j in list_water_top_left_land_big:
        	self.background_layer[i][j]=(2,0)
        for i,j in list_water_bot_right_land_big:
        	self.background_layer[i][j]=(4,2)
        for i,j in list_water_top_right_land_big:
        	self.background_layer[i][j]=(4,0)
        #Edges
        self.background_layer[4][31]=(2,0)
        self.background_layer[8][31]=(4,0)
        self.background_layer[4][35]=(2,2)
        self.background_layer[8][35]=(4,2)

        









    
    def draw_all(self):
        #redraws the entire map, blitting over players
        for i in range(DIMENSIONS[0]):
            for j in range(DIMENSIONS[1]):
                self.draw_tile((i,j))
        
    def draw_tile(self,coordinate):
        #redraws the a single tile, blitting over players
        draw_image_to_coord(self.background_layer[coordinate], coordinate)
        draw_image_to_coord(self.background_layer2[coordinate], coordinate)
        
        if self.foreground_layer[coordinate][0] != -1: draw_image_to_coord (self.foreground_layer[coordinate[0]][coordinate[1]], coordinate)
        if self.interactive_layer[coordinate][0][0] != -1: 
            if self.interactive_layer[coordinate][1] ==0: # need to see which spritesheet to blit from
                draw_image_to_coord (self.interactive_layer[coordinate][0], coordinate)
            else:
                draw_image_to_coord (self.interactive_layer[coordinate][0], coordinate,images_list=char_images)
    
    def interation_logic(self,coordinate,object_code,player,players,status_bar):
        #this might get tricky
        if object_code==((47,1),1):
            #be careful when updating this due to the way cycling of spawn locations is done
            axe_spawns=[(20,20),(35,30),(2,38) ] #MAP_PARAMS
            
            self.interactive_layer[coordinate]=((-1,-1),0)
            self.draw_tile(coordinate)
            current_spawn= axe_spawns.index(coordinate)
            new_spawn=axe_spawns[(current_spawn+random.randint(1,2))%3]
            self.interactive_layer[new_spawn]=((47,1),1)
            
            self.draw_tile(new_spawn)
            player.item+=2
            if player.item >5:
                player.item =5
            status_bar.update_values(players)
            status_bar.draw_all()

        if object_code==((36,3),1):
            shield_spawns=[(33,11), (15,14), (39,2)]
            
            self.interactive_layer[coordinate]=((-1,-1),0)
            self.draw_tile(coordinate)
            current_spawn2= shield_spawns.index(coordinate)
            new_spawn2=shield_spawns[(current_spawn2+random.randint(1,2))%3]
            self.interactive_layer[new_spawn2]=((36,3),1)

            self.draw_tile(new_spawn2)
            if players[not(player.id-1)].item >= 3:
                players[not(player.id-1)].item-=3
            status_bar.update_values(players)
            status_bar.draw_all()


    def is_passable(self,coordinate):
        #tests to see if the tile in question is passable
        listImpassable = [(13,9), (3,1), (3,0), (3,2), (2,1), (4,1), (2,0), (4,0), (2,2), (4,2), (24,10),(15,11),(15,10),(26,11),(26,10),(22,9)]
        condition1=tuple(self.foreground_layer[coordinate[0]][coordinate[1]]) in listImpassable
        condition2=tuple(self.background_layer[coordinate[0]][coordinate[1]]) in listImpassable
        condition3=tuple(self.background_layer2[coordinate[0]][coordinate[1]]) in listImpassable
        if  condition1 or condition2 or condition3:
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
        self.item= 0
   
    def damage(self, players, status_bar):
		other_player = players[not(self.id-1)]
		if self.item:
			x_dis = abs(other_player.location[0] - self.location[0])
			y_dis = abs(other_player.location[1] - self.location[1])
			if x_dis + y_dis <= 4:
				self.item -= 1
				other_player.health -= 1
				status_bar.update_values(players)
				status_bar.draw_all()



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
    
    def interact(self,game_map,status_bar,players):
        #interact with the map
        for direction in [(i,j) for i in range(-1,2) for j in range(-1,2)]:
            coordinate=add_coords(self.location,direction)
            object= tuple(game_map.interactive_layer[coordinate])
            game_map.interation_logic(coordinate,object,self,players,status_bar)
        print self.item, "item amount"    
                
                
                
def debug_grid():
    
    for i in range(DIMENSIONS[0]):
        pygame.draw.line(SURFACE,pygame.Color("black"),(16*i,0),(16*i,640))
        pygame.draw.line(SURFACE,pygame.Color("black"),(0,16*i),(640,16*i))
    for i in range(DIMENSIONS[0]):
        for j in range(DIMENSIONS[1]):
            label_x = myfont.render(str(i), 1,pygame.Color("black"))
            label_y = myfont.render(str(j), 1,pygame.Color("black"))
            SURFACE.blit(label_x, (16*i+2, 16*j-1))
            SURFACE.blit(label_y, (16*i+2, 16*j+6))
     
class StatusBar:
    def __init__(self,players):
        self.update_values(players)


        

    def update_values(self, players):
    	self.player1_hp=players[0].health
        self.player2_hp=players[1].health
        self.item_durability1=players[0].item
        self.item_durability2=players[1].item
        

    def draw_all(self):
        # updates the status bar at the bottom of the screen
        for i in range(40): #paint a background
            draw_image_to_coord((45,26), (i,40))
            draw_image_to_coord((45,26), (i,41))
        
        # player1  ----------------------------------------      
            #--- health bar ----
        if self.player1_hp > 0 :
            draw_image_to_coord((33,25), (5,41))
        else: 
            draw_image_to_coord((33,26), (5,41))
        for i in range(2,10):
            if self.player1_hp >= i:
                draw_image_to_coord((31,25), (4+i,41))
            else:
                draw_image_to_coord((31,26), (4+i,41))
        if self.player1_hp == 10 :
            draw_image_to_coord((34,25), (14,41))
        else: 
            draw_image_to_coord((34,26), (14,41))
        
            #--- item bar ----
        if self.item_durability1 > 0 :
            draw_image_to_coord((33,29), (5,40))
        else: 
            draw_image_to_coord((33,30), (5,40))
        for i in range(2,5):
            if self.item_durability1 >= i:
                draw_image_to_coord((31,29), (4+i,40))
            else:
                draw_image_to_coord((31,30), (4+i,40))
        if self.item_durability1 == 5 :
            draw_image_to_coord((34,29), (9,40))
        else: 
            draw_image_to_coord((34,30), (9,40))

        
        # player2  ----------------------------------------      
            #--- health bar ----
        if self.player2_hp > 0 :
            draw_image_to_coord((34,25), (34,41))
        else: 
            draw_image_to_coord((34,26), (34,41))
        for i in range(2,10):
            if self.player2_hp >= i:
                draw_image_to_coord((31,25), (35-i,41))
            else:
                draw_image_to_coord((31,26), (35-i,41))
        if self.player2_hp == 10 :
            draw_image_to_coord((33,25), (25,41))
        else: 
            draw_image_to_coord((33,26), (25,41))
        
            #--- item bar ----
        if self.item_durability2 > 0 :
            draw_image_to_coord((34,29), (34,40))
        else: 
            draw_image_to_coord((34,30), (34,40))
        for i in range(2,5):
            if self.item_durability2 >= i:
                draw_image_to_coord((31,29), (35-i,40))
            else:
                draw_image_to_coord((31,30), (35-i,40))
        if self.item_durability2 == 5 :
            draw_image_to_coord((33,29), (30,40))
        else: 
            draw_image_to_coord((33,30), (30,40))

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
        if DEBUG:debug_grid()
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

        if keys[pygame.K_SLASH]:
        	#player1's interact
        	players[0].interact(game_map,status_bar,players)

        if keys[pygame.K_q]:
        	#player2's interact
        	players[1].interact(game_map,status_bar,players)

        if keys[pygame.K_PERIOD]:
        	#player1's attack
            players[0].damage(players, status_bar)

        if keys[pygame.K_1]:
        	#player2's attack
        	players[1].damage(players, status_bar)


            
        
        for player in players: 
            #redraw the players each frame
            player.draw_player()
        
        pygame.display.flip() # this draws all the updates to the screen
        clock.tick(FPS) 
    
if __name__ == "__main__":
    main()