import webbrowser, sys
if len(sys.argv) > 2:
    # 从命令行获取参数（程序名，程序参数）
    print(sys.argv)
    # 保留除了第一个参数的所有参数，并将其由列表串联成字符串
    address = ' '.join(sys.argv[1:])
