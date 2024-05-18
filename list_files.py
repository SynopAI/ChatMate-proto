import os

def list_files(startpath, max_depth, output_file):
    with open(output_file, 'w') as f:
        for root, dirnames, files in os.walk(startpath):
            # 计算当前目录的深度
            level = root.replace(startpath, '').count(os.sep)
            if level >= max_depth:
                # 如果当前深度超过了最大深度，则不再深入遍历
                del dirnames[:]
            indent = ' ' * 4 * level
            f.write('{}{}/\n'.format(indent, os.path.basename(root)))
            subindent = ' ' * 4 * (level + 1)
            for file in files:
                f.write('{}{}\n'.format(subindent, file))

if __name__ == "__main__":
    # 获取用户主目录
    user_home = os.path.expanduser('~')

    # 获取用户主目录的上两级目录
    upper_two_levels = os.path.abspath(os.path.join(user_home, "../../"))

    max_depth = 1  # 最大深度为3
    output_file = 'list_files_tree.txt'  # 输出文件名

    # 用户指定的目录集合
    dirs = {'Applications', '用户'}  # 替换为你想要遍历的目录名

    with open(output_file, 'w') as f:
        for dir_name in dirs:
            dir_path = os.path.join(upper_two_levels, dir_name)
            if os.path.exists(dir_path):
                f.write(f"{dir_name}/\n")
                list_files(dir_path, max_depth, output_file)
            else:
                f.write(f"{dir_name} (目录不存在)\n")

    print(f"文件路径树已写入 {output_file}")