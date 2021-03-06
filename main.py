import sys,pygame,random,time, pygame.mixer, json
import os
from pygame.locals import *
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

clock = pygame.time.Clock()

nodes = {}
world = {}

def new_node(name,attributes):
    nodes[name] = attributes
    return

def print_nodes():
    for x in nodes:
        print(x)
        print(nodes[x])
    return

def play_sound(sound):
    pygame.mixer.music.load(sound)
    pygame.mixer.music.play()

def write(text, start_x,y):
    xadd = 0
    text = text.upper()
    for letter in str(text):
        screen.blit(pygame.image.load("textures/Numbers/"+letter+".png"),(start_x+xadd,y))
        xadd += 7

new_node("grass",{"description" : "Grass","hard" : False, "texture": "Grass.png"})
new_node("tnt",{"description" : "Tnt","hard" : False,"texture" : "TNT.png"})
new_node("tallgrass",{"description" : "TallGrass","hard" : False,"passthrough":True, "texture": "TallGrass.png"})
new_node("door",{"description" : "Door","hard" : True,"passthrough":True, "texture": "Door.png"})
new_node("door_closed",
         {"description": "Door_Closed",
          "hard": True,
          "texture": "Door_Closed.png"
         })
new_node(
    "door2",
    {"description" : "Door2",
     "hard" : True,
     "passthrough":True,
     "texture": "Door2.png"
    })
new_node("door_closed2",{"description" : "Door_Closed2","hard" : True, "texture": "Door_Closed2.png"})
new_node("water",{"description" : "Water","hard" : False,"passthrough":True, "texture": "Water.png"})
new_node("flowingwater",{"description" : "FlowingWater","hard" : False,"passthrough":True, "texture": "FlowingWater.png"})
new_node("flowingwater2",{"description" : "FlowingWater2","hard" : False,"passthrough":True, "texture": "FlowingWater2.png"})
new_node("backwall",{"description" : "BackWall","hard" : False,"passthrough":True, "texture": "BackWall.png" })
new_node("leaves",{"description" : "Leaves","hard" : False,"passthrough":True, "texture": "Leaves.png"})
new_node("tree",{"description" : "Tree","hard" : False,"passthrough":True, "texture": "Tree.png"})
new_node("iron",{"description" : "Iron","hard" : True, "texture": "Iron.png"})
new_node("gold",{"description" : "Gold","hard" : True, "texture": "Gold.png"})
new_node("stone",{"description" : "Stone","hard" : True, "texture": "Stone.png"})
new_node("brick",{"description" : "Brick","hard" : True, "texture": "Brick.png"})
new_node("air",{"description" : "Air","hard" : False,"passthrough":True})
new_node("sand",{"description" : "Sand","hard" : False, "texture": "Sand.png"})
new_node("wood",{"description" : "Wood","hard" : False, "texture": "Wood.png"})
new_node("sapling",{"description" : "Sapling","hard" : False, "texture": "Sapling.png"})
new_node("cactus",{"description" : "Cactus","hard" : False,"passthrough":True,"ow":True, "texture": "Cactus.png"})
new_node("iron_block",{"description" : "Iron_block","hard" : True, "texture": "Iron_block.png"})
new_node("gold_block",{"description" : "Gold_block","hard" : False, "texture": "Gold_block.png"})
# This old function isn't needed. It justs prints the nodes that exist before the game starts.
# If you really need to see the nodes that exist, look at the lines above.
# print_nodes()

def place_node(x, y, name, delta=(0, 0)):
    name = name.lower() # You can put in either the description or the lowercase name.
    if name in nodes:
        world[(x + delta[0], y + delta[1])] = name
    else:
        raise KeyError("{} is an invalid node type".format(name))

# convenience for logic readability

def place_node_above(x, y, name):
    place_node(x, y, name, delta=(0, 1))

def place_node_below(x, y, name):
    place_node(x, y, name, delta=(0, -1))

def place_node_right_of(x, y, name):
    place_node(x, y, name, delta=(1, 0))

def place_node_left_of(x, y, name):
    place_node(x, y, name, delta=(-1, 0))


def dig_node(x,y,inventory,health):
    old_node = get_node(x,y)
    if get_node(x,y).lower() in inventory:
        if inventory["pick"] != "" or not nodes[get_node(sx,sy).lower()]["hard"] or flags["mode"] == "Creative":
            inventory[get_node(x,y).lower()] += 1
            place_node(x,y,"air")
        if inventory["pick"] == "" and "ow" in nodes[old_node.lower()] and flags["mode"] == "Survival":
            health -= 1
    else:
        if inventory["pick"] != "" or not nodes[get_node(sx,sy).lower()]["hard"] or flags["mode"] == "Creative":
            inventory[get_node(x,y).lower()] = 1
            place_node(x,y,"air")

