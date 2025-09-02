import kan.KANLayer
import torch
from . import Model


class KAN_Conv(Model):
    def __init__(self, in_channels=3, out_channels=1, kernel_size=3, stride=1, padding=1, dilation=1, groups=1, bias=True):
        super(KAN_Conv, self).__init__()
        self.conv = torch.nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, stride=stride, padding=padding, dilation=dilation, groups=groups, bias=bias)
        self.kan1 = kan.KANLayer(out_channels, out_channels)

    def forward(self, input):
        output = self.conv(input).transpose(-3, -1)
        size_rec = output.shape[:-1]
        output = self.kan1(output.flatten(0, -2))[0].unflatten(0, size_rec).transpose(-3, -1)
        return output
        

class KAN_GRU(Model):
    def __init__(self, input_size=2, hidden_size=5):
        super(KAN_GRU, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.kan1 = kan.KANLayer(input_size+hidden_size, hidden_size)
        self.kan2 = kan.KANLayer(input_size+hidden_size, hidden_size)
        self.kan3 = kan.KANLayer(input_size+hidden_size, hidden_size)

    def forward(self, input, initial_state):
        prev_h = initial_state
        bs, T, i_size = input.shape

        output = torch.zeros(bs, T, h_size)

        for t in range(T):
            r_t = self.kan1(torch.cat((input[:, t, :], prev_h), dim=-1))[0]
            z_t = self.kan2(torch.cat((input[:, t, :], prev_h), dim=-1))[0]
            n_t = self.kan3(torch.cat((input[:, t, :], r_t*prev_h), dim=-1))[0]
            h_t = (1 - z_t) * n_t + z_t * prev_h
            prev_h = h_t
            output[:, t, :] = prev_h # 将最新状态的hidden_state移动到输出矩阵中

        return output, prev_h

if __name__ == '__main__':

    # #region test KAN GRU

    # #定义常量
    # bs, T, i_size, h_size = 2, 3, 4, 5
    # input = torch.randn(bs, T, i_size) #输入序列
    # h0 = torch.randn(bs, h_size) #初始值,不需要训练
    # target = torch.rand(bs, T, h_size) #目标序列

    # #定义模型
    # model = KAN_GRU(i_size, h_size)

    # # train prepare
    # loss_f = torch.nn.L1Loss()

    # opt = torch.optim.Adam(model.parameters(), lr=0.01)

    # # train

    # for i in range(500):
    #     output, h = model(input, h0)
    #     opt.zero_grad()
    #     loss = torch.nn.functional.mse_loss(output, target)
    #     loss.backward()
    #     opt.step()
    #     print(loss.item())
    #     # optimizer.step()
    # #endregion

    #region test KAN Conv
    b, c, w, h = 5, 3, 28, 28
    input = torch.randn(b, c, w, h)
    target = torch.zeros(b)
    target[:b//2] = 1
    target = target.long()

    model = torch.nn.Sequential(
        KAN_Conv(3, 1, 3),
        torch.nn.Flatten(1),
        torch.nn.Linear(28*28, 2)
    )

    loss_f = torch.nn.CrossEntropyLoss()

    opt = torch.optim.Adam(model.parameters(), lr=0.01)

    for i in range(500):
        output = model(input)
        opt.zero_grad()
        loss = loss_f(output, target)
        loss.backward()
        opt.step()
        print(loss.item())
        # optimizer.step()
    #endregion