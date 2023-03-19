
import os
import itertools
import random
import numpy as np
import time


def genDsl (name, stc, step):
    ## generating dsl file 

    dsl = open (name + "t" + str(step) + ".idsl", 'w')
    # dsl header
    dsl.write("parameter L, M, N;\n")
    dsl.write("iterator k, j, i;\n")
    dsl.write("double in[L,M,N], out[L,M,N];\n\n")

    dsl.write("copyin in, out;\n\n")

    dsl.write("stencil randstc (out, in) {\n")

    if step == 1:
        dsl.write("\tout[k][j][i] = ")
    if step == 2:
        dsl.write("\tdouble temp[L,M,N];\n")
        dsl.write("\ttemp[k][j][i] = ")

    dsl.write("0.2 * in[k][j][i]")
    for i in range(1, len(stc)):
        (x, y, z) = stc[i]
        strX = str(x)
        if x >= 0:
            strX = '+' + strX
        strY = str(y)
        if y >= 0:
            strY = '+' + strY
        strZ = str(z)
        if z >= 0:
            strZ = '+' + strZ
        dsl.write("\n\t\t\t+ 0.2 * in[k" + strZ + "][j" + strY + "][i" + strX + "]")

    if step == 2:
        dsl.write(";\n\n")
        dsl.write("\tout[k][j][i] = 0.2 * temp[k][j][i]")
        for i in range(1, len(stc)):
            (x, y, z) = stc[i]
            strX = str(x)
            if x >= 0:
                strX = '+' + strX
            strY = str(y)
            if y >= 0:
                strY = '+' + strY
            strZ = str(z)
            if z >= 0:
                strZ = '+' + strZ
            dsl.write("\n\t\t\t+ 0.2 * temp[k" + strZ + "][j" + strY + "][i" + strX + "]")
        

    dsl.write(";\n}\n")
    dsl.write("randstc (out, in);\n")
    dsl.write("copyout out;")
    dsl.close()
    print("dsl sucessfully generated")

stencils = []

def gen3d (name):

    stc = [(0, 0, 0)]
    curRing = [(0, 0, 0)]

    p = np.array([26, 124, 342, 728]) / 1220
    maxOrder = np.random.choice([1, 2, 3, 4], p = p.ravel())
    name = str(maxOrder) + "r" + name

    for order in range (0, maxOrder):
        nextRing = []
        for (x, y, z) in curRing:
            # left side
            if x == -order:
                move = itertools.product([-1, 0, 1], repeat=2)
                for (dy, dz) in move:
                    if x-1 >= 0 and y+dy >= 0 and z+dz >= 0:
                        nextRing.append((x-1, y+dy, z+dz))
    
            # right side
            if x == order:
                move = itertools.product([-1, 0, 1], repeat=2)
                for (dy, dz) in move:
                    if x+1 >= 0 and y+dy >= 0 and z+dz >= 0:
                        nextRing.append((x+1, y+dy, z+dz))
    
            # down side
            if y == -order:
                move = itertools.product([-1, 0, 1], repeat=2)
                for (dx, dz) in move:
                    if x+dx >= 0 and y-1 >= 0 and z+dz >= 0:
                        nextRing.append((x+dx, y-1, z+dz))
    
            # up side
            if y == order:
                move = itertools.product([-1, 0, 1], repeat=2)
                for (dx, dz) in move:
                    if x+dx >= 0 and y+1 >= 0 and z+dz >= 0:
                        nextRing.append((x+dx, y+1, z+dz))
        
            # back side
            if z == -order:
                move = itertools.product([-1, 0, 1], repeat=2)
                for (dx, dy) in move:
                    if x+dx >= 0 and y+dy >= 0 and z-1 >= 0:
                        nextRing.append((x+dx, y+dy, z-1))
        
            # front side
            if z == order:
                move = itertools.product([-1, 0, 1], repeat=2)
                for (dx, dy) in move:
                    if x+dx >= 0 and y+dy >= 0 and z+1 >= 0:
                        nextRing.append((x+dx, y+dy, z+1))
        
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
    for (x, y, z) in stc:
        full_stc += itertools.product([x, -x], [y, -y], [z, -z])
    full_stc = list(set(full_stc))


    ## generate dsl file
    genDsl (name, full_stc, 1)
    genDsl (name, full_stc, 2)


    ## save stencil as npz
    npstc = np.zeros((9,9,9), dtype=int)
    for (x,y,z) in full_stc:
        npstc[x+4][y+4][z+4] = 1
    np.savez(name + ".npz", npstc)
    
    #print(name)
    #print(npstc)
    os.system("bash create.sh " + name + " t1 &")
    os.system("bash create.sh " + name + " t2 &")
    return True

if __name__ == '__main__':
    cnt = 0
    while cnt < 500:
        if gen3d(str(cnt)):
            cnt += 1
            time.sleep(1)
