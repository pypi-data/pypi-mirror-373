import numpy as np
import math

def normalization_spatial(spatial):
    spatial1=np.zeros(spatial.shape)
    maxx=np.max(spatial[:,0])
    minx=np.min(spatial[:,0])
    maxy=np.max(spatial[:,1])
    miny=np.min(spatial[:,1])

    x=(spatial[:,0]-minx)/(maxx-minx)
    y=(spatial[:,1]-miny)/(maxy-miny)
    spatial1[:,0]=x
    spatial1[:,1]=y
    return spatial1


def Rasterization(spatial, embedding,nx=40,ny=40):
    x=spatial[:,0]
    y=spatial[:,1]
    minx=np.min(x)
    maxx=np.max(x)
    miny=np.min(y)
    maxy=np.max(y)

    dx=(maxx-minx)/nx
    dy=(maxy-miny)/ny
    spatial_return=np.zeros([1,2])
    gene_return=np.zeros([1,embedding.shape[1]])
    
    for i in range(nx):
        for j in range(ny):
            xmi=minx+i*dx
            xma=minx+(i+1)*dx
            
            ymi=miny+j*dy
            yma=miny+(j+1)*dy
            
            xarray=np.where((x>=xmi) & (x<xma))[0]
            yarray=np.where((y>=ymi) & (y<yma))[0]
            
            gene1=np.zeros([1,embedding.shape[1]])
            spatial1=np.zeros([1,2])
            if(xarray.shape[0]!=0 and yarray.shape[0]!=0):
                for m in xarray:
                    if(m in yarray):
                        gene1=np.vstack((gene1,embedding[m,:]))
                        spatial1=np.vstack((spatial1,spatial[m,:]))
            if(gene1.shape[0]>1):
                gene1=np.delete(gene1, 0, 0)
                gene1=np.mean(gene1,axis=0)
                spatial1=np.delete(spatial1, 0, 0)
                spatial1=np.mean(spatial1,axis=0)
                spatial_return=np.vstack((spatial_return,spatial1))
                gene_return=np.vstack((gene_return,gene1))
    spatial_return=np.delete(spatial_return, 0, 0)
    gene_return=np.delete(gene_return, 0, 0)
    
    return spatial_return, gene_return


def alternative_landmark(spatial1, spatial2, embedding1, embedding2, n = 'Default'):
    cor=np.corrcoef(embedding1,embedding2)[range(0,embedding1.shape[0]),:][:,range(embedding1.shape[0],embedding1.shape[0]+embedding2.shape[0])]
    cell1=[]
    cell2=[]
    D=cor.copy()
    if(n == 'Default'):
        n = math.floor(np.min(D.shape)/4)
    for i in range(n):
        cloc=np.where(D==np.max(cor))
        cell1.append(cloc[0][0])
        cell2.append(cloc[1][0])
        dloc=np.where(cor==np.max(cor))
        cor=np.delete(cor, dloc[0][0], axis=0)
        cor=np.delete(cor, dloc[1][0], axis=1)
    lm1=spatial1[cell1,:]
    lm2=spatial2[cell2,:]

    return lm1, lm2


def screen_landmark(lm1, lm2, n = 10):
    for i in range(lm2.shape[0]-n):
        one=np.ones(lm2.shape[0])
        lm2_1=np.insert(lm2,2,one,axis=1)
        M=np.dot(np.dot(np.linalg.inv(np.dot(lm2_1.T,lm2_1)),lm2_1.T),lm1)
        lm2_tran=np.dot(lm2_1,M)
        d=np.sum(np.power(lm2_tran-lm1,2),axis=1)
        lm2=np.delete(lm2, np.argmax(d), axis=0)
        lm1=np.delete(lm1, np.argmax(d), axis=0)

    return lm1, lm2


def caculate_angle(pt1, pt2):
    delta_x = pt2[0] - pt1[0]
    delta_y = pt2[1] - pt1[1]
    sin = delta_y/math.sqrt(delta_x**2 + delta_y**2)
    cos = delta_x/math.sqrt(delta_x**2 + delta_y**2)
    if sin>=0 and cos>=0: 
        return math.asin(sin) 
    elif sin>=0 and cos<0:
        return math.pi-math.asin(sin)
    elif sin<0 and cos<0:
        return math.pi-math.asin(sin)
    elif sin<0 and cos>=0:
        return 2*math.pi+math.asin(sin)
    

