#%% init project env
import esypro
sfs = esypro.ScriptResultManager('zqf',locals(), version=0)

import torch
import torch.utils
import torch.utils.data

class CheckOut(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.output = None
    def forward(self, x):
        self.output = x
        return x

class Model(torch.nn.Sequential):
    """
    1. 带有设备参数的模型，用于设备自动适配。
    2. 带有保存和加载方法的模型，用于模型持久化。
    3. 带有参数数量属性的模型，用于模型参数计数。
    4. 带有输出属性的模型，用于前向输出。
    """
    
    def __init__(self, *layers):
        """
        使用层初始化模型。
        """
        super().__init__()
    
        device_parameter = torch.tensor([0], dtype=torch.int64)
        # 注册设备参数
        self.register_buffer('device_parameter', device_parameter)
        
        
        for idx, module in enumerate(layers):
            self.add_module(f'layer{idx}', module)
    
    def get_output(self, x):
        return super().forward(x)
        
    def forward(self, *args, **kwargs):
        """
        前向传播

        参数:
            x (Tensor): 输入张量

        返回:
            Tensor: 输出张量
        """
        self.output = self.get_output(*args, **kwargs)
        return self.output

    #region device
    @ property
    def device(self):
        return self.device_parameter.device
        
    
    #endregion

    #region param count
    @ property
    def param_num(self):
        params = list(self.parameters())
        k = 0
        for i in params:
            l = 1
            for j in i.size():
                l *= j
            k = k + l
        return k
    #endregion

import copy
class IterableData(torch.utils.data.Dataset):
    """
    一个自定义数据集类，继承自 `torch.utils.data.Dataset`，用于处理张量数据并提供额外的功能，如迭代、数据加载和k折交叉验证。 \n
    **属性**:\n
        sample_selection (torch.Tensor): 包含要使用的样本索引的张量。\n
        tensors (list of torch.Tensor): 包含数据的张量列表。\n
    **方法**:\n
        __init__(self, tensors, sample_selection=None):\n
            使用给定的张量和可选的样本选择初始化数据集。\n
        __iter__(self):\n
            初始化数据集的迭代器。\n
        __next__(self):\n
            在迭代过程中返回数据集中的下一个项目。\n
        get_loader(self, batch_size=4, shuffle=True):\n
            返回具有指定批量大小和随机选项的数据加载器。\n
        __getitem__(self, select_index):\n
            返回指定索引处的项目。\n
        __len__(self):\n
            返回数据集的长度。\n
        subset(self, sample_selection):\n
            创建一个具有新样本选择的数据集副本。\n
        k_split(self, k):\n
            将数据集分成k折进行交叉验证，并返回(train_subset, val_subset)元组的列表。
    """
    def __init__(self, iterable_obj, sample_selection=None, name=None):
        """
        使用给定的张量和可选的样本选择初始化数据集。
        参数:
            tensors (list of torch.Tensor): 包含数据的张量列表。
            sample_selection (torch.Tensor): 包含要使用的样本索引的张量。
        """
        # 如果没有指定要使用的样本索引，则全按顺序
        sample_index = torch.arange(len(iterable_obj))
        if sample_selection is None:
            sample_selection = sample_index


        if name is None:
            name = type(self).__name__
        
        self.sample_selection = sample_selection
        self.iterable_obj = iterable_obj
        self.name = name
    
    # region math
    def __add__(self, other):
        if not isinstance(other, IterableData):
            return NotImplemented

        if isinstance(self.iterable_obj, torch.Tensor):
            iterable_obj_merged = torch.cat([self.iterable_obj, other.iterable_obj], dim=0)
        else:
            iterable_obj_merged = self.iterable_obj + other.iterable_obj

        return IterableData(iterable_obj_merged, torch.cat([self.sample_selection, other.sample_selection + len(self.iterable_obj)], dim=0))

    def __sub__(self, other):
        if not isinstance(other, IterableData):
            return NotImplemented
        
        assert not isinstance(self.iterable_obj, torch.Tensor), "Tensor does not support subtraction operation." # TODO: 需要实现
        
        return IterableData(self.iterable_obj - other.iterable_obj, self.sample_selection)
    # endregion

    #region iterable
    def __iter__(self):
        self.iter_count = -1
        return self

    def __next__(self):
        self.iter_count += 1
        if self.iter_count >= len(self):
            raise StopIteration
        return self[self.iter_count]
    #endregion
    
    def __repr__(self):
        return self.name + f': {len(self)} samples'

    def get_loader(self, batch_size=4, shuffle=True, **args):
        """
        返回具有指定批量大小和随机选项的数据加载器。
        参数:
            batch_size (int): 数据加载器的批量大小。
            shuffle (bool): 是否随机打乱数据。
        返回:
            (DataLoader): 数据加载器。
        """
        return torch.utils.data.DataLoader(self, batch_size=batch_size, shuffle=shuffle, **args)

    def __getitem__(self, select_index):

        # index取数
        index = self.sample_selection[select_index].item()
        return self.iterable_obj[index]

    def __len__(self):
        return len(self.sample_selection)

    def subset(self, sample_selection):
        """
        拷贝一个共享所有属性的数据集，单独替换sample_selection
        参数:
            sample_selection (torch.Tensor): 包含要使用的样本索引的张量。
        返回:
            (Dataset): 具有新样本选择的数据集副本。
        """
        # 如果sample_selection是truefalse向量，转换为索引
        if sample_selection.dtype == torch.bool:
            sample_selection = self.sample_selection[sample_selection]
        
        copyset = copy.copy(self)
        copyset.sample_selection = sample_selection
        return copyset
    
    def k_split(self, k:int, shuffle:bool=True):
        """
        按照k折划分验证的要求，返回交叉验证数据集.
        参数:
            k (int): 交叉验证的折数。
        返回:
            (Dataset, Dataset): (train_subset, val_subset)元组的列表。
        """
        total_index = self.sample_selection
        # shuffle
        if shuffle:
            total_index = total_index[torch.randperm(len(total_index))]
        
        # split
        subsets = []
        for i in range(k):
            val_index = total_index[i::k]
    
            train_index = total_index[~torch.isin(total_index, val_index)]        
            val_subset = self.subset(val_index)
            train_subset = self.subset(train_index)
            subsets.append((train_subset, val_subset))
        
        return subsets
        
    
class Dataset(IterableData):
    """
    一个自定义数据集类，继承自 `torch.utils.data.Dataset`，用于处理张量数据并提供额外的功能，如迭代、数据加载和k折交叉验证。 \n
    **属性**:\n
        sample_selection (torch.Tensor): 包含要使用的样本索引的张量。\n
        tensors (list of torch.Tensor): 包含数据的张量列表。\n
    **方法**:\n
        __init__(self, tensors, sample_selection=None):\n
            使用给定的张量和可选的样本选择初始化数据集。\n
        __iter__(self):\n
            初始化数据集的迭代器。\n
        __next__(self):\n
            在迭代过程中返回数据集中的下一个项目。\n
        get_loader(self, batch_size=4, shuffle=True):\n
            返回具有指定批量大小和随机选项的数据加载器。\n
        __getitem__(self, select_index):\n
            返回指定索引处的项目。\n
        __len__(self):\n
            返回数据集的长度。\n
        subset(self, sample_selection):\n
            创建一个具有新样本选择的数据集副本。\n
        k_split(self, k):\n
            将数据集分成k折进行交叉验证，并返回(train_subset, val_subset)元组的列表。
    """
    def __init__(self, tensors, sample_selection=None, **kwargs):
        """
        使用给定的张量和可选的样本选择初始化数据集。
        参数:
            tensors (list of torch.Tensor): 包含数据的张量列表。
            sample_selection (torch.Tensor): 包含要使用的样本索引的张量。
        """
        sample_index = torch.arange(len(tensors[0]))
        super().__init__(sample_index, sample_selection, **kwargs) 
        
        self.child_datasets = [
            tensor if isinstance(tensor, IterableData) 
            else IterableData(tensor, self.sample_selection) 
            for tensor in tensors
        ]

    def __getitem__(self, select_index):
        """返回指定索引处的项目。
        参数:
            select_index (int): 要获取的项目的索引。
        返回:
            list: 包含所有张量在指定索引处的值的列表。[index, tensor1_value, tensor2_value, ...]
            
        """
        index = super().__getitem__(select_index)
        result = [tensor[index] for tensor in self.child_datasets]
        return result

ParallelDataset = Dataset

class SerialDataset(IterableData):
    def __init__(self, datasets, sample_selection=None):
        """
        数据集中必须有一个是SerialDataset，可以通过以下方式构建:
        [
            Dataset(
                [
                    Dataset(xxx),
                    Dataset(xxx)
                ]
            )
        ]
        """
        # first, sample_index
        dataset_indexs = []
        inner_indexs = []
        for i, dataset in enumerate(datasets):
            d_index = torch.tensor([i]*len(dataset))
            i_index = torch.arange(len(dataset))
            dataset_indexs.append(d_index)
            inner_indexs.append(i_index)
        dataset_indexs = torch.cat(dataset_indexs)
        inner_indexs = torch.cat(inner_indexs)      
        sample_index = torch.stack([dataset_indexs, inner_indexs], dim=1)
        super().__init__(sample_index, sample_selection)

        self.child_datasets = [
            dataset if isinstance(dataset, IterableData)
            else IterableData(dataset)
            for dataset in datasets
        ]
        
    def __getitem__(self, select_index):
        data_index, inner_index = self.get_hiarchical_index(select_index)
        return self.child_datasets[data_index][inner_index]

    def get_hiarchical_index(self, select_index):
        """
        获取高阶索引
        参数:
            select_index (int): 选择的索引
        返回:
            (int, int): (dataset_index, inner_index)
        """
        data_index, inner_index = super().__getitem__(select_index)
        return data_index.item(), inner_index.item()
#%% main
if __name__ == '__main__':
    print(f'start {__file__}')

    data1 = torch.arange(10)
    data2 = torch.arange(10) + 10
    serial_dataset = SerialDataset([data1, data2])
    print(serial_dataset[1])
    parallel_dataset = ParallelDataset([data1, data2])
    print(parallel_dataset[1])
    

    #%% end script
    print(f'end {__file__}')