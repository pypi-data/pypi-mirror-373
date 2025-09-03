from torch.utils.data import Dataset, DataLoader
import torch

class PoseDataset(Dataset):
    def __init__(self, pose_data, max_seq_length=30):
        self.data = [self.pad_or_truncate(seq, max_seq_length) for seq in pose_data]

    def pad_or_truncate(self, seq, max_length):
        if seq.shape[0] < max_length:
            pad = torch.zeros(max_length - seq.shape[0], seq.shape[1])
            return torch.cat((seq, pad), dim=0)
        return seq[:max_length]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


pose_data = [torch.randn(45, 34), torch.randn(30, 34), torch.randn(20, 34)]  # Different video lengths
dataset = PoseDataset(pose_data)
dataloader = DataLoader(dataset, batch_size=16, shuffle=True)