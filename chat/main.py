import openai
import dearpygui.dearpygui as dpg
from configparser import ConfigParser
import ast

promptList=[]
api_key=""
setShow=False
promptNum=0
temperature = 0.7
presence_penalty = 0.5
max_tokens = 2000

config = ConfigParser()
config.read('config.ini')
noFirst=config.getboolean("USER","noFirst")
promptList=ast.literal_eval(config.get("SET","promptList"))
api_key=config.get("SET","api_key")
promptNum=config.getint("USER","promptNum")  
temperature=config.getfloat("USER","temperature")
presence_penalty=config.getfloat("USER","presence_penalty")   
max_tokens=config.getint("USER","max_tokens")  

if(not noFirst):
    setShow=True
    
i = 0
outText = ""
openai.api_key = api_key

MODEL = "gpt-3.5-turbo"
model = MODEL
messages = [{"role": "system", "content":promptList[promptNum] }]
# listPrompt=["You are a helpful assistant.","You're a pirate, offering the least help"]
dpg.create_context()

width, height, channels, copyimg = dpg.load_image('img/copy.png')
width, height, channels, redoimg = dpg.load_image('img/redo.png') 
width, height, channels, sendimg = dpg.load_image('img/send.png') 
width, height, channels, setimg = dpg.load_image('img/set.png') 
with dpg.texture_registry():
    dpg.add_static_texture(width, height, copyimg , tag="texture_Copy")
    dpg.add_static_texture(width, height, redoimg , tag="texture_Redo")
    dpg.add_static_texture(width, height, sendimg , tag="texture_Send")
    dpg.add_static_texture(width, height, setimg , tag="texture_Set")
# 注册字体，自选字体
with dpg.font_registry():
    with dpg.font("MSYH.TTC", 24) as font1:  # 增加中文编码范围，防止问号
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Simplified_Common)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
    dpg.bind_font(font1)

dpg.create_viewport(width=1024,
                    height=800,
                    x_pos=400,
                    y_pos=150,
                    title="YunqiGPT",
                    resizable=False,
                    max_width=1024,
                    max_height=800,
                    decorated=True)
dpg.set_viewport_small_icon("img/logo.ico")
dpg.set_viewport_large_icon("img/logo.ico")


def click(user):
    global i
    global outText
    global messages
    messages.append({"role": "user", "content": user})
   
    # Call the OpenAI api for Chat GPT, and pass our complete list of messages
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        presence_penalty=presence_penalty,
        max_tokens=max_tokens,
        stream=True,
    )
    dpg.add_text(default_value="AI: ",
                 wrap=780,
                 parent="AIlist",
                 tag="AI" + str(i))
    res = ''
    collected_chunks = []
    collected_messages = []
    for chunk in response:
        collected_chunks.append(chunk)  # save the event response
        chunk_message = chunk['choices'][0]['delta']  # extract the message
        collected_messages.append(chunk_message)  # save the message
        full_reply_content = ''.join(
            [m.get('content', '') for m in collected_messages])
        # print("\r", full_reply_content, end="", flush=True)
        dpg.set_value("AI" + str(i), "AI:\n" + full_reply_content)
        dpg.configure_item("loading",show=False) 
    outText += dpg.get_value("AI" + str(i)) + "\n"
    

def submit_click():
    dpg.configure_item("loading",show=True)    
    user = dpg.get_value('AIinput')
    global i
    global outText
    i = i + 1
    dpg.add_text(default_value="你:\n" + user, wrap=780, parent="AIlist")
    outText += "你: " + user + "\n"
    click(user)


def quit_click():
    print("exitsys")
    os._exit(0)


def copy_click():
    dpg.set_clipboard_text(outText)
    
def redo_click():  
    global messages,outText
    dpg.configure_item("loading",show=False)       
    outText=""
    dpg.delete_item("AIlist")
    dpg.add_child_window(width=800, height=550, pos=(103, 40), tag="AIlist",parent="Main")    
    messages = [{"role": "system", "content":promptList[promptNum] }]
        
def set_click():
    dictWin=dpg.get_item_configuration("setWin")
    if(dictWin['show']==False):       
        dpg.configure_item("setWin",show=True,modal=True)
