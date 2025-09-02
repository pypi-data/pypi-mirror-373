import esypro
sfs = esypro.ScriptResultManager('zqf', locals())
import torch
from torch.nn import Identity
from . import Model


class Squeeze(torch.nn.Module):
    def __init__(self, dim=None):
        super().__init__()
        self.dim = dim

    def forward(self, x):
        return torch.squeeze(x, dim=self.dim)
    
class Unsqueeze(torch.nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, x):
        return torch.unsqueeze(x, dim=self.dim)

class Flatten(torch.nn.Flatten):
    def __init__(self, start_dim=0, end_dim=-1):
        super().__init__(start_dim, end_dim)
        self.original_shape = None
        self.output_shape = None
    def forward(self, x):
        self.original_shape = tuple(x.shape)
        r = super().forward(x)
        self.output_shape = tuple(r.shape)
        return r

class Unflatten(torch.nn.Module):
    def __init__(self, dim, sizes):
        super().__init__()
        self.dim = dim
        self.sizes = sizes
        
    def forward(self, x):
        sizes = self.sizes
        if isinstance(sizes, Flatten):
            sizes = sizes.original_shape[sizes.start_dim:sizes.end_dim+1]
        
        return torch.unflatten(x, self.dim, sizes)

class AlignStack(torch.nn.Module):
    def __init__(self, align_dim=1, target_size=0):
        """
        align tensors to the same size on align_dim, and stack them on 0 dim
        :param stack_dim: the dim to stack
        :param align_dim: the dim to align, index orignally
        :param target_size: the target size of align_dim
        """
        super().__init__()
        self.align_dim = align_dim
        self.target_size = target_size
        
    def forward(self, tensors: list[torch.Tensor]):
        target_size = self.target_size
        if target_size == 0:
            target_size = max([tensor.shape[self.align_dim] for tensor in tensors])
        
        example_size = tensors[0].shape
        example_size = list(example_size)
        example_size[self.align_dim] = target_size
        example_size = [len(tensors)] + example_size
        result = torch.zeros(example_size, device=tensors[0].device)
        
        for i, tensor in enumerate(tensors):
            slices = [slice(None)] * len(tensor.shape)
            slices[self.align_dim] = slice(None, tensor.shape[self.align_dim])
            slices = [slice(i)] + slices
            result[slices] = tensor

        return result

class View(torch.nn.Module):
    def __init__(self, *shape):
        super().__init__()
        self.shape = shape
        self.original_shape = []
        
    def forward(self, x):
        self.original_shape[0] = x.shape.copy()
        id = 0
        shape = []
        for s in self.shape:
            if s == -1:
                shape.append(x.size(id))
                id += 1
            else:
                shape.append(s)
        return x.view(*shape)

class PadUnflatten(torch.nn.Module):
    def __init__(self, dim, size):
        """
        unflatten a dim to size, pad if not match
        """
        super().__init__()
        self.dim = dim
        self.size = size
        self.ideal_size = torch.tensor(size).cumprod(0)[-1].item()
    
    def forward(self, x):
        if not x.size(self.dim) == self.ideal_size:
            pad_size = self.ideal_size - x.size(self.dim)
            if self.dim == -1:
                pad = torch.zeros(*x.size()[:self.dim], pad_size, device=x.device)
            else:
                pad = torch.zeros(*x.size()[:self.dim], pad_size, *x.size()[self.dim+1:], device=x.device)
            x = torch.cat([x, pad], dim=self.dim)
        return torch.unflatten(x, self.dim, self.size)

class Permute(torch.nn.Module):
    def __init__(self, *dims):
        super().__init__()
        self.dims = dims
    
    def forward(self, x):
        return x.permute(*self.dims)

class Transpose(torch.nn.Module):
    def __init__(self, dim0, dim1):
        super().__init__()
        self.dim0 = dim0
        self.dim1 = dim1
    
    def forward(self, x):
        return x.transpose(self.dim0, self.dim1)

class OutputSelect(torch.nn.Module):
    def __init__(self, selector=0):
        """
        here is an example:
        import torch

        # 假设你有一个tensor
        tensor = torch.randn(3, 5, 7)

        # 使用slice对象
        selector = (slice(None), 4, slice(None))
        
        """
        super().__init__()
        self.selector = selector
        
    def forward(self, x):
        self.output = x[self.selector]
        return self.output

class Stack(torch.nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim
    
    def forward(self, xs):
        return torch.stack(xs, dim=self.dim)

class Concatenate(torch.nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim
    
    def forward(self, xs):
        return torch.cat(xs, dim=self.dim)

#region math
class SUM(Model):
    def __init__(self, *routes):
        super().__init__(*routes)
        self.routes = routes

    def manipulate(self, x1, x2):
        return x1 + x2

    def forward(self, x):
        rs = [route(x) for route in self.routes]
        result = rs[0]
        for r in rs[1:]:
            result = self.manipulate(result, r)
        self.output = result
        return result


class Multiply(SUM):
    def manipulate(self, x1, x2):
        return x1 * x2


class MatrixMultiply(Multiply):
    def manipulate(self, x1, x2):
        return x1 @ x2


class Exp(torch.nn.Module):
    def forward(self, x):
        return torch.exp(x)
#endregion



# hilbert
class HilbertSelect(torch.nn.Module):
    def __init__(self, level):
        super().__init__()
        self.level = level
        self.hilbert_matrix = self.create_hilbert_matrix(level)
        
    def forward(self, x):
        """
        :param x: a tensor with shape (..., length)
        """
        # trans sequecne to matrix using hilbert matrix
        return x[..., self.hilbert_matrix]
    
    @ staticmethod
    def create_hilbert_matrix(level):
        """
        创建一个矩阵，这个矩阵中的数值为希尔伯特曲线上的index
        """
        return
    

if __name__ == '__main__':

    matrix_depth = 3
    line = torch.arange(2**matrix_depth*2**matrix_depth*1).reshape(1, -1)
    
    model = HilbertSelect(matrix_depth)
    print(model(line))
    
    

