import esypro
sfs = esypro.ScriptResultManager('zqf', locals())

from . import Model
import torch

class TemporalRes(Model):
    def __init__(self, rnn: torch.nn.RNN,  res_length: int = 1, res_interval: int = None):
        super().__init__()
        self.rnn = rnn
        
        if res_interval is None:
            res_interval = res_length
        
        self.res_length = res_length
        self.res_interval = res_interval
        
    def forward(self, x:torch.Tensor, initial_hidden=None, padding=None):
        """
        :param x: (batch, seq, channels) is a sequential input
        :return: (batch, seq, channels)
        """
        
        # pad sequence
        if padding is None:
            padding = self.res_length - x.size(1) % self.res_length
        x = torch.nn.functional.pad(x, (0, 0, padding, 0))
        
        # seperate x
        x_blocks = x.unfold(1, self.res_length, self.res_interval).permute(1, 0, 3, 2)  # (block, batch, seq, channels)
        
        outputs, hidden = [], []
        
        # first bolck is used to initialize the hidden state
        inital_block = x_blocks[0]
        inital_output, initial_hidden = self.rnn(inital_block, initial_hidden)  # output(batch, seq, channels), hidden(num_layers, batch, channels)
        outputs.append(inital_output)
        res_hidden = initial_hidden * 0
        
        # iterate over the blocks
        for res_block in x_blocks[1:]:
            input_hidden = res_hidden + initial_hidden
            output, hidden = self.rnn(res_block, input_hidden)
            res_hidden = initial_hidden
            initial_hidden = hidden
            outputs.append(output)
        
        # make the output
        outputs = torch.cat(outputs, dim=1)[:, padding:]
        
        
        return outputs, hidden
            
            
            
        

if __name__ == '__main__':

    
    rnn = torch.nn.RNN(
        input_size=10,
        hidden_size=20,
        num_layers=2,
        batch_first=True
    )
    
    seq_length = 20000
    
    sim_inpput = torch.randn(4, seq_length, 10)  # (batch, seq, channels)
    sim_output = torch.randn(2, 4, 20)  # (batch, seq, channels)
    
    model = TemporalRes(rnn, 3)
    simple_rnn = torch.nn.RNN(
        input_size=10,
        hidden_size=20,
        num_layers=2,
        batch_first=True
    )
    loss_fc = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    optimizer_simple = torch.optim.Adam(simple_rnn.parameters(), lr=0.001)
    
    losses = []
    losses2 = []
    
    for i in range(100):
        output, hidden = model(sim_inpput)
        
        loss = loss_fc(hidden, sim_output)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        output, hidden = simple_rnn(sim_inpput)
        loss2 = loss_fc(hidden, sim_output)
        optimizer_simple.zero_grad()
        loss2.backward()
        optimizer_simple.step()
        
        
        print(f'epoch {i}:',loss.item(), loss2.item())
        losses.append(loss.item())
        losses2.append(loss2.item())
    
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(torch.tensor(losses)/max(losses), label='TemporalRes')
    plt.plot(torch.tensor(losses2)/max(losses2), label='SimpleRNN')
    plt.legend()
    plt.savefig(sfs.path_of('loss-norm', 'png').ensure())
    
    