def set_close():
    global api_key,promptNum,temperature,presence_penalty,max_tokens,messages    
    api_key=dpg.get_value("api_key")
    openai.api_key = api_key
    promptNum=promptList.index(dpg.get_value("promptCombo"))
    temperature=dpg.get_value("temperature")
    presence_penalty=dpg.get_value("presence_penalty")
    max_tokens=dpg.get_value("max_tokens")
    config.set('SET', 'api_key', dpg.get_value("api_key"))
    config.set('SET', 'promptList', str(promptList))
    config.set('USER', 'nofirst', str(True))
    config.set('USER', 'promptNum', str(promptNum))
    config.set('USER', 'temperature', str(temperature))
    config.set('USER', 'presence_penalty', str(presence_penalty))
    config.set('USER', 'max_tokens', str(max_tokens))
    
    messages = [{"role": "system", "content":promptList[promptNum] }]
    with open('config.ini', 'w') as f:
        config.write(f)
    print("setWin is close")
def add_prompt():
    userPrompt=dpg.get_value("userPrompt")
    if(userPrompt!="" and   userPrompt!="your prompt..."):
        promptList.append(userPrompt)
        dpg.configure_item("promptCombo",items=promptList)
        
 
 
with dpg.window(width=1006,
                height=760,
                no_background=True,
                tag="Main",
                no_title_bar=True,
                no_resize=True,
                no_move=True):
    
     
    dpg.add_child_window(width=800, height=550, pos=(103, 40), tag="AIlist")
    dpg.add_loading_indicator(circle_count=8,pos=(820,600),color=(0,255,0,255),radius=3,thickness=3,tag="loading",show=False)

    dpg.add_input_text(pos=(103, 700),
                       width=700,
                       default_value="我的问题是...",
                       tag="AIinput")
   
   
    with dpg.window(width=600, height=450, pos=(200, 200), tag="setWin",label="Set",no_resize=True,show=setShow,modal=True,on_close=set_close):
        dpg.add_text(default_value="api_key:",pos=(20,50))
        dpg.add_input_text(pos=(40, 100),width=500,default_value=api_key,tag="api_key")   
        dpg.add_text(default_value="sysetem_prompt:",pos=(20,140))
        dpg.add_combo(items=promptList,width=500,pos=(40,180),tag="promptCombo",default_value=promptList[promptNum])
        dpg.add_button(width=60,pos=(40,230),tag="add",label="+Add",callback=add_prompt)
        dpg.add_input_text(tag="userPrompt",width=430,default_value="your prompt...",pos=(110,230))
        with dpg.tree_node(label="Set More",pos=(20,280)):
            dpg.add_text(default_value="temperature:",pos=(40,310))
            dpg.add_slider_float(pos=(160, 310),width=400,default_value=temperature,tag="temperature",min_value=0.0,max_value=2.0,)  
            dpg.add_text(default_value="presence_penalty:",pos=(40,350))
            dpg.add_slider_float(pos=(210, 350),width=350,default_value=presence_penalty,tag="presence_penalty",min_value=-2.0,max_value=2.0,)  
            dpg.add_text(default_value="max_tokens:",pos=(40,390))
            dpg.add_slider_int(pos=(160, 390),width=400,default_value=max_tokens,tag="max_tokens",min_value=50,max_value=2048)  
        
    dpg.add_image_button(texture_tag="texture_Set",pos=(950, 700),width=24,height=24, callback=set_click)
   
    with dpg.group(horizontal=True,pos=(380, 620),label="Copy"):             
        dpg.add_button(width=90, label="     Copy", callback=copy_click)
        dpg.add_image(texture_tag="texture_Copy",pos=(388,624),width=20,height=20) 
    with dpg.group(horizontal=True,pos=(550, 620),label="Redo"):             
        dpg.add_button(width=90, label="     Redo", callback=redo_click)
        dpg.add_image(texture_tag="texture_Redo",pos=(558,624),width=20,height=20)  
    with dpg.group(horizontal=True,pos=(842, 700),label="Send"):             
        dpg.add_button(width=90, label="     Send", callback=submit_click)
        dpg.add_image(texture_tag="texture_Send",pos=(850,704),width=20,height=20)  


   
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()