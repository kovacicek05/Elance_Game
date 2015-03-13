'''
Created on Feb 16, 2015

@author: Milan
'''

import pygame
import random
from os.path import exists
from os import remove


class Colors:
    BLACK    = (   0,   0,   0)
    WHITE    = ( 255, 255, 255)
    GREEN    = (   0, 255,   0)
    RED      = ( 255,   0,   0)
    BLUE     = (   0,   0, 255)
    YELLOW   = ( 255, 255,   0)

# This sets the width and height of each grid location    
DIMENSION = 10
# This sets the MARGIN between each cell
MARGIN = 1

start_angles = [0, 45, 315]
angles = {0     :   [ 1 ,  0],
          45    :   [ 1 , -1],
          90    :   [ 0 , -1],
          135   :   [-1 , -1],
          180   :   [-1 ,  0],
          225   :   [-1 ,  1],
          270   :   [ 0 ,  1],
          315   :   [ 1 ,  1]                     
          }

Emiters = list()
GridElements = list()

class Button:
    def __init__(self, text):
        self.text = text
        self.color = Colors.BLACK
        self.font_color = Colors.WHITE
        self.obj = None

    def label(self):
        '''button label font'''
        font = pygame.font.Font(None, 20)
        return font.render(self.text, 1, self.font_color)
 
    def draw(self, screen, mouse, rectcoord, labelcoord):
        ''' Draw button'''
        self.obj  = pygame.draw.rect(screen, self.color, rectcoord)
        screen.blit(self.label(), labelcoord)

class GridElement():
    """
        Every square in the grid is used as object, mainly for collision with the balls.
        If center coordinates of the element are equal with the center coordinates of the
        ball, then the ball is considered to be on the same spot as the element
    """
    def __init__(self, value, color, x_begin, y_begin):
        self.value = value
        self.color = color
        self.x_begin = x_begin
        self.y_begin = y_begin
        self.x_center = x_begin + DIMENSION//2
        self.y_center = y_begin + DIMENSION//2
    
    def __str__(self):
        """
            Used in develop and debug phase when investigating overlapping of the
            elements and the ball. Returns center coordinates of the element, value and color 
        """          
        return "%s %s %s %s" % (self.value, self.color, self.x_center, self.y_center)
        
    def draw(self, screen):
        """
            Draw element on the screen
        """
        pygame.draw.rect(screen,
                         self.color,
                         [self.x_begin,
                          self.y_begin,
                          DIMENSION,
                          DIMENSION])
#end class GridElement        
   
