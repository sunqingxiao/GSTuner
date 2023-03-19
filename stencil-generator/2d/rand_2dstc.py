
import numpy as np
import random
import os


def genDsl (name, stc, step):
    ## generating dsl file 

    dsl = open (name + "t" + str(step) + ".idsl", 'w')
    # dsl header
    dsl.write("parameter M, N;\n")
    dsl.write("iterator j, i;\n")
    dsl.write("double in[M,N], out[M,N];\n\n")

    dsl.write("copyin in, out;\n\n")

    dsl.write("stencil randstc (out, in) {\n")

    if step == 1:
        dsl.write("\tout[j][i] = ")
    if step == 2:
        dsl.write("\tdouble temp[M,N];\n")
        dsl.write("\ttemp[j][i] = ")

    dsl.write("0.2 * in[j][i]")
    for i in range(1, len(stc)):
        (x, y) = stc[i]
        strX = str(x)
        if x >= 0:
            strX = '+' + strX
        strY = str(y)
        if y >= 0:
            strY = '+' + strY
        dsl.write("\n\t\t\t + 0.2 * in[j" + strY + "][i" + strX + "]")

    if step == 2:
        dsl.write(";\n\n")
        dsl.write("\tout[j][i] = 0.2 * temp[j][i]")
        for i in range(1, len(stc)):
            (x, y) = stc[i]
            strX = str(x)
            if x >= 0:
                strX = '+' + strX
            strY = str(y)
            if y >= 0:
                strY = '+' + strY
            dsl.write("\n\t\t\t + 0.2 * temp[j" + strY + "][i" + strX + "]")
        

    dsl.write(";\n}\n")
    dsl.write("randstc (out, in);\n")
    dsl.write("copyout out;")
    dsl.close()
    print("dsl sucessfully generated")


stencils = []

def gen2d (name):

    stc = [(0, 0)]
    curRing = [(0, 0)]
    
    p = np.array([8, 24, 48, 80]) / 160
    maxOrder = np.random.choice([1, 2, 3, 4], p = p.ravel())
    name = str(maxOrder) + "r" + name

    for order in range (0, maxOrder):
        nextRing = []
        for (x, y) in curRing:
            # left side
            if x == -order and x >= 1:
                if y >= 1:
                    nextRing.append((x-1, y-1))
                nextRing.append((x-1, y))
                nextRing.append((x-1, y+1))
    
            # right side
            if x == order:
                if y >= 1:
                    nextRing.append((x+1, y-1))
                nextRing.append((x+1, y))
                nextRing.append((x+1, y+1))
    
            # down side
            if y == -order and y >= 1:
                if x >= 1:
                    nextRing.append((x-1, y-1))
                nextRing.append((x, y-1))
                nextRing.append((x+1, y-1))
    
            # up side
            if y == order:
                if x >= 1:
                    nextRing.append((x-1, y+1))
                nextRing.append((x, y+1))
                nextRing.append((x+1, y+1))
        
        # delet the duplicate points
        nextRing = list(set(nextRing))
        # generate the number of points for current order
        cnt = random.randint(1, len(nextRing))

        random.shuffle(nextRing)

        curRing = nextRing[0:cnt]

        for point in curRing:
            stc.append (point)

    if stc in stencils:
        print(name, " in stencils")
        return False
    stencils.append(stc)


    full_stc = []
    for (x, y) in stc:
        full_stc.append((x, y))
        full_stc.append((x, -y))
        full_stc.append((-x, y))
        full_stc.append((-x, -y))
    full_stc = list(set(full_stc))

    ## generate dsl file
    genDsl (name, full_stc, 1)
    genDsl (name, full_stc, 2)

    ## save stencil as npz
    npstc = np.zeros((9,9), dtype=int)
    for (x,y) in full_stc:
        npstc[x + 4][y + 4] = 1
    np.savez(name + ".npz", npstc)
    
    #print(name)
    #print(npstc)
    os.system("bash create.sh " + name + " t1 &")
    os.system("bash create.sh " + name + " t2 &")
    return True

        
if __name__ == '__main__':
    cnt = 0
    while cnt < 500:
        if gen2d(str(cnt)):
            cnt += 1
