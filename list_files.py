import os

def list_files(startpath, max_depth):
    for root, dirs, files in os.walk(startpath):
        # 计算当前目录的深度
        level = root.replace(startpath, '').count(os.sep)
        if level >= max_depth:
            # 如果当前深度超过了最大深度，则不再深入遍历
            del dirs[:]
        indent = ' ' * 4 * level
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))

if __name__ == "__main__":
    startpath = os.path.expanduser('~')  # 从用户主目录开始
    max_depth = 4  # 最大深度为5
    list_files(startpath, max_depth)