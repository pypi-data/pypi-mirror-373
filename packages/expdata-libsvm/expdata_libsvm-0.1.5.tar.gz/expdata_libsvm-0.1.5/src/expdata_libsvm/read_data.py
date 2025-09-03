import numpy as np
from torch.utils.data import Dataset
import torch
from sklearn.datasets import load_svmlight_file
from torch.utils.data import TensorDataset

class LibSVMDataset(Dataset):
    def __init__(self, data_path, data_name=None):
        X_sparse, y = load_svmlight_file(data_path) # type: ignore
        self.X = torch.from_numpy(X_sparse.toarray()).float() # type: ignore

        # Automatically process labels
        y = np.asarray(y)

        if data_name is not None:
            data_name = data_name.lower()
            
            # Binary classification, with the label -1/1
            if data_name in ["a9a", "w8a", "ijcnn1"]:  
                y = (y > 0).astype(int)  # Convert to 0/1
            
            # Multi-category, labels usually start with 1
            elif data_name in ["letter", "shuttle"]:  
                y = y - 1  # Start with 0
            
        else:
            # Default policy: Try to avoid CrossEntropyLoss errors
            if np.min(y) < 0:  # e.g. [-1, 1]
                y = (y > 0).astype(int)
            elif np.min(y) >= 1:
                y = y - 1

        self.y = torch.from_numpy(y).long()

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# <LibSVMDataset>

# <get_libsvm_data>
def _load_libsvm_dataset(train_path, test_path, data_name):
    train_dataset = LibSVMDataset(train_path, data_name)
    test_dataset = LibSVMDataset(test_path, data_name)
    # libSVM typically features numerical characteristics and does not require image transformation
    transform = None  

    return train_dataset, test_dataset, transform
# <get_libsvm_data>
# <ToTensor>
def get_libsvm_data(train_path, test_path, data_name):
    # laod data
    train_dataset, test_dataset, transform = _load_libsvm_dataset(train_path, test_path, data_name)
    train_data = TensorDataset(train_dataset.X, train_dataset.y)
    test_data = TensorDataset(test_dataset.X, test_dataset.y)

    return train_data, test_data, transform
# <ToTensor>


def main(data_name):
    train_path = f"./exp_data/{data_name}/training_data"
    test_path = f"./exp_data/{data_name}/test_data"

    train_dataset, test_dataset, transform = get_libsvm_data(
                train_path + ".txt", test_path + ".txt", data_name)

    return train_dataset, test_dataset, transform

