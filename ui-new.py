import pygame
import sys
from copy import deepcopy
from chatbot_new import chatBuddy
import threading
'''
Messing in Lines and Chat?
See what we did is we created two different things, first is a line class where each line gets stored, with the line image, line image has the image we will use to make the line
while also storing how many images stacked that will complete the line
on the second class we create the whole chat using the help of lines, we store each line is a object using the line class then we iterate through each line to display each line
as wanted
'''
''''
Woroooods!
We are dealing with a lot of text in many palces so we will create a text class which will have methods for text
'''
class text:
    '''Handles all your text methods'''
    def __init__(self) :
        pass
    def  word_wrap(self,message,char_width:int,chat_width:int,letters_inEachLine=None)->list[str]:
            '''Format/Wrap to: List with each ith item as another list containing the sentance of the ith line'''
            #Getting letters in each line
            if letters_inEachLine is None:
                letters_inEachLine = round(chat_width/char_width)
            else:
                letters_inEachLine=letters_inEachLine
    
            #BS Case-> If we can't even enter fit one char, then seriously this is an error or someone is literally on nuts But we won't check as this is a insider fucntion so I think person knwos what he is doing
            # if (letters_inEachLine<=1):
            #     sys.exit("What The Hell!")
    
            #Compensating for padding -> Don't have to as we do it with spaces
            # letters_inEachLine-=1
    
            #meta-formatting
            message=" ".join(message.strip().partition("\n"))
            message=message.split()
            message=[word for word in message if word!=''] #Removing empty characters whcih can cost us double space, ideally it should be there(as user typed it) but we will wipe them off for better messaging
    
            wrapped_message =[] #our return list where we need to load words
            char_loaded=0 #number of char alreayd loaded for this line to check if we reach character limit
            word_loaded=0#number of words already loaded for this line which we can remove from unloaded messages
            while (len(message)>0):
                '''
                How do words wrap work?
                See here we are doing word wrapping, what we are doing is, we are loaidng words in formatted message's line until we run out of words for the current line
                Each time we enter the loop we are processing a word.
                1st if check if we hit overflow of characters while loading in the line, if we did that means current word is insufficient to fit, now you might say, couldn't it be just sufficient
                to fit, and if yes we don't hit this if as you see we used > not >=. But one thing to notice here eahc word means word+one space even if its last word. I know its missing a edge case
                But we don't need to worry as it looks better than overflow and in addition to that we will add padding also a bit margin like so this thign will look good in that, maybe a  bit off in rare case
                but still good enough to work with
                2nd If checks if we ran out of word if yes, that means 2 things first we still have sapce to store this and second but still we ran out of words so we don't have to add a
                new line and can add all these words to this line only so we are not unloading the word rather loading all the loaded in
                3rd This checks for \n charcaters if entered inside line as we didn't heit end of line nor end of messages, then the new line is intended by the person so we will add a new line there so we will end the loading for that line
                and move to next line, also we will truncate \n as its functionality we already handled so it will just be there for nothing(a question mark character marking new line I guess?) so we will remove it
                4th The else , here we handle if we are in a line, in a line we just keep loading words and so charcters loaded increase, but in addition to words charcter we add one after each
                word, which represents another character added, what is this charcter? You guessed the space after each word.
                5th this the the lines that load line, and adds new line , when yu run this all the loaded words get's stored int he specific line and then we move to new line and we reset both words loaded for line
                and character laoded for line
                One thing new, what if we have a really long word, how do we know? So we will truncate words before hand if any word have lenght greater than the screen we will truncate it into smaller word whcih fits
                now for the next word if that too is too long to fit, again we only take what we cna print and pass the remainign to next word
                '''
                if (char_loaded>letters_inEachLine):
                        #end of line + word limit for this line=current loaded word-1 as when we are seeing this we already loaded the word whcih shoudl be on next line so just unloading it using word_loaded-=1
                        word_loaded-=1
                elif (word_loaded>=len(message) ):
                    #message ends
                    pass
                elif (message[word_loaded]=="\n"):
                    message=message[:word_loaded]+message[word_loaded+1:]
                else:
                    
                    if (len(message[word_loaded]))>letters_inEachLine:
                        #breaking into smaller words
                        smaller_words=[message[word_loaded][:letters_inEachLine-char_loaded-1] , message[word_loaded][letters_inEachLine-char_loaded-1:]] #Removing 1 beacuse of sapce whcih is at end whcih will cause everytime that word is one longer than the limit so the code again goes back, but as the word itself isn't larger than the limit so aagin loads it, but again beacuse of space it overflows so it again comes back, so to fix it we substracted one
                        message[word_loaded]=smaller_words[0] #repalcing the smaller word there and inserting the next part after wards to next index
                        message.insert(word_loaded+1,smaller_words[1])

                    #char_loaded +=   char in word                      +    sapce after word
                    char_loaded +=   len(message[word_loaded])  +     1
                    word_loaded+=1
                    continue
                wrapped_message.append(message[:word_loaded])
                message= message[word_loaded:]
                char_loaded=0
                word_loaded=0
    
            '''
            After this fromatted has lists each list has words which are for that line, we need to convert each list of that into a sentence using the words
            and a sentence is a string
            '''
            for line_index ,each_line in enumerate(wrapped_message):
                line_sentence=" ".join(each_line)
                #This changes the formatting of the message form list of words to string
                wrapped_message[line_index]=line_sentence
            return wrapped_message
    

