import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty
from kivy.graphics import Rectangle

Rows_For_First_Level = 3

class BBox(Button):
    BNumber = NumericProperty(0)
    AppInstance = ObjectProperty(None)
    
    def __init__(self,**kwargs):
        super(BBox,self).__init__(**kwargs)
        self.row = 0
        self.col = 0
        self.isClear = False
        with self.canvas:
            self.bg_rect = Rectangle(source="flag.png", pos=self.pos, size=self.size)
    
    def Clear(self):
        '''
        triggered when user click the button and think it's empty or has a number
        '''
        if self.BNumber == -1:
            '''
            A Bomb, game over
            '''
            self.MarkB(true)
            self.Explode()
            AppInstance.root.GameOver()
        elif self.BNumber == 0:
            '''
            It's empty, show it and all the around empty boxes
            '''
            self.MarkEmpty()
        elif self.BNumber > 0:
            '''
            Has bomb around, show number only
            '''
            self.MarkNumber()
            
        self.isClear = True
        self.disabled = True
            
    def Explode(self):
        '''
        Animation needed
        '''
        pass
    
    def MarkEmpty(self):
        '''
        Not only mart itself as empty, also mark all around boxes if they are empty
        '''
        pass
    
    def MarkB(self,gameover=False):
        '''
        If this was marked correctly, then gameover should be false and color is black
        otherwise, color is red
        '''
        if self.isClear:
            return
        
        if gameover:
            self.color = (1,0,0,1)
        else:
            self.color = (0,0,0,1)

        #Draw flag
        
        
    
    def MarkNumber(self):
        self.text = '{}'.format(self.BNumber)
    

class PlayArea(GridLayout):
    def SetLevel(self,level):
        self.cols = self.rows = level + Rows_For_First_Level
        

class FindBWidget(BoxLayout):
    level=NumericProperty(1)
    scrore=NumericProperty(0)
    
    
    def on_level(self,instance,value):
        self.status_bar.label_level.text = 'L:{}'.format(self.level)
        
    def on_score(self,instance,value):
        self.status_bar.label_score.text = 'S:{}'.format(self.score)

    def Restart(self):
        self.play_area.SetLevel(self.level)
        self.play_area.clear_widgets()
        for i in range(1,(self.level + Rows_For_First_Level) * (self.level + Rows_For_First_Level) + 1):
            self.play_area.add_widget(BBox(text='',BNumber=i))
    
    def ShowAll(self):
        pass
    
class FindBApp(App):    
    def build(self):
        return FindBWidget()


if __name__ == '__main__':
    FindBApp().run()