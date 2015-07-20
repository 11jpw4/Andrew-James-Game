import sys
import pygame
import numpy as np
from pygame.locals import *
from utilities.spritesheet import spritesheet # for loading the spritesheet
import os # for paths
import random
import math

'''
    -RULES-
    TBD
    
    -CONTROLS- 
    PLAYER1 arrow keys
    PLAYER2 WASD
     
'''


os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (30,30) # set where the window open on the screen
DIMENSIONS=(40,40) 
DEBUG=0
SURFACE = pygame.display.set_mode((16*DIMENSIONS[0],16*DIMENSIONS[1]+32)) # each tile is 16 pixels wide additionally two tiles are used for the HUD at the bottom
#this is everything I could have ever asked for and more
pygame.init()
myfont = pygame.font.SysFont("monospace", 10)
FPS = 30
clock = pygame.time.Clock()
SURFACE.fill(pygame.Color('black'))


# --- load in images ---
ss = spritesheet(os.path.join('spritesheet/roguelikeSheet_transparent.png'))
char_ss = spritesheet(os.path.join('spritesheet/roguelikeChar_transparent.png'))
# Sprite is 16x16 pixels at location 0,0 in the file...
# Load  images into an array, their transparent bit is (255, 255, 255)
images = [ss.images_at([(17*j, 17*i, 16,16) for i in range(36)],colorkey=(255, 255, 255)) for j in range(57)]
char_images = [char_ss.images_at([(17*j, 17*i, 16,16) for i in range(12)],colorkey=(255, 255, 255)) for j in range(54)]

# --- Load in sounds ---
pygame.mixer.init()

music_1= pygame.mixer.music.load("sounds\music1.mp3")
pygame.mixer.music.set_volume(0.8)
sound_attack_p1 =pygame.mixer.Sound("sounds\OOT_YoungLink_Attack1.wav")
sound_attack_p2 =pygame.mixer.Sound("sounds\OOT_YoungLink_Attack3.wav")
sound_hurt =pygame.mixer.Sound("sounds\OOT_AdultLink_Hurt1.wav")
sound_death =pygame.mixer.Sound("sounds\OOT_YoungLink_Scream1.wav")