class Ball(pygame.sprite.Sprite):
    """
        Ball class
    """
    #used when writing data to the save file
    SaveData = [None, None, None]
    
    def __init__(self, x, y, angle, energy, name, index = 0):
        pygame.sprite.Sprite.__init__(self, self.updategroup, self.displaygroup)
        self.image = pygame.Surface((DIMENSION-1, DIMENSION-1)).convert()
        self.image.fill(Colors.RED)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.emiter = [x, y]
        self.now = [x , y]
        self.angle = angle
        self.initial_energy = energy 
        self.energy = energy
        self.index = index
        self.name = name
        self.collision = False
    
    def destroy(self):
        """
            Kills the object and updates proper variables used for rendering.
        """  
        Game.AliveBalls -= 1
        if self.name == "Ball":
            Game.BallList[0] = None
        elif self.name == "SubBall1":
            Game.BallList[1] = None
        elif self.name == "SubBall2":
            Game.BallList[2] = None
        else:
            pass
        self.save_data()
        self.kill()
        
    def save_data(self):
        """
            Write data in save file if there is no alive balls.
            If there was no collision simply write data, otherwise check for which
            ball/sub ball method has been called and update SaveData list.
        """
        filename = "Save.txt"   
        if self.name == "Ball":
            Ball.SaveData[0] = "%s, %d, %d, %d, %d, %d, %d, " % ( Game.TotalNumerOfBalls,
                                                                  self.index, 
                                                                  DIMENSION,
                                                                  DIMENSION,
                                                                  self.emiter[0],
                                                                  self.emiter[1],
                                                                  self.initial_energy)
            if self.collision == False:                
                Ball.SaveData[1] = "NA, NA, NA, NA, NA, "
                Ball.SaveData[2] = "NA, NA, NA, NA\n"
        elif self.name == "SubBall1":
            Ball.SaveData[1] = "%d, %d, %s, %s, %s, " % ( self.angle,
                                                          self.energy,
                                                          "NA", "NA", "NA"       
                                                        )
        elif self.name == "SubBall2":
            Ball.SaveData[2] = "%d, %s, %s, %s\n" % ( self.energy,
                                                      "NA", "NA", "NA"       
                                                    )
        else:
            pass
        
        #Write to file if data for ball and all sub balls (if there were any) is entered,
        #otherwise skip
        print_to_file = True
        data = ""
        for item in Ball.SaveData:            
            if item == None:
                print_to_file = False
            else:
                data += item
        if print_to_file == True:
            Ball.SaveData = [None, None, None]
            with open(filename , "a") as f:
                f.write(data)
  
    def update(self):
        """
            Method to be called 
        """
        x_koef = angles[self.angle][0]
        y_koef = angles[self.angle][1]
        self.now = [self.now[0] + x_koef, self.now[1] + y_koef]
        self.rect.center = [self.now[0], self.now[1]]
        
        #check if ball is out of boundaries
        if self.now[0] < 0 or self.now[0] > Game.FieldSize[0] or self.now[1] <0 or self.now[1] > Game.FieldSize[1]:
            self.destroy()
        
        #check if collision happened
        for elem in GridElements:
            if elem.x_center == self.now[0] and elem.y_center == self.now[1]:
                #print "COLLISION", elem.x_center, elem.y_center
                if elem.value == "G":
                    print "Ground"
                    self.destroy()
                elif elem.value == "W":
                    if self.name == "Ball":
                        split = random.choice([True,False])
                        if split == False:
                            print "Go Through"
                        else:
                            self.collision = True
                            angle1 = random.choice(angles.keys())
                            angle2 = (angle1+180) % 360
                            print angle1, angle2
                            Game.BallList[1] = Ball(self.now[0], self.now[1], angle1, (Game.BallEnergy * 36) // 100, "SubBall1" )
                            Game.BallList[2] = Ball(self.now[0], self.now[1], angle2, (Game.BallEnergy * 64) // 100, "SubBall2" )
                            Game.AliveBalls += 2
                            self.destroy()
                    else:
                        self.destroy()
                elif elem.value == "E":
                    pass
                else:
                    self.energy = self.energy - int(elem.value)
                    if self.energy <= 0:
                        self.energy = 0
                        self.destroy()
        

class Game:
    TotalNumerOfBalls = 0
    NumberOfBallsLeft = 0
    BallEnergy = 0
    BallSpeed = 0
    BoardFile = ""
    AliveBalls = 0
    FieldSize = 0
    BallList = [ None , None , None ]
    
    def __init__(self):        
        self.n_rows = 0
        self.n_columns = 0
        
        self.read_cfg()
        self.remove_save_file()
        self.create_grid()
        self.render()
        
    def read_cfg(self): 
        """
            Read config.cfg file and write values to Game class attributes
        """   
        with open("config.cfg", "r") as f:
            for line in f:
                key, value = line.strip().split(":")
                if key == "Ball_Energy":
                    Game.BallEnergy = int(value.strip())
                elif key == "Ball_Speed":
                    Game.BallSpeed = int(value.strip())
                elif key == "Total_Number_Balls":
                    Game.TotalNumerOfBalls = int(value.strip())
                    Game.NumberOfBallsLeft = int(value.strip())
                elif key == "Board_File":
                    Game.BoardFile = value.strip()
                else:
                    pass
    
    def remove_save_file(self):
        """
            Remove save file when started game because the same file will be created later
        """
        filename = "Save.txt"  
        if exists(filename):
            remove (filename)
    
    def create_grid(self):
        """
            Read grid file and based on that create grid
        """
        if Game.BoardFile == "":
            print "Config file was not properly read"
            exit()
        else:
            try:
                f = open(Game.BoardFile, "r")
            except:
                print "Can't open board file %s" % self.board_file
                exit()
            
            #read number of rows and columns
            self.n_columns = len(f.readline().strip())
            f.seek(0,0)
            self.n_rows = sum(1 for _ in f)
            f.seek(0,0)
            #check limits
            if self.n_columns < 4  or self.n_rows < 4:
                print "Lower limits error"
                exit()
            if self.n_columns > 100 or self.n_rows > 100:
                print "Higher limits error"
                exit()                
            
            #create 2D array that will hold the data
            grid = []
            for row in range(self.n_rows):
                grid.append(list())
                for column in range(self.n_columns):
                    grid[row].append(0)
                
            #fill the array
            for i, line in enumerate(f.readlines()):
                line = line.strip()        
                for j, value in enumerate(line):
                    grid[i][j] = value
            
            #create GridElements objects based on the values in the array
            for row in range(self.n_rows):
                for column in range(self.n_columns):
                    value = grid[row][column]
                    if value == "E":
                        color = Colors.RED
                    elif value == "W":
                        color = Colors.BLUE
                    elif value == "G":
                        color = Colors.YELLOW
                    elif int(value) == 0:
                        color = Colors.BLACK
                    else:
                        color = Colors.GREEN    
                    x_begin = (MARGIN+DIMENSION)*column+MARGIN
                    y_begin = (MARGIN+DIMENSION)*row+MARGIN
                    element = GridElement(value, color, x_begin, y_begin)          
                    GridElements.append(element)
                    if  value == "E":
                        Emiters.append(element)
            for item in Emiters:
                print item
                                             

    def draw_grid(self, screen):
        # Set the screen background
        screen.fill(Colors.WHITE)        
        # Draw the grid
        for element in GridElements:
            element.draw(screen)
                            
    def render(self):
        frame_count = 0 
        pygame.init()  
             
        # Set the height and width of the screen
        x_size = self.n_columns*(DIMENSION+MARGIN)
        y_size = self.n_rows*(DIMENSION+MARGIN)
        size = [self.n_columns*(DIMENSION+MARGIN)+120, self.n_rows*(DIMENSION+MARGIN)]
        Game.FieldSize = [x_size, y_size]
        
        print "Window size", size
        print "Field size", Game.FieldSize
        screen = pygame.display.set_mode(size)
        background = pygame.Surface(screen.get_rect().size)               
        pygame.display.set_caption("Play The Game")       
      
        # Used to manage how fast the screen updates
        clock = pygame.time.Clock() 
        
        displaygroup = pygame.sprite.RenderUpdates()
        Ball.updategroup = pygame.sprite.Group()
        Ball.displaygroup = displaygroup       
        # create Start button
        button = Button("Start") 
        
        end = False     
        done = False
        begin = False
        ball_index = 1
        while done == False:                
                mouse = pygame.mouse.get_pos()
                if begin == True:
                    if Game.NumberOfBallsLeft > 0:           
                        if Game.AliveBalls == 0:
                            emiter = random.choice(Emiters)
                            print "Random emiter",  emiter.x_center, emiter.y_center
                            angle = random.choice(start_angles) 
                            Game.BallList[0] = Ball(emiter.x_center, emiter.y_center, angle, Game.BallEnergy, "Ball",  ball_index )                
                            Game.AliveBalls += 1
                            ball_index += 1
                            Game.NumberOfBallsLeft -= 1
                        frame_count += 1 
                    else:
                        if Game.AliveBalls == 0:
                            end = True  
                for event in pygame.event.get(): # User did something
                    if event.type == pygame.QUIT: # If user clicked close
                        done = True # Flag that we are done so we exit this loop
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if button.obj.collidepoint(mouse):
                            begin = True
                            button.text = "Start"
                            
                    
                displaygroup.clear(screen, background)
                
                #refresh grid
                self.draw_grid(screen) 
                #Update time     
                self.update_time(screen, frame_count)      
                    
                #Update Ball location
                for item in Game.BallList:
                    if item != None:
                        item.update()
                # Draw button
                if begin == False:
                    self.draw_button(button, screen, mouse) 
                
                if end == True:
                    font = pygame.font.Font(None, 20)
                    text = font.render("Game Over", True, Colors.BLACK)
                    screen.blit(text, [self.n_columns*(DIMENSION+MARGIN) + 10, 25]) 
                      
                # Go ahead and update the screen with what we've drawn.
                pygame.display.update(displaygroup.draw(screen))
                pygame.display.flip()
                # Limit to ball speed that is read from the .cfg file
                clock.tick(Game.BallSpeed)
        print "Game Over"
            

    def draw_button(self, button, screen, mouse):
        x_pos = self.n_columns*(DIMENSION+MARGIN) + 10
        y_pos = 15
        x_size = 100
        y_size = 20
        x_label = x_pos + 35
        y_label = y_pos + 3
        button.draw(screen, mouse, (x_pos,y_pos,x_size,y_size), (x_label,y_label))

                
    def update_time(self, screen, frame_count): 
        """
            Update time for every frame
        """       
        # Calculate total seconds
        total_seconds = frame_count // Game.BallSpeed            
        # Divide by 60 to get total minutes
        minutes = total_seconds // 60            
        # Use modulus (remainder) to get seconds
        seconds = total_seconds % 60
        
        # Use python string formatting to format in leading zeros
        output_string = "Time: {0:02}:{1:02}".format(minutes, seconds)
        
        # Blit to the screen
        font = pygame.font.Font(None, 20)
        text = font.render(output_string, True, Colors.BLACK)
        screen.blit(text, [self.n_columns*(DIMENSION+MARGIN) + 10, 0])


def main():
    Game()
    
if __name__ == "__main__":
    main()