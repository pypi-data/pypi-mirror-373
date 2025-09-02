#%% init project env
import esypro
sfs = esypro.ScriptResultManager('zqf',locals(), version=0)
import torch
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 如果有esyimg就导入esyimg，否则导入tqdm
rich_tqdm_available = False
try:
    from esyimg.process_bar import rich_tqdm as tqdm
    from esyimg.process_bar import progress
    rich_tqdm_available = True
except ImportError:
    from tqdm import tqdm

class TrainningProcess:
    rich_tqdm_available = rich_tqdm_available
    def __init__(self, result_dir, val_index=0, device='cuda:0'):
        if isinstance(result_dir, str):
            self.result_dir = esypro.MyPath(result_dir)
        
        self.val_index = val_index
        self.device = device
        self.result_dir = result_dir.ensure()
    
    def continue_train_of(self, result_dir):
        # 复制result_dir下的所有文件到self.result_dir下
        import shutil
        shutil.copytree(result_dir, self.result_dir, dirs_exist_ok=True)
    
    def init_dataset(self, record=None):

        if not self.result_dir.cat('dataset.pth').exist():
            
            from .basic import Dataset
            total_dataset = Dataset([torch.randn(100, 10), torch.randint(0, 10, (100,))])
            trainset, valset = total_dataset.k_split(5)[self.val_index]

            torch.save((total_dataset, trainset, valset), self.result_dir.cat('dataset.pth'))
        else:
            total_dataset, trainset, valset = torch.load(self.result_dir.cat('dataset.pth'))
        
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
        
        from .blocks import FullConnectedLayer
        model = FullConnectedLayer(10, 10).to(self.device)
        
        if self.result_dir.cat('model_last.pth').exist():
            model.load_state_dict(torch.load(self.result_dir.cat('model_last.pth'), weights_only=True, map_location=self.device))
        
        if record is not None:
            record['model'] = model
        
        return model
    
    def init_optimizer(self, record):
        from torch.optim import SGD
        model = record['model']
        optimizer = SGD(model.parameters(), lr=1e-3)
        record['optimizer'] = optimizer
        return optimizer
    
    def batch_step(self, record):
        batch_data = record['batch_data']
        model = record['model']
        index, x, y = batch_data
        x, y = x.to(self.device), y.to(self.device)
        y_pred = model(x)
        loss = torch.nn.functional.cross_entropy(y_pred, y)
        
        batch_result = {'model_output':y_pred, 'loss':loss}
        
        record['batch_result'] = batch_result
        
        return batch_result
    
    def record_init(self):
        record = {}
        
        self.init_dataset(record)
        self.init_model(record)        
        self.init_optimizer(record)
        
        return record
    
    def after_batch_description(self, record):
        return f'epoch{record["epoch"]}, train lossL{record["train_batch_result"]["loss"]}, val loss:{record["val_batch_result"]["loss"]}'
    
    def after_batch(self, record):
        description = self.after_batch_description(record)
        # insert description into log using logging
        logging.info(description)
        if self.rich_tqdm_available:
            progress.update(progress.task_ids[-1], description=description)
        else:
            print(description)
    
    def after_epoch(self, record):
        print('finish epoch',record['epoch'],'======================================')
        
        # save model
        torch.save(record['model'].state_dict(), self.result_dir.cat(f'model_last.pth'))
        
    
    def train(self, epoch_num=5):
        record = self.record_init()

        # train
        for epoch in tqdm(range(epoch_num)):
            record['epoch'] = epoch
            for train_batch, val_batch in tqdm(zip(record['train_loader'], record['val_loader']), total=len(record['train_loader'])):

                # train
                record['batch_data'] = train_batch
                train_batch_result = self.batch_step(record)
                record['train_batch_result'] = train_batch_result
                record['optimizer'].zero_grad()
                train_batch_result['loss'].backward()
                record['optimizer'].step()
                                
                # val
                with torch.no_grad():
                    record['batch_data'] = val_batch
                    val_batch_result = self.batch_step(record)
                    record['val_batch_result'] = val_batch_result
                    
                self.after_batch(record)
                
            self.after_epoch(record)
                    
        return record

class BatchStepProcess:
    @ staticmethod
    def simple_forward(model, batch_data, device='cuda:0'):
        """
        A simple forward step for a model, used in training or validation.
        Args:
            model (torch.nn.Module): The model to be evaluated.
            batch_data (tuple): A tuple containing the input data and labels.
            device (str): The device to run the model on, default is 'cuda:0'.
        Returns(dict):
            model_output (torch.Tensor): The output of the model.
            loss (torch.Tensor): The computed loss.
        """
        x, y = batch_data
        x, y = x.to(device), y.to(device)
        y_pred = model(x)
        loss = torch.nn.functional.cross_entropy(y_pred, y)
        return {'model_output': y_pred, 'loss': loss}
    
    @ staticmethod
    def denoise_step(model, original_data, noise_step=1, device='cuda:0'):
        """
        A denoise step for a model, used in training or validation.
        Args:
            model (torch.nn.Module): The model to be evaluated.
            original_data (torch.Tensor): The original data to be denoised.
            step (int): The step number.
            device (str): The device to run the model on, default is 'cuda:0'.
        Returns(dict):
            denoised_output (torch.Tensor): The denoised output of the model.
        """
        alpha_t = 1-torch.exp(-noise_step - 1)
        alpha_t_ =  1-torch.exp(-noise_step)
        
        original_data = original_data.to(device)
        alpha_t_ = alpha_t_.to(device)
        alpha_t = alpha_t.to(device)
        
        size = [alpha_t.size(0), *original_data.size()]
        
        noise_data_current = (torch.sqrt(alpha_t).view(-1, 1, 1, 1).expand(size))*(original_data.unsqueeze(0).expand(size)) + (torch.sqrt(1-alpha_t).view(-1, 1, 1, 1).expand(size))* (torch.randn_like(original_data).unsqueeze(0).expand(size))
        denoised_data_next = (torch.sqrt(alpha_t_).view(-1, 1, 1, 1).expand(size))*(original_data.unsqueeze(0).expand(size)) + (torch.sqrt(1-alpha_t_).view(-1, 1, 1, 1).expand(size))* (torch.randn_like(original_data).unsqueeze(0).expand(size))
        
        target_output = denoised_data_next - noise_data_current
        
        # batch flatten and channel add
        noise_data_current = noise_data_current.flatten(0, 1).unsqueeze(1)
        target_output = target_output.flatten(0, 1).unsqueeze(1)
        
        denoised_output = model(noise_data_current)
        
        if False:
            from esyimg import web_matplotlib_util as plt
            figure = plt.figure(figsize=(15, 10))
            plt.imshow(denoised_output[0, 0].cpu().detach().numpy(), cmap='gray')
            plt.show()
        
        loss = torch.nn.functional.mse_loss(denoised_output, target_output)
        return {'denoised_output': denoised_output, 'loss': loss}
    
    
                
                
        

#%% main
if __name__ == '__main__':
    print(f'start {__file__}')

    
    
    #%% end script
    print(f'end {__file__}')
