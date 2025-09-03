import torch
import torch.optim as optim



device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ImprovedPoseVAE().to(device)
optimizer = optim.Adam(model.parameters(), lr=1e-3)

for epoch in range(100):
    model.train()
    total_loss = 0

    for batch in dataloader:
        batch = batch.to(device)
        optimizer.zero_grad()

        recon, mu, logvar = model(batch)
        loss = loss_function(recon, batch, mu, logvar)

        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoc h +1}, Loss: {total_loss / len(dataloader):.4f}")