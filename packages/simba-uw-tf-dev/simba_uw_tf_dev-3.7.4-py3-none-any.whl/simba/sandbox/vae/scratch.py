from torch.utils.data import Dataset, DataLoader
import torch
import torch.nn as nn
from torch import optim
import numpy as np
from simba.utils.read_write import read_df
from torch.utils.data import DataLoader, TensorDataset
import torch.nn.functional as F


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


class ImprovedPoseVAE(nn.Module):
    def __init__(self, input_dim=18, latent_dim=64):
        super().__init__()

        # Encoder
        self.encoder = nn.LSTM(input_dim, 128, batch_first=True, bidirectional=True)
        self.fc_mu = nn.Linear(256, latent_dim)
        self.fc_logvar = nn.Linear(256, latent_dim)

        # Decoder
        self.decoder_input = nn.Linear(latent_dim, 256)
        self.decoder = nn.LSTM(256, input_dim, batch_first=True)

    def encode(self, x):
        encoded, _ = self.encoder(x)
        encoded = encoded[:, -1, :]  # Last time step
        mu = self.fc_mu(encoded)
        logvar = self.fc_logvar(encoded)
        return mu, logvar

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z, seq_length):
        z = z.unsqueeze(1).repeat(1, seq_length, 1)
        decoder_input = self.decoder_input(z)
        decoded, _ = self.decoder(decoder_input)
        return decoded

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        return self.decode(z, x.size(1)), mu, logvar


def vae_loss(recon_x, x, mu, logvar):
    recon_loss = F.mse_loss(recon_x, x, reduction='sum')
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    return recon_loss + kl_loss


df = read_df(file_path='/mnt/c/troubleshooting/mitra/project_folder/csv/outlier_corrected_movement_location/501_MA142_Gi_Saline_0513.csv', file_type='csv')
data = df.drop(df.columns[2::3], axis=1).values.reshape(len(df), -1, 2).astype(np.int32)
data_tensor = torch.tensor(data, dtype=torch.float32)
data_loader = DataLoader(TensorDataset(data_tensor), batch_size=120, shuffle=True)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = ImprovedPoseVAE(input_dim=2, latent_dim=64).cuda()
optimizer = optim.Adam(model.parameters(), lr=1e-4)

def train(model, data_loader, epochs=900):
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for batch in data_loader:
            batch = batch[0].cuda()
            optimizer.zero_grad()
            recon_batch, mu, logvar = model(batch)
            loss = vae_loss(recon_batch, batch, mu, logvar)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss / len(data_loader.dataset):.4f}")

            #break
        #
        #
        #
        #
        #
        #
        #
        #




train(model, data_loader)

#
#     print(f"Epoch {epoch + 1}, Loss: {total_loss / len(dataloader):.4f}")
#
#
# def generate_new_poses(model, num_samples=10, latent_dim=64, seq_length=30):
#     model.eval()
#     with torch.no_grad():
#         z = torch.randn(num_samples, latent_dim).to(device)
#         new_poses = model.decode(z, seq_length)
#     return new_poses
#
# # Generate 10 new pose sequences
# new_pose_data = generate_new_poses(model, num_samples=10)
# print(new_pose_data.shape)  # (10, 30, 34)