from tkinter import *
import random

class GUIDie(Canvas):
    '''6-sided Die class for GUI'''

    def __init__(self, master, valueList=[1, 2, 3, 4, 5, 6], colorList=['black'] * 6):
        '''GUIDie(master,[valueList,colorList]) -> GUIDie
        creates a GUI 6-sided die
          valueList is the list of values (1,2,3,4,5,6 by default)
          colorList is the list of colors (all black by default)'''
        # create a 60x60 white canvas with a 5-pixel grooved border
        Canvas.__init__(self, master, width=60, height=60, bg='white', bd=5, relief=GROOVE)
        # store the valuelist and colorlist
        self.valueList = valueList
        self.colorList = colorList
        #... initialize the top value to be a random number
        self.top = random.randrange(1, 7)

    def get_top(self):
        '''GUIDie.get_top() -> int
        returns the value on the die'''
        return self.valueList[self.top - 1]

    def roll(self):
        '''GUIDie.roll()
        rolls the die'''
        self.top = random.randrange(1, 7)
        self.draw()

    def draw(self):
        """GUIDie.draw()
        draws the pips on the die"""
        # clear old pips first
        self.erase()
        # location of which pips should be drawn
        pipList = [
            [(1, 1)],
            [(0, 0), (2, 2)],
            [(0, 0), (1, 1), (2, 2)],
            [(0, 0), (0, 2), (2, 0), (2, 2)],
            [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)],
            [(0, 0), (0, 2), (1, 0), (1, 2), (2, 0), (2, 2)],
        ]
        for location in pipList[self.top - 1]:
            self.draw_pip(location, self.colorList[self.top - 1])

    def draw_pip(self, location, color):
        '''GUIDie.draw_pip(location,color)
        draws a pip at (row,col) given by location, with given color'''
        (centerx, centery) = (15 + 20 * location[1], 15 + 20 * location[0])  # center
        self.create_oval(centerx - 5, centery - 5, centerx + 5, centery + 5, fill=color)

    def erase(self):
        '''GUIDie.erase()
        erases all the pips'''
        pipList = self.find_all()
        for pip in pipList:
            self.delete(pip)


class GUIFreezeableDie(GUIDie):
    '''a GUIDie that can be "frozen" so that it can't be rolled'''

    def __init__(self, master):
        '''GUIFreezeableDie(master,[valueList,colorList]) -> GUIFreezeableDie
        creates a GUI 6-sided freeze-able die
          valueList is the list of values (1,2,3,4,5,6 by default)
          colorList is the list of colors (all black by default)'''
        # copy the constructor from the super class
        GUIDie.__init__(self, master)
        self.isFrozen = False
        self.isFreezable = False
        self.valueList = [1, 2, 3, 4, 5, 6]
        self.colorList= (['red'] + ['black']) * 3
    
    #... note: it shows how to share the data between two classes
    def freeze(self, rollButton, freezeButton, dice, \
               actionLabel, currentAttempt, scoreLabel, update_score_callback):
        #... change the status of the die to be frozen
        self.isFrozen = True
        self.configure(bg='gray')
        #... Disable the freeze button
        freezeButton['state'] = DISABLED
        #... count frozen dice and current score
        numFrozen = 0
        updatedScore = 0
        #... check number of frozen dice, and total score after the freeze
        for n in range(len(dice)):
            if dice[n].isFrozen:
                numFrozen += 1
                updatedScore += dice[n].get_top()
        if numFrozen == len(dice):
            rollButton['state'] = DISABLED
            if currentAttempt == numAttempt:
                actionLabel['text'] = 'It is the last attempt. Click stop.'
            else:
                actionLabel['text'] = 'All dice are frozen. Click stop to next attempt.'
        else:
            #... enable the roll button
            rollButton['state'] = ACTIVE

        #... accumulate the top number into the score of the current attempt
        # scoreLabel['text'] = 'Attempt #{} Score: {}'.format\
        #                           (currentAttempt, updatedScore)
        
        # Use the callback to update the score in DecathDiscus
        update_score_callback(updatedScore)
        
    def remove_freeze(self):
        '''GUIFreezeableDie.toggle_freeze()
        toggles the frozen status'''
        self.isFrozen = False
        self.configure(bg='white')
        
    def is_frozen(self):
        '''GUIFreezeableDie.is_frozen() -> bool
        returns True if the die is frozen, False otherwise'''
        return self.isFrozen
    
    def is_freezable(self):
        self.isFreezable = False
        #... dice of even top is freezable
        if self.get_top() % 2 == 0:
            self.isFreezable = True
        return self.isFreezable
            
    def roll(self):
        '''GuiFreezeableDie.roll()
        overloads GUIDie.roll() to not allow a roll if frozen'''
        if not self.isFrozen:
            oldTop = self.get_top()
            self.top = random.randrange(1, 7)
            while self.top == oldTop:
                self.top = random.randrange(1, 7)
            self.draw()

