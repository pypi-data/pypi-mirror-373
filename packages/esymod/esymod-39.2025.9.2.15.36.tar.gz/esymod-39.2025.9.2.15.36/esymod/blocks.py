#%% init project env
import esypro
sfs = esypro.ScriptResultManager('zqf',locals(), version=0)

import torch
from torch import nn
from . import Model, manipulators

class ResConv(Model):
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1,
                 stimuli=nn.Hardswish):
        """
        conv block with res connection
        :param in_channels:
        :param out_channels:
        :param kernel_size:
        :param stride:
        """

        super().__init__()
        
        if stimuli is None:
            stimuli = nn.Identity
        
        if isinstance(kernel_size, int):
            padding = kernel_size // 2
        else:
            padding = [k // 2 for k in kernel_size]
        self.res_conv = nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=1, stride=stride ** 2)
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, stride=stride,
                      padding=padding),
            stimuli()
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(in_channels=out_channels, out_channels=out_channels, kernel_size=kernel_size, stride=stride,
                      padding=padding),
            stimuli()
        )

    def get_output(self, x):
        direct = self.conv2(self.conv1(x))
        res = self.res_conv(x)
        return res + direct


class ResTConv(Model):
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1,
                 stimuli=nn.Hardswish):
        """
        conv block with res connection
        :param in_channels:
        :param out_channels:
        :param kernel_size:
        :param stride:
        """

        super().__init__()
        self.res_conv = nn.ConvTranspose2d(in_channels=in_channels, out_channels=out_channels, kernel_size=1,
                                           stride=stride ** 2)
        self.conv1 = nn.Sequential(
            nn.ConvTranspose2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size,
                               stride=stride,
                               padding=kernel_size // 2),
            stimuli()
        )
        self.conv2 = nn.Sequential(
            nn.ConvTranspose2d(in_channels=out_channels, out_channels=out_channels, kernel_size=kernel_size,
                               stride=stride,
                               padding=kernel_size // 2),
            stimuli()
        )

    def get_output(self, x):
        direct = self.conv2(self.conv1(x))
        res = self.res_conv(x)
        return res + direct

class MultiplyLayer(manipulators.Multiply):
    def __init__(self, input_dim, output_dim, bias=True):
        route1 = nn.Linear(input_dim, output_dim, bias=bias)
        route2 = nn.Linear(input_dim, output_dim, bias=bias)
        super().__init__(route1, route2)

class FullConnectedLayer(torch.nn.Sequential):
    def __init__(self, input_dim, output_dim, bias=True, stimuli=nn.Hardswish()):
        super().__init__(
            nn.Linear(input_dim, output_dim, bias=bias),
            stimuli
        )


class SparseLinear(torch.nn.Module):
    
    def __init__(self, in_features, out_features, stimuli=torch.nn.ReLU):
        super(SparseLinear, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = torch.nn.Parameter(torch.rand(out_features, in_features))
        self.bias = torch.nn.Parameter(torch.rand(out_features))
        self.stimuli = stimuli()
    
    def forward(self, din):
        x = din.to_sparse()
        
        indicies = x.indices()
        values = x.values()
        
        used_weights = self.weight.T
        used_weights = self.weight.unsqueeze(0).expand(x.size(0), -1, -1)
        used_weights = used_weights[indicies[0], indicies[1]]   
        
        used_bias = self.bias
        used_bias = used_bias.unsqueeze(0).expand(x.size(0), -1)
        used_bias = used_bias[indicies[0], indicies[1]]
        
        biased_values = values + used_bias
        
        r_values = (biased_values.unsqueeze(-1).expand(used_weights.size())*used_weights)
        
        batch_sum_r = torch.zeros(x.size(0), self.out_features).to(x.device)
        batch_sum_r = batch_sum_r.index_add(0, indicies[0], r_values)
        
        r = self.stimuli(batch_sum_r)
        return r
        

        
class VAE(Model):
    def __init__(self, encoder, decoder):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
        
    def get_output(self, x):
        mu, log_var = self.encode(x)
        z = self.resample(mu, log_var)
        return self.decoder(z)
    
    def encode(self, x):
        mu, log_var = self.encoder(x).chunk(2, dim=1)
        return mu, log_var
    
    def resample(self, mu, log_var):
        z = mu + torch.randn_like(mu) * torch.exp(log_var / 2)
        return z
    
class unsqueeze(torch.nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim
    
    def get_output(self, x):
        return x.unsqueeze(self.dim)
    
class squeeze(torch.nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim
    
    def get_output(self, x):
        return x.squeeze(self.dim)


class SpinConv(Model):
    """
    旋转卷积，目的是使用池化的同时将卷积的维度转移到channel上。 TODO：有点奇怪的是，假如用channel填充被池化的位置，那么，邻域相关性会怎么体现呢
    """
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, padding=None, stimuli=nn.Hardswish, pool_kernel_size=2, pool_padding=0):
        if padding is None:
            padding = kernel_size // 2
        hidden_channels = in_channels * (pool_kernel_size ** 2)
        
        super().__init__()
        
        
        self.conv1 = Model(
            nn.Conv2d(in_channels=in_channels, out_channels=hidden_channels, kernel_size=kernel_size, stride=stride, padding=padding),
            nn.MaxPool2d(kernel_size=pool_kernel_size, stride=pool_kernel_size, padding=pool_padding),
        )
        
        self.conv2 = nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, stride=stride, padding=padding)
        
        self.conv_res = nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=1, stride=stride ** 2)
        
        self.stimuli = stimuli()
        self.dim_unflatten = Model(
            manipulators.Unflatten(1, (in_channels, pool_kernel_size, pool_kernel_size)),
            manipulators.Permute(((0, 1, 2, 4, 3, 5))),  # b, c, c1, c2, w, h -> b, c, c1, w, c2, h
            manipulators.Flatten(2, 3),  # b, c, c1, w, c2, h -> b, c, c1 * w, c2, h
            manipulators.Flatten(-2, -1)  # b, c, c1 * w, c2, h -> b, c, c1 * w , c2 * h
        )
        
    def get_output(self, x):
        direct = self.conv_res(x)
        
        straight_conv = self.conv1(x)
        
        # flatten channel to the 2d dims
        straight_conv = self.dim_unflatten(straight_conv)  # b, c, c1, c2, w, h -> b, c, c1 * w, c2 * h
        
        straight_conv = self.stimuli(straight_conv)
        
        straight_conv = self.conv2(straight_conv)
        
        straight_conv = self.stimuli(straight_conv)
        
        return direct + straight_conv
    
class SpinConv1d(Model):
    """
    旋转卷积，但是Conv1d，目的是使用池化的同时将卷积的维度转移到channel上。
    """
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, padding=None, stimuli=nn.Hardswish, pool_kernel_size=2, pool_padding=0):
        if padding is None:
            padding = kernel_size // 2
        hidden_channels = in_channels * pool_kernel_size
        
        super().__init__()
        
        self.conv1 = Model(
            nn.Conv1d(in_channels=in_channels, out_channels=hidden_channels, kernel_size=kernel_size, stride=stride, padding=padding),
            nn.MaxPool1d(kernel_size=pool_kernel_size, stride=pool_kernel_size, padding=pool_padding),
        )
        
        self.conv2 = nn.Conv1d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, stride=stride, padding=padding)
        
        self.conv_res = nn.Conv1d(in_channels=in_channels, out_channels=out_channels, kernel_size=1, stride=stride ** 2)
        
        self.stimuli = stimuli()
        self.dim_unflatten = Model(
            manipulators.Unflatten(1, (in_channels, pool_kernel_size)),
            manipulators.Flatten(-2, -1),  # b,c, c1, w -> b,c,c1*w
        )
        
    def get_output(self, x):
        direct = self.conv_res(x)
        
        straight_conv = self.conv1(x)
        
        # flatten channel to the 2d dims
        straight_conv = self.dim_unflatten(straight_conv)  # b,c,c1 -> b,c*c1
        
        straight_conv = self.stimuli(straight_conv)
        
        straight_conv = self.conv2(straight_conv)
        
        straight_conv = self.stimuli(straight_conv)
        
        return direct + straight_conv

