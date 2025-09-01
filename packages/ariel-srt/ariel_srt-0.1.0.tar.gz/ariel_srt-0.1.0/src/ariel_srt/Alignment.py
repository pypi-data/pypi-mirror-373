import numpy as np
import thinplate as tps


def rigid_alignment(coord2, lm1, lm2, return_lm = True):
    one=np.ones(lm2.shape[0])
    lm2_1=np.insert(lm2,2,one,axis=1)
    M=np.dot(np.dot(np.linalg.inv(np.dot(lm2_1.T,lm2_1)),lm2_1.T),lm1)
    lm2_tran=np.dot(lm2_1,M)
    coord2_1=np.c_[coord2,np.ones(coord2.shape[0])]
    coord2_tran=np.dot(coord2_1,M)
    if(return_lm):
        return coord2_tran, lm2_tran
    else:
        return coord2_tran
    

def b0(x):
    x=((1-x)**3)/6
    return x

def b1(x):
    x=(3*x**3-6*x**2+4)/6
    return x

def b2(x):
    x=(-3*x**3+3*x**2+3*x+1)/6
    return x

def b3(x):
    x=x**3/6
    return x


def warp(points,grid,gx,gy):
    warp_p=np.zeros(points.shape)
    for i in range(points.shape[0]):
        xleft=int(points[i,0]/gx)
        ylow=int(points[i,1]/gy)
    
        dx=points[i,0]/gx-xleft
        dy=points[i,1]/gy-ylow

        if(xleft==19):
            if(ylow==19):
                warp_p[i,:]=grid[xleft,ylow]
            elif(ylow>0 and ylow<18):
                warp_p[i,:]=grid[xleft,ylow-1]*b0(dy)+grid[xleft,ylow]*b1(dy)+grid[xleft,ylow+1]*b2(dy)+grid[xleft,ylow+2]*b3(dy)
            else:
                warp_p[i,:]=grid[xleft,ylow]*(1-dy)+grid[xleft,ylow+1]*dy
            
        elif(xleft>0 and xleft<18):
            if(ylow==19):
                warp_p[i,:]=grid[xleft-1,ylow]*b0(dx)+grid[xleft,ylow]*b1(dx)+grid[xleft+1,ylow]*b2(dx)+grid[xleft+2,ylow]*b3(dx)
            elif(ylow>0 and ylow<18):
                warp_p[i,:]=grid[xleft-1,ylow-1,:]*b0(dx)*b0(dy)+grid[xleft-1,ylow]*b0(dx)*b1(dy)+grid[xleft-1,ylow+1]*b0(dx)*b2(dy)+grid[xleft-1,ylow+2]*b0(dx)*b3(dy)+grid[xleft,ylow-1]*b1(dx)*b0(dy)+grid[xleft,ylow]*b1(dx)*b1(dy)+grid[xleft,ylow+1]*b1(dx)*b2(dy)+grid[xleft,ylow+2]*b1(dx)*b3(dy)+grid[xleft+1,ylow-1]*b2(dx)*b0(dy)+grid[xleft+1,ylow]*b2(dx)*b1(dy)+grid[xleft+1,ylow+1]*b2(dx)*b2(dy)+grid[xleft+1,ylow+2]*b2(dx)*b3(dy)+grid[xleft+2,ylow-1]*b3(dx)*b0(dy)+grid[xleft+2,ylow]*b3(dx)*b1(dy)+grid[xleft+2,ylow+1]*b3(dx)*b2(dy)+grid[xleft+2,ylow+2]*b3(dx)*b3(dy)
            else:
                warp_p[i,:]=grid[xleft-1,ylow]*b0(dx)*(1-dy)+grid[xleft-1,ylow+1]*b0(dx)*dy+grid[xleft,ylow]*b1(dx)*(1-dy)+grid[xleft,ylow+1]*b1(dx)*dy+grid[xleft+1,ylow]*b2(dx)*(1-dy)+grid[xleft+1,ylow+1]*b2(dx)*(dy)+grid[xleft+2,ylow]*b3(dx)*(1-dy)+grid[xleft+2,ylow+1]*b3(dx)*dy
            
        else:
            if(ylow==19):
                warp_p[i,:]=grid[xleft,ylow]*(1-dx)+grid[xleft+1,ylow]*dx
            elif(ylow>0 and ylow<18):
                warp_p[i,:]=grid[xleft,ylow-1]*(1-dx)*b0(dy)+grid[xleft,ylow]*(1-dx)*b1(dy)+grid[xleft,ylow+1]*(1-dx)*b2(dy)+grid[xleft,ylow+2]*(1-dx)*b3(dy)+grid[xleft+1,ylow-1]*dx*b0(dy)+grid[xleft+1,ylow]*dx*b1(dy)+grid[xleft+1,ylow+1]*dx*b2(dy)+grid[xleft+1,ylow+2]*dx*b3(dy)
            else:
                warp_p[i,:]=grid[xleft,ylow,:]*(1-dx)*(1-dy)+grid[xleft+1,ylow,:]*dx*(1-dy)+grid[xleft+1,ylow+1,:]*dx*dy+grid[xleft,ylow+1,:]*(1-dx)*dy
            
    return warp_p
            

def non_linear_align(coord1,coord2,lm1,lm2, return_lm = True):

    theta2 = tps.tps_theta_from_points(lm1,lm2, reduced=True)
    grid2 = tps.tps_grid(theta2, lm2, (20,20))
    grid2= np.swapaxes(grid2, 0, 1)

    grid_or=np.zeros(grid2.shape)
    xseq=np.linspace(0,1,20)
    yseq=np.linspace(0,1,20)
    for i in range(grid_or.shape[0]):
        for j in range(grid_or.shape[1]):
            grid_or[:,j,0]=xseq
            grid_or[i,:,1]=yseq

    gx=grid_or[1,1,0]-grid_or[0,1,0]
    gy=grid_or[1,1,1]-grid_or[1,0,1]

    coord2_tran=warp(coord2,grid2,gx,gy)
    lm2_tran=warp(lm2,grid2,gx,gy)

    if(return_lm):
        return coord2_tran, lm2_tran
    else:
        return coord2_tran