class DecathDiscus(Frame):
    '''frame for a game of Discus'''

    def __init__(self, master, name):
        '''DecathDiscus(master,name) -> DecathDiscus
        creates a new Discus frame
        name is the name of the player'''
        # set up Frame object
        Frame.__init__(self, master)
        self.grid()
        # label for player's name
        Label(self, text=name, font=('Arial', 18)).grid(columnspan=2, sticky=W)
        # label for action message at the bottom
        self.actionLabel = Label(self, text="Click Roll button to start", font=('Arial', 18))
        self.actionLabel.grid(row=3, columnspan=5)
        # initialize game data: attempt, current score, high score among attempts
        self.attempt = 1
        self.score = 0
        self.hscore = 0
        # set up lables of current score and high score
        self.scoreLabel = Label(self, text='Attempt #1 Score: 0', font=('Arial', 18))
        self.scoreLabel.grid(row=0, column=2, columnspan=3)
        self.hscoreLabel = Label(self, text='High Score: {:02d}'.format(0), font=('Arial', 18))
        self.hscoreLabel.grid(row=0, column=5, columnspan=3, sticky=E)
        # initialize list of dice
        self.dice = []
        #... initialize the list of freezeButton, each component is a freezeButton
        self.freezeButton = []
        #... set up dice and freezeButton list
        for n in range(5):
            #... set up die list
            die = GUIFreezeableDie(self)
            self.dice.append(die)
            die.grid(row=1, column=n)
            #... set up freeze button
            freeze_button = Button(self, text='Freeze', state=DISABLED)
            freeze_button.grid(row=2, column=n, columnspan=1)
            self.freezeButton.append(freeze_button)
            #... note: the button should be config to share data between two classes
            freeze_button.config(command=lambda d=die, f=freeze_button: \
                    d.freeze(self.rollButton, f, self.dice, \
                             self.actionLabel, self.attempt, \
                             self.scoreLabel, self.update_score))
        
        # set up buttons: roll, stop
        self.rollButton = Button(self, text='Roll', command=self.roll)
        self.rollButton.grid(row=1, column=len(self.dice), columnspan=3)
        self.stopButton = Button(self, text='Stop', state=DISABLED, command=self.stop)
        self.stopButton.grid(row=2, column=len(self.dice), columnspan=3)
    
    #... note: recall the data from the other class back to current
    def update_score(self, new_score):
        '''Updates the score and the score label'''
        self.score = new_score
        self.scoreLabel['text'] = f'Attempt #{self.attempt} Score: {self.score}'

    def roll(self):
        '''DecathShotPut.roll()
        handler method for the roll button click'''
        #... initialize the number of die which is freezable
        numFreezable = 0
        #... initialize the number of die which is frozen
        numFrozen = 0
        #... show message
        self.actionLabel['text'] = "Click Roll button to start"
        #... disable all freezeButton when a new roll starts
        for n in range(len(self.dice)):
            self.freezeButton[n]['state'] = DISABLED

        # when roll button is clicked, roll all dice
        for n in range(len(self.dice)):
            #... roll dice, when freezed, the dice will not roll
            self.dice[n].roll()
            #... get status of dice
            if self.dice[n].is_freezable():
                #... active freeze button
                if self.dice[n].isFrozen:
                    #... number of frozen die
                    numFrozen += 1
                elif not self.dice[n].isFrozen:
                    #... number of freezable die
                    numFreezable += 1
                    #... enable freezeButton after roll
                    self.freezeButton[n]['state'] = ACTIVE
                    self.actionLabel['text'] = 'Freeze a die to continue or stop this attempt.'
                
        #... if no die is freezable, it is a FOUL
        if numFreezable == 0:
            self.stopButton.grid_remove() # Make the button invisible
            self.foulButton = Button(self, text='FOUL', state=ACTIVE, command=self.foul)
            self.foulButton.grid(row=2, column=len(self.dice), columnspan=1)     
            self.actionLabel['text'] = 'Sorry, it is a foul.'
         
        # #... when all dice are frozen
        # if numFrozen == len(self.dice):
        #     self.game_over()

        #... disable roll after it is clicked
        self.rollButton['state'] = DISABLED
        #... enable stop after roll
        self.stopButton['state'] = ACTIVE
        
    def stop(self):
        '''DecathShotPut.stop()
        handler method for the stop button click'''
        #... the stop button is clicked, update the high score
        if self.score > self.hscore:
            self.hscore = self.score
        
        #... update score label
        self.hscoreLabel['text'] = 'High Score: {:2d}'.format(self.hscore)
        #... initialize score
        self.score = 0
        
        #... the last attempt
        if self.attempt == numAttempt:
            #... stop game
            self.game_over()
        else:
            #... update label
            self.actionLabel['text'] = "Click Roll button to start"
            
            #... remove dice to start a new attempt
            for n in range(len(self.dice)):
                #... count the score
                if self.dice[n].isFrozen:
                    numTop = self.dice[n].get_top()
                    self.score += numTop
                #... reset dice
                self.dice[n].erase()
                self.dice[n].remove_freeze()
                self.freezeButton[n]['state'] = DISABLED
                
            #... disable stop after stop
            self.stopButton['state'] = DISABLED
            self.rollButton['state'] = ACTIVE
            #... attempt + 1
            self.attempt += 1
            
            self.score = 0
            #... when stop, reset score and increase an attempt
            self.scoreLabel['text'] = 'Attempt #{} Score: {}'.format\
                                      (self.attempt, self.score)

    def foul(self):
        '''DecathShotPut.foul()
        handler method for the foul button click'''
        if self.attempt == numAttempt:
            #... disable foul button
            self.foulButton['state'] = DISABLED
            #... stop game
            self.game_over()
        else:
            #... when fouled, reset score, gameround, and increase an attempt
            self.attempt += 1
            self.scoreLabel['text'] = 'Attempt #{} Score: {}'.format\
                                      (self.attempt, self.score)
            #... remove dice to start a new attempt
            for idice in self.dice:
                idice.erase()
            #... activate roll if not last attempt
            if self.attempt <= numAttempt:
                self.rollButton['state'] = ACTIVE
            #... remove old buttons
            self.foulButton.grid_remove()
            #... make new stop button
            self.stopButton = Button(self, text='Stop', state=DISABLED, command=self.stop)
            self.stopButton.grid(row=2, column=len(self.dice), columnspan=1)

            for n in range(len(self.dice)):
                self.dice[n].remove_freeze()
    
    def game_over(self):
        #... disable buttons
        self.stopButton['state'] = DISABLED
        self.rollButton['state'] = DISABLED
        #... disable freeze buttons
        for n in range(len(self.dice)):
            self.freezeButton[n]['state'] = DISABLED
        #... show message
        self.actionLabel['text'] = 'Game over'
        
#... define the maxium attemptes allowed
numAttempt = 3
# play the game
name = input("Enter your name: ")
root = Tk()
root.title('Discus')
game = DecathDiscus(root, name)
game.mainloop()
