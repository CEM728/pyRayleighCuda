#!/usr/bin/env python

import numpy as np;

from math import *;

#######
# Function: get1DshiftFilter
#   Returns a matrix describing a shift operation on a 1-D function
#   that is discretely represented as an array. The should be used like g = M*f,
#   where f is the original function, M is the matrix returned from here, and g is the rebinned function.
#   Re-binning assumes the new bins are equal to or larger than the original bins. 

def get1DshiftFilter(originalEdges, newEdges):
    
    nn = len(originalEdges)-1
    
    M = np.zeros([nn,nn])
    
    dx1 = originalEdges[1] - originalEdges[0]
    
    for iprime in range(0,nn):
    
        x2c = newEdges[iprime];
        x2d = newEdges[iprime+1];
        
        i_c = floor((x2c - originalEdges[0])/dx1)
        i_d = i_c+1
        
        if (i_c >= 0 and i_c < nn) :
            xa = originalEdges[i_c];
            fiprime_c = 1.0 - (x2c-xa)/(dx1);
            M[iprime, i_c] = fiprime_c;
            
        if (i_d >= 0 and i_d < nn) :
            xb = originalEdges[i_d];
            fiprime_d = (x2d-xb)/(dx1);
            M[iprime, i_d] = fiprime_d;
        
    return M
    

def shiftImageRegular3D(originalIm, edgeX, edgeY, edgeZ, shift ):
    
   # Nx = len(edgeX)-1 
   # Ny = len(edgeY)-1
   # Nz = len(edgeZ)-1
    
    m11 = get1DshiftFilter(edgeX, edgeX+shift[0])
    m22 = get1DshiftFilter(edgeY, edgeY+shift[1])
    m33 = get1DshiftFilter(edgeZ, edgeZ+shift[2])
    
    #Im3 = np.tensordot(m33, val, axes=([1],[2]))
    #Im3 = np.tensordot(m22, Im3, axes=([1],[2]))
    #Im3 = np.tensordot(m11, Im3, axes=([1],[2]))
    
    Im3 = np.tensordot(m11,\
            np.tensordot(m22,\
                np.tensordot(m33, originalIm, axes=([1],[2])),\
            axes=([1],[2])),\
        axes=([1],[2]))
    
    return Im3
    
def NDrebin( NDorig, inputAxisLocations, outputAxisLocations ):
    """
    Rebin the n-dimensional numpy array 'NDorig'
    :param NDorig: An n-dimensional numpy array
    :param inputAxisLocations: a set of edges for each axis of 'NDorig'
    :param outputAxisLocations: a set of new edges for each axis
    
    len() input and outputAxisLocations must equal NDrebin.ndim
    
    returns rebinned array
    """
    
    nd = NDorig.ndim
    
    if len(inputAxisLocations) != nd:
        raise ValueError("len(inputAxisLocations) != NDorig.ndim")
        
    if len(outputAxisLocations) != nd:
        raise ValueError("len(outputAxisLocations) != NDorig.ndim")
    
    newArray = NDorig.copy()
    axes = tuple(map(lambda x: [x], range(1,nd) ) )
    
    filters = []
    for ax in range(nd):
        filters[ax] = calc_bin2bin_AvgFilter( inputAxisLocations[ax], outputAxisLocations[ax] )
        
    for ax in range(nd-1, -1, -1):
        
        newArray = np.tensordot(filters[ax], newArray, axes=axes)
        
    return newArray, filters
    
def calc_bin2bin_AvgFilter( X, Y ):
    """
    
    Computes an average / normalization-preserving operator
    to convert one basis to another
    
    X-original bin edges
    Y-new bins edges
    
    returns matrix F
    
    N = len(X)-1
    M = len(Y)-1
    F = matrix size MxN
    
    
    Result used like
    vy = F.dot(vx)
    """
    
    N = len(X)-1
    M = len(Y)-1
    
    F = np.zeros([M,N])
    
    n=0
    m=0
    
    up_x=True
    up_y=True
    while( (n<(N)) and (m<(M)) ):
        
        if up_x:
            xa=X[n]
            xb=X[n+1]
            up_x=False
        if up_y:
            ya=Y[m]
            yb=Y[m+1]
            up_y=False
        
        #X:   a    b
        #     |    |
        #  | |
        #Y:a b 
        if xa >= yb:
            #print(" 1: ",(m,n))
            m = m+1
            up_y=True
            continue
        
        #X: a    b
        #   |    |
        #         | |
        #Y:       a b 
        if ya >= xb:
            #print(" 2: ",(m,n))
            n = n+1;
            up_x=True
            
            continue;
        
        #X:  a    b
        #    |----|
        #   |      |
        #Y: a      b 
        if ya <= xa and yb >= xb:
            
            #print(" 3: ",(m,n), 1)
            F[m,n] += 1;
            
            n = n+1;
            up_x=True
            
            continue;
        
        #X:  a    b
        #    |--  |
        #   |  |
        #Y: a  b 
        if ya <= xa and yb > xa:
            #print(" 4: ",(m,n), (yb - xa)/(xb - xa))
            F[m,n] += (yb - xa)/(xb - xa);
            m = m+1;
            
            up_y=True
            continue;
        
        #X:  a    b
        #    |   -|
        #        |  |
        #Y:      a  b 
        if ya > xa and yb >= xb:
            #print(" 5: ",(m,n), (xb - ya)/(xb - xa))
            F[m,n] += (xb - ya)/(xb - xa);
            n = n+1;
            up_x=True
            continue;
        
        
        #X: a      b
        #   | ---- |
        #     |  |
        #Y:   a  b 
        if ya > xa and yb < xb:
            #print(" 6: ",(m,n), (yb-ya)/(xb-xa))
            F[m,n] += (yb-ya)/(xb-xa);
            m = m+1;
            up_y=True
            continue;
        
    return F



