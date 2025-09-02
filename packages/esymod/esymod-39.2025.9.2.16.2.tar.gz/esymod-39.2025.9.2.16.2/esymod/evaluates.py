#%% init project env
import esypro
sfs = esypro.ScriptResultManager('zqf', locals())

#%% performance for classifying
import torch
def confusion_matrix(target_label, output_distribution):
    """
    confusion matrix for each layer
    Args:
        target_label (torch.Tensor): target label
        output_distribution (torch.Tensor): output distribution
    Returns:
        confusion_matrix (torch.Tensor): confusion matrix
    """
    # device
    if target_label.device != output_distribution.device:
        target_label = target_label.to(output_distribution.device)
    if len(target_label.size()) > 1:
        target_label = target_label.squeeze()
    assert target_label.size(0) == output_distribution.size(0)
    output_label = output_distribution.argmax(dim=-1)
    num_classes = output_distribution.size(1)
    confusion_matrix = torch.zeros(num_classes, num_classes)
    for i in range(target_label.size(0)):
        confusion_matrix[target_label[i], output_label[i]] += 1
    return confusion_matrix

def accuracy(target_label, output_distribution):
    """
    accuracy for each layer
    Args:
        target_label (torch.Tensor): target label
        output_distribution (torch.Tensor): output distribution
    Returns:
        accuracy (torch.Tensor): accuracy
    """
    if target_label.device != output_distribution.device:
        target_label = target_label.to(output_distribution.device)
    if target_label.dim() > 1:
        target_label = target_label.squeeze()
    assert target_label.size(0) == output_distribution.size(0)
    output_label = output_distribution.argmax(dim=-1)
    correct_num = (target_label == output_label).sum()
    return correct_num / target_label.size(0)

def precision(confusion_matrix):
    """
    precision 
    Args:
        confusion_matrix (torch.Tensor): confusion matrix
    Returns:
        precision (torch.Tensor): precision
    """
    num_classes = confusion_matrix.size(0)
    precisions = torch.zeros(num_classes)
    for i in range(num_classes):
        precisions[i] = confusion_matrix[i, i] / (confusion_matrix[i].sum()+1e-6)
    return precisions



#%% main
if __name__ == '__main__':
    print(f'start {__file__}')
    
    
    
    #%% end script
    