def explode(x,y,inventory,health):
    play_sound("sounds/explode.ogg")
    dig_node(x,y,inventory,health)
    for sx in range(-1,2):
        for sy in range(-1,2):
            if get_node(x+sx,y+sy).lower() == "tnt":
                explode(x+sx,y+sy,inventory,health)
            else:
                dig_node(x+sx,y+sy,inventory,health)
def get_node(x, y):
    coordinates = (int(round(float(x))), int(round(float(y))))
    return world.get(coordinates, 'stone')

# some convenience functions to make logic more readable

def get_node_above(x, y):
    return get_node(x, y+1)

def get_node_below(x, y):
    return get_node(x, y-1)

def get_node_left_of(x, y):
    return get_node(x-1, y)

def get_node_right_of(x, y):
    return get_node(x+1, y)


def get_player_x():
    scrollcheck = scrollx%16
    if scrollcheck > 8:
        return int(scrollx/16)+1
    else:
        return int(scrollx/16)

def get_player_y():
    return(scrolly/16)
# Generate a 2d world

maplimitx1 = -50
maplimitx2 = 50
maplimity1 = -50
maplimity2 = 50

def mapgen(grass,stone,air,iron,gold,tree,leaves,water,sand,tallgrass):
    MAPGEN_WATER = 0
    MAPGEN_BIOME = "Grassy"
    MAPGEN_HEIGHT = 0
    #PREMAPGEN
    x = maplimitx1-1
    while x != maplimitx2+1:
        y = maplimity1-1
        while y != maplimity2+1:
            place_node(x,y,air)
            y += 1
        x += 1
    #STONE MAPGEN
    x = maplimitx1
    while x != maplimitx2:
        y = maplimity1
        while y != maplimity2:
            if y < 1 and y > -11:
                place_node(x,y,stone)
            elif y < -10:
                randoint = random.randint(1,15)
                if randoint < 2:
                    place_node(x,y,iron)
                elif randoint == 15 and y < -5:
                    place_node(x,y,gold)
                else:
                    place_node(x,y,stone)
            else:
                if get_node(x,y).lower()== air:
                    place_node(x,y,air)
            y+= 1
        x+=1
    #MAPGEN
    x = maplimitx1
    while x != maplimitx2:
        if MAPGEN_HEIGHT > -1:
            if get_node(x-1,0).lower() == water:
                place_node(x,0,sand)
                place_node(x-1,-1,sand)
            else:
                if random.randint(1,10) == 1 and MAPGEN_BIOME == "Grassy":
                    MAPGEN_BIOME = "Desert"
                if random.randint(1,7) == 1 and MAPGEN_BIOME == "Desert":
                    MAPGEN_BIOME = "Grassy"
                if MAPGEN_BIOME == "Grassy":
                    place_node(x,MAPGEN_HEIGHT,grass)
                    gy = MAPGEN_HEIGHT
                    while gy > 0:
                        gy -= 1
                        place_node(x,gy,stone)
                elif MAPGEN_BIOME == "Desert":
                    place_node(x,MAPGEN_HEIGHT,sand)
                    gy = MAPGEN_HEIGHT
                    while gy > 0:
                        gy -= 1
                        place_node(x,gy,stone)
                    if random.randint(1,2) == 1:
                        place_node(x,MAPGEN_HEIGHT-1,sand)
        else:
            if get_node(x-1,0).lower() == grass or get_node(x-1,1).lower() == grass: # Make Shores
                place_node(x-1,0,sand)
            else:
                if random.randint(1,3) == 2 and get_node_left_of(x, y).lower() != sand:
                    place_node(x,0,water)
                    place_node(x,-1,water) # Make deeper sand banks
                    place_node(x,-2,sand)
                else:
                    place_node(x,0,water) # Make normal water
                    place_node(x,-1,sand)
        if random.randint(1,5) == 1 and MAPGEN_HEIGHT > 0 and MAPGEN_BIOME == "Grassy":
            treeheight = 1
            for i in range(1,random.randint(3,4)):
                place_node(x,i+MAPGEN_HEIGHT,tree)
                treeheight += 1
            place_node(x,treeheight+MAPGEN_HEIGHT,leaves)
            place_node(x+1,treeheight+MAPGEN_HEIGHT-1,leaves)
            place_node(x-1,treeheight+MAPGEN_HEIGHT-1,leaves)
        elif random.randint(1,5) == 1 and MAPGEN_WATER == 0 and MAPGEN_BIOME == "Grassy": # You may wonder what is different here. This new random will be different from the first, which causes this to work. Don't code like this, though.
            place_node(x,y+1+MAPGEN_HEIGHT, tallgrass)
        elif random.randint(1,5) == 1 and MAPGEN_WATER == 0 and MAPGEN_BIOME == "Desert":
            place_node(x,1+MAPGEN_HEIGHT,"cactus")
            place_node(x,2+MAPGEN_HEIGHT,"cactus") # Meh, forget asking for cactus name. I think I'll stop using arguments for this function eventually.
        MAPGEN_HEIGHT += random.randint(-1,1)
        if MAPGEN_HEIGHT > 4:
            MAPGEN_HEIGHT = 4
        if MAPGEN_HEIGHT < -1:
            MAPGEN_HEIGHT = -1
        x += 1
    return

