from langchain_core.runnables import RunnableLambda
from langchain_core.runnables import chain

def find_sum(x):
    return sum(x)
def find_square(x):
    return x*x

chain1 = RunnableLambda(find_sum) | RunnableLambda(find_square)

print(chain1.invoke([2,3,5]))

@chain
def runnable_sum(x):
    return sum(x)

@chain
def runnable_square(x):
    return x*x

chain2 = runnable_sum | runnable_square

print(chain2.invoke([2,3,5]))