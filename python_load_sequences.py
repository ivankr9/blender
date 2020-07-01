import bpy
import os



def getFirstNumFrameFile(filename):
    numer = 0
    firstframe = ''
    for ch in filename[::-1]:
        if numer == 0 or ch.isdigit():
            if ch.isdigit():
                firstframe = ch + firstframe
                numer = 1
        else:
            break		
    return firstframe

def LoadSequenceFromDir(directory,endfile='exr',use_sharp=True):
    len_ext = len(endfile)
    files = os.listdir(directory)
    count = 1
    counts = []
    sequences = []
    WithoutDigitName = ''
    seqfiles = []
    listmaxi = []
    currentindex = -1
    for f in sorted(files):
        if os.path.isfile(directory+'/'+f):
            if endfile == f[-len_ext:]:
                WithoutDigitName = ''.join([i for i in f if not i.isdigit()])
                if WithoutDigitName not in  sequences:
                    if len(sequences) > 0:
                        count = 1
                    sequences.append(WithoutDigitName)
                    seqfiles.append(f)
                    counts.append(count)
                    currentindex += 1
                    fr = int(f.split('.')[-2])
                    listmaxi.append(fr)
                else:
                    count += 1
                    counts.append(count)
                    fr = int(f.split('.')[-2])
                    if listmaxi[currentindex] < fr:
                        listmaxi[currentindex] = fr
    try:				
        lastframes = str(listmaxi[0])
    except:lastframes = '0'
    r = [0,0]
    seqParms = []
    if len(counts) > 0:
        numberofframes = max(counts)
        for seqF in seqfiles:
            firstFrame = getFirstNumFrameFile(seqF)
            intFF = int(firstFrame)
            r[0] = intFF
            intLF = int(firstFrame)+(numberofframes-1)
            r[1] = intLF
            padding = len(firstFrame)
            str_padding = '%0'+str(padding)+'d'
            if use_sharp:
                str_padding = '#' * padding
            spath = seqF.replace(firstFrame,str_padding)
            seqParms.append((directory.replace('\\','/'),r,spath,numberofframes,lastframes))
    return seqParms

def getDirsWithEXR(ix,dir_limmit,directory,dirlist,ext='exr'):
    print('#Search:',directory)
    if ix < dir_limmit:
        ix += 1
        for item in os.listdir(directory):
            try:
                itempath = directory+'/'+item
                if os.path.isdir(itempath):
                    rawcontentdir = str(os.listdir(itempath))
                    if ext in rawcontentdir:
                        dirlist.append(itempath)
                    getDirsWithEXR(ix,dir_limmit,itempath,dirlist)
            except:pass
    else:
        pass

def AddNodeImage(d='',i='',dur=1,a=0,locx=0,locy=0,offset=0):
    n = d.split('/')[-1]
    dontLocation = False
    if not n in ['hZemRL','neboRL','neboRL','charsRL','skyRL','bgRL']:
        image_node = tree.nodes.new(type='CompositorNodeImage')
    else:
        dontLocation = True
        #Find Node name
        if 'Cryptomatte_oM' in i:
            image_node = tree.nodes[n+'_Cryptomatte_oM']
        elif 'geometry' in i:
            image_node = tree.nodes[n+'_geometry']
        else:
            image_node = tree.nodes[n]
    dd = d.replace('/','\\')
    fp = dd+'\\'+i
    id = bpy.data.images.load(fp, check_existing=False)
    imgbld = id.name
    image_node.image = bpy.data.images[imgbld]
    if not dontLocation:
        image_node.location = locx,locy
    bpy.data.images[imgbld].source = 'SEQUENCE'
    image_node.frame_duration = dur
    image_node.frame_offset = offset
    image_node.label = n

    #image_node.hide = 0
    if a:
        image_node.colorspace_settings.name = 'Utility - Linear - Rec.709'


bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree

filepath = bpy.data.filepath
print(filepath)
droped = os.path.dirname(filepath)
dirpy = droped
parfolder = os.path.dirname(dirpy)
if '\\' in droped:
    dirpy = droped.replace('\\','/')
name = dirpy.split('/')[-1]

print('#From Folder:  ',dirpy)
#print(dirpy,'\n')
seqdirs = []
dir_limmit = 5
ix = 0
getDirsWithEXR(ix,dir_limmit,dirpy,seqdirs)
seqdirs.append(dirpy)
sequences = []
for sd in seqdirs:
    sp = LoadSequenceFromDir(sd)
    sequences += sp
dd = {}
i = 0
txt = ''


locx = 0
locy = 0
maxdur = 0
aces = 0
cdir = ''
for seq in sequences:
    print(seq[0])
    if cdir != seq[0]:
        cdir = seq[0]
        locx = 0
        locy -= 350
    locy -= 150
    seqstart = seq[1][0]
    duration = int(seq[4]) - seqstart + 1
    AddNodeImage(seq[0],seq[2].replace('####',str(seqstart).zfill(4)),duration,aces,locx,locy,seqstart-1)

    locx += 200
    if maxdur < duration:
        maxdur = duration

bpy.context.scene.frame_end = maxdur
sfilepath = filepath.split('/')
folderepsc = ''
for sf in sfilepath:
    if 'ep' in sf:
        if 'sc' in sf:
            folderepsc = sf
            break
#/dataserver/Project/MALYSH/output/ep34/render_tiff/ep34sc04/ep34sc04_
ep = folderepsc.split('sc')[0]
out = '/dataserver/Project/MALYSH/output/'+ep + '/render_tiff/' +folderepsc + '/' + folderepsc + '_'
bpy.context.scene.render.filepath = out
#/dataserver/Project/MALYSH/output/ep34/render_tiff/ep34sc02/ep34sc02_
