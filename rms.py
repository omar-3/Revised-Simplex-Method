#!/usr/bin/python3.7
from array import *
from shutil import get_terminal_size

def printCenterTerminal(s):
    terminal_width, _ = get_terminal_size()
    columns = get_terminal_size().columns
    print("-" * terminal_width)
    print(s.center(columns))
    print("-" *terminal_width)



#tolerances
epsilon1 = 0.00001
epsilon2 = 0.000001

#constraints number
m = None

#variables number
n = None


# Variables objects
class variable:
    def __init__(self, label, value): #label is like X1 so we denoted by 1 and value is the value of "1"
        self.label = label
        self.value = value
    def __lt__(self, other):
        return self.value < other.value
    def __gt__(self, other):
        return self.value > other.value

# that is the column that is different from the identity matrix,
# we need it to change the basis matrix

class Eta:
    def __init__(self, col, values):
        self.col = col
        self.values = values


#________________________________________________________________________________________________#
#________________________________________________________________________________________________#
#                               These are functions just for printing                            #
#                               All the algorithm logic is in the __main__                       #
#________________________________________________________________________________________________#
#________________________________________________________________________________________________#
def matrixPrint( r , c, matrix=[]):
    for R in range(r):
        for C in range(c):
            print(matrix[R * (m+n) + C], end = "\t")
        print("")
    
def lpPrint(objectiveFunc=[], b=[], matrix=[]):
    print("m =",end = " ")
    print(m)
    print("n =",end = " ")
    print(n)
    print("c =",end = " [ ")
    for i in range(m+n):
        print(objectiveFunc[i], end=" ")
    print("]\nb =", end = " [ ")
    for i in range(m):
        print(b[i].value, end=" ")
    
    print("]\n A=")
    matrixPrint(m, n+m, matrix=matrix)

def variablePrint(nonbasic=[],b=[]):
    print("N = {", end=" ")
    for i in range(n):
        print("x",end="")
        print(nonbasic[i] + 1, end=" ")
    
    print("} B = { ",end="")

    for i in range(m):
        print("x",end="")
        print(b[i].label + 1,end=" ")
    print("}")
    print()

def BbarPrint(b=[]):
    print("bbar =",end=" ")
    for i in range(m):
        print(b[i].value, end=" ")
    print()

def finalvariablePrint(b=[], nonbasic=[]):
    varVariables = [0]*(m+n)
    for row in range(m):
        varVariables[b[row].label] = b[row].value
    
    for col in range(n):
        varVariables[nonbasic[col]] = 0.0

    print("Decision Variables: ",end=" ")

    for i in range(n):
        print(i+1,end=" ")
        print(varVariables[i],end=" ")
    print("\nSlack Variables: ")
    i = n
    while i < m+n:
        print(i+1,end=" ")
        print(varVariables[i],end=" ")
        i=i+1
    print()

def familyOfSolutionsPrint(d,largestCoeff, enterigLabel, z,b=[],nonbasic=[]):
    #we need to "memoize" the row of the basic variable in the basis
    class varInfo:
        def __init__(label, value, row_in_basis, isBasic):
            self.label = label
            self.value = value
            self.row_in_basis = row_in_basis
            self.isBasic = isBasic
    info = [0]*(m+n)
    for row in range(m):
        v = b[row]
        info[v.label] = varInfo(v.label, v.value, row, true)
    
    for col in range(n):
        info[nonbasic[col]] = varInfo(nonbasic[col],0.0,0,false)
    
    #decision variables
    print("Decision variables ", end="")

    for i in range(n):
        print(i+1,end=" ")
        print("= ",end="")
        print(info[i].value, end=" ")
        if info[i].isBasic:
            print("+ ",end="")
            print(d[info[i].row_in_basis]*(-1.0),end=" ")
            print("x",end=" ")
            print(enterigLabel+1, end=" ")
    print()
    print("Slack variables: ",end="")

    i = n
    while i < m+n:
        print(i+1, end=" = ")
        print(info[i].value,end=" ")
        if info[i].isBasic:
            print("+ ",end="")
            print(d[info[i].row_in_basis]*(-1.0), end="x")
            print(enterigLabel+1, end="")
        i=i+1
    
    print(f"\nZ = {z} + {largestCoeff}x{enterigLabel+1}",end=", ")
    print(f"with x{enterigLabel+1} >= 0")


