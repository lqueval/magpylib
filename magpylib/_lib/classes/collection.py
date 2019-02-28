#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%% IMPORTS

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from numpy import array,amax, linspace, pi, sin, cos
from magpylib._lib.classes.magnets import Box,Cylinder,Sphere
from magpylib._lib.classes.currents import Line, Circular
from magpylib._lib.classes.moments import Dipole
from magpylib._lib.mathLibPrivate import angleAxisRotation, fastNorm3D
from magpylib._lib.mathLibPublic import rotatePosition
class Collection():
    """
    Create a collection of sources for common manipulation.
    
    Class Initialization:
    ----------------
    *sources : source objects
        python magic variable passes source objects to the collection at initialization.
    
    Class Variables:
    ----------------
    sources : list of source objects
        List of all sources that have been added to the collection.
        
    Class Methods:
    --------------
    addSource(source) :  
        adds the source object `source` to the collection.
    
    move(displacement) : takes vec3[mm] - return None
        Moves collection by the `displacement` argument.

    rotate(angle,axis,anchor=[0,0,0]) : takes float[deg],vec3[],kwarg(vec3)[mm] - returns None
        Rotate the collection by `angle` about an axis parallel to `axis` running
        through center of rotation `anchor`.

    getB(pos) : takes vec3[mm] - returns arr3[mT]
        Gives the magnetic field generated by the collection in units of [mT]
        at the position `pos`.
    
    displaySystem() : takes None - returns matplotlib graphics object
        Display the collection geometry in a 3D interactive graph.
        
    Example:
    --------
    >>> magpylib as magPy
    >>> pm1 = magPy.magnet.Box(mag=[0,0,1000],dim=[1,1,1])
    >>> pm2 = magPy.magnet.Cylinder(mag=[0,0,1000],dim=[1,1])
    >>> pm3 = magPy.magnet.Sphere(mag=[0,0,1000],dim=1)
    >>> col = magPy.Collection(pm1,pm2,pm3)
    >>> B = col.getB([1,0,1])
    >>> print(B)
      [99.3360625 0.0 31.2727683]
    """
    
    def __init__(self,*sources):
        self.sources = []
        
        for s in sources:
            self.sources += [s]

    
    def addSource(self,source):
        """
        This method adds the argument source object to the collection.
        
        Parameters:
        ----------
        source : source object
            adds the source object `source` to the collection.
        
        Returns:    
        --------
        None
            
        Example:
        --------
        >>> magpylib as magPy
        >>> pm1 = magPy.magnet.Box(mag=[0,0,1000],dim=[1,1,1])
        >>> pm2 = magPy.magnet.Cylinder(mag=[0,0,1000],dim=[1,1])
        >>> pm3 = magPy.magnet.Sphere(mag=[0,0,1000],dim=1)
        >>> col = magPy.Collection(pm1)
        >>> print(col.getB([1,0,1]))
          [42.9223532 0.0 13.7461635]
        >>> col.addSource(pm2)
        >>> print(col.getB([1,0,1]))
          [77.2389756 0.0 23.9070726]
        >>> col.addSource(pm3)
        >>> print(col.getB([1,0,1]))
          [99.3360625 0.0 31.2727683]
        """        
        self.sources += [source]

    
    def getB(self,pos):
        """
        This method returns the magnetic field vector generated by the whole
        collection at the argument position `pos` in units of [mT]
        
        Parameters:
        ----------
        pos : vec3 [mm]
            Position where magnetic field should be determined.
        
        Returns:    
        --------
        magnetic field vector : arr3 [mT]
            Magnetic field at the argument position `pos` generated by the
            collection in units of [mT].
        """
        Btotal = sum([s.getB(pos) for s in self.sources])
        return Btotal


    def move(self,displacement):
        """
        This method moves each source in the collection by the argument vector `displacement`. 
        Vector input format can be either list, tuple or array of any data
        type (float, int).
        
        Parameters:
        ----------
        displacement : vec3 - [mm]
            Displacement vector
            
        Returns:    
        --------
        None
            
        Example:
        --------
        >>> magpylib as magPy
        >>> pm1 = magPy.magnet.Box(mag=[0,0,1000],dim=[1,1,1])
        >>> pm2 = magPy.magnet.Cylinder(mag=[0,0,1000],dim=[1,1])
        >>> print(pm1.position,pm2.position)
          [0. 0. 0.] [0. 0. 0.]
        >>> col = magPy.Collection(pm1,pm2)
        >>> col.move([1,1,1])
        >>> print(pm1.position,pm2.position)
          [0. 0. 0.] [0. 0. 0.]
        """
        for s in self.sources:
            s.move(displacement)
    
    
    def rotate(self,angle,axis,anchor='self.position'):
        """
        This method rotates each source in the collection about `axis` by `angle`. The axis passes
        through the center of rotation anchor. Scalar input is either integer or
        float. Vector input format can be either list, tuple or array of any
        data type (float, int).
        
        Parameters:
        ----------
        angle  : scalar [deg]
            Angle of rotation in units of [deg]
        axis : vec3
            Axis of rotation
        anchor : vec3
            The Center of rotation which defines the position of the axis of rotation.
            If not specified all sources will rotate about their respective center.
            
        Returns:    
        --------
        None
            
        Example:
        --------
        >>> magpylib as magPy
        >>> pm1 = magPy.magnet.Box(mag=[0,0,1000],dim=[1,1,1])
        >>> pm2 = magPy.magnet.Cylinder(mag=[0,0,1000],dim=[1,1])
        >>> print(pm1.position, pm1.angle, pm1.axis)
          [0. 0. 0.] 0.0 [0. 0. 1.]
        >>> print(pm2.position, pm2.angle, pm2.axis)
          [0. 0. 0.] 0.0 [0. 0. 1.]
        >>> col = magPy.Collection(pm1,pm2)
        >>> col.rotate(90, [0,1,0], anchor=[1,0,0])
        >>> print(pm1.position, pm1.angle, pm1.axis)
          [1. 0. 1.] 90.0 [0. 1. 0.]
        >>> print(pm2.position, pm2.angle, pm2.axis)
          [1. 0. 1.] 90.0 [0. 1. 0.]
        """
        for s in self.sources:
            s.rotate(angle,axis,anchor=anchor)
         
    
    def displaySystem(self):
        """
        This method displays the collection in an interactive plot. 
        WARNING: As a result of an inherent problem in matplotlib the 
        Poly3DCollections z-ordering fails when bounding boxes intersect.
        
        Parameters:
        -----------
        None
                
        Returns:    
        --------
        matplotlib graphics object
            graphics object is displayed through plt.show()
            
        Example:
        --------
        >>> magpylib as magPy
        >>> pm1 = magPy.magnet.Box(mag=[0,0,1000],dim=[1,1,1],pos=[-1,-1,-1],angle=45,axis=[0,0,1])
        >>> pm2 = magPy.magnet.Cylinder(mag=[0,0,1000],dim=[2,2],pos=[0,-1,1],angle=45,axis=[1,0,0])
        >>> pm3 = magPy.magnet.Sphere(mag=[0,0,1000],dim=3,pos=[-2,1,2],angle=45,axis=[1,0,0])
        >>> C1 = magPy.current.Circular(curr=100,dim=6)
        >>> col = magPy.Collection(pm1,pm2,pm3,C1)
        >>> col.displaySystem()
        """ 
        fig = plt.figure(dpi=80,figsize=(8,8))
        ax = fig.gca(projection='3d')
        
        #count magnets
        Nm = 0
        for s in self.sources:
            if type(s) is Box or type(s) is Cylinder or type(s) is Sphere:
                Nm += 1
        cm = plt.cm.hsv
        #select colors
        colors = [cm(x) for x in linspace(0,1,Nm+1)]
        
        SYSSIZE = 0
        
        for ii,s in enumerate(self.sources):
            if type(s) is Box:
                P = s.position
                D = s.dimension/2
                #create vertices in canonical basis
                v0 = array([D,D*array([1,1,-1]),D*array([1,-1,-1]),D*array([1,-1,1]),
                                   D*array([-1,1,1]),D*array([-1,1,-1]),-D,D*array([-1,-1,1])])
                #rotate vertices + displace
                v = array([ angleAxisRotation(s.angle,s.axis,d)+P for d in v0])
                #create faces
                faces = [[v[0],v[1],v[2],v[3]],
                         [v[0],v[1],v[5],v[4]],
                         [v[4],v[5],v[6],v[7]],
                         [v[2],v[3],v[7],v[6]],
                         [v[0],v[3],v[7],v[4]],
                         [v[1],v[2],v[6],v[5]]]
                # plot
                boxf = Poly3DCollection(faces, facecolors=colors[ii], linewidths=0.5, edgecolors='k', alpha=1)
                ax.add_collection3d(boxf)
                #check system size
                maxSize = amax(abs(v))
                if maxSize > SYSSIZE:
                    SYSSIZE = maxSize
            
            elif type(s) is Cylinder:
                P = s.position
                R,H = s.dimension/2
                
                resolution = 20
                
                #vertices
                phis = linspace(0,2*pi,resolution)
                vertB0 = array([[R*cos(p),R*sin(p),-H] for p in phis])
                vertT0 = array([[R*cos(p),R*sin(p),H] for p in phis])
                #rotate vertices+displacement
                vB = array([ angleAxisRotation(s.angle,s.axis,d)+P for d in vertB0])
                vT = array([ angleAxisRotation(s.angle,s.axis,d)+P for d in vertT0])
                #faces
                faces = [[vT[i],vB[i],vB[i+1],vT[i+1]] for i in range(resolution-1)]
                faces += [vT,vB]
                #plot
                coll = Poly3DCollection(faces, facecolors=colors[ii], linewidths=0.5, edgecolors='k', alpha=1)
                ax.add_collection3d(coll)
                #check system size
                maxSize = max([amax(abs(vB)),amax(abs(vT))])
                if maxSize > SYSSIZE:
                    SYSSIZE = maxSize
                
            elif type(s) is Sphere:
                P = s.position
                R = s.dimension/2
                
                resolution = 12
                
                #vertices
                phis = linspace(0,2*pi,resolution)
                thetas = linspace(0,pi,resolution)
                vs0 = [[[R*cos(phi)*sin(th),R*sin(phi)*sin(th),R*cos(th)] for phi in phis] for th in thetas]
                #rotate vertices + displacement
                vs = array([[ angleAxisRotation(s.angle,s.axis,v)+P for v in vss] for vss in vs0])
                #faces
                faces = []
                for j in range(resolution-1):
                    faces += [[vs[i,j],vs[i+1,j],vs[i+1,j+1],vs[i,j+1]] for i in range(resolution-1)]
                #plot
                boxf = Poly3DCollection(faces, facecolors=colors[ii], linewidths=0.5, edgecolors='k', alpha=1)
                ax.add_collection3d(boxf)
                #check system size
                maxSize = amax(abs(vs))
                if maxSize > SYSSIZE:
                    SYSSIZE = maxSize
                    
            elif type(s) is Line:
                P = s.position
                vs0 = s.vertices
                #rotate vertices + displacement
                vs = array([ angleAxisRotation(s.angle,s.axis,v)+P for v in vs0])
                #plot
                ax.plot(vs[:,0],vs[:,1],vs[:,2],lw=1,color='k')
                #check system size
                maxSize = amax(abs(vs))
                if maxSize > SYSSIZE:
                    SYSSIZE = maxSize
            
            elif type(s) is Circular:
                P = s.position
                R = s.dimension/2
                
                resolution = 20
                
                #vertices
                phis = linspace(0,2*pi,resolution)
                vs0 = array([[R*cos(p),R*sin(p),0] for p in phis])
                #rotate vertices + displacement
                vs = array([ angleAxisRotation(s.angle,s.axis,v)+P for v in vs0])
                #plot
                ax.plot(vs[:,0],vs[:,1],vs[:,2],lw=1,color='k')
                #check system size
                maxSize = amax(abs(vs))
                if maxSize > SYSSIZE:
                    SYSSIZE = maxSize

            elif type(s) is Dipole:
                P = rotatePosition(s.position,s.angle,s.axis) 
                M = rotatePosition(s.moment,s.angle,s.axis) 
                
                maxSize = amax(abs(P))
                if maxSize > SYSSIZE:
                    SYSSIZE = maxSize
                if SYSSIZE == 0: ## Avoids inf. small volume
                    SYSSIZE=1

                plt.quiver(P[0],P[1],P[2], # X,Y,Z position
                           M[0],M[1],M[2], # Components of the Vector
                           normalize=True,
                           length=SYSSIZE/5) # View is Always at least 5 times smaller
                
        for tick in ax.xaxis.get_ticklabels()+ax.yaxis.get_ticklabels()+ax.zaxis.get_ticklabels():
            tick.set_fontsize(12)
        ax.set_xlabel('x[mm]', fontsize=12)
        ax.set_ylabel('y[mm]', fontsize=12)
        ax.set_zlabel('z[mm]', fontsize=12)
        ax.set(
            xlim=(-SYSSIZE,SYSSIZE),
            ylim=(-SYSSIZE,SYSSIZE),
            zlim=(-SYSSIZE,SYSSIZE),
            aspect=1
            )
        plt.tight_layout()
        plt.show()
        