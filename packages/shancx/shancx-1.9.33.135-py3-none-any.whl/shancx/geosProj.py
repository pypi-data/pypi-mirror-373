import numpy as np
import warnings

class goesProj():
    def __init__(self,lonD=-75.2,resolution=2000):

        self.ea=6378.137
        self.eb=6356.7523
        self.h=42164
        self.lambdaD=np.radians(lonD)        

        OFF = {500: 10991.5, 1000: 5495.5, 1250: 4576, 2000: 2747.5, 4000: 1373.5, 5000: 1144}
        FAC = {500: 81865099, 1000: 40932549, 1250: 32746038, 2000: 20466274, 4000: 10233137, 5000: 8186510}
        
        self.COFF=OFF[resolution]
        self.LOFF=OFF[resolution]
        self.CFAC=FAC[resolution]
        self.LFAC=FAC[resolution]

    def transform(self,latD,lonDe,RO=0.5):
        lat=np.radians(latD)
        lon=np.radians(lonDe)
        ba2=np.square(self.eb/self.ea)
        phie=np.arctan(ba2*np.tan(lat))
        diffLon0=lon-self.lambdaD
        re=self.eb/np.sqrt(1-(1-ba2)*np.square(np.cos(phie)))

        r1=self.h-re*np.cos(phie)*np.cos(diffLon0)
        r2= -re*np.cos(phie)*np.sin(diffLon0)
        r3=re*np.sin(phie)
        rn=np.sqrt(np.square(r1)+np.square(r2)+np.square(r3))


        x= np.degrees(np.arctan(-r2/r1))
        y= np.degrees(np.arcsin(-r3/rn))

        c=(self.COFF+x*np.power(2.0,-16)*self.CFAC -RO).astype(np.int32)
        l=(self.LOFF+y*np.power(2.0,-16)*self.LFAC -RO).astype(np.int32)
        return (l,c)
    
    
import numpy as np
import warnings

class goesProjMSG10():
    def __init__(self,lonD=-75.2,resolution=2000):

        self.ea=6378.137
        self.eb=6356.7523
        self.h=42164
        self.lambdaD=np.radians(lonD)        

        OFF = {500: 10991.5, 1000: 5495.5, 1250: 4576, 2000: 2747.5, 4000: 1373.5, 5000: 1144}
        FAC = {500: 81865099, 1000: 40932549, 1250: 32746038, 2000: 20466274, 4000: 10233137, 5000: 8186510}
        
        self.COFF=OFF[resolution]
        self.LOFF=OFF[resolution]
        self.CFAC=FAC[resolution]
        self.LFAC=FAC[resolution]

    def transform(self,latD,lonDe,ROC=5,ROL=-5):
        lat=np.radians(latD)
        lon=np.radians(lonDe)
        ba2=np.square(self.eb/self.ea)
        phie=np.arctan(ba2*np.tan(lat))
        diffLon0=lon-self.lambdaD
        re=self.eb/np.sqrt(1-(1-ba2)*np.square(np.cos(phie)))

        r1=self.h-re*np.cos(phie)*np.cos(diffLon0)
        r2= -re*np.cos(phie)*np.sin(diffLon0)
        r3=re*np.sin(phie)
        rn=np.sqrt(np.square(r1)+np.square(r2)+np.square(r3))


        x= np.degrees(np.arctan(-r2/r1))
        y= np.degrees(np.arcsin(-r3/rn))

        c=(self.COFF+x*np.power(2.0,-16)*self.CFAC -ROC).astype(np.int32)
        l=(self.LOFF+y*np.power(2.0,-16)*self.LFAC -ROL).astype(np.int32)
        return (l,c)