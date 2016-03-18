import kivy
from random import Random
kivy.require('1.9.1')

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

Rows_For_First_Level = 3

class BButton(Button):    
    def __init__(self,box,**kwargs):
        super(BButton,self).__init__(**kwargs)
        self.box = box
        self.isMarking = False
        
    def on_press(self):
        self.isMarking = self.box.root.status_bar.toggle_mark.state=='down'
        if self.isMarking:
            if self.image.opacity == 1:
                self.image.opacity = 0
                self.box.state=0
            else:
                self.image.opacity = 1
                self.box.state=1
        else:
            self.box.Clear()
            self.box.state = -1

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
        
        self.blabel = Label(box=self,text=('{}'.format(self.BNumber)) if self.BNumber > 0 else '')
        self.bbutton = BButton(box=self)
        
        self.add_widget(self.blabel)
        
    def CalculateBNumber(self):
        for i in range(self.row - 1, self.row + 1):
            if i <= 0 or i > (self.root.level + Rows_For_First_Level):
                continue
            for j in range(self.col - 1, self.col + 1):
                if j <= 0 or j > (self.root.level + Rows_For_First_Level):
                    continue
                
                if i == self.row and j == self.col:
                    continue
                
                if self.root.BBoxList[j + (i-1)*(self.root.level + Rows_For_First_Level)].isBomb:
                    self.BNumber += 1
                    
    
    def Clear(self):
        '''
        triggered when user click the button and think it's empty or has a number
        '''
        if self.BNumber == -1:
            '''
            A Bomb, game over
            '''
            self.Explode()
            self.root.GameOver()
        else:
            self.MarkNumberOrEmpty()


    def Explode(self):
        '''
        Animation needed
        '''
        pass
    
    def MarkNumberOrEmpty(self):
        '''
        Not only mark itself as empty, also mark all around boxes if they are empty
        '''
        if self.BNumber == 0 and self.isClear == False:
            self.clear_widgets()
            self.add_widget(self.blabel)
            self.isClear = True
        
            for i in range(self.row - 1, self.row + 1):
                if i <= 0 or i > (self.root.level + Rows_For_First_Level):
                    continue
                for j in range(self.col - 1, self.col + 1):
                    if j <= 0 or j > (self.root.level + Rows_For_First_Level):
                        continue
                    
                    if i == self.row and j == self.col:
                        continue
                    
                    self.root.BBoxList[j + (i-1)*(self.root.level + Rows_For_First_Level)].MarkNumberOrEmpty()
                    
        elif self.BNumber > 0 and self.isClear == False:
            self.clear_widgets()
            self.add_widget(self.blabel)
            self.isClear = True
       
    
class PlayArea(GridLayout):
    def SetLevel(self,level):
        self.cols = self.rows = level + Rows_For_First_Level
        

class FindBWidget(BoxLayout):
    level=NumericProperty(1)
    scrore=NumericProperty(0)
    
    def __init__(self,**kwargs):
        super(FindBWidget,self).__init__(**kwargs)
        self.BBoxList=[]
        
    def on_level(self,instance,value):
        self.status_bar.label_level.text = 'L:{}'.format(self.level)
        
    def on_score(self,instance,value):
        self.status_bar.label_score.text = 'S:{}'.format(self.score)

    def Restart(self):
        self.play_area.SetLevel(self.level)
        self.play_area.clear_widgets()
        
        for i in range(1,self.level + Rows_For_First_Level + 1):
            for j in range(1,self.level + Rows_For_First_Level + 1):
                b = BBox(root=self,isBomb=(True if Random().randint(0,2) else False))
                b.row=i
                b.col=j
                b.CalculateBNumber()
                self.BBoxList.append(b)
                self.play_area.add_widget(b)
        
    
    def ShowAll(self):
        pass
    
    def GameOver(self):
        pass
    
class FindBApp(App):    
    def build(self):
        return FindBWidget()


if __name__ == '__main__':
    FindBApp().run()