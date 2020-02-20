from __future__ import print_function
from ortools.algorithms import pywrapknapsack_solver
import sys
    
def main(args):
    filename = args[0]
    with open(filename) as fp:
        # reading input:
        # l1 = fp.readline()
        # vl1 = l1.split(' ')

    # Body of the function goes here
        
    with open(filename.split('.')[0]+".out","w") as fp:
        #writing output:
        #fp.write(result+'\n')
        
if __name__ == '__main__':
    # usage: python main.py ./data/<datasetname>
    main(sys.argv[1:])
