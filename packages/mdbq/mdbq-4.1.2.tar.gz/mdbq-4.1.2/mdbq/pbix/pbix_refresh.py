import time
import os
import psutil
# from pywinauto.application import Application


def pbi(_path, _timeout=300):
    """
    _path: pbi文件路径
    _timeout: 刷新等待时间
    如果连接失败，请将 power bi 文件名的特殊字符(空格等)去掉或改为英文文件名试试
    """
    # 关闭已打开的 power bi进程
    procname = "PBIDesktop.exe"
    for proc in psutil.process_iter():
        if proc.name() == procname:
            proc.kill()
    time.sleep(1)

    # 启动 Power bi
    os.system('start "" "' + _path + '"')
    time.sleep(5)

    # 通过 connect 方法连接进程
    app = Application(backend='uia').connect(path=procname)
    # title_re可以通过正则表达式连接：".*Power BI Desktop", 仅限 2023年9月之前的 Power bi版本
    # 2023年10月之后的版本没有此窗口后缀, 因此需用文件名找窗口
    # 如果同时打开了其他同名的文件（非 power bi文件时）, 可能会引发错误
    _filename = os.path.splitext(os.path.basename(_path))[0]  # 文件名不含后缀
    win = app.window(title_re=f'{_filename}.*?')  # 连接 pbi 窗口
    time.sleep(10)
    # win.print_control_identifiers()  # 打印窗口全部信息, 推荐使用 inspect 开发工具查询窗口句柄信息
    num = 0
    while True:
        try:
            win['刷新'].wait("enabled", timeout=_timeout)
            time.sleep(3)
            win['刷新'].click()
            break
        except:
            print(f'{_path}, 未识别窗口句柄, 连接超时')
            num += 1
            if num > 1:
                break

    num = 0
    while True:
        try:
            win['保存'].wait("enabled", timeout=_timeout)  # timeout 通过"保存"按键状态, 等待刷新窗口关闭, 时间不要设置太短
            time.sleep(3)
            win['保存'].click()
            break
        except:
            print(f'{_path}, 未识别窗口句柄, 文件未保存')
            num += 1
            if num > 1:
                break
    # win.type_keys("^s")
    win.wait("enabled", timeout=15)
    win.close()

    # 关闭进程
    for proc in psutil.process_iter():
        if proc.name() == procname:
            proc.kill()


if __name__ == '__main__':
    path = r'C:\Users\Administrator\Downloads\cs.pbix'
    pbi(path)