def draw_profile(x_bodary,y_bodary,plot = False):
    count = 0
    angle_list = []
    x_sort=[]
    y_sort=[]
    while(len(x_bodary) > 0):
        if(count == 0):
            if(np.where(np.array(y_bodary)==min(y_bodary))[0].shape[0]==1):
                y_sort.append(min(y_bodary))
                x_sort.append(x_bodary[y_bodary.index(min(y_bodary))])

                x_bodary.pop(y_bodary.index(min(y_bodary)))
                y_bodary.pop(y_bodary.index(min(y_bodary)))
                
                count = 1

            else:
                d=np.concatenate((np.array(x_bodary).reshape(len(x_bodary),1),np.array(y_bodary).reshape(len(y_bodary),1)),axis=1)

                y_sort.append(min(y_bodary))
                x_sort.append(min(d[np.where(d[:,1]==min(d[:,1]))[0],:][:,0]))
            
                y_bodary.pop(np.where((d[:,1]==min(d[:,1])) & (d[:,0]==min(d[np.where(d[:,1]==min(d[:,1]))[0],:][:,0])))[0][0])
                x_bodary.pop(np.where((d[:,1]==min(d[:,1])) & (d[:,0]==min(d[np.where(d[:,1]==min(d[:,1]))[0],:][:,0])))[0][0])
                count = 1
        else:
            for j in range(len(x_bodary)):
                pt1 = np.array([x_sort[-1],y_sort[-1]])
                pt2 = np.array([x_bodary[j],y_bodary[j]])
                angle_list.append(caculate_angle(pt1, pt2))
            index = angle_list.index(min(angle_list))
            angle_list = []
            x_sort.append(x_bodary[index])
            y_sort.append(y_bodary[index])
            x_bodary.pop(index)
            y_bodary.pop(index)
    x_sort.append(x_sort[0])
    y_sort.append(y_sort[0])
    return x_sort,y_sort


def Count_inter(ray_point,line_start,line_end):  
    x0 = line_start[0]
    y0 = line_start[1]
    x1 = line_end[0]
    y1 = line_end[1]
    y2 = ray_point[1]
    angle = caculate_angle(line_start,line_end)   
    if(angle == 0): 
        return 0                                                                                                 
    elif ((y2 == y0)):                 
        k = (y1 - y0)/(x1 - x0)                                 
        b = y0                                                  
        x2 = (y2 - b)/k + x0
        if(x2 > ray_point[0] and ((x2 > x0 and x2 < x1) or (x2 < x0) and (x2 > x1))): 
            return 2  
    else: 
        k = (y1 - y0)/(x1 - x0)                                 
        b = y0                                                  
        x2 = (y2 - b)/k + x0                                    
        if(x2 > ray_point[0] and ((x2 > x0 and x2 < x1) or (x2 < x0) and (x2 > x1))):
            return 1
        elif(x2 < ray_point[0] and ((x2 > x0 and x2 < x1) or (x2 < x0) and (x2 > x1))):
            return 3


def Judge_inter(x_test,y_test,x_sort,y_sort):  
    result_x = []
    result_y = []
    flag = 0
    flag2 = 0
    sum_points = 0
    result=[]
    for i in range(len(x_test)):
        on_the_line=False
        ray_point = np.array([x_test[i],y_test[i]])  
        for j in range(len(x_sort) - 1):
            line_start = np.array([x_sort[j],y_sort[j]])
            line_end = np.array([x_sort[j+1],y_sort[j+1]])
            flag = Count_inter(ray_point, line_start, line_end) 
            if(flag == 0):
                if(y_test[i]==y_sort[j] and x_test[i]>=np.min([x_sort[j],x_sort[j+1]]) and x_test[i]<=np.max([x_sort[j],x_sort[j+1]])):
                    on_the_line=True
            elif(flag == 2):
                if(j == 0): 
                    line_start = np.array([x_sort[-2],y_sort[-2]])
                else:
                    line_start = np.array([x_sort[j-1],y_sort[j-1]])
                flag2 = Count_inter(ray_point, line_start, line_end)            
                if(flag2 == 3 or flag2 == 1): 
                    result.append(i)
            elif(flag == 1): 
                sum_points = sum_points + 1
        if(on_the_line==True or sum_points % 2):  
            result_x.append(ray_point[0])
            result_y.append(ray_point[1])
            result.append(i)
        sum_points = 0
    return result