def main():
    game_map=GameMap()
    
    player1=Player(location=(2,2),appearance=(6,0,0,80,20,0),id=1)
    player2=Player(location=(10,30),appearance=(8,0,0,0,0,0),id=2)
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
        
        self.interactive_layer[20][20]=((47,1),1) #axe spawn

        self.interactive_layer[33][11]=((37,4),1) #shield spawn
        
        #trees, bushes and grasses
        list_trees = [(3,3),(7,5),(11,9),(33,29),(18,22),(32,22)]
        list_cacti = [(27,1),(31,7),(33,4),(37,15),(33,13)]
        list_cacti2 = [(27,5),(35,8)]
        list_cacti3 = [(31,11),(38,6)]
        list_bushes = [(22,38), (24,38), (2,30), (26,24)]
        list_grass1 = [(15,15),(24,18),(16,36),(24,11),(33,18)]
        list_grass2 = [(22,17),(32,37),(36,21),(4,28),(5,12)]
        list_wild_flower1=[(8,18),(27,28)]
        list_wild_flower2=[(4,12),(27,10),(31,18)]
        list_wild_flower3=[(23,17),(13,13),(11,0)]
        list_wild_flower4=[(23,28),(23,21),(32,17),(15,2),(23,13)]
        list_tall_dg_tree_base=[(4,17),(30,32),(26,31),(21,9),(37,37)]
        list_tall_dg_tree_top=[add_coords(x,(0,-1)) for x in list_tall_dg_tree_base]
        list_tall_pointy_tree_base=[(16,36),(38,33),(22,34),(29,36),(28,35),(28,38),(27,36),
                                    (26,35),(27,38),(25,36),(25,34),(25,38),(23,37),(31,37),(26,38)]
        list_tall_pointy_tree_top=[add_coords(x,(0,-1)) for x in list_tall_pointy_tree_base]
        
        #camp stuff
        list_white_tent_t_l=[(28,13),(24,14)]
        list_white_tent_t_r=[(29,13),(25,14)]
        list_white_tent_b_r=[(29,14),(25,15)]
        list_white_tent_b_l=[(28,14),(24,15)]
        list_camp_fire=[(28,16)]
        list_fish_rope_right=[(27,14)]
        list_fish_rope_left=[(26,14)]
        list_sleepingbag1=[(26,16)]
        
        #lillypads and water stuff
        list_lillypad1 = [(5,33),(18,13)]
        list_lillypad2 = [(15,8),(10,7)]
        list_water_rock1 = [(17,8)]
        list_dock_right =[(8,33)]
        list_dock_middle=[]
        list_dock_left=[]
        
        #dirt
        list_dirt_top_left=[(24,13)]
        list_dirt_top=[(25+i,13) for i in range(5)]
        list_dirt_top_right=[(30,13)]
        list_dirt_middle_left=[(24,15),(24,14)]
        list_dirt_middle=[(25+i,14+j) for i in range(5) for j in range(3)] +[(30,15)]
        list_dirt_middle_right=[(30,14),]
        list_dirt_bottom_left=[(25,17),(24,16)]
        list_dirt_bottom=[(28,17),(27,17),(26,17)]
        list_dirt_bottom_right=[(29,17),(30,16)]
        
        list_path_horizontal=[(31+i,15) for i in range(4)]+[(36+i,14) for i in range(4)]
        list_path_bend_bottom_right=[(35,15)]
        list_path_bend_top_left=[(35,14)]
        
        #house stuff
        list_roof_top_left=[(11,28)]
        list_roof_top_right=[(12,28)]
        list_roof_middle_left=[(11,29)]
        list_roof_middle_right=[(12,29)]
        list_roof_bottom_left=[(11,30)]
        list_roof_bottom_right=[(12,30)]
        list_building_top_left=[]
        list_building_top=[]
        list_building_top_right=[]
        list_building_middle_left=[(11,30),]
        list_building_middle=[]
        list_building_middle_right=[(12,30)]
        list_building_bottom_left=[(11,31)]
        list_building_bottom=[]
        list_building_bottom_right=[(12,31)]
        list_doors_right=[(12,31)]
        list_doors_left=[(11,31)]
        list_chimney=[(12,28)]
        list_window1= []
        
        
        
        
        
        # water tiles
        list_water = [(5,34),(6,34),(7,34),(5,33),(6,33),(7,33),(5,32),(6,32),(7,32)] +[(15,8),(16,8),(17,7),(10,7)]+[(17,8+i) for i in range(1,4)]
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
        
        #desert tiles
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
        
        #trees and cacti
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
        for i,j in list_tall_pointy_tree_base:
        	self.foreground_layer[i][j]=(16,11)
        for i,j in list_tall_pointy_tree_top:
        	self.foreground_layer[i][j]=(16,10)
        for i,j in list_bushes:
        	self.foreground_layer[i][j]=(24,10)
        for i,j in list_cacti:
        	self.foreground_layer[i][j]=(22,9)
        for i,j in list_cacti2:
        	self.foreground_layer[i][j]=(26,10)
        for i,j in list_cacti3:
        	self.foreground_layer[i][j]=(26,9)
        for i,j in list_wild_flower1:
        	self.foreground_layer[i][j]=(28,9)
        for i,j in list_wild_flower2:
        	self.foreground_layer[i][j]=(29,9)
        for i,j in list_wild_flower3:
        	self.foreground_layer[i][j]=(30,9)
        for i,j in list_wild_flower4:
        	self.foreground_layer[i][j]=(31,9)
        
        
        #house stuff
        for i,j in list_roof_top_left:
        	self.background_layer2[i][j]=(20,21)
        for i,j in list_roof_top_right:
        	self.background_layer2[i][j]=(21,21)
        for i,j in list_roof_middle_left:
        	self.background_layer2[i][j]=(20,22)
        for i,j in list_roof_middle_right:
        	self.background_layer2[i][j]=(21,22)
        for i,j in list_roof_bottom_left:
        	self.background_layer2[i][j]=(20,23)
        for i,j in list_roof_bottom_right:
        	self.background_layer2[i][j]=(21,23)
        for i,j in list_building_top_left:
        	self.background_layer[i][j]=(17,21)
        for i,j in list_building_top:
        	self.background_layer[i][j]=(18,21)
        for i,j in list_building_top_right:
        	self.background_layer[i][j]=(19,21)
        for i,j in list_building_middle_left:
        	self.background_layer[i][j]=(17,22)
        for i,j in list_building_middle:
        	self.background_layer[i][j]=(18,22)
        for i,j in list_building_middle_right:
        	self.background_layer[i][j]=(19,22)
        for i,j in list_building_bottom_left:
        	self.background_layer[i][j]=(17,23)
        for i,j in list_building_bottom:
        	self.background_layer[i][j]=(18,23)
        for i,j in list_building_bottom_right:
        	self.background_layer[i][j]=(19,23)
        for i,j in list_doors_right:
        	self.interactive_layer[i][j]=((29,6),0)
        for i,j in list_doors_left:
        	self.interactive_layer[i][j]=((28,6),0)
        for i,j in list_chimney:
        	self.foreground_layer[i][j]=(36,20)
        for i,j in list_window1:
        	self.foreground_layer[i][j]=(43,5)
        
        
        #dirt
        for i,j in list_dirt_top_left:
        	self.background_layer2[i][j]=(7,9)
        for i,j in list_dirt_top:
        	self.background_layer2[i][j]=(8,9)
        for i,j in list_dirt_top_right:
        	self.background_layer2[i][j]=(9,9)
        for i,j in list_dirt_middle_left:
        	self.background_layer2[i][j]=(7,10)
        for i,j in list_dirt_middle:
        	self.background_layer2[i][j]=(8,10)
        for i,j in list_dirt_middle_right:
        	self.background_layer2[i][j]=(9,10)
        for i,j in list_dirt_bottom_left:
        	self.background_layer2[i][j]=(7,11)
        for i,j in list_dirt_bottom:
        	self.background_layer2[i][j]=(8,11)
        for i,j in list_dirt_bottom_right:
        	self.background_layer2[i][j]=(9,11)  
        for i,j in list_path_horizontal:
        	self.background_layer2[i][j]=(9,8)
        for i,j in list_path_bend_bottom_right:
        	self.background_layer2[i][j]=(8,8)
        for i,j in list_path_bend_top_left:
        	self.background_layer2[i][j]=(7,7)
        
        #camp stuff
        for i,j in list_white_tent_t_l:
        	self.foreground_layer[i][j]=(48,10)
        for i,j in list_white_tent_t_r:
        	self.foreground_layer[i][j]=(49,10)
        for i,j in list_white_tent_b_r:
        	self.foreground_layer[i][j]=(49,11)
        for i,j in list_white_tent_b_l:
        	self.foreground_layer[i][j]=(48,11)
        for i,j in list_camp_fire:
        	self.foreground_layer[i][j]=(15,8)
        for i,j in list_fish_rope_right:
        	self.foreground_layer[i][j]=(52,13)
        for i,j in list_fish_rope_left:
        	self.foreground_layer[i][j]=(51,13)
        for i,j in list_sleepingbag1:
        	self.foreground_layer[i][j]=(12,2)    
         
        #lillypads and water stuff
        for i,j in list_lillypad1:
        	self.foreground_layer[i][j]=(26,11)
        for i,j in list_lillypad2:
        	self.foreground_layer[i][j]=(25,11)
        for i,j in list_water_rock1:
        	self.foreground_layer[i][j]=(55,23)
        for i,j in list_dock_right:
        	self.foreground_layer[i][j]=(53,12)
        for i,j in list_dock_middle:
        	self.foreground_layer[i][j]=(53,13)
        for i,j in list_dock_left:
        	self.foreground_layer[i][j]=(53,14)
        
        #water tiles
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
        if object_code==((47,1),1): # axe
            #be careful when updating this due to the way cycling of spawn locations is done
            axe_spawns=[(20,20),(35,30),(2,38),(8,2),(23,3),(11,34) ] #MAP_PARAMS
            
            self.interactive_layer[coordinate]=((-1,-1),0)
            self.draw_tile(coordinate)
            current_spawn= axe_spawns.index(coordinate)
            spawn_count=len(axe_spawns)
            new_spawn=axe_spawns[(current_spawn+random.randint(1,spawn_count-1))%spawn_count]
            self.interactive_layer[new_spawn]=((47,1),1)
            
            self.draw_tile(new_spawn)
            player.item+=2
            if player.item >5:
                player.item =5
            status_bar.update_values(players)
            status_bar.draw_all()

        if object_code==((37,4),1):# shield
            shield_spawns=[(33,11), (15,14), (39,2)]
            
            self.interactive_layer[coordinate]=((-1,-1),0)
            self.draw_tile(coordinate)
            current_spawn2= shield_spawns.index(coordinate)
            new_spawn2=shield_spawns[(current_spawn2+random.randint(1,2))%3]
            self.interactive_layer[new_spawn2]=((37,4),1)

            self.draw_tile(new_spawn2)
            players[not(player.id-1)].item-=3
            if players[not(player.id-1)].item < 0:
                players[not(player.id-1)].item = 0
            status_bar.update_values(players)
            status_bar.draw_all()
        
        if object_code == ((29,6),0): # building doors right closed
            self.interactive_layer[coordinate]=((29,8),0)
            self.interactive_layer[add_coords(coordinate,(-1,0))]=((28,8),0)
            self.draw_tile(coordinate)
            self.draw_tile(add_coords(coordinate,(-1,0)))
            
        elif object_code == ((28,6),0): # building doors left closed
            self.interactive_layer[coordinate]=((28,8),0)
            self.interactive_layer[add_coords(coordinate,(1,0))]=((29,8),0)
            self.draw_tile(coordinate)
            self.draw_tile(add_coords(coordinate,(1,0)))
        
        elif object_code == ((29,8),0): # building doors right open
            self.interactive_layer[coordinate]=((29,6),0)
            self.interactive_layer[add_coords(coordinate,(-1,0))]=((28,6),0)
            self.draw_tile(coordinate)
            self.draw_tile(add_coords(coordinate,(-1,0)))
            
        elif object_code == ((28,8),0): # building doors left open
            self.interactive_layer[coordinate]=((28,6),0)
            self.interactive_layer[add_coords(coordinate,(1,0))]=((29,6),0)
            self.draw_tile(coordinate)
            self.draw_tile(add_coords(coordinate,(1,0)))
        
    def animate(self,counter):
        #deals with animated tiles, should probably write it so that drawing only happens when necessary in the future
        
        #fire
        if counter%30<15:
            self.foreground_layer[(28,16)]=(15,8)
        else: 
            self.foreground_layer[(28,16)]=(14,8)
        self.draw_tile((28,16))  
        

        
        
    def is_passable(self,coordinate):
        #tests to see if the tile in question is passable
        listImpassable = [(13,9), (3,1), (3,0), (3,2), (2,1), 
                            (4,1), (2,0), (4,0), (2,2), (4,2), 
                            (24,10),(15,11),(15,10),(26,9),(26,10),
                            (22,9),(16,11),(16,10),
                            (48,10),(48,11),(49,11),(49,10)]+ [(17+i,21+j) for i in range(5) for j in range(3)]
        list_passable= [(53,12+i) for i in range(3)]
        condition1=tuple(self.foreground_layer[coordinate[0]][coordinate[1]]) in listImpassable
        condition2=tuple(self.background_layer[coordinate[0]][coordinate[1]]) in listImpassable
        condition3=tuple(self.background_layer2[coordinate[0]][coordinate[1]]) in listImpassable
        condition4=tuple(self.foreground_layer[coordinate[0]][coordinate[1]]) in list_passable
        
        if  (condition1 or condition2 or condition3) and not condition4:
        	return False
        return True
    
