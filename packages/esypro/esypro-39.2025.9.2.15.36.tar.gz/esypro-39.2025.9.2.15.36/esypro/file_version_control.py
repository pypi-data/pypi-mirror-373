# -*- coding: utf-8 -*-
# @Time    : 2024/7/11 12:03
# @Author  : Quanfa
# @Desc    : new version
#region import
from .path_tool import MyPath
from .project import Project
import sys
#endregion

def pickle_save(object, path):
    import pickle
    MyPath(path).ensure()
    with open(path, 'wb') as f:
        pickle.dump(object, f)
        
def pickle_load(path):
    import pickle
    with open(path, 'rb') as f:
        return pickle.load(f)
    
def auto_suffix(name, suffix=None):
    if suffix == '':
        return name
    return name + '.' + suffix

import torch
def my_repr(tensor, d=1):
    description = 'Tensor'
    try:
        shape = tuple(tensor.shape)
        description += str(shape)
    except:
        pass
    
    try:
        device = tensor.device
        description += '-'+str(device)
    except:
        pass
    
    try:
        if not sum(tensor.shape) < 10:
            max_value = tensor.max().item()
            description += f'|max:{max_value:.{d}f}'
    except:
        pass
    
    try:
        if not sum(tensor.shape) < 10:
            min_value = tensor.min().item()
            description += f'|min:{min_value:.{d}f}'
    except:
        pass
    
    try:
        if not sum(tensor.shape) < 10:
            if 'float' in str(tensor.dtype):
                mean = tensor.mean().item()
                std = tensor.std().item()
                description += f'|mean:{mean:.{d}f},std:{std:.{d}f})'
    except:
        pass
    
    try:
        # 如果是稀疏张量
        if tensor.is_sparse:
            description += f'|sparse'
        else:
            description += f'({tensor.cpu().detach().numpy()})'
    except:
        pass
    
    return description
    
class ScriptResultManager:
    """
    一个脚本结果管理器，用于管理结果的存储。主要具有以下功能：
    1. 修改torch.Tensor的显示方式
    2. 添加项目目录、结果目录和脚本目录到环境变量
    3. 根据结果目录、脚本名称和作者信息自动生成脚本的结果目录，如果是主脚本则创建新的目录，否则使用已有目录
    """    
    #region static properties
    project_path = None
    def __init__(self, author: str, locals:dict, project_path: MyPath=None, result_path: MyPath=None, version=None, release=True):       
        self.script_path = MyPath(locals['__file__'])
        
        if author is None:
            author = 'auto'  
        
        if self.project_path is not None:
            project_path = self.project_path
            
        if project_path is None:
            project_path = Project.from_folder(MyPath(locals['__file__']).get_parent())
            
        project_path = MyPath(project_path)
        
        project_settings = None
        if project_path.cat('Project.esy').exist():
            import pandas as pd
            project_settings = pd.read_csv(project_path.cat('Project.esy'))
            if result_path is None:
                result_path = project_settings['result_path'][0]

        if result_path is None:
            result_path = self.script_path.get_parent()
        
        result_path = MyPath(result_path)
            
        self.init_once(project_path, result_path)
        
        self.result_path = result_path
        self.author = author
             
        self.script_name =self.script_path.get_level(-1)[:-3]  # just for .py file
        
        self.__sub_result_folder_name = f'_l_{self.author}_{self.script_name}_v'
        if release is False:
            self.__sub_result_folder_name = f'_l_{self.author}{self.script_path.relative_to(self.project_path)[:-3]}_v'
        
        self.set_version = False
        if version is not None:
            self.set_version = True
        
        if version is None:
            version = len(self.result_path.get_files(self.__sub_result_folder_name))
            if not locals['__name__'] == '__main__':
                version -= 1    
                
        self.version = version     
        
        self.locals = locals
        
        self.package_path = self.script_path.get_parent()
        if locals['__package__'] in ['', None]:
            locals['__package__'] = self.package_path.relative_to(self.project_path)[1:].replace('/', '.')
            
    def set_result_path(self, result_path: MyPath):
        self.result_path = result_path
        if not self.set_version:
            version = len(self.result_path.get_files(self.__sub_result_folder_name))
            if not self.is_main:
                    version -= 1
            self.version = version
        
        
    
    def path_of(self, name_suffix: str='', suffix=''):
        """
        advice the path of the object.

        Args:
            name (str): name of the object.
            suffix (str): if None, use the type of the object.

        Returns:
            path(MyPath): the path of the object.
        """
        if suffix != '':
            name_suffix = name_suffix + '.' + suffix
        return self.result_path.cat(f'{self.__sub_result_folder_name}{self.version}/{name_suffix}')
        
    def init_once(self, project_path, result_path):
        if ScriptResultManager.project_path is None:
            # environment path   
            sys.path.append(result_path)
            sys.path.append(project_path)
            sys.path.append(self.script_path.get_parent())
            ScriptResultManager.project_path = project_path
            
            # debug for pytorch
            try:
                import torch
                torch.Tensor.__repr__ = my_repr
            except:
                pass
    
    @ property
    def is_main(self):
        return self.locals['__name__'] == '__main__'
    

    
        