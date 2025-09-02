#%%
import esypro
sfs = esypro.ScriptResultManager('zqf', locals())

import torch
from esymod import Dataset, ParallelDataset
from scipy.sparse import csr_matrix
import h5py

class H5DenseSample(Dataset):
    def __init__(self, h5_path, X_path='raw/obs/cell_type/codes'):
        """
        一个H5数据集
        """
        self.h5_path = h5_path
        self.X_path = X_path
        super().__init__([torch.arange(len(self.Xs)),])
        print(self)
        
    def __getitem__(self, index):
        index = super().__getitem__(index)[0]
        x_values = self.Xs[index]
        
        return x_values
    
    @ property
    def h5(self):
        return h5py.File(self.h5_path, 'r')
    
    @ property
    def Xs(self):
        try:
            r= self.h5[self.X_path]
        except:
            print(f'err when get {self.X_path} from {self.h5_path}')
        return r

import numpy as np
class H5StrSample(H5DenseSample):
    def __init__(self, h5_path, X_path='raw/obs/cell_type/codes'):
        super().__init__(h5_path, X_path)
        
        categories = np.array(self.Xs)
        categories = np.unique(categories)
        self.categories = categories.tolist()
        
    def __getitem__(self, index):
        r = super().__getitem__(index)
        return self.categories.index(r)
    



class H5SparseSample(ParalellDtaset):
    def __init__(self, h5_path, X_path='raw/X/data', indices_path='raw/X/indices', indptr_path='raw/X/indptr', data_shape=(1, 70000)):
        """
        一个H5数据集
        """
        self.h5_path = h5_path
        self.X_path = X_path
        self.indices_path = indices_path
        self.indptr_path = indptr_path
        self.data_shape = data_shape
        
        super().__init__([torch.arange(len(self.indptrs)-1),])
    
    @property
    def h5(self):
        return h5py.File(self.h5_path, 'r')
    
    @property
    def Xs(self):
        return self.h5[self.X_path]
    @property
    def indices(self):
        return self.h5[self.indices_path]
    @property
    def indptrs(self):
        return self.h5[self.indptr_path]
        
    def __getitem__(self, index):
        index = super().__getitem__(index)[0]
        x_values = self.Xs[self.indptrs[index]:self.indptrs[index+1]]
        x_indexs = self.indices[self.indptrs[index]:self.indptrs[index+1]]
        x_pointers = self.indptrs[index:index+2] - self.indptrs[index]
        
        data_sparse = csr_matrix((x_values, x_indexs, x_pointers), self.data_shape)
        
        return data_sparse
    
    def to_dense(self):
        dataset = DensedH5SparseSample(self.h5_path, self.X_path, self.indices_path, self.indptr_path, self.data_shape)
        dataset.sample_selection = self.sample_selection
        return dataset
    
class DensedH5SparseSample(H5SparseSample):
    def __getitem__(self, index):
        r = super().__getitem__(index)
        return torch.tensor(r.toarray())



def mv_sparse_data(src_h5_path, dst_h5_path, selection):
    assert len(selection.shape) == 1  # now only support 1D selection
    
    with h5py.File(src_h5_path, 'r') as src_file:
        X_data = src_file['raw/X/data']
        X_indices = src_file['raw/X/indices']
        X_indptr = src_file['raw/X/indptr']
    
        write_selected_sparse(X_data, X_indices, X_indptr, selection, dst_h5_path)
    
    return True

from esyimg.process_bar import rich_tqdm as tqdm
def write_selected_sparse(X_data, X_indices, X_indptr, selection, dst_h5_path):

    data_num = 0
    for i, select in enumerate(selection):
        if select:
            data_num += X_indptr[i+1] - X_indptr[i]
    
    with h5py.File(dst_h5_path, 'w') as dst_file:
        dst_file.require_dataset('raw/X/data', shape=(data_num,), dtype='float32')
        dst_file.require_dataset('raw/X/indices', shape=(data_num,), dtype='int64')
        dst_file.require_dataset('raw/X/indptr', shape=(selection.sum()+1,), dtype='int64')
        
        dst_file['raw/X/indptr'][0] = 0
        select_indptr_end = 0
        last_indptr = 0
        n = 0
        for i, select in tqdm(enumerate(selection), total=len(selection)):
            if select:
                select_data = X_data[X_indptr[i]:X_indptr[i+1]]
                select_indices = X_indices[X_indptr[i]:X_indptr[i+1]]
                select_indptr_end = last_indptr+select_data.shape[0]
                dst_file['raw/X/data'][last_indptr:select_indptr_end] = select_data
                dst_file['raw/X/indices'][last_indptr:select_indptr_end] = select_indices
                n += 1         
                dst_file['raw/X/indptr'][n] = select_indptr_end
                
                last_indptr = select_indptr_end


# %%
if __name__ == '__main__':
    print(f'start {__file__}')

    #%%
    print(f'end {__file__}')