class Player:
    def __init__(self,location,appearance,id):
        self.location=location
        self.appearance= appearance
        ''' appearance is a length 6 tuple
            body type : 0-3
            pant type : 0-9  4 and 9 are for dresses
            shoe type : 0-9  4 and 9 are for dresses
            shirt type: guhhh
            hair type: 
            hair2 (beard) type:
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
                sound_hurt.play()
                status_bar.update_values(players)
                status_bar.draw_all()
        if self.id ==1: sound_attack_p1.play()
        elif self.id ==2: sound_attack_p2.play()
        


    def move(self,direction,distance,game_map,players,npc_list):
        #moves the player in the direction desired if possible
        #direction is a tuple either (1,0),(-1,0),(0,1) or (0,-1)
        for _ in range(distance):   
            destination=add_coords(self.location,direction)
            no_npcs_in_tile= not sum([npc.location==destination for npc in npc_list])
            if game_map.is_passable(destination) and  players[not(self.id-1)].location!=destination and no_npcs_in_tile: #check to see if movement is valid
                game_map.draw_tile(self.location)
                self.location = add_coords(self.location,direction)
            else:
                #break out of the loop if the player encounters an obstacle 
                break
                
    def draw_player(self):
        #draw the player and all their items        
        draw_image_to_coord((0, self.appearance[0]), self.location, images_list=char_images) # draw the body
        '''draw_image_to_coord((3, self.appearance[1]), self.location, images_list=char_images)  #draw the pants
        draw_image_to_coord((4, self.appearance[2]), self.location, images_list=char_images)  #draw the shoes
        draw_image_to_coord((6+self.appearance[3]%12, self.appearance[3]/12), self.location, images_list=char_images)  #draw the shirt
        draw_image_to_coord((19+self.appearance[4]%8, self.appearance[4]/8), self.location, images_list=char_images)  #draw the hair1
        draw_image_to_coord((19+self.appearance[5]%8, self.appearance[5]/8), self.location, images_list=char_images)  #draw the hair2 TO_DO add in the white hair'''
        
    
    def interact(self,game_map,status_bar,players):
        #interact with the map
        for direction in [(i-1,j-1) for i in range(3) for j in range(3)]:
            coordinate=add_coords(self.location,direction)
            
            object= tuple(game_map.interactive_layer[coordinate])
            game_map.interation_logic(coordinate,object,self,players,status_bar) 
            if object !=((-1,-1),0): break # this is for the doors not auto close themselves    
                
