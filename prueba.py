a = []

def add_num(i):
    global a
    if i > 2:
        a.append(i)
        return True
    return False

for i in range(10):
    if add_num(i):
        print(a)