class each_chat_line:
    '''This handles each chat line'''
    def __init__(self,chat_block_height,sentence:str,font:pygame.font.Font,colour:tuple[int,int,int],role:str):
        #Required text_lines for each letter height
        self.no_of_chat_block = ((font.size("A"))[1])/chat_block_height

        #Round to smallest integer greater than or equal to them
        if (self.no_of_chat_block%1==0):
            self.no_of_chat_block=int(self.no_of_chat_block)
        else:
            self.no_of_chat_block=int(self.no_of_chat_block)+1

        #Creating the text
        self.sentence = font.render(sentence,True,colour)

        #Loading 1 chatblock which we can draw multiple times
        self.chat_block=pygame.image.load(f"images/{role}_chat/text_line.png")
        



class each_chat:
    '''Thsi handles each chat message'''
    def __init__(self, chat_block_height, sentences: list[str], font: pygame.font.Font, colour: tuple[int, int, int], role: str):
        #Each line is a object having own sentence and all those combines in chat
        self.chat=[]
        for sentence in sentences:
            self.chat.append(each_chat_line(chat_block_height, sentence, font, colour, role))
        self.PADDING=5
        #loading top and bottom iamges
        self.top=pygame.image.load(f"images/{role}_chat/top.png")
        self.bottom=pygame.image.load(f"images/{role}_chat/bottom.png")

        #making top and bottom in a good format -> {"image":<has the pygame image>,"rect":<has the rect for the image>}
        self.top={"image":self.top,"rect":self.top.get_rect()}
        self.bottom={"image":self.bottom,"rect":self.bottom.get_rect()}

    def display_chat(self,screen,pos:tuple[int, int]):
        '''Uses top left corner to display your chat based on that and displays the curson where last messag ends'''


        #This is our cursor to draw chat while pos is our cursor to draw text
        chat_draw_cursor=pos

        #Drawing top
        self.top["rect"].topleft=chat_draw_cursor # type: ignore
        screen.blit(self.top["image"],self.top["rect"]) # type: ignore

        #Moving cursors
        pos=self.top["rect"].bottomleft # type: ignore
        chat_draw_cursor=self.top["rect"].bottomleft # type: ignore

        #Getting each line object
        for chat_line in self.chat:

            #Getting each image in each line object

            #Getting lines to draw
            lines_to_draw=chat_line.no_of_chat_block

            while (lines_to_draw>0):
                #Getting the image
                image_chat_line = chat_line.chat_block
                #For each image gettign rect

                image_chat_line_rect=image_chat_line.get_rect()

                #positioning rect

                image_chat_line_rect.topleft=chat_draw_cursor

                #Using rect to draw the chat_block

                screen.blit(image_chat_line,image_chat_line_rect)

                #Updating our cursor for next chat block to draw

                chat_draw_cursor=image_chat_line_rect.bottomleft

                #Updating number of block drawn
                lines_to_draw-=1

            #After drawing the chatblock for that line now drawing the text on top on the position of the line
            screen.blit(chat_line.sentence,(pos[0]+self.PADDING,pos[1]))
            #Updating line pos/ pos is like our cusror we move it to where we want to draw text
            pos=chat_draw_cursor

        #Drawing bottom
        self.bottom["rect"].topleft=chat_draw_cursor # type: ignore
        screen.blit(self.bottom["image"],self.bottom["rect"]) # type: ignore

        #Moving cursor
        pos=self.bottom["rect"].bottomleft # type: ignore
        chat_draw_cursor=self.bottom["rect"].bottomleft # type: ignore

        return pos

