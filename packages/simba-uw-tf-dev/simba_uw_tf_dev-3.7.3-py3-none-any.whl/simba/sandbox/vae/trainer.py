import torch
import torch.nn as nn


class ImprovedPoseVAE(nn.Module):
    def __init__(self, input_dim=34, latent_dim=64):
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