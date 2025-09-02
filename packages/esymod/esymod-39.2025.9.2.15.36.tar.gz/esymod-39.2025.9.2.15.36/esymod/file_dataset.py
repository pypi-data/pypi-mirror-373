import esypro
sfs = esypro.ScriptResultManager('zqf', locals())

import torch
import esypro

def max_level_of(dataset_path, max_search=10):
    """
    获取dataset_path下样本的最大深度
    """
    max_level = 1
    current_path = dataset_path
    while max_level < max_search:
        files = current_path.get_files(list_r=True)
        if len(files) > 0:
            break
        current_path = current_path / max(list(current_path.get_files('').keys()))
        max_level += 1
    return max_level

def sample_index_to_path(max_level, sample_index, code=100):

    # 获取每一级的索引
    path = []
    for i in range(max_level-1):
        path.append(sample_index % code)
        sample_index = sample_index // code
    path.append(sample_index)
    path.reverse()  
    
    # 转换为路径
    p = '/'.join([str(p) for p in path])
    return p
        
def path_to_sample_index(path, code=100):
    """
    将路径转换为样本索引
    """
    path = path.split('/')

    sample_index = 0
    for i, p in enumerate(path):
        sample_index += int(p) * (code ** (len(path) - i - 1))
    return sample_index

def save_samples_in_dataset(dataset_path, samples, indexs=None, suffix='.pt', max_level=None, code=100, bar=False):
    """
    将样本保存到文件系统中，每个样本是一个文件，文件名是样本的索引
    由于文件系统子文件夹数量有限，所以子文件夹下最多有100个对象，每100个对象则构建更深一层目录（其实就是按照100进制存储）
    """
    if indexs is None:
        indexs = torch.arange(len(samples))
        
    if max_level is None:
        max_level = 1
        while indexs.max().item() > code ** max_level:
            max_level += 1

    if bar:
        from tqdm import tqdm
        bar = tqdm(zip(indexs, samples), total=len(indexs))
    else:
        bar = zip(indexs, samples)
    for idx, sample in bar:
        p =  dataset_path / (sample_index_to_path(max_level, idx.item(), code) + suffix)
        # 确保文件夹存在，由于可能需要适配多线程，所以使用try
        try:
            p.ensure()
        except:
            pass
        
        torch.save(sample, p)

def multi_process_save(dst_path, iterable_obj, indexs=None, suffix='.pt', max_level=None, code=100, bar=False):
    """
    多进程保存
    Args:
        dst_path (esypro.MyPath): 保存路径
        iterable_obj (object): 可迭代对象
        indexs (list): 索引列表, 每个子进程处理一个索引
        suffix (str, optional): 后缀. Defaults to '.pt'.
        max_level (int, optional): 最大深度. Defaults to None.
        code (int, optional): 每层最大数量. Defaults to 100.
        bar (bool, optional): 是否显示进度条. Defaults to False.
    """
    total_indexs = torch.arange(len(iterable_obj))
    
    # 把total_index转换为dask array
    from dask import array as dask_array
    dasked_index = dask_array.from_array(total_indexs.numpy(), chunks=(code,))
    
    dasked_index.map_blocks(lambda x: save_samples_in_dataset(dst_path, [iterable_obj[i] for i in x], x, suffix, max_level, code, bar), dtype='object').compute()
    

def max_index_in(folder):
    """
    获取文件夹下最大的索引
    """
    files = folder.get_files(list_r=False)
    if len(files) == 0:
        return -1
    return max([int(f.split('.')[0]) for f in files.keys()])

def last_sample_path(dataset_path, max_level=None, code=100):
    """
    获取dataset_path下最后一个样本的路径
    """
    if max_level is None:
        max_level = max_level_of(dataset_path)
    
    current_path = dataset_path
    for level in range(max_level):
        files = current_path.get_files(list_r=True)
        if len(files) == 0:  # 如果当前目录下没有文件，则进入最大的子目录
            current_path = current_path / str(max([int(n) for n in list(current_path.get_files('', list_r=False).keys())]))
        else:  # 如果当前目录下有文件，则输出最大的文件路径
            path = current_path / str(max_index_in(current_path))
            
    return path.relative_to(dataset_path)[1:]

from . import Dataset
class FileDataset(Dataset):
    def __init__(self, dataset_path, sample_selection=None, suffixs=['.pt'], code=100):
        # 获取最大深度
        max_level = max_level_of(dataset_path)
        
        if sample_selection is None:
            # 获取最大样本的路径
            last_sample = last_sample_path(dataset_path, max_level)
            # 获取最大样本的索引
            max_index = path_to_sample_index(last_sample)
            sample_selection = torch.arange(max_index+1)
        tensors = [sample_selection]
        super().__init__(tensors, sample_selection)
        self.dataset_path = dataset_path
        self.max_level = max_level
        self.code = code
        self.suffixs = suffixs
        
    def __getitem__(self, select_index):
        index = super().__getitem__(select_index)[0]
        path = self.dataset_path / sample_index_to_path(self.max_level, index.item(), self.code)
        result = []
        for suffix in self.suffixs:
            result.append(torch.load(path + suffix))
        return result

if __name__ == '__main__':
    import torch
    data_index = torch.arange(150)
    
    dataset_path = sfs.path_of('dataset', '').ensure()
    
    save_samples_in_dataset(dataset_path, data_index, suffix='.pt')
    
    print(max_level_of(dataset_path))
    
    print(last_sample_path(dataset_path))
    
    dataset = FileDataset(dataset_path)
    
    for batch_result in dataset.get_loader(batch_size=4):
        print(batch_result)
        break
    
    
        