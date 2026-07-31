import requests
import json
from copy import deepcopy
'''
Some response Structure
1st/0th message always contain predfined static info about how the message to be sent
2nd/1st message always contain memory, base memory text is in request_base.json when updating just concat to it.
             When concating with older memory always delte the current memory response and re add it with base to concat again
3rd/2nd+ message contains normal chat history and chats


Stroing and Getting response from server is different
While stroing assistant's response we use a simple {"role":"","content":""} format for the sake of simplicity
But when reciving we recive "content" in two parts one is "reply" and one is "memory", we deal with each part differently
but when after dealing is complete we now wnat to store the history so for the sake of simplicity we remove the "memory"
section from the original response and in content there is the data from the reply section. By this section of code we
have stripped off the "memory" section of the original response, why? Beacuse we assume when we reach this section
of the pogram denoted by *, we have already stored the memory in desired place


Storing data on disk
To store data on disk we need only to store one thing that is chat_history.json and that will do the work
I will request the reader to seperate stroing from reading as both are handled differently also updating is a different task


Loading chat
when we first load up we will load previous 10 conversations(20 responses) from the chat_history only , not more that that.
If there is context from previous it needs to get it from the chort memory, thats our idea


Updating chat_history
To update history we will only update the chat_history which will do all things. We will add the responses there and thats it, nothing more. We won't save the default system messages there so first two elements of the messages variable
will never be stored.


Updating context
Updating context(excluding the memory) just means appedning new chats to the message section which directly links to the 
base_response's message section(throught here I will not use base_response's message section but I will say it messages)
When the lenght of the messages section hits 10(excluding 2 system message) conservation(user-chat) we will stipe off the 1st 
conversation.
Rather than going from bottom we will go from top to do so as it will be easier-> after system message 1st message will be
user's then the next one will be chat's so this way we will delete 1 consecutive chat.
We won't defensive check this as we are assuming our pogram ran fine and followed it's order, as given pogram's order its not
possible to ger user response and not chat's response, even if empty we will get chat's response else our pogram will crash
so that nothing is saved. 
We are relying on this to not make any checks for chat structure

Hardcoding vs General
The 10 you saw mentioned above is a hardcoded value but while writing code we used a general value it is just beacuse
that is a good practice, you can hard code 10 too no issues
----End of old comment----
What's new in this version?
Nothing core framework is same Just now we used OOP also known as Object Oriented Pogramming to maange it, why?
Just a niche choice to handle multiple chat bots, you cna use older or this one both as conceptually both operates
exactly same just some OOP differences of how you use classes and object else its same and the structure you read
in old comment is still as relevant as it was before as conceptually almsot nothing is different, Oh I forgot to mention 
one thing that is different and for it we used OOP as normal pogrmaming will make it hectic , is we can now create
multiple history for different chat, not just one in one dump. It is because...See for yourself in the code you will see
we load history from a name form the object's attribute which enables us to make multiple history without taking user input
and directly from code with minium lines, which is why many people use OOP

Why deepcopy(old+new)?
So it turns out everytime we store we are stroing self.user and self.chat now the problem is both of them are python dict so
upon storing and formating they too get formatted so every response looks like last response, so we are deep copying so further
changes to it won't change the history
'''
class chatBuddy:
    #Setting Up Enviroment
    def __init__(self,chat_name,model="gemma2:2b"):
        '''This single constrcutor sets up the enviroment'''
        #loading base response
        with open("request_base.json","r") as fd:
            self.base_response=json.load(fd)

        #loading user response
        with open("base_response_format.json","r") as fd:
            response_format=json.load(fd)
        self.user=response_format["user"]
        self.chat=response_format["chat"]


        #loading current memory
        try:
            #loading previous chat history
            fd = open(f"history/{chat_name}.json","r")

        except FileNotFoundError:
            #Creating new chat history from base model
            fd = open(f"history/{chat_name}.json","w")
            base_history = open("base_chat_history.json","r")

            #copying base model
            fd.write(base_history.read())

            #closing the temp files
            base_history.close()
            fd.close()

            #reopening the file
            fd = open(f"history/{chat_name}.json","r")

        #loading data
        self.chat_history=json.load(fd)
        self.chat_name=chat_name

        #closing file
        fd.close()
        

        #Static variables
        self.base_response["model"]=model
        self.chat_url="http://127.0.0.1:11434/api/chat"
        self.default_memory_response=deepcopy(self.base_response["messages"][1])
        self.CONV_LIMIT=10

        #Variables to be updated every prompt
        self.messages=self.base_response["messages"]
        self.messages.extend(self.chat_history["chat_history"][-10:]) #Loading Last 10 messages

    #Method to store chat
    def store_chat(self):
        print("Storing conversation.....")
        with open(f"history/{self.chat_name}.json","w") as fd:
            json.dump(self.chat_history,fd)
        print("Storing chat finished")

    #Method to update user sided messages
    def update_user(self):
        self.messages.append(deepcopy(self.user))
        self.chat_history['chat_history'].append(deepcopy(self.user))

    #Method to update chatB's message also desyncs the self.chat
    def update_chatB(self):
        '''After this is run self.chat is desynchnrosied from chat response and should be resync first to reuse'''
        #reformating chat's response to a more *storable one
        self.chat["content"]=self.chat["content"]["reply"]

        #storing chat
        self.messages.append(deepcopy(self.chat))
        self.chat_history['chat_history'].append(deepcopy(self.chat))

        


    #Method to get chatB's response/Sync chat
    def sync_chat(self):
        '''After this fuction self.chat is re/synced to chat's response, it can be used to print then store'''
        #getting response
        chat_response = requests.post(self.chat_url,json=self.base_response)
        
        #extracting required response from the packet given
        self.chat = json.loads(chat_response.text)['message']

        #converting type to favorable
        self.chat["content"]=json.loads(self.chat["content"])

        

    #Method to print chat
    def printChat(self):
        '''Running this requires re/synced self.chat
          Also it doesn't affect sync of chat'''
        #printing chat's reply
        print("Chat:"+self.chat["content"]["reply"])

    #Method to update cache/current memory
    def update_current_memory(self):
        '''Running this requires re/synced self.chat
            Also it doesn't affect sync of chat'''
        #updating memory
        self.chat_history["current_memory"]=self.chat["content"]["memory"]

    #Method for resetting base_response
    def reset_base_response(self):
        '''After this you can start for next chat'''
        #resetting base_response
        self.base_response["messages"][1]=self.default_memory_response
        #adding memory
        self.base_response["messages"][1]["content"]+=self.chat_history["current_memory"]

    #Method to trim currrent history/message for efficiency when required
    def trim_messages_when_req(self):
        #checking if over CONV_LIMIT conversation
        if (len(self.messages)-2)>=(self.CONV_LIMIT*2):
        # messages=  System message    +   Messages except top 2(1 conversation)
            self.messages=    self.messages[0:2]      +     self.messages[4:]
        #resyncing messages with base_response
        self.base_response["messages"]=self.messages

    #Method to sync user with a message
    def sync_user(self,message):
        '''uses message to sync the user into the chat'''
        #crafting response for user
        self.user["content"]=message


    #Method to take user input and run the chat for how much user wants
    def run_chat(self):
        '''used to run the chat bot'''
        running=True
        while running:
            #getting message from user
            user_msg=input("You:")

            #special stop message
            if (user_msg=="/break"):
                    running=False
                    break
            elif(user_msg=="/save"):
                self.store_chat()
                continue
            #Crafting user's response/syncing user with chat
            self.sync_user(user_msg)

            #updating user
            self.update_user()

            #getting chat's response/syncing chat
            self.sync_chat()

            #printing chat
            self.printChat()

            #updating current/cache memory
            self.update_current_memory()

            #updating chat/chatB
            self.update_chatB()

            #trimming
            self.trim_messages_when_req()

            #resetting self.base_response for next chat
            self.reset_base_response()
        self.store_chat()

if __name__=='__main__':
    mychatB = chatBuddy("late_night_chat")
    mychatB.run_chat()