from langchain_core.runnables import RunnableLambda

find_sum = lambda x: sum(x)

print(find_sum([2,3,5]))

find_square = lambda x: x*x

print(find_square(10))

runnable_sum = RunnableLambda(lambda x: sum(x))

runnable_square = RunnableLambda(lambda x: x*x)

chain = runnable_sum | runnable_square

print(chain.invoke([2,3,5]))

chain.get_graph().print_ascii()
