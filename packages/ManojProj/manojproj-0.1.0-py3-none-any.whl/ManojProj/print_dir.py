import datetime
import os
import pathlib
numdir=0
numfiles=0
f=open('print_dir_out','w')
f.truncate(0)

def writerec(levelstr, objname, f):
    try:
        f.write(f"{levelstr} {objname}\n")
    except Exception as e:
        print(f"Error writing to file: {e}")
    
def printdir(level,path,f):
    global numdir, numfiles
    levelstr=level*'|'
    levelstr+='|__'
    #print(levelstr,'<',path.name,'>')
    #f.write(f"{levelstr} < {path.name} >\n")
    writerec(levelstr, '<'+path.name+'>', f)
    try:
        for x in pathlib.Path(path).iterdir():
            if x.is_dir():
                printdir(level+1,x,f)
                numdir+=1
            else:
                #print(levelstr,x.name)
                #f.write(f"{levelstr} {x.name}\n")
                writerec(levelstr, x.name, f)
                numfiles+=1
    except PermissionError as e:
        print(levelstr, 'PermissionError:', e)

#printdir(0,pathlib.Path('.'),f)
printdir(0,pathlib.Path('C:/Users/svman/Project'),f)
f.close()
print('Total directories:', numdir)
print('Total files:', numfiles) 