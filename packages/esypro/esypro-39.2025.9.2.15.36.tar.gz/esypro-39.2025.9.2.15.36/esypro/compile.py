import compileall
import os
import runpy
import sys

from shutil import copy as scopy
from os import remove
from . import MyPath


def copy(src, dst):
    pdst = os.path.dirname(dst)
    if not os.path.exists(pdst):  # 如果路径不存在
        os.makedirs(pdst)
    scopy(src, dst)
    print('copy:', src, '->', dst)


def delete_gap_dir(dir):
    if os.path.isdir(dir):
        for d in os.listdir(dir):
            delete_gap_dir(os.path.join(dir, d))
        if not os.listdir(dir):
            os.rmdir(dir)


def compile_condition(compile_c, file):
    if not compile_c:
        return '.py' == file[-3:]
    else:
        if '__init__' in file:
            return '.py' == file[-3:]
        return '.pyc' == file[-4:]
def compile_to(
        src,
        dst,
        author,
        author_email,
        name=None,
        version=None,
        py_version=None,
        delete=False,
        upload=False,
        compile_c=True,
        description='A python lib for xxxxx',
        twin_user=None,
        twin_psd=None
):
    """
    打包并发布
    :param src: 需要打包的python package文件夹的路径
    :param dst: 打包后的文件存放的位置
    :param py_version: python版本
    :param version: 包的版本
    :param delete: 是否删除预编译文件
    :param upload: 是否自动上传
    :param compile_c: 是否以预编译模式打包
    :return:
    """
    #region 参数检查
    # 检查路径
    src = MyPath(src)
    dst = MyPath(dst)

    if name is None:
        name = src.get_name()
    if py_version is None:
        py_version = sys.version[:3].replace('.', '')

    # 检查版本
    if version is None:
        from datetime import datetime
        version = py_version + '.' + datetime.now().strftime("%Y.%m.%d.%H.%M")
    version = version.replace('.0', '.')

    # 检查缓存路径
    release_folder = dst.cat('release_' + name).ensure()

    # 检查python package的缓存路径
    pakage_copy = release_folder.cat(name).ensure()

    #endregion

    #region clear
    # 清除原本的预编译文件
    for root, dirs, files in os.walk(src):
        for file in files:
            if '.pyc' in file:
                path = MyPath(root).cat(file)
                remove(path)

    # 清除缓存中的预编译文件
    for root, dirs, files in os.walk(pakage_copy):
        for file in files:
            path = MyPath(root).cat(file)
            remove(path)
    #
    # # 删除空的缓存的文件夹
    # delete_gap_dir(pakage_copy)
    #endregion

    #region ==============编译文件==============
    compileall.compile_dir(src)
    # 把预编译或原始文件挪到缓存文件夹
    for root, dirs, files in os.walk(src):
        for file in files:
            src_path = MyPath(root).cat(file)
            dst_path = src_path.replace(src, pakage_copy)
            if compile_condition(compile_c, file):
                # 替换预编译文件的路径
                dst_path = dst_path.replace('/__pycache__', '').replace('.cpython-' + py_version, '')
                if '_l_' in src_path:
                    print('skip:', src_path)
                    continue
                copy(src_path, dst_path)
    #endregion

    #region ==============set_up_file==============
    
    # generate setup
    dst_path = pakage_copy.get_level(0, -1)

    f = dst_path.cat('setup.py')
    f.ensure()
    f = open(f, 'w')
    f.write(
        """# -*- coding:utf-8 -*-
import sys
sys.argv.append('sdist')
from distutils.core import setup
from setuptools import find_packages

setup(name=\'""" + name + """\',
            version=\'""" + version + """\',
            packages=[\'""" + name + """\',],
            description=\'""" + description + """\',
            long_description='',
            author=\'""" + author + """\',
            include_package_data = True,
            author_email=\'""" + author_email + """\',
            url='http://www.xxxxx.com/',
            license='MIT',
            )

            """
    )
    f.close()
    #endregion
    
    #region ==============manifest==============
    
    # generate manifest
    f = dst_path.cat('MANIFEST.in').ensure()
    with open(f, 'w') as f:
        f.write('recursive-include ' + name + ' *')
    f.close()
    
    if True:
        f = dst_path.cat('compile.py')
        f.ensure()
        f = open(f, 'w')
        f.write(
            """# -*- coding:utf-8 -*-
from os.path import abspath
path = abspath(__file__).replace('\\\\', '/')
mask = 'T20'
paths = path.split('/')
root_path = ''
for c in paths:
    root_path += c
    if mask in c:
        break
    root_path += '/'
import sys

sys.path.append(root_path)
from distutils.core import setup
from setuptools import find_packages
import os
sys.argv.append('sdist')
dst_path = \'""" + dst_path + """\'
os.chdir(dst_path)
import runpy
runpy.run_path(r\'""" + dst_path.cat('setup.py') + """\')
                    """
        )
        f.close()
        r = runpy.run_path(str(dst_path.cat('compile.py')))


        release_name = name + '-' + version + '.tar.gz'
        rp = dst.cat(release_name)
        copy(dst_path.cat('dist', release_name.lower()), rp)
    #endregion
                

    if delete:
        for root, dirs, files in os.walk(release_folder):
            for file in files:
                path = os.path.join(root, file)
                remove(path)

        try:
            delete_gap_dir(release_folder)
        except:
            pass

    if upload:
        mycmd = f"{sys.executable} -m twine upload -u {twin_user} -p {twin_psd} {rp}"
        s = os.system(mycmd)
        print(s)