class chat_window:
    def __init__(self,screen,dimensions:tuple[int,int],height:int,initial_pos:tuple[int,int],is_active:bool=True):
        #getting screen
        self.screen = screen

        #Creating the surface/window for chat
        self.dimensions=dimensions
        self.chat_window_holder=pygame.Surface(dimensions)
        self.chat_window = pygame.Surface((dimensions[0],height))
        #Heigth of chat widnow
        self.height=height
        #active flag
        self.is_active=is_active
        #Chat Position
        self.chat_pos=initial_pos
        #Chat scroller cursor
        self.scroll_cursor=(0,0)
        #Creating a scroll multiplier
        self.scroll_scaler=20

    def scroll_chat_window(self,dy:int):
        '''Updates surface based on scroll dy'''
        if not self.is_active:
            return
        
        newY=self.scroll_cursor[1]+(dy*self.scroll_scaler)
        if (newY>0): #or ((newY-self.dimensions[1])<(-self.height)): 
            '''
            SCROOOOLING in limits
            While scorolling ,scrolling down means -ve direction and scrollign up means positive, but when you scroll down text goes up
            See in this command we see (newY-self.screen.get_size()[1] will give bottom as a negative for example if I am at (0,0) and 
             height is 20 so it will say (0,-20) which means we techniclaly showed 20 pixels so our cusor surrently is at -20 and -self.dimensions[1] represnts 
             what is maximum we can scroll down as the surface size is (100,500)(let) so it says maximum the cursor can go is -500 and from first info 
             we get our cursor is currently as -20
            SO this way we will only scroll required
            But we will remove the limit for just now
            '''
            return
        else:
            self.scroll_cursor=(self.scroll_cursor[0],newY)

    def display_chat_window(self):
        '''Displays chat window'''
        self.chat_window_holder.blit(self.chat_window,self.scroll_cursor)
        self.chat_window.fill((255,255,255))
        self.screen.blit(self.chat_window_holder,self.chat_pos)

class input_window:
    '''Here we can display the message after getting what is typed'''
    def __init__(self,screen,size:tuple[int,int],pos:tuple[int,int],input_box_width:int,font:pygame.font.Font,height:int,is_active:bool=True):
        self.screen=screen
        self.size=size
        self.window=pygame.Surface(size)
        self.input_box_width=input_box_width
        self.char_width,self.char_height=font.size("A")
        self.font = font
        #position of text_box
        self.pos=pos
        #position for scroll cursor in text box
        self.scroll_cursor=(0,0)
        #is active flag
        self.is_active=is_active
        #Buffer containing text objects for each line
        self.lines=[]
        #Height of text box
        self.height=height
        #Scroll scaler
        self.scroll_scaler=12
        #Loading a text_box outline on top
        self.text_box=pygame.Surface((size[0],height),pygame.SRCALPHA)
        #intial typing cursor
        self.typing_cursor=(0,0)
        #loading image of text block
        self.text_box_image=pygame.image.load("images/system/text_block.png").convert_alpha()
       
    def display_input_window(self,text_to_cursor):
        '''Handles the Drawing of message on text box'''
        self.text_box.fill((255,255,255,0))
        self.text_box.fill((255,255,255,0))
        self.window.fill((250,250,250))
        self.display_typing(text_to_cursor=text_to_cursor)
        #loading the text_box's scroll cursor position in window
        self.window.blit(self.text_box,self.scroll_cursor)
        #laoding the outline on top of text box
        self.window.blit(self.text_box_image,(0,0))

        self.screen.blit(self.window,self.pos)

    def load_typing(self,input_buffer:list[str]):
        '''Loads the buffer for displaying'''
        lines=[]
        for line in input_buffer:
            line_buffer=[]
            for letter in line:
                line_buffer.append(self.font.render(letter,True,(0,0,0)))
            lines.append(line_buffer)
        self.lines=lines[:]
        
    def display_typing(self,initial_pos=(8,5),spacing=0,text_to_cursor:int=0):
        '''Displays loaded buffer'''
        cursor=initial_pos
        for line in self.lines:
            left=cursor[0]
            bottom=0
            #Going for each letter
            for letter in line:
                #Gettign rect
                letter_rect=letter.get_rect()
                #Putting it there of cursor
                letter_rect.topleft=cursor
                #getting bottom of this text so after compelting line we can update cursor
                bottom=letter_rect.bottom
                #Adding given spacing
                letter_rect.left+=spacing
                #Checking if it is cursor if yes then drawing cursor
                if text_to_cursor==0:
                    pygame.draw.line(self.text_box,(0,0,0),letter_rect.topleft,letter_rect.bottomleft,1)
                                    
                #Drawing the text
                self.text_box.blit(letter,letter_rect)
                #Updating letter required to reach cursor
                text_to_cursor-=1
                #moving cursor to next letter
                cursor=letter_rect.topright
            cursor=(left,bottom)
            


    def scroll_text_box(self,dy:int):
            '''Updates surface based on scroll dy'''
            if not self.is_active:
                return
            newY=self.scroll_cursor[1]+(dy*self.scroll_scaler)
            if (newY>0) or ((newY-self.window.get_size()[1])<(-self.height)): 
                return
            else:
                self.scroll_cursor=(self.scroll_cursor[0],newY)
    
        

