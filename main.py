import kivy
from random import Random
kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty,StringProperty
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.audio import Sound, SoundLoader
from time import clock
import json


Rows_For_First_Level = 3

class BButton(Button):
    def __init__(self,box,**kwargs):
        super(BButton,self).__init__(**kwargs)
        self.box = box
        self.isMarking = False

    def on_press(self):
        self.press()

    def press(self):
        if self.box.root.gameover:
            return
        
        self.isMarking = self.box.root.status_bar.toggle_mark.state=='down'

        if self.isMarking:
            if self.image.opacity == 1:
                self.MarkNormal()
            else:
                self.MarkB()
        else:
            self.box.Clear()

    def MarkB(self):
        self.image.opacity = 1
        self.box.state=1
        
        if self.box.root.mute == False:
            self.box.root.sounds['state'].play()
        
        if self.box.root.gameover == False:
            self.box.root.bfound += 1

    def MarkNormal(self):
        self.image.opacity = 0
        self.box.state=0
        
        if self.box.root.mute == False:
            self.box.root.sounds['state'].play()
            
        if self.box.root.gameover == False:
            self.box.root.bfound -= 1

class BLabel(Label):
    pass

class BBox(RelativeLayout):
    def __init__(self,root,**kwargs):
        super(BBox,self).__init__(**kwargs)
        self.isBomb = False
        self.BNumber = 0
        self.root = root
        self.isClear = False
        self.row = 0
        self.col = 0
        self.state=0 # 0 means normal, 1 means marked as bomb, -1 means cleared already
        
        self.blabel = BLabel()
        self.bbutton = BButton(box=self)
        
        self.add_widget(self.bbutton)
        
    def CalculateBNumber(self):
        self.BNumber = 0
        if self.isBomb == False:
            self.BNumber += 1 if self.root.CheckBomb(self.row - 1,self.col - 1) else 0
            self.BNumber += 1 if self.root.CheckBomb(self.row - 1,self.col) else 0
            self.BNumber += 1 if self.root.CheckBomb(self.row - 1,self.col + 1) else 0
            self.BNumber += 1 if self.root.CheckBomb(self.row,self.col - 1) else 0
            self.BNumber += 1 if self.root.CheckBomb(self.row,self.col + 1) else 0
            self.BNumber += 1 if self.root.CheckBomb(self.row + 1,self.col - 1) else 0
            self.BNumber += 1 if self.root.CheckBomb(self.row + 1,self.col) else 0
            self.BNumber += 1 if self.root.CheckBomb(self.row + 1,self.col + 1) else 0

            self.blabel.text = '{}'.format(self.BNumber) if self.BNumber > 0 else ''
        else:
            self.blabel.text='*'
    
    

    
    def Clear(self,isShowAll=False):
        '''
        triggered when user click the button and think it's empty or has a number
        '''
        if self.isBomb and self.state==0:
            '''
            A Bomb, game over
            '''
            if isShowAll == False:
                self.root.GameOver()
                self.Explode()
                self.bbutton.image.source='gameoverflag.png'
        else:
            self.MarkNumberOrEmpty()
            
        self.root.CheckSucceed()


    def Explode(self):
        '''
        Animation needed
        '''  
        if self.root.mute == False:
            self.root.sounds['bomb'].play()
            
        self.root.ShowAll()
    
    def MarkNumberOrEmpty(self):
        '''
        Not only mark itself as empty, also mark all around boxes if they are empty
        '''
        if self.state == 1:
            return
        
        if self.BNumber == 0 and self.isClear == False:
            self.clear_widgets()
            self.add_widget(self.blabel)
            self.isClear = True

            self.root.Clear(self.row - 1,self.col - 1)
            self.root.Clear(self.row - 1,self.col)
            self.root.Clear(self.row - 1,self.col + 1)
            self.root.Clear(self.row,self.col - 1)
            self.root.Clear(self.row,self.col + 1)
            self.root.Clear(self.row + 1,self.col - 1)
            self.root.Clear(self.row + 1,self.col)
            self.root.Clear(self.row + 1,self.col + 1)
                    
        elif self.BNumber > 0 and self.isClear == False:
            self.clear_widgets()
            self.add_widget(self.blabel)
            self.isClear = True
            
        self.state = -1
        
        if self.root.mute == False:
            self.root.sounds['state'].play()
       
    
class PlayArea(GridLayout):
    pass