def print_world():
    for x in world:
        print(world[x])
    return

mapgen("grass","stone","air","iron","gold","tree","leaves","water","sand","tallgrass")

hints = ["Logs can be used as one way ladders. You can jump without falling.","There is no method of healing, yet.","The code is open source.","There is no need to memorize craft recipes, just use the menu.","Only falling and cactus causes damage.","Don't punch the cactus, unless you have a pick.","Playing the game isn't much fun. Developing it is better."]
print("HAVE FUN!")
"""pygame window stuff"""
size = width,height = 600,400
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Building Blocks")
flags = {"mute":False,"mode":"Creative"}
def menu():
    menubutton = Rect(300,200,50,30)
    soundbutton = Rect(300,250,62,23)
    exitbutton = Rect(300,300,41,23)
    modebutton = Rect(300,350,127,37)
    leave = 0
    hintnumber = random.randint(0,len(hints)-1)
    while leave != 1:
        screen.blit(pygame.image.load("textures/menu.png"),(0,0))
        screen.blit(pygame.image.load("textures/Menu/Play!.png"),(300,200))
        screen.blit(pygame.image.load("textures/Menu/Sound_"+str(flags["mute"])+".png"),(300,250))
        screen.blit(pygame.image.load("textures/Menu/Exit_up.png"),(300,300))
        screen.blit(pygame.image.load("textures/Menu/"+flags["mode"]+".png"),(300,350))
        write(hints[hintnumber],30,30)
        mouse_x,mouse_y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # print(mouse_x,mouse_y)
                if pygame.Rect.collidepoint(menubutton,(mouse_x,mouse_y)):
                    play_sound("sounds/click.ogg")
                    screen.blit(pygame.image.load("textures/Menu/PLAY!.png"),(300,200))
                    pygame.display.flip()
                    time.sleep(0.5)
                    screen.blit(pygame.image.load("textures/Menu/Play!.png"),(300,200))
                    pygame.display.flip()
                    time.sleep(1)
                    leave = 1
                if pygame.Rect.collidepoint(soundbutton,(mouse_x,mouse_y)):
                    play_sound("sounds/click.ogg")
                    print("Sound (Un)Muting!")
                    flags["mute"] = not flags["mute"]
                if pygame.Rect.collidepoint(exitbutton,(mouse_x,mouse_y)):
                    play_sound("sounds/click.ogg")
                    print(";( Goodbye.")
                    screen.blit(pygame.image.load("textures/Menu/Exit_down.png"),(300,200))
                    time.sleep(0.5)
                    sys.exit()
                if pygame.Rect.collidepoint(modebutton,(mouse_x,mouse_y)):
                    if flags["mode"] == "Creative":
                        flags["mode"] = "Survival"
                    else:
                        flags["mode"] = "Creative"
                    print("Okay, "+flags["mode"]+" mode it is!")
        pygame.display.flip()

