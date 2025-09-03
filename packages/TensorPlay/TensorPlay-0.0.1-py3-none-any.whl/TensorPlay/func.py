def sphere(x, y):
    return x ** 2 + y ** 2

def matyas(x, y):
    return 0.26 * (x ** 2 + y ** 2) - 0.48 * x * y

def goldstein(x, y):
    return (1 + (x + y + 1) ** 2 * (19 - 14 * x + 3 * x ** 2 - 14 * y + 6 * x * y + 3 * y ** 2)) * (
            30 + (2 * x - 3 * y) ** 2 * (18 - 32 * x + 12 * x ** 2 + 48 * y - 36 * x * y + 27 * y ** 2))

def higher_optimizer(x, epoch, func, verbose=False):
    """
    基于牛顿法的二阶单变量函数优化器
    :param x: 初始值
    :param epoch: 迭代次数
    :param func: 目标函数
    :param verbose: 是否打印每次迭代的结果
    :return: 优化后的变量和函数值
    """
    for i in range(epoch):
        y = func(x)
        y.name = 'y'
        if verbose:
            print(f"第{i + 1}次迭代: x={x.vector}, y={y.vector}")
        y.backward(higher_grad=True)
        gx = x.grad
        gx.name = 'gx'
        x.zero_grad()
        gx.backward()
        gx2 = x.grad
        x.zero_grad()
        x.vector -= gx.vector / gx2.vector

    return x, y