class FindBWidget(BoxLayout):
    level=NumericProperty(1)
    bfound = NumericProperty(0)
    bnumber = NumericProperty(0)
    
    def __init__(self,**kwargs):
        super(FindBWidget,self).__init__(**kwargs)
        self.BBoxList=[]
        self.gridSize = 0
        self.bnumber = 0
        self.badded = 0
        self.bfound = 0
        self.mute=True
        self.gameover = False
        
        self.sounds = {'bomb':SoundLoader.load('bomb.wav'),
                       'state':SoundLoader.load('state.wav'),
                       'upgrade':SoundLoader.load('upgrade.wav')}
        
        self.start_clock = clock()
        self.config = None
        
    def on_level(self,instance,value):
        self.status_bar.label_level.text = 'L:{}'.format(self.level)
        
    def on_bfound(self,instance,value):
        self.status_bar.label_left_bomb.text = '{}'.format(self.bnumber - self.bfound)
        self.CheckSucceed()

    def on_bnumber(self,instance,value):
        self.status_bar.label_left_bomb.text = '{}'.format(self.bnumber - self.bfound)

    def Restart(self):
        self.BBoxList = []
        self.gridSize = self.level + Rows_For_First_Level
        self.bnumber = 0
        self.badded = 0
        self.bfound = 0
        self.start_clock = clock()
        self.gameover = False
        self.play_area.clear_widgets()
        self.play_area.cols = self.gridSize
        self.play_area.rows = self.gridSize
        
        for i in range(0,self.gridSize):
            for j in range(0,self.gridSize):
                b = BBox(root=self)
                b.row=i
                b.col=j
                self.BBoxList.append(b)
                self.play_area.add_widget(b)
        
        self._calculate_bombs()
        
        self.status_bar.toggle_mark.disable = False
        self.status_bar.button_reset.image.source='smile.png'

                
    def _calculate_bombs(self):
        if self.level < 6:
            self.brate = 0.11
        elif self.level < 11:
            self.brate = 0.13
        elif self.level < 20:
            self.brate = 0.15
        elif self.level < 30:
            self.brate = 0.18
        else:
            self.brate = 0.2
            
        self.bnumber = int(self.brate * self.gridSize * self.gridSize)
        
        self.badded = 0
        while True:
            if self._add_bomb():
                self.badded += 1
                
            if self.badded >= self.bnumber:
                break
                
        for i in range(0,len(self.BBoxList)):
            self.BBoxList[i].CalculateBNumber()
    
    def _add_bomb(self):
        i = Random().randint(0,len(self.BBoxList) - 1)
        
        if self.BBoxList[i].isBomb:
            return False
        else:
            self.BBoxList[i].isBomb = True
            return True
        
    def CheckBomb(self,row,col):
        if row < 0 or row >= self.gridSize or col < 0 or col >= self.gridSize:
            return False
        
        index = row*self.gridSize + col
        if index < 0 or index >= len(self.BBoxList):
            return False
        
        return self.BBoxList[index].isBomb
    
    def Clear(self,row,col):
        if row < 0 or row >= self.gridSize or col < 0 or col >= self.gridSize:
            return
        
        index = row*self.gridSize + col
        if index < 0 or index >= len(self.BBoxList):
            return
        
        self.BBoxList[index].MarkNumberOrEmpty()
    
    def ShowAll(self):
        self.status_bar.toggle_mark.state='normal'
        for i in range(0,len(self.BBoxList)):
            if self.BBoxList[i].isBomb:
               self.BBoxList[i].bbutton.MarkB()
            else:
                self.BBoxList[i].Clear()
                
    def CheckSucceed(self):
        if self.bfound > 0 and self.bfound == self.bnumber:
            for i in range(0,len(self.BBoxList)):
                if self.BBoxList[i].state == 0:
                    return False
            
            #upgrade level  
            if self.mute == False:
                self.sounds['upgrade'].play()
            
            
            duraton = (clock() - self.start_clock)/10000
            self.config.set('UserData','CurrentLevel',self.level + 1)
            print self.config.get('UserData','CurrentLevel')
            levels = json.loads(self.config.get('UserData','Levels'))
            print levels
            #levels[self.level] = round(duraton,2)
            #self.config.set('UserData','Levels',json.dump([levels]))

            self.level += 1
            self.Restart()
            
            return True
        else:
            return False
    
    def GameOver(self):
        self.status_bar.toggle_mark.disable = True
        self.status_bar.button_reset.image.source='gameover.png'
        self.gameover = True
    
class FindBApp(App): 
    use_kivy_settings = False
    def build(self):
        findb = FindBWidget()
        findb.config = self.config
        findb.Restart() 
        return findb
    
    def build_config(self, config):
        config.setdefaults('SystemConfig',{
                                          'Mute':True
                                          }
                          )
        config.setdefaults('UserData',{
                                          'CurrentLevel':1,
                                          'Levels':'[{1:0}]'
                                          }
                          )
        
    def build_settings(self, settings):
        jsondata = """[
                        { "type": "bool",
                        "title": "Mute",
                        "desc": "Play without sound",
                        "section": "SystemConfig",
                        "key": "Mute"}
                    ]"""
        settings.add_json_panel('Poker80',self.config,data=jsondata)
            
    def on_config_change(self, config, section, key, value):
        if config is self.config:
            token = (section, key)
            if token == ('SystemConfig', 'Mute'):
                self.root.mute = (value == '1')

if __name__ == '__main__':
    FindBApp().run()