class Npc:
    def __init__(self,location,appearance,id,type):
        self.location=location
        self.appearance=appearance
        self.id=id
        self.type=type
        self.target=0
    
    def npc_logic(self,players,status_bar,game_map,npc_list):
        # npc ai handled here
    
        if self.type==0: # aggressive 
            # this ai will chases a player if it has a target, if not it will chase the closest player , ah and try to hurt them
            raw_distances=[(abs(-self.location[0]+players[0].location[0]),abs(players[0].location[1]-self.location[1])),
                            (abs(-self.location[0]+players[1].location[0]),abs(players[1].location[1]-self.location[1]))]
            distances= [math.sqrt(raw_distances[0][0]**2+raw_distances[0][1]**2),math.sqrt(raw_distances[1][0]**2+raw_distances[1][1]**2)]
            
                
            if self.target:
                victim=players[self.target-1]
                victim_dist=distances[self.target-1]
            else:
                
                if distances[0]<distances[1]:
                    victim=players[0]
                    victim_dist=distances[0]
                else:
                    victim=players[1]
                    victim_dist=distances[1]
                    
            if  victim_dist <3:
            
                    self.damage(players,status_bar,victim)
            directions=((1,0),(-1,0),(0,1),(0,-1))
            coords=map(lambda x: add_coords(x,self.location), directions)
            raw_dists=map(lambda x: (abs(-x[0]+victim.location[0]),abs(-x[1]+victim.location[1])),coords)
            dists=map(lambda x: abs(x[0])+abs(x[1]) , raw_dists)
            
            direction= directions[dists.index(min(dists))]
            self.move(direction,1,game_map,players,npc_list)
            
               

            
    def damage(self, players, status_bar,victim):
		
        x_dis = abs(victim.location[0] - self.location[0])
        y_dis = abs(victim.location[1] - self.location[1])
        if x_dis + y_dis <= 4:
            victim.health -= 1
            sound_hurt.play()
            status_bar.update_values(players)
            status_bar.draw_all()
    
    def move(self,direction,distance,game_map,players,npc_list):
        #moves the player in the direction desired if possible
        #direction is a tuple either (1,0),(-1,0),(0,1) or (0,-1)
        for _ in range(distance):   
            destination=add_coords(self.location,direction)
            no_npcs_in_tile= not sum([npc.location==destination for npc in npc_list])
            if game_map.is_passable(destination) and  players[not(self.id-1)].location!=destination and no_npcs_in_tile: #check to see if movement is valid
                game_map.draw_tile(self.location)
                self.location = add_coords(self.location,direction)
            else:
                #break out of the loop if the player encounters an obstacle 
                break
    
    def draw_npc(self):
        #draws the npc
        draw_image_to_coord((1, self.appearance[0]), self.location, images_list=char_images) 
    
