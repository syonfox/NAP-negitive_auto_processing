import matplotlib.pyplot as plt
import subprocess as sp
import argparse
import numpy as np
import timeit
import json
from skimage.io import imread, imshow,imsave
from matplotlib import animation

from datetime import datetime

def take_pic(f,roll, frame, take, desc):
    print("Taking PIcture...")
    fname = f+"roll_"+str(roll)+"-frame_"+str(frame)+"-take_"+str(take)+"_("+desc+")"
    sp.call(['gphoto2', '--auto-detect','--capture-image-and-download','--force-overwrite',('--filename='+fname+'.%C') ])

    print("Done")
    #img = imread(fname+".ppm")
    return fname



def process_pic(f):
    print("Procssing...")
    sp.call(['ufraw-batch','--temperature=2000', f+'.cr2'])
    sp.call(['/usr/bin/gimp','-i', '-b','(convert-negitive "'+f+'.ppm")', '-b','(gimp-quit 0)'], shell=False )
    print("Done")

def save_rolls(f, r):
    print("Saving Rolls to Json ("+f+")...")
    meta = json.dumps(rolls)
    try:
        meta_f = open(f, 'w+')
        meta_f.write(meta)
        meta_f.close()
    except:
        return False
    print("Done")
    return True;

def load_rolls(f):
    print("Loading Rolls from Json ("+f+")...")
    try:
        meta_f = open(f, 'r')
    except:
        print("FAILED TO OPEN FILE: "+ f + ", Not Loading")

        return False

    meta = meta_f.read()
    rolls = json.loads(meta)
    print(rolls)
    print("Done")
    return rolls

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Captures pics')
    parser.add_argument("--save_path", type=str, default='./test')
    args = parser.parse_args()


    saved=False
    json_save_path= args.save_path+"filmbox2018.json"
    preview_save_path = args.save_path+".preview_filmbox2018.ppm"

    #open("save.json", 'r')
    rolls = load_rolls(json_save_path)
    rid = '1'
    if(not rolls or '1' not in rolls):
        rolls = {}

        rolls[rid] = {}
        rolls[rid]['next_frame'] = 1
        # rolls[rid]['next_take'] = 0
        rolls['next_id'] = '2'

    plt.show()

    while(True):


        r = rid
        f = rolls[r]['next_frame']
        if(f in rolls[r]):
            d = rolls[r][f]['desc']
            if('takes' in rolls[rid][f]):
                t = rolls[rid][f]['takes']
            else:
                t = 1
        else:
            d = ""
            t = 1

        opt = input("Next pic is in Roll:" + rid + " Frame:" + str(rolls[rid]['next_frame'])+ " Take:" + str(t) +"\nInput Frame Discription or option(h for help)["+d+"]: ")

        if(opt == "r"):

            id = input("Input Roll Id ["+str(rolls['next_id'])+"]: ")
            if(id not in rolls):
                print("Creating new Roll.")
                if(id.strip() == ""):
                    id = str(rolls['next_id'])
                    rolls['next_id'] += 1


                rolls[id] = {}
                rolls[id]['next_frame'] = 1
                desc = input("Roll Description (Optional): ")
                rolls[id]['desc'] = desc
            else:
                print("Roll with that id already exists switching to it")

            rid = id
        elif(opt == "f"):
            frame = input("Input The Desired Frame Number: ")
            rolls[rid]['next_frame'] = int(float(frame))
        elif(opt == "b"):
            print("Going back")
            rolls[rid]['next_frame'] -= 1
        elif(opt == "s"):
            savefile = input("Input the save file path: ")
            saved = save_rolls(savefile, rolls)
        elif(opt == "l"):
            load_path = input("Input the load file path: ")
            if(rolls):
                rolls = load_rolls(load_path)


        elif(opt == "p"):
            print("Taking Preview")
            fname = take_pic(args.save_path+"preview", "", "", "", "" )

            #process_pic(fname)
            img = imread(fname + ".ppm")
            positive = 255 - img

            imsave(preview_save_path, positive)

            plt.imshow(img)
           # plt.title(roll.name)
            plt.draw()
            #time.sleep(0.1)
            plt.pause(0.0001)

        elif(opt == "h"):
            print("Help For Capture:")
            print("r - create or switch to a roll")
            print("f - switch whitch file to work on")
            print("b - go back one fram to retake it")
            print("s - save the state of the program")
            print("l - load the state of the program")
            print("p - takes a preview picture")
            print("q - exit withough saving")




        elif(opt == "q"):
            break

        else:

            r = rid
            f = rolls[r]['next_frame']
            if(f not in rolls[r]):
                rolls[r][f] = {}
                rolls[r][f]['takes'] = 1
                rolls[r][f]['fnames'] = []
                rolls[r][f]['times'] = []
                rolls[r][f]['desc'] = ""

            if(opt.strip() != ""):
                rolls[r][f]['desc'] = opt

            take = rolls[r][f]['takes']

            fname = take_pic(args.save_path, r, f, take, opt )
            rolls[r][f]['fnames'].append(fname)
            rolls[r][f]['times'].append(str(datetime.utcnow())+'Z')
            print(rolls[r][f]['times'])

            process_pic(fname)
            img = imread(fname + ".ppm")
            #positive = 255 - img

            #imsave(preview_save_path, positive)

            plt.imshow(img)
           # plt.title(roll.name)
            plt.draw()
            #time.sleep(0.1)
            plt.pause(0.0001)
            save_rolls(json_save_path, rolls)
            if (saved): save_rolls(savefile,rolls) #save file to path instead of default path onl
            rolls[r][f]['takes'] += 1
            rolls[r]['next_frame'] += 1