class typing_input:
    '''Handles taking input by typing'''
    def __init__(self,input_window:input_window,is_active:bool=True) :
        #initialising window
        self.input_window=input_window.window
        #event pipeline 
        self.event=None
        #typing activated or not
        self.is_active=is_active
        #Creating cursor ->format [line,char] and initialising it to [0,0]
        self.cursor=[0,0]
        #Creating input_buffer->Holder for the text
        
        self.input_buffer=[['']]

        self.char_line_max=round(input_window.input_box_width/input_window.font.size("A")[0])
        #Formatted cursor
        self.formatted_cursor=(0,0)
        #special keys
        self.arrow_keys=[pygame.K_UP,pygame.K_DOWN,pygame.K_LEFT,pygame.K_RIGHT]
        self.special_keys=[pygame.K_HOME,pygame.K_END,pygame.K_DELETE,pygame.K_BACKSPACE ,pygame.K_RETURN]
  
    
    def move_cursor(self,line:int,char:int,safe:bool=False):
        '''Moves cursor to the speicified location'''
        #Only move to valid pos when safe is true
        if safe:
            if line>=len(self.input_buffer) or line<0:
                return False
            elif char>len(self.input_buffer[line]) or char<0:
                return False
        self.cursor=[line,char]
        return True

    def get_correct_cursor_pos(self,line:int,char:int):
        '''To get the cursor position you might be wanting, recomended to use after you knwo your cursor is wrong, else just move cursor, always safe and inside range'''
        if line<0:
            line=0
        if line>=len(self.input_buffer):
            line=len(self.input_buffer)-1
        if char<0:
            #Checking if upward line avaliable and storign orginal cursor pos as it will be temporarily changed
            original_pos=self.cursor[:]
            if self.move_cursor(line-1,0,True):
                line=line-1
                char=len(self.input_buffer[line])
                self.move_cursor(original_pos[0],original_pos[1])
            else:
                #If no then it must be start of first line
                line=0
                char=0
        if char>len(self.input_buffer[line]):
            #Checking if downward line avaliable and storing orginal cursor pos as it will be temporarily changed
            original_pos=self.cursor[:]
            if self.move_cursor(line+1,0,True):
                line=line+1
                char=0
                self.move_cursor(original_pos[0],original_pos[1])
            else:
                #If not they must want last char of last line
                line=len(self.input_buffer)-1
                char=len(self.input_buffer[line])
        #After all checks return the corect pos
        return [line,char]
        


    
    def enter_letter(self,letter:str):
        '''Enters letter in current cursor position'''
        if self.cursor[0]>=len(self.input_buffer):
            self.input_buffer.append([])
        self.input_buffer[self.cursor[0]].insert(self.cursor[1],letter)
        pass
            

    def remove_letter(self,back:bool=False):
        '''Removes the given letter\nback says 0 for delete and 1 for backsapce'''
        if back:
            #Check if its normal backspace
            if self.move_cursor(self.cursor[0],self.cursor[1]-1,True):
                pass
            #If not we are currently at start of line most probably
            else:
                #if we are top line start we have nothign to delete
                if self.cursor[0]==0:
                    return False
                #else we will join the line of bottom and up to up
                else:
                    #moving the cursor to top line end
                    self.move_cursor(self.cursor[0]-1,len(self.input_buffer[self.cursor[1]])-1)
                    #joining the bottom line to up
                    self.input_buffer[self.cursor[0]].extend(self.input_buffer[self.cursor[0]+1])
                    #deleting bottom line
                    del self.input_buffer[self.cursor[0]+1]
        else:
            #checking if we are at end of line by tryign to go beyond this
            original_pos=self.cursor[:]
            #If it runs means we are currently at end of line so we will join the bottom line to this line and delete bottom line if it exists meas we are not at end line
            moved=self.move_cursor(self.cursor[0],self.cursor[1]+1,True)
            if not moved and (self.cursor[0]!=len(self.input_buffer)-1):
                #adding that content to current line
                self.input_buffer[self.cursor[0]].extend(self.input_buffer[self.cursor[0]+1][:])
                #Deleting bottom line
                del self.input_buffer[self.cursor[0]+1]
                return True
            elif moved:
                #Normal delete move the cursor back to original pos and delete
                self.move_cursor(original_pos[0],original_pos[1])
                pass
            else:
                return False
        #For normal cases
        del self.input_buffer[self.cursor[0]][self.cursor[1]]
        return True

    def new_line(self):
        '''Used to make new line at cursor position'''
        #Geting pre-content of the new line
        pre_content = self.input_buffer[self.cursor[0]][self.cursor[1]:]
        #Removing the charcters after it
        self.input_buffer[self.cursor[0]]=self.input_buffer[self.cursor[0]][:self.cursor[1]]
        #Moving to new line
        self.move_cursor(self.cursor[0]+1,0)
        #Adding new line
        self.input_buffer.insert(self.cursor[0],[])
        #Adding the pre content
        self.input_buffer[self.cursor[0]].extend(pre_content)
        return True
    '''
    See even if len returns index+1 but for char we have to have a last index, which will be last one means A| see the cursor is not at A its after A it means we need a last ghost
    index so we cna directly use len
    '''
    def type(self,letter:str,key):
        '''Handles typing in the letters, and cursor'''
        #Checking for arrow keys typed
        #Easy to undersatnd
        if key in self.arrow_keys:
            if key==pygame.K_UP:
                #Where I want to move
                to_move_to=[self.cursor[0]-1,self.cursor[1]]
                #If we can move htere move, if not
                if not self.move_cursor(to_move_to[0],to_move_to[1],True):
                    #Then get where we have to move then move it there
                    correct_location = self.get_correct_cursor_pos(to_move_to[0],to_move_to[1])
                    self.move_cursor(correct_location[0],correct_location[1])
            elif key==pygame.K_DOWN:
                #Where I want to move
                to_move_to=[self.cursor[0]+1,self.cursor[1]]
                #If we cna move htere move, if not
                if not self.move_cursor(to_move_to[0],to_move_to[1],True):
                    #Then get where we have to move then move it there
                    correct_location = self.get_correct_cursor_pos(to_move_to[0],to_move_to[1])
                    self.move_cursor(correct_location[0],correct_location[1])
            elif key==pygame.K_LEFT:
                #Where I want to move
                to_move_to=[self.cursor[0],self.cursor[1]-1]
                #If we cna move htere move, if not
                if not self.move_cursor(to_move_to[0],to_move_to[1],True):
                    #Then get where we have to move then move it there
                    correct_location = self.get_correct_cursor_pos(to_move_to[0],to_move_to[1])
                    self.move_cursor(correct_location[0],correct_location[1])
            elif key==pygame.K_RIGHT:
                #Where I want to move
                to_move_to=[self.cursor[0],self.cursor[1]+1]
                #If we cna move htere move, if not
                if not self.move_cursor(to_move_to[0],to_move_to[1],True):
                    #Then get where we have to move then move it there
                    correct_location = self.get_correct_cursor_pos(to_move_to[0],to_move_to[1])
                    self.move_cursor(correct_location[0],correct_location[1])

        #Self understainding very easy just call respective methods but with certain twists
        elif key in self.special_keys:
            if key==pygame.K_BACKSPACE:
                self.remove_letter(True)
            elif key==pygame.K_DELETE:
                self.remove_letter()
            elif key==pygame.K_HOME:
                if pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL] :
                    self.move_cursor(0,0,True)
                else:
                    self.move_cursor(self.cursor[0],0,True)
            elif key==pygame.K_END:
                if pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL] :
                    self.move_cursor(len(self.input_buffer)-1,len(self.input_buffer[-1])-1,True)
                else:
                    self.move_cursor(self.cursor[0],len(self.input_buffer[self.cursor[0]]),True)
            elif key==pygame.K_RETURN:
                self.new_line()
        else:
            if letter:
                self.enter_letter(letter)
                self.move_cursor(self.cursor[0],self.cursor[1]+1)
        pass

    def get_cursor_pos_from_first_char(self):
        '''Self explanatory name, just try once'''
        char_loaded=0
        line=self.cursor[0]-1#We don't need the line it's currently one as it's char we know we need len of all previous lines
        char=self.cursor[1]
        while line>=0:
            char_loaded+=len(self.input_buffer[line])+1#1 for the end line char
            line-=1
        char_loaded+=char
        return char_loaded

        
    def format_buffer(self):
        '''Returns message after formatting to give clean message with wrapping'''
        lines=[]
        lines_buffer=self.input_buffer[:]
        for line_index,line in enumerate(lines_buffer):
            #For each line we will split into as much lines required for fitting into the space
            line_buffer=""
            char_loaded=0
            #If char_loaded exceeded we stop and split and put the first one in , and if we reahc end of this line withotu hcar_loaded we just load it fully
            while char_loaded<self.char_line_max and char_loaded<len(line):
                line_buffer+=line[char_loaded]
                char_loaded+=1
            #Adding a end line char
            line_buffer+=' '
            #If char_loaded still points to valid index it means that char need to be added and still hasn't been added so we will add that to the lines_buffer to process next time in next line
            if char_loaded<len(line):
                lines_buffer.insert(line_index+1,line[char_loaded+1:])
            #Then we append the line to the lines
            lines.append(line_buffer)
        return lines
    
    def get_input(self,event_pipline:pygame.event.Event):
        '''Returns input and enters into buffer'''
        if self.is_active:
            if event_pipline.type==pygame.KEYDOWN:
                #Getting the key
                typed_unicode = event_pipline.unicode
                typed_key=event_pipline.key
                #typing the letter in message
                #Handiling Enter key
                if typed_unicode=="\r":
                    typed_unicode="\n"
                self.type(typed_unicode,typed_key)
        #Input buffer holds the buffer
        return self.format_buffer()
        
    def get_message(self):
        '''Make the text in message format and return and clears input'''
        message=""
        for line in self.input_buffer:
            for letter in line:
                message+=letter
            message+='\n'
        #Resetting the input buffer
        self.input_buffer=[['']]
        return message