class StatusBar:
    def __init__(self,players):
        self.update_values(players)


        

    def update_values(self,players):
    	self.player1_hp=players[0].health
        self.player2_hp=players[1].health
        self.item_durability1=players[0].item
        self.item_durability2=players[1].item
        self.player1_appearance=players[0].appearance
        self.player2_appearance=players[1].appearance
        

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
        
            #--- portrait ---
        draw_image_to_coord((0, self.player1_appearance[0]), (2,41), images_list=char_images) 
        
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
            
            #--- portrait ---
        draw_image_to_coord((0, self.player2_appearance[0]), (37,41), images_list=char_images) 

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
    
    pygame.mixer.music.play(loops=-1)
    #this function contain the main game loop
    game_map.draw_all()
    status_bar.draw_all()
    
    p1_interact_cooldown=10
    p1_attack_cooldown=10
    p2_interact_cooldown=10
    p2_attack_cooldown=10
    counter=0
    orc=Npc(location=(20,20),appearance=(3,0,0,80,20,0),id=1,type=0)
    npc_list=[orc]
    
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
            players[0].move(direction,1,game_map,players,npc_list)
            
            
        if keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_s] or keys[pygame.K_w]:
            #player2's movement 
            if keys[pygame.K_w]: direction= (0,-1)
            elif keys[pygame.K_s]: direction= (0,1)
            elif keys[pygame.K_d]: direction= (1,0)
            elif keys[pygame.K_a]: direction= (-1,0)
            players[1].move(direction,1,game_map,players,npc_list)

        if keys[pygame.K_SLASH] and p1_interact_cooldown<0:
        	#player1's interact
            players[0].interact(game_map,status_bar,players)
            p1_interact_cooldown=30

        if keys[pygame.K_q] and p2_interact_cooldown<0:
        	#player2's interact
            players[1].interact(game_map,status_bar,players)
            p2_interact_cooldown=30

        if keys[pygame.K_PERIOD]and p1_attack_cooldown<0:
        	#player1's attack
            players[0].damage(players, status_bar)
            p1_attack_cooldown=15

        if keys[pygame.K_1]and p2_attack_cooldown<0:
        	#player2's attack
            players[1].damage(players, status_bar)
            p2_attack_cooldown=15


        #---animations---
        counter=(counter+1)%150
        game_map.animate(counter)    
        
        
        #--- Npc stuff ---
        if counter%5==0:
            orc.npc_logic(players,status_bar,game_map,npc_list)
            orc.draw_npc()
        
        
        for player in players: 
            #redraw the players each frame
            player.draw_player()
        if not players[0].health or not players[1].health:
            #check for victory
            break
        
        
        p1_interact_cooldown-=1
        p1_attack_cooldown-=1
        p2_interact_cooldown-=1
        p2_attack_cooldown-=1
        
        
        pygame.display.flip() # this draws all the updates to the screen
        clock.tick(FPS) 
    
    #end of game loop
    sound_death.play()
    music_victory= pygame.mixer.music.load("sounds\win1.mp3")
    pygame.mixer.music.play()
    
    
    myfont = pygame.font.SysFont("monospace", 10)
    if players[0].health==0:
        label= myfont.render("PLAYER 2 WINS", 1,pygame.Color("black"))
    else:   
        label= myfont.render("PLAYER 1 WINS", 1,pygame.Color("black"))
    pygame.draw.rect(SURFACE,pygame.Color("white"),(220,240,200,40))
    pygame.draw.rect(SURFACE,pygame.Color("black"),(220,240,200,40),2)
    SURFACE.blit(label, (280,255))
    pygame.display.flip() # this draws all the updates to the screen
    
    
    while True:
        #end of game
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
        clock.tick(FPS) 
    
    
if __name__ == "__main__":
    main()