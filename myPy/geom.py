#!/usr/bin/env python3

import numpy
import re;
import csv;

from math import sin,cos,pi

def readNDI_csv(filename, nmax=None, startcol=0):
    csvfile=open(filename)
    reader=csv.reader(csvfile)
    text=list(reader)
    csvfile.close()
    
    if re.search( 'Tools', text[0][0]):
        text.pop(0)
        
    if nmax is not None:
        text = text[0:nmax]
    
    err = np.array( list(map( lambda x: x[startcol + 12], text )), dtype='float')
    txyz = np.array( list(map( lambda x: x[startcol + 9:startcol + 12], text )), dtype='float')
    q0xyz = np.array( list(map( lambda x: x[startcol + 5:startcol + 9], text )), dtype='float')
    
    return (q0xyz, txyz, err)

def write_VTK_points(filename, xyz):

    N = len(xyz)
    d = len(xyz[0])
    if d != 3:
        return 1
    
    f = open(filename,mode='w')
    f.write('# vtk DataFile Version 3.0\n')
    f.write('vtk output\n')
    f.write('ASCII\n')
    f.write('DATASET POLYDATA\n')
    f.write('POINTS %d ' % N)
    f.write('float\n')

    for i in range(0,N):
        for j in range(0,3):
            f.write("%.8f " % xyz[i][j] )
        f.write('\n')
        
    f.write('\n\n')
    f.write('VERTICES %d %d\n' % ( N,2*N) )
    
    for i in range(0,N):
        f.write('%d %d\n' % ( 1, i) )
        
    f.close()
    
    return 0
    

def translate3vecs(inputVecs, delta, overwrite=False):
    """
    vectors is an Nx3 numpy array.  There are N vectors with 3 cartesion components
    delta is a 3-element array

    return is vectors + data
    """
    N=len(inputVecs)
    if overwrite:
        newvecs = inputVecs
    else:
        newvecs = numpy.zeros([N,3])
    
    for n in range(0,N):
        newvecs[n] = inputVecs[n] + delta
        
    return newvecs

def getRotZYZarray(az, ayp, azpp, translationColumn=None):
    
    if translationColumn is not None:
        R = numpy.zeros([4,4])
        R[:,3] = translationColumn
    else:
        R = numpy.zeros([3,3])
    
    c1 = cos(az)
    s1 = sin(az)
    c2 = cos(ayp)
    s2 = sin(ayp)
    c3 = cos(azpp)
    s3 = sin(azpp)
    
    R[0,:] = [ c1*c2*c3 - s1*s3 , s1*c2*c3 + c1*s3 , -s2*c3]
    R[1,:] = [-c1*c2*s3 - s1*c3 ,-s1*c2*s3 + c1*c3,   s2*s3]
    R[2,:] = [            c1*s2 ,           s1*s2 ,      c2]
    
    return R

def cart2sphere(x,y,z):
    """
    (r,theta,phi) = cart2sphere(x,y,z)
    Theta is polar angle. Angles returned in radians
    """
    
    r = numpy.sqrt( x**2 + y**2 + z**2 )
    theta = numpy.arccos(z/r)
    phi = numpy.arctan2(y,x)
    
    if type(r)==numpy.ndarray:
        gimbles=numpy.abs(r) < 1e-12
        theta[gimbles]=0.0
    elif abs(r) < 1e-12:
        theta=0.0
        

    return (r,theta,phi)

def cart2sphere_deg(x,y,z):
    """
    (r,theta,phi) = cart2sphere_deg(x,y,z)
    Theta is polar angle. Angles returned in degrees
    """
    rtod=180.0/np.pi
    (r,theta,phi) = cart2sphere(x,y,z)
    return (r,theta*rtod,phi*rtod)

def rot(matrix,v):
    u=numpy.array(list(map ( lambda vec: matrix.dot(vec), v)))
    return u
    
def ring(d,n, z=0.0, rot=0):
    dphi = 2.0*pi/n;
    phis = numpy.arange(0.0,2*pi,dphi) + rot
    vecs = numpy.zeros([n,3]);
    r=d/2;
    
    vecs[:,0] = r*numpy.cos(phis);
    vecs[:,1] = r*numpy.sin(phis);
    vecs[:,2] = z;
    
    return (vecs, r)
    
def equilateral_tri(d, z=0.0):
    h=d*sin(pi/3);
    return (numpy.array([[-d/2, -h/2, z], [d/2, -h/2, z], [0, h/2, z] ]), h)

def cross(d, z=0.0):
    return numpy.array([[0,0,z], [d, 0, z], [0, d, z], [-d, 0, z], [0, -d, z] ])


def inSphere(x,y,z,r=0.005):
    """
    Determine wether point (x,y,z) lies in the ellipsoid specified by r= and centered on the origin.
    Returns boolean
    """
    return numpy.sqrt(x**2 + y**2 + z**2)<=r
    
def inEllipse(x,y,z,a=0.005,b=0.005,c=0.005):
    """
    Determine wether point (x,y,z) lies in the ellipsoid specified by (a=,b=,c=) and centered on the origin.
    Returns boolean
    """
    return numpy.sqrt((x/a)**2 + (y/b)**2 + (z/c)**2)<=1.0
    
def roiGen(focalPattern, isContainedFunc, gxp, gyp, gzp):
    """
    focalPattern is an (m x 3) array
    """
    nf = len(focalPattern)
    mask=numpy.zeros_like(gxp,dtype=bool)
    for i in range(0,nf):
        mask= numpy.logical_or( mask, isContainedFunc(gxp - focalPattern[i][0], gyp - focalPattern[i][1], gzp - focalPattern[i][2]) )
    return mask