'''
We will also handle things like arrow key and home key for it we will introduce our concept of cursor
Also the text box is a 2d array row represents lines and columns represnt letters in each row
'''
class send_button:
    '''Creates the send button'''
    def __init__(self,typing_input:typing_input,chat_buddy:chatBuddy,screen:pygame.Surface):
        self.typing_input=typing_input
        self.chat_buddy=chat_buddy
        self.image=pygame.image.load("images/system/send_box.png")
        self.image_rect=self.image.get_rect()
        self.screen=screen

    def send_request(self,message:str):
        '''Sends request to get chat and returns current reply'''
        #Sequence form chatBuddy not to be explained here tbh I also don't udnerstand fully now, but i knwo how to implement
        self.chat_buddy.sync_user(message)
        self.chat_buddy.update_user()
        self.chat_buddy.sync_chat()
        self.chat_buddy.update_chatB()
        self.chat_buddy.trim_messages_when_req()
        self.chat_buddy.reset_base_response()
        #storing physically too
        self.chat_buddy.store_chat()
        #returning the message
        return self.chat_buddy.chat
    def display_send_button(self,pos:tuple[int,int]):
        '''Displays send button'''
        self.image_rect.topleft=pos
        self.screen.blit(self.image,self.image_rect)
    def check_send(self,event:pygame.event.Event):
        '''checks if button is clicked'''
        if event.type==pygame.MOUSEBUTTONDOWN:
            if self.image_rect.collidepoint(event.pos[0],event.pos[1]):
                return True
            return False