def craft():
    infotext = ""
    scroll = 0
    leave = 0
    while leave != 1:
        woodpick = Rect(150+scroll,200,32,32)
        woodbutton = Rect(100+scroll,200,32,32)
        door1button = Rect(200+scroll,200,32,32)
        door2button = Rect(250+scroll,200,32,32)
        exitbutton = Rect(300,300,41,23)
        saplingbutton = Rect(300+scroll,200,32,32)
        wallbutton = Rect(350+scroll,200,32,32)
        ironbutton = Rect(400+scroll,200,32,32)
        goldbutton = Rect(450+scroll,200,32,32)
        mouse_x,mouse_y = pygame.mouse.get_pos()
        textures = [pygame.image.load("textures/Wood.png"),pygame.image.load("textures/Pick_Wood.png"),pygame.image.load("textures/Menu/Tiny_Door.png"),pygame.image.load("textures/Menu/Tiny_Door2.png"),pygame.image.load("textures/Sapling.png"),pygame.image.load("textures/BackWall.png"),pygame.image.load("textures/Iron_block.png"),pygame.image.load("textures/Gold_block.png")]
        screen.blit(pygame.image.load("textures/craft.png"),(0,0))
        screen.blit(pygame.image.load("textures/Menu/Exit_up.png"),(300,300))
        keys = ["wood","pick","left door","right door","sapling","wall","iron","gold"]
        crafts = {"wood":["1 Tree",woodbutton],"pick":["4 Wood",woodpick],"sapling":["1 Leaf Block",saplingbutton],"left door":["6 Wood planks",door1button],"right door":["6 Wood planks",door2button],"wall":["1 Tree",wallbutton],"iron":["1 Iron Ore",ironbutton],"gold":["1 Gold Ore",goldbutton]}
        i = 0
        for texture in textures:
            tilebackground = pygame.image.load("textures/Menu/Craft_Background.png")
            if pygame.Rect.collidepoint(Rect((96 + (i * 50))+scroll,196,40,40),(mouse_x,mouse_y)):
                tilebackground = pygame.transform.scale(tilebackground,(45,45))
                scaleimage = 4
            else:
                tilebackground = pygame.transform.scale(tilebackground,(40,40))
                scaleimage = 0
            screen.blit(tilebackground,((96 + (i * 50))+scroll,196))
            screen.blit(pygame.transform.scale(texture,(32+scaleimage,32+scaleimage)),((100 + (i * 50))+scroll,200))
            screen.blit(pygame.font.Font('freesansbold.ttf',7).render(crafts[keys[i]][0],True,(0,0,0)),((90 + (i * 50))+scroll,240))
            screen.blit(pygame.font.Font('freesansbold.ttf',7).render(keys[i].upper(),True,(0,0,0)),((95 + (i * 50))+scroll,185))
            i += 1
        screen.blit(pygame.image.load("textures/Menu/ScrollLeft.png"),(0,0))
        screen.blit(pygame.image.load("textures/Menu/ScrollRight.png"),(500,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # print(mouse_x,mouse_y)
                if pygame.Rect.collidepoint(woodbutton,(mouse_x,mouse_y)):
                    play_sound("sounds/click.ogg")
                    if not "wood" in inventory:
                        inventory["wood"] = 0
                    if "tree" in inventory:
                        if inventory["tree"] >= 1:
                            print("You have crafted some wood.")
                            inventory["wood"] += 4
                            inventory["tree"] -= 1
                            infotext = "Wood is made from trees."
                        else:
                            infotext = "You do not have enough items. (You need 1 log.)"
                    else:
                        inventory["tree"] = 0
                        infotext = "You do not have enough items. (You need 1 log.)"
                if pygame.Rect.collidepoint(woodpick,(mouse_x,mouse_y)):
                    play_sound("sounds/click.ogg")
                    if "wood" in inventory:
                        if inventory["wood"] >= 4:
                            print("You have crafted a pick.")
                            inventory["pick"] = "Pick_Wood"
                            inventory["wood"] -= 4
                            infotext = "With a wood pick, you can mine stone and ore."
                        else:
                            infotext = "You do not have enough items. (You need 4 wood.)"
                    else:
                        inventory["wood"] = 0
                        infotext = "You do not have enough items. (You need 4 wood.)"
                if pygame.Rect.collidepoint(saplingbutton,(mouse_x,mouse_y)):
                    play_sound("sounds/click.ogg")
                    if not "sapling" in inventory:
                        inventory["sapling"] = 0
                    if "leaves" in inventory:
                        if inventory["leaves"] >= 1:
                            print("You have crafted a sapling.")
                            inventory["sapling"] += 1
                            inventory["leaves"] -= 1
                            infotext = "Plant saplings to make more trees. You will need lots of trees"
                        else:
                            infotext = "You need to mine leaves for saplings. Get more leaves from trees."
                    else:
                        inventory["leaves"] = 0
                        infotext = "You need to mine leaves for saplings. Get more leaves from trees."
                if pygame.Rect.collidepoint(door1button,(mouse_x,mouse_y)):
                    play_sound("sounds/click.ogg")
                    if not "door" in inventory:
                        inventory["door"] = 0
                    if "wood" in inventory:
                        if inventory["wood"] >= 6:
                            print("You have crafted a door.")
                            inventory["door"] += 1
                            inventory["wood"] -= 6
                            infotext = "This is a right side door. Doors can be opened and closed with a right click."
                        else:
                            infotext = "You do not have enough items. (You need 6 wood.)"
                    else:
                        inventory["wood"] = 0
                        infotext = "You do not have enough items. (You need 6 wood.)"
                if pygame.Rect.collidepoint(door2button,(mouse_x,mouse_y)):
                    play_sound("sounds/click.ogg")
                    if not "door2" in inventory:
                        inventory["door2"] = 0
                    if "wood" in inventory:
                        if inventory["wood"] >= 6:
                            print("You have crafted a door.")
                            inventory["door2"] += 1
                            inventory["wood"] -= 6
                            infotext = "This is a left side door. Doors can be opened and closed with a right click. (You need 6 wood.)"
                        else:
                            infotext = "You do not have enough items. (You need 6 wood.)"
                    else:
                        inventory["wood"] = 0
                        infotext = "You do not have enough items."
                if pygame.Rect.collidepoint(wallbutton,(mouse_x,mouse_y)):
                    play_sound("sounds/click.ogg")
                    if not "backwall" in inventory:
                        inventory["backwall"] = 0
                    if "tree" in inventory:
                        if inventory["tree"] >= 1:
                            print("You have crafted a door.")
                            inventory["backwall"] += 16
                            inventory["tree"] -= 1
                            infotext = "This is a back wall, which you can use to make your house not see-through."
                        else:
                            infotext = "You do not have enough items. (You need 1 log)"
                    else:
                        inventory["tree"] = 0
                        infotext = "You do not have enough items. (You need 1 log)"
                if pygame.Rect.collidepoint(ironbutton,(mouse_x,mouse_y)):
                    play_sound("sounds/click.ogg")
                    if not "iron_block" in inventory:
                        inventory["iron_block"] = 0
                    if "iron" in inventory:
                        if inventory["iron"] >= 1:
                            print("You have crafted an iron block.")
                            inventory["iron_block"] += 1
                            inventory["iron"] -= 1
                            infotext = "This iron block is appropriate for steel block bases."
                        else:
                            infotext = "You do not have enough items. (You need 1 iron ore)"
                    else:
                        inventory["iron"] = 0
                        infotext = "You do not have enough items. (You need 1 iron ore)"
                if pygame.Rect.collidepoint(goldbutton,(mouse_x,mouse_y)):
                    play_sound("sounds/click.ogg")
                    if not "gold_block" in inventory:
                        inventory["gold_block"] = 0
                    if "gold" in inventory:
                        if inventory["gold"] >= 1:
                            print("You have crafted a gold block.")
                            inventory["gold_block"] += 1
                            inventory["gold"] -= 1
                            infotext = "Ooooh!!! Pretty!"
                        else:
                            infotext = "You do not have enough items. (You need 1 gold ore)"
                    else:
                        inventory["gold"] = 0
                        infotext = "You do not have enough items. (You need 1 gold ore)"
                if pygame.Rect.collidepoint(exitbutton,(mouse_x,mouse_y)):
                    play_sound("sounds/click.ogg")
                    print("Okay, Crafting Completed.")
                    screen.blit(pygame.image.load("textures/Menu/Exit_down.png"),(300,200))
                    time.sleep(0.5)
                    leave = 1
        if mouse_x > 500:
            scroll -= 2
        if mouse_x < 100:
            scroll += 2

        write(infotext,30,30)
        pygame.display.flip()

menu()
resolution = 2 # This affects the zoom. Use higher values to zoom in and use less textures. (Note that for values bigger than 5, you cant see or dig anything below you.)
ychange = -1
animationvariable = 0
timer = 0
scrollx = 0
scrolly = 0
direction = ["right","","0"]
jumpyness = 0
yvelocity = 0
selectnode = "stone"
selectvar = 1
health = 3
gametime = 3000
selectlist = ["stone","grass","iron","gold","brick","tree","backwall","water","sand","door","door2","wood","tnt","sapling","iron_block","gold_block"]
inventory = {"pick":""}
pygame.key.set_repeat(1, 2)
gravitytimer = 0
dropthrough = ["air","water","flowingwater","backwall","tallgrass"]
old_top_text = ""
top_text = ""
top_text_timer = 0
moving = False
## Functions to make it easier.
def get_node_passible(x,y,modder):
    return nodes[get_node(x+modder,y).lower()].get("passthrough")

## End of Functions
while True:
    gametime += 1
    if gametime > 12000:
        gametime = 0
    if gametime > 3000 and gametime < 10000:
        screen.fill((125,125,255)) # Day
    elif (gametime < 3001 and gametime > 2250) or (gametime > 10000 and gametime < 10250):
        screen.fill((255,125,125)) # Dawn or Dusk
    else:
        screen.fill((50,50,100)) # Night
    write(top_text,10,10) # This is the text that appears up at the top of the screen. Usefull for messages to the player.
    if top_text != old_top_text:
        top_text_timer = 300
    old_top_text = top_text
    top_text_timer -= 1
    if top_text_timer <= 0:
        top_text = ""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Quit
            sys.exit()
        elif event.type == pygame.KEYDOWN and pygame.key.get_pressed()[K_LEFT]:
            # Go left
            moving = True
            ajust = 0
            if (scrollx/16.0) > 0:
                ajust = 0.75

            direction[0] = "left"
            direction[1] = ""
            if get_node_passible((scrollx/16.0)+ajust,(scrolly/16)+1,-0.25) and get_node_passible((scrollx/16)+ajust,(scrolly/16)+2,-0.25):
                if get_node(get_player_x(),get_player_y()) == "Water" or get_node(get_player_x(),get_player_y()) == "FlowingWater":
                    scrollx += 2
                    ychange += 1
                    if ychange > 3:
                        ychange = -1
                    scrolly += ychange
                else:
                    scrollx += 2
        elif not event.type == pygame.KEYDOWN and not event.type == pygame.MOUSEBUTTONDOWN:
            moving = False
        elif event.type == pygame.KEYDOWN and pygame.key.get_pressed()[K_RIGHT]:
            direction[0] = "right"
            direction[1] = ""
            moving = True
            # Go right
            if get_node_passible((scrollx/16),(scrolly/16)+1,0) and get_node_passible((scrollx/16),(scrolly/16)+2,0):
                if get_node(get_player_x(),get_player_y()) == "water" or get_node(get_player_x(),get_player_y()) == "flowingwater":
                    scrollx -= 2
                    ychange += 1
                    if ychange > 3:
                        ychange = -1
                    scrolly += ychange
                else:
                    scrollx -= 2
        elif not event.type == pygame.KEYDOWN and pygame.key.get_pressed()[K_RIGHT]:
            moving = False
        elif event.type == pygame.KEYDOWN and pygame.key.get_pressed()[K_UP]:
            # Jump
            if get_node(scrollx/16,scrolly/16) != "air" and get_node_passible(get_player_x(),get_player_y()+3,0):
                if get_node(get_player_x(),get_player_y()) == "water" or get_node(get_player_x(),get_player_y()) == "FlowingWater":
                    scrolly += 2
                else:
                    # scrolly += 28
                    yvelocity += 20
                    gravitytimer = 0
        elif event.type == pygame.KEYDOWN and event.key == K_g:
            # Find the node under the player and print it (if you are using a terminal)
            print(get_node(scrollx/16,scrolly/16))
            print(scrollx%16)
        elif event.type == pygame.KEYDOWN and event.key == K_c:
            # Change Clothing
            if direction[2] == "0":
                direction[2] = "1"
            elif direction[2] == "1":
                direction[2] = "2"
            elif direction[2] == "2":
                direction[2] = "0"
        elif event.type == pygame.KEYDOWN and event.key == K_m:
            # Make stuff, or craft if your from minecraft.
            if flags["mode"] == "Survival":
                craft()
        elif event.type == pygame.KEYDOWN and event.key == K_s:
            # Save
            play_sound("sounds/Save.wav")
            # if world/ doesn't exist, create it
            if not os.path.isdir("world"):
                os.mkdir("world")
            WorldSave = open("world/world.txt","w")
            # fix the keys so world can be serialized
            serializable_world = dict([
                (str(k).strip('()'), v)
                for k, v in world.items()
            ])
            WorldSave.write(json.dumps(serializable_world))

            WorldSave.close()
            pos_and_gametime = {"pos":str(scrollx) + "," + str(scrolly),"gametime":gametime,"inventory":inventory}
            PosSave = open("world/pos.txt","w")
            PosSave.write(json.dumps(pos_and_gametime))

            PosSave.close()
            top_text = "Saved."
        elif event.type == pygame.KEYDOWN and event.key == K_l:
            # Load
            try:
                play_sound("sounds/Load.wav")
                WorldSave = open("world/world.txt","r")
                iterate = 0
                raw_world = json.loads(WorldSave.read())
                # convert world keys back to tuples
                world = dict([
                    ((int(k.split(", ")[0]), int(k.split(", ")[1])), v)
                    for k, v in raw_world.items()
                ])
                WorldSave.close()
                PosSave = open("world/pos.txt","r")
                pos_and_gametime = json.loads(PosSave.read())
                newplayerpos = pos_and_gametime["pos"]
                newplayerx,newplayery = newplayerpos.split(",")
                scrollx = int(newplayerx)
                scrolly = int(newplayery)
                gametime = pos_and_gametime["gametime"]
                inventory = pos_and_gametime["inventory"]
                PosSave.close()
                top_text = "Load Complete"
            except:
                top_text = "Load Failure, maybe your file is old?"

        elif event.type == pygame.KEYDOWN and event.key == K_n:
            # Make a new world, so you don't need to restart.
            top_text = "Are you sure? Press Y to confirm, or press any key to stop."
            end = 0
            while end != 1:
                write(top_text,10,10)
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == K_y:
                        mapgen("grass","stone","air","iron","gold","tree","leaves","water","sand","tallgrass")
                        end = 1
                    elif event.type == pygame.KEYDOWN and event.key != K_y:
                        end = 1
                pygame.display.flip()

            top_text = "Created another world."
            gametime = 3000
        elif event.type == pygame.KEYDOWN and event.key == K_SPACE:
            # Change selected item
            selectvar += 1
            if selectvar > len(selectlist) -1:
                selectvar = 0
            selectnode = selectlist[selectvar]
        elif event.type == pygame.KEYDOWN and event.key == K_LCTRL:
            # Change selected item
            selectvar -= 1
            if selectvar < 1:
                selectvar = len(selectlist) - 1
            selectnode = selectlist[selectvar]
        elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
            # Pause and go to the menu.
            menu()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Build or dig
            mouse_x,mouse_y = pygame.mouse.get_pos()
            spos = sx,sy = (int(round((-((mouse_x+(308*(resolution-1)))/(16*resolution))+19.75)+scrollx/(16))),int(round((-((mouse_y+(208*(resolution-1)))/(16*resolution)))+14.75+(scrolly/16))))
            if event.button == 1: # Dig or Build
                if get_node(sx,sy) == "air" or get_node(sx,sy) == "water" or get_node(sx,sy) == "flowingwater":
                    if selectnode in inventory and flags["mode"] == "Survival" and inventory[selectnode] > 0:
                        place_node(sx,sy,selectnode)
                        inventory[selectnode] -= 1
                    elif flags["mode"] == "Creative":
                        place_node(sx,sy,selectnode)
                    direction[1] = "build"
                    if flags["mute"] == False:
                        play_sound("sounds/place.ogg")
                else:
                    dig_node(sx,sy,inventory,health)
                    direction[1] = "pick"
                    if flags["mute"] == False:
                        play_sound("sounds/dig.ogg")
            elif event.button == 3: # Open Doors, press buttons, etc.
                if get_node(sx,sy) == "door":
                    place_node(sx,sy,"door_closed")
                elif get_node(sx,sy) == "door_closed":
                    place_node(sx,sy,"door")
                if get_node(sx,sy) == "door2":
                    place_node(sx,sy,"door_closed2")
                elif get_node(sx,sy) == "door_closed2":
                    place_node(sx,sy,"door2")
                if get_node(sx,sy) == "tnt":
                    explode(sx,sy,inventory,health)
    if moving == True:
        animationvariable += 1
        if animationvariable == 10:
            direction[1] = "walk"
            animationvariable = 1
        elif animationvariable > 5:
            direction[1] = "walk"
        else:
            direction[1] = ""
    elif moving == False:
        direction[1] = ""

    scrollcheck = (scrollx%16)
    if not yvelocity <= 0:
        yvelocity -= 4
        scrolly += yvelocity
    # Gravity and Falling to death
    if scrolly < -800:
        health -=1 # If you fall off of the world, you will die.
    if get_node(get_player_x(),get_player_y()) in dropthrough:
        gravityon = True
        if get_node(get_player_x(),get_player_y()) == "water" or get_node(get_player_x(),get_player_y()) == "flowingwater":
            scrolly -= 1
            gravitytimer = 0
        else:
            gravitytimer += 1
            scrolly -= 4
    else:
        gravityon = False
        if gravitytimer > 30 and flags["mode"] == "Survival":
            play_sound("sounds/damage.ogg")
            health -= 1
            if gravitytimer > 60: # If I fell even farther, give even more damage.
                health -= 1
        gravitytimer = 0
    if not gravityon: # Puts you strait on the ground if you missed it.
        scrolly += scrolly%16 - 12
        if (not get_node(get_player_x(),get_player_y() + 1) in dropthrough) and not get_node_passible(get_player_x(),get_player_y()+1,0):
            scrolly += 16
    if scrolly > -290:
        screen.blit(pygame.image.load("textures/Underground.png"),(0,scrolly+((int(300)-14.5)))) # Makes underground background.
    else:
        screen.blit(pygame.image.load("textures/Underground.png"),(0,0)) # Makes underground dark.
    # ABMs, Physics, Block drawing, etc.
    for block in world:
        x, y = block
        here = world[block]
        above = get_node_above(*block)
        below = get_node_below(*block)
        to_right = get_node_right_of(*block)
        to_left = get_node_left_of(*block)

        # Do water and sand physics
        if here == "water":
            if below != "air":
                if to_left == "air":
                    place_node_left_of(*block,"flowingwater")
                if to_right == "air":
                    place_node_right_of(*block,"flowingwater")
            else:
                place_node_below(*block, "flowingwater")
            if below in ("air", "flowingwater"):
                place_node_below(*block, "water")
        if here == "flowingWater":
            if "water" not in (to_left, to_right):
                place_node(*block, "air")
                here = world[block]
            if below != "air":
                if to_left == "air" and (below != "air" and below != "water" and below != "flowingwater"):
                    place_node_left_of(*block, "flowingwater2")
                if to_right == "air" and (below != "air" and below != "water" and below != "flowingwater"):
                    place_node_right_of(*block, "flowingwater2")
            if below == "air" or below == "flowingwater":
                place_node_below(*block, "water")
        if here == "flowingwater2":
            if to_left != "flowingwater" and to_right != "flowingwater":
                place_node(*block, "air")
        if here == "sand" and timer == 10:
            if below == "air" or below == "tallgrass":
                place_node(*block, "air")
                here = world[block]
                place_node_below(*block, "sand")
        # Grow Saplings
        if here == "sapling" and timer == 10 and random.randint(1,10) == 1:
            place_node(*block,"tree")
            here = world[block]
            place_node_above(*block,"tree")
            if random.randint(1,3) == 3:
                tree = {
                    (0, 2): "tree",
                    (1, 2): "leaves",
                    (-1, 2): "leaves",
                    (0, 3): "leaves"
                }
            else:
                tree = {
                    (1, 1): "leaves",
                    (-1, 1): "leaves",
                    (0, 2): "leaves"
                }
            for delta, ntype in tree.items():
                place_node(*block, ntype, delta)
        # Render blocks
        if here != "air":
            if scrollx+((x-20) * -16) < 610 and scrollx+((x-20) * -16) > -10:
                if scrolly+((y-14)* -16) < 410 and scrolly+((y-14)* -16) > -30:
                    if "texture" in nodes[get_node(x,y).lower()]:
                        picture = pygame.image.load("textures/" + nodes[get_node(x,y).lower()]["texture"])
                        size = height,width = picture.get_size()
                        screen.blit(pygame.transform.scale(picture,(width*resolution,height*resolution)),((scrollx*resolution+((x-19.5) * -16*resolution))-(308*(resolution-1)),(scrolly+((y-14.5)* -16))*resolution-(208*(resolution-1))))
                    else:
                        picture = pygame.image.load("textures/" + get_node(x,y) + ".png")
                        size = height,width = picture.get_size()
                        screen.blit(pygame.transform.scale(picture,(width*resolution,height*resolution)),((scrollx*resolution+((x-19.5) * -16*resolution))-(308*(resolution-1)),(scrolly+((y-14.5)* -16))*resolution-(208*(resolution-1))))
    if flags["mode"] == "Survival": # Hearts, Death Screen and Respawn.
        if health > 2:
            screen.blit(pygame.image.load("textures/player/heart.png"),(20,20))
        if health > 1:
            screen.blit(pygame.image.load("textures/player/heart.png"),(35,20))
        if health > 0:
            screen.blit(pygame.image.load("textures/player/heart.png"),(50,20))
        if health <= 0:
            screen.blit(pygame.image.load("textures/Death.png"),(250,250))
            health = 0
        if health == 0 and timer == 15:
            health = 3
            scrollx = 0
            scrolly = 0
    # Render the player
    player = pygame.transform.scale(pygame.image.load("textures/player/playerleft" + direction[1] + direction[2] + ".png"),(32*resolution,40*resolution))
    if direction[0] == "right":
        # If he is pointing in another direction, turn around.
        player = pygame.transform.flip(player,True,False)
    screen.blit(player,(306,204))
    screen.blit(pygame.image.load("textures/BlockSelect.png"),(550,25))
    if "texture" in nodes[selectnode]:
        screen.blit(pygame.image.load("textures/" + nodes[selectnode]["texture"]),(552,27))
    else:
        screen.blit(pygame.image.load("textures/" + nodes[selectnode]["description"] + ".png"),(552,27))
    if flags["mode"] == "Survival":
        xadd = 0
        if selectnode in inventory:
            for letter in str(inventory[selectnode]):
                screen.blit(pygame.image.load("textures/Numbers/"+letter+".png"),(535+xadd,40))
                xadd += 10
        else:
            screen.blit(pygame.image.load("textures/Numbers/0.png"),(535,40))
        if not inventory["pick"] == "":
            screen.blit(pygame.image.load("textures/" + inventory["pick"] + ".png"),(552,47))
    # Timer for certain things.
    if timer >= 15:
        timer = 0
    timer += 1
    if scrolly > -50: # If you aren't underground, then show the sky.
        # The Dark. At night time. (And some stars.)
        if gametime > 10250:
            screen.blit(pygame.image.load("textures/TheDark.png"),(0,0))
            screen.blit(pygame.image.load("textures/Stars.png"),((gametime - 10250)/10,0))
            screen.blit(pygame.image.load("textures/Stars.png"),(((gametime - 10250)/10) - 400,0))
        if gametime < 2250:
            screen.blit(pygame.image.load("textures/TheDark.png"),(0,0))
            screen.blit(pygame.image.load("textures/Stars.png"),((gametime + 175)/10,0))
            screen.blit(pygame.image.load("textures/Stars.png"),(((gametime + 175)/10) - 400,0))
        # The sun. At day time.
        if gametime > 3000 and gametime < 10000:
            screen.blit(pygame.image.load("textures/Sun.png"),((gametime - 3000)/17.5,10))
    # Update the screen.
    pygame.display.flip()