#___________________________________________________________________________________________
#___________________________________________________________________________________________
#____________________________________   Main Function
#___________________________________________________________________________________________
#___________________________________________________________________________________________


def main():
    global m
    global n

    m = int(input("Enter the number of constraints"))
 
    
    n = int(input("Enter the number of variables"))


    objectiveFunction = [0]*(m+n)

    for col in range(n):
        objectiveFunction[col] = float(input(f"Enter the coefficient {col+1} of the objective function"))
    
    #### pad the rest of the "costs" of the objective function to zeros ==> the non basic variables costs

    i = n
    while i < n+m:
        objectiveFunction[i] = 0.0
        i = i+1
    
    ### now it is time to initizalize matrix A

    A = [0]*(m*(n+m))

    #______________________________________
    #_____________ Important Note
    #_____________ I'm visualizing the matrix as a linear 1D array in which the rows are stacked together
    #______________________________________

    b = [0]*(m) #_________________________ the values of the basic variables

    nonbasic = [0]*(n)

    #______________________________________________________
    #______________________________________________________
    #   We are reading the coefficients of the constraints
    for row in range(m):
        for col in range(n+1):
            if col == n:
                bRow = float(input("Enter the (b) value of this constraint"))
                x = n + row
                bVar = variable(x,bRow)
                b[row] = bVar
            else:
                A[row*(m+n)+col] = float(input(f"Enter the coeffiecient of the {col+1} variable in the constraint  {row+1}"))

    for row in range(m):
        base = (m+n)*row+n
        for col in range(m):
            if col != row:
                A[base+col] = 0.0
            else:
                A[base+col] = 1.0
    
    for i in range(n):
        nonbasic[i] = i
    printCenterTerminal("This is your Problem Settings")
    lpPrint(objectiveFunc=objectiveFunction,b=b,matrix=A)
    print()
    variablePrint(nonbasic=nonbasic, b=b)
    print()
    BbarPrint(b=b)
    print()

    #if any value of the b vector is negative the linear programming problem is infeasible
    for row in range(m):
        if b[row].value < 0.0:
            print("The LPP is infeasible, exiting the program")
            #TO DO: make the b vector positive
            return
    
    #let's proceed to the algorithm :"D

    #to keep the number of iterations
    counter = 1

    #list of eta matrices E0,E1,E2,E3,...
    #representing the previous pivots

    pivots = list()


    #initialize the value of the objective function

    z = 0.0

    while True:
        print()
        printCenterTerminal(f"Iteration {counter}")
        print()

        # yB = C
        
        y = [0] * (m)

        # B is the basis matrix so y = Cb at the first iteration

        for row in range(m):
            v = b[row]
            y[row] = objectiveFunction[v.label]

        # initialize y in yB = Cn
        for vector in reversed(pivots):
            pivot = vector
            changedCol = pivot.col
            originalY = y[changedCol]
            for row in range(len(pivot.values)):
                if row != changedCol:
                    originalY  = originalY - pivot.values[row] * y[row]
            newY = originalY / pivot.values[changedCol]
            y[changedCol] = newY
        
        print("y = ",end="")

        for i in y:
            print(i,end=" ")
        print()

        # now you need to choose the entering column
        # the column which has the biggest C (please refer to the explaination in the report)

        # vector to keep track of these variable

        cnbars = list()

        enteringLabel = nonbasic[0]
        largestCoeff = -1.0
        print("Cnbar: ","")

        for i in range(n):
            varLabel = nonbasic[i]
            cni = objectiveFunction[varLabel]
            yai = 0.0
            for yIndex in range(m):
                yai += y[yIndex] * A[yIndex * (m+n) + varLabel]

            cnbar = cni - yai
            print("x",end="")
            print(varLabel+1,end=" ")
            print(cnbar,end="\t")
            if cnbar > epsilon1:       #===> I'm not 100% clear on why we compare with cnbar, but it seems to make the algorithm work ;)
                v = variable(varLabel,cnbar)
                cnbars.append(v)
                if cnbar > largestCoeff:
                    largestCoeff = cnbar
                    enteringLabel = varLabel
        cnbars.sort(key= lambda v : v.value, reverse=True)
        print()

        if len(cnbars) == 0:
            print("There is no entering values in the next iteration so the optimal point is {z}")
            finalvariablePrint(b=b,nonbasic=nonbasic)
            return
        else:
            print(f"The new entering variable is x{enteringLabel+1}")
            
        entVarIndex = 0
        
        #The column changing in Abar for the new variable with the eta matrix E0,E1,... now this is kind of recursion

        d = [0]*(m)
        leavingLabel = 0
        leavingRow = 0
        smallest_t = 0.0

        #now we are trying to get into the REAL algorithm

        while True:
            leavingLabel = -1
            leavingRow = -1
            smallest_t -1
            if entVarIndex > 0:
                print("The diagonal element in the matrix eta is close to zero")
            
            if entVarIndex < len(cnbars):
                enteringLabel = cnbars[entVarIndex].label
                if entVarIndex > 0:
                    print(f"Entering variable is {enteringLabel+1}")
            else:
                print(f"No entering var. Optimal value of {z} has been reached")
                finalvariablePrint(b=b,nonbasic=nonbasic)
                return
            

            #Initializing d to be the entering column
            for row in range(m):
                d[row] = A[row*(m+n) + enteringLabel]
            

            #Now iterating through the eta matrix , fml
            for i in pivots:
                pivot = i
                changedRow = pivot.col
                originalD = d[changedRow]
                # kind of normalizing, please refer to the report
                d[changedRow] = originalD / pivot.values[changedRow]
                for row in range(len(d)):
                    if row != changedRow:
                        d[row] = d[row] - pivot.values[row] * d[changedRow]
            
            print("d = ")
            for i in d:
                print(i)

            print()

            #okay now we have one negative for example
            #we need to calculate the coefficient of the entering variable

            for row in range(len(d)):
                if d[row] > 0.0:
                    leavingLabel = b[row].label
                    leavingRow = row
                    smallest_t = b[row].value / d[row]
            
            # if no ratio is computed. then there is some zeros then the problem is unbounded
            if leavingLabel == -1:
                print("\nThe problem is unbounded")
                familyOfSolutionsPrint(d,largesCoeff,enterigLabel,z,b=b,nonbasic=nonbasic)
                return 

            print("ratio: ",end="")

            #okay now we are at the position like in the simplex method and we need
            # to choose the smallest ratio to kick out the row


            for row in range(len(d)):
                if d[row] < 0:
                    continue

                t_row = b[row].value / d[row]

                if t_row >= 0:
                    print("x",end="")
                    print(b[row].label+1,end=" ")
                    print(t_row,end=" ")
                
                if t_row < smallest_t:
                    leavingLabel = b[row].label
                    leavingRow = row
                    smallest_t = t_row
            
            if d[leavingRow] > epsilon2:    #this thing is real annoying
                print("\nThe variable leaving is x",end="")
                print(leavingLabel+1)
                break
            else:
                entVarIndex = entVarIndex + 1
                continue
        
        # now we have a definite entering the leaving variables
        # entering variable is positive and diagonal entry in the eta is fairly far from zero

        #___________________________________________________
        #___________________________________________________
        #___________________________________________________
        #___________________________________________________

        #some little boilerplate

        enteringVar = variable(enteringLabel,smallest_t)
        b[leavingRow] = enteringVar

        for row in range(len(b)):
            if row != leavingRow:
                b[row].value = b[row].value - d[row] * smallest_t
        

        ###########################################
        ####            New Eta Matrix            #
        ###########################################
        pivot = Eta(leavingRow, d)
        pivots.append(pivot)

        print(f"Eta matrix now at iteration {counter} the {leavingRow} row left")

        for i in d:
            print(i," ")
        
        print()

        nonbasic[enteringLabel] = leavingLabel

        variablePrint(nonbasic=nonbasic,b=b)

        BbarPrint(b=b)

        increased = largestCoeff * smallest_t

        z = z + increased
        print(f"The value of the objective function now is {z}")

        counter = counter + 1
        



            
main()