#%% main
if __name__ == '__main__':
    print(f'start {__file__}')
    sample_num = 1000

    y = (torch.rand(sample_num) * 5).long()

    x = torch.randn(sample_num, 3, 32)
    
    for i in range(sample_num):
        x_i = x[i]
        y_i = y[i] * 0.01
        x_i[x_i < y_i] = 0
        x[i] = x_i

    #%% analyse data
    # import umap
    # d2_x = umap.UMAP(n_components=2, n_neighbors=10, min_dist=0.1).fit_transform(x.reshape(sample_num, -1))

    # import matplotlib.pyplot as plt
    # plt.scatter(d2_x[:, 0], d2_x[:, 1], c=y, cmap='jet', s=1)
    # plt.colorbar()
    # plt.title('UMAP of x')

    #%% train model for classification
    from .train import TrainningProcess
    from . import basic
    class SimTrainProcess(TrainningProcess):
        def init_dataset(self, record=None):
            total_dataset = basic.Dataset([x, y], name='simulated dataset')
            trainset, valset = total_dataset.k_split(5)[self.val_index]
                
            train_loader = trainset.get_loader(64, num_workers=4, shuffle=False)
            val_loader = valset.get_loader(16, num_workers=4, shuffle=False)
            
            if record is not None:
                record['trainset'] = trainset
                record['valset'] = valset
                record['total_dataset'] = total_dataset
                record['train_loader'] = train_loader
                record['val_loader'] = val_loader
                
            return total_dataset, trainset, valset, train_loader, val_loader
        
        def init_model(self, record=None):
            model = Model(
                SpinConv1d(3, 3, kernel_size=3, stride=2, stimuli=nn.Hardswish, pool_kernel_size=2),
                manipulators.Flatten(1),
                FullConnectedLayer(3 * 8, 5, stimuli=nn.Hardswish()), 
            )
            
            if self.result_dir.cat('model_last.pth').exist():
                model.load_state_dict(torch.load(self.result_dir.cat('model_last.pth'), weights_only=True, map_location=self.device))
            
            if record is not None:
                record['model'] = model
                
            model.to(self.device)
            
            return model

    training_process = SimTrainProcess(sfs.path_of('spin_conv1d').ensure(), device='cuda:0', val_index=0)

    #%%
    training_process.train(3)
        
    
    
    #%% end script
    print(f'end {__file__}')
