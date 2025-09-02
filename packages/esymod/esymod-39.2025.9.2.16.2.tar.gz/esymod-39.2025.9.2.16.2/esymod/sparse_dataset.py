#%% init project env
import esypro
import scipy.sparse
sfs = esypro.ScriptResultManager('zqf',locals(), version=0)

from . import basic
import torch
import scipy


class CSRMatrixDataset(basic.IterableData):
    """
    Iterate over a CSR matrix.
    The dataset will return a dense vector for each index.
    """
    def __init__(self, csr_matrix, sample_selection=None, **kwargs):
        self.indicies = torch.tensor(csr_matrix.indices)
        self.indptrs = torch.tensor(csr_matrix.indptr)
        self.data = torch.tensor(csr_matrix.data)
        self.shape = csr_matrix.shape
        self.line_index = torch.arange(len(self.indptrs)-1)
        
        super().__init__(self.line_index, sample_selection=sample_selection, **kwargs)
        
    def __getitem__(self, select_index):
        index = super().__getitem__(select_index)
        x_values = self.data[self.indptrs[index]:self.indptrs[index+1]]
        x_indexs = self.indicies[self.indptrs[index]:self.indptrs[index+1]]
        x_pointers = self.indptrs[index:index+2] - self.indptrs[index]
        csr_matrix = scipy.sparse.csr_matrix((x_values, x_indexs, x_pointers), shape=(1, self.shape[1]))
        dense_vector = torch.tensor(csr_matrix.todense()).squeeze(0)
        return dense_vector
        
    
    

#%% main
if __name__ == '__main__':
    print(f'start {__file__}')

    data = scipy.sparse.csr_matrix([[1, 0, 0], [0, 2, 0], [3, 0, 4]])
    dataset = CSRMatrixDataset(data)
    
    #%%
    dataset[0]
    
    #%% end script
    print(f'end {__file__}')
