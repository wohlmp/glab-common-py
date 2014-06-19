import scipy.io as sio
import numpy as np

def load_mat(filename):
    '''
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    '''
    data = sio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)

def _check_keys(dict):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in dict:
        if isinstance(dict[key], sio.matlab.mio5_params.mat_struct):
            dict[key] = _todict(dict[key])
    return dict

def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, sio.matlab.mio5_params.mat_struct):
            dict[strg] = _todict(elem)
        else:
            dict[strg] = elem
    return dict

def load_rDAT(fin,nheaderrows = 0,fmt=None):
    if fmt == None: #replace with your own rdat format
        fmt = [('session','i4'),
               ('trial','i4'),
               ('normal','b'),
               ('stimulus','a64'),
               ('class','i4'),
               ('R_sel','i4'),
               ('R_acc','i4'),
               ('ReactionTime','f4'),
               ('Reinforced','b'),
               ('TimeOfDay','a8'),
               ('Date','a8'),
               ];

    while True:
        if nheaderrows > 100:
            raise ValueError('Recursively found more than 100 header rows.')
        try:
            data = np.genfromtxt(fin,dtype=fmt,invalid_raise=False,skip_header=nheaderrows)
            return data
        except ValueError:
            nheaderrows += 1

## http://stackoverflow.com/questions/13059011/is-there-any-python-function-library-for-calculate-binomial-confidence-intervals
def binP(N, p, x1, x2):
    p = float(p)
    q = p/(1-p)
    k = 0.0
    v = 1.0
    s = 0.0
    tot = 0.0

    while(k<=N):
            tot += v
            if(k >= x1 and k <= x2):
                    s += v
            if(tot > 10**30):
                    s = s/10**30
                    tot = tot/10**30
                    v = v/10**30
            k += 1
            v = v*q*(N+1-k)/k
    return s/tot

def binomial_ci(vx, vN, vCL = 95):
    '''
    Calculate the exact confidence interval for a binomial proportion

    Usage:
    >>> calcBin(13,100)    
    (0.07107391357421874, 0.21204372406005856)
    >>> calcBin(4,7)   
    (0.18405151367187494, 0.9010086059570312)
    ''' 
    vx = float(vx)
    vN = float(vN)
    #Set the confidence bounds
    vTU = (100 - float(vCL))/2
    vTL = vTU

    vP = vx/vN
    if (vx==0):
        dl = 0.0
    else:
        v = vP/2
        vsL = 0
        vsH = vP
        p = vTL/100

        while((vsH-vsL) > 10**-5):
            if(binP(vN, v, vx, vN) > p):
                vsH = v
                v = (vsL+v)/2
            else:
                vsL = v
                v = (v+vsH)/2
        dl = v

    if (vx==vN):
        ul = 1.0
    else:
        v = (1+vP)/2
        vsL =vP
        vsH = 1
        p = vTU/100
        while((vsH-vsL) > 10**-5):
            if(binP(vN, v, 0, vx) < p):
                vsH = v
                v = (vsL+v)/2
            else:
                vsL = v
                v = (v+vsH)/2
        ul = v
    return (dl, ul)

def vinjegallant(response):

    R = np.asarray(response[:])
    n = np.float_(len(R))
    eps = spacing(np.float64(1))

    A = ((R.sum()/n)**2) / (((R**2).sum()/n) + eps)
    S = (1 - A) / (1 - 1/n)
    
    return S