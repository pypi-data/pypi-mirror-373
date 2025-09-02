import torch.utils
import torch.utils.data
import esypro
sfs = esypro.ScriptResultManager('zqf', locals())

"""

"""
from esymod import Model
import torch
from .blocks import FullConnectedLayer
    
        

class BaseLayer(Model):
    def __init__(self, taylor_order: int=3, work_points: int=3, input_dim: int=10, output_dim: int=10):
        """
        
        """
        super(BaseLayer, self).__init__()
        self.w_model = torch.nn.Linear(input_dim*taylor_order*work_points, output_dim*taylor_order*work_points)
        self.alpha_model = torch.nn.Linear(input_dim*taylor_order*work_points, output_dim*taylor_order*work_points)
        self.taylor_order = taylor_order
        self.work_points = work_points
        
        
        
    def forward(self, x):
        """
        forward the model.
        """
        # construct din
        din = []
        for i in range(self.taylor_order):
            din.append(x**i)
        din = torch.cat(din, dim=-1)
        din = din.unsqueeze(-2).expand(-1, 3, -1).flatten(-2)
        
        # forward
        wx = self.w_model(din)
        alpha = self.alpha_model(din)
        return wx*alpha

        
        


if __name__ == '__main__':
    
    import torch
    
    dataset = torch.utils.data.TensorDataset(torch.randn(100, 100000).cuda(2), torch.randn(100, 10).cuda(2))
    
    data_loader = torch.utils.data.DataLoader(dataset, batch_size=100)
    
    model = torch.nn.Sequential(
        torch.nn.Linear(100000, 10000),
        torch.nn.ReLU(),
        torch.nn.Linear(10000, 1000),
        torch.nn.ReLU(),
        torch.nn.Linear(1000, 10),
    ).cuda(2)
    
    for i in range(10000):
        for x, y in data_loader:
            y_pred = model(x)
            loss = torch.nn.functional.mse_loss(y_pred, y)
            loss.backward()
            print(loss)
    
    
    
    
