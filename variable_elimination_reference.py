import numpy as np

# restrict
def restrict(factor,variable,value):
    newShape = np.array(factor.shape)
    newShape[variable]=1
    sliceList = [slice(None)]*factor.ndim
    sliceList[variable]=value
    return factor[sliceList].reshape(newShape)

# sumout
def sumout(factor,variable):
    return np.sum(factor,axis=variable,keepdims=True)

# multiply
def multiply(factor1,factor2):
    return factor1*factor2

# normalize
def normalize(factor):
    return factor / np.sum(factor.flatten())

# inference
def inference(factorList,queryVariables,orderedListOfHiddenVariables,evidenceList):

    print "Restrict:"
    for index in np.arange(len(factorList)):
        shape = np.array(factorList[index].shape)
        for evidence in evidenceList:
            if shape[evidence[0]] > 1:
                factorList[index] = restrict(factorList[index],evidence[0],evidence[1])
        shape = np.array(factorList[index].shape)
        print("f{}({})={}\n".format(index,variables[shape>1],np.squeeze(factorList[index])))

    print "Eliminate"
    hiddenId = 5
    for variable in orderedListOfHiddenVariables:
        print("Eliminating {}".format(variables[variable]))

        factorsToBeMultiplied = []
        for index in np.arange(len(factorList)-1,-1,-1):
            shape = np.array(factorList[index].shape)
            if shape[variable] > 1:
                factorsToBeMultiplied.append(factorList.pop(index))

        # multiply
        product = factorsToBeMultiplied[0]
        for factor in factorsToBeMultiplied[1:]:
            product = multiply(product,factor)

        # sumout
        newFactor = sumout(product,variable)
        factorList.append(newFactor)
        shape = np.array(newFactor.shape)
        hiddenId = hiddenId + 1
        print("New factor: f{}({})={}\n".format(hiddenId,variables[shape>1],np.squeeze(newFactor)))

    # multiply remaining factors
    print "Multiplying remaining factors"
    answer = factorList[0]
    for factor in factorList[1:]:
        answer = multiply(answer,factor)
        shape = np.array(answer.shape)

    # normalize
    print "Normalize"
    answer = normalize(answer)
    shape = np.array(answer.shape)
    print("Result: f{}({})={}\n".format(hiddenId+2,variables[shape>1],np.squeeze(answer)))
    return answer

variables = np.array(['OC','Trav','Fraud','FP','IP','CRP'])
values = np.array(['false','true'])

false=0
true=1

OC=0
Trav=1
Fraud=2
FP=3
IP=4
CRP=5