class Ui:
    def __init__(self,chat:str):
        '''Intialising UI'''
        #setting up chatBuddy
        self.chat_buddy=chatBuddy(chat)
        #initialising pygame
        pygame.init()

        #Setting up screen
        self.screen = pygame.display.set_mode((800,600))

        #Setting up text handler
        self.text = text()

        #loading font
        self.font=pygame.font.Font("fonts/Comic Code.otf",20)

        #Setting up chat window->initlaly deactive
        self.chat_surface = chat_window(self.screen,(600,500),1200,(200,0),False)

        #Having a varibale for laoded chats
        self.loaded_chats=[]
        #Having a variable for chats
        self.messages=self.chat_buddy.chat_history['chat_history'][:]
        #Input->Initlially active
        self.input_window = input_window(self.screen,(600,100),(200,500),580,self.font,1200,True)
        self.input_typing = typing_input(self.input_window,True)
        #Send Button
        self.send_button = send_button(self.input_typing,self.chat_buddy,self.screen)
        #Setting up title:
        pygame.display.set_caption("Chat Buddy")
        #setting up time
        self.clock = pygame.time.Clock()
        self.fps=30

        #setting run flag
        self.running=False

    
    def end(self):
        '''Ending warp up'''
        pygame.quit()
        sys.exit(0)

    def get_window_active(self,window:pygame.Surface,event_pipeline:pygame.event.Event,pos:tuple[int,int]):
        '''Get if any given window is active or not'''
        window_rect=window.get_rect()
        window_rect.topleft=pos
        if event_pipeline.type==pygame.MOUSEBUTTONDOWN:
            return window_rect.collidepoint(event_pipeline.pos[0],event_pipeline.pos[1])

    

    def event_handler(self):
            '''Envent handler for UI'''
            for event in pygame.event.get():

                #Quit event
                if event.type==pygame.QUIT:
                    self.end()

                #Scroll event
                if event.type==pygame.MOUSEWHEEL:
                    #scrolling chat
                    self.chat_surface.scroll_chat_window(event.y)
                    #scrolling text box
                    self.input_window.scroll_text_box(event.y)
                #Input event
                #Reloading text_box
                self.input_window.load_typing(self.input_typing.get_input(event))
                #reply
                self.replying_chat=None
                #Send event
                if self.send_button.check_send(event):
                    self.update_chat_new_thread()
                #Window click event
                if event.type==pygame.MOUSEBUTTONDOWN:
                    self.input_typing.is_active=self.get_window_active(self.input_window.window,event,self.input_window.pos) # type: ignore
                    self.input_window.is_active=self.input_typing.is_active
                    self.chat_surface.is_active=self.get_window_active(self.chat_surface.chat_window_holder,event,self.chat_surface.chat_pos) #type: ignore

                

    def display_chat_window(self):
        '''Displays the chat window'''
        self.screen.fill((230, 230, 230))
        self.display_chats(padding=(10,20))
        self.chat_surface.display_chat_window()

    def display_input_window(self):
        '''Dispalys input on screen'''
        self.input_window.display_input_window(text_to_cursor=self.input_typing.get_cursor_pos_from_first_char())
        
    def load_chats(self):
        '''Loads Chats from self.messages from first'''
        self.loaded_chats=[]
        for message in self.messages:
            self.loaded_chats.append(each_chat(24,self.text.word_wrap(message["content"],self.font.size("A")[0],500),self.font,(0,0,0),message["role"]))

    def display_chats(self,padding:tuple[int,int]):
        '''Displays loaded chat into chat window'''
        cursor=padding
        for chat in self.loaded_chats:
            cursor=chat.display_chat(self.chat_surface.chat_window,cursor)
            cursor=(cursor[0],cursor[1]+padding[1])

    def update_chat(self):
        '''Updates chat'''
        #loading message
        user_input=self.input_typing.get_message()
        self.messages.append({'role':'user','content':user_input})
        #loading user message in GUI
        self.load_chats()
        #Getting reply
        reply=self.send_button.send_request(user_input)
        #loading reply
        self.messages.append(reply)

        #loading reply in GUI
        self.load_chats()
    
    def update_chat_new_thread(self):
        update_thread=threading.Thread(target=self.update_chat)
        if self.replying_chat is None:
            self.replying_chat=update_thread
        else:
            self.replying_chat.join()
        update_thread.start()

    def run_ui(self):
        #Loads chat once before starting
        self.load_chats()
        self.running=True
        while self.running:

            #Event handler
            self.event_handler()
            
            #Displaying chat window
            self.display_chat_window()

            #Displaying input window
            self.display_input_window()
            #Displaying send button
            self.send_button.display_send_button((0,500))
            
            #Running the clock
            self.clock.tick(self.fps)
            pygame.display.flip()

        self.end()
    
if __name__=='__main__':
    chat=input("Enter Chat Name:")
    u = Ui(chat)
    u.run_ui()
