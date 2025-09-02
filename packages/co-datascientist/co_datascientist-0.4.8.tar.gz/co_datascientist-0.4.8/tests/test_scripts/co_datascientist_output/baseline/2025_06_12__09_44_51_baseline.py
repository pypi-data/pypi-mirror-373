import torch
import torch.nn as nn

model = nn.Sequential(nn.Linear(2, 4), nn.ReLU(), nn.Linear(4, 1), nn.Sigmoid())
inputs = torch.tensor([[0., 0.], [0., 1.], [1., 0.], [1., 1.]])
outputs = torch.tensor([[0.], [1.], [1.], [0.]])
optimizer = torch.optim.Adam(model.parameters(), lr=0.1)

for _ in range(10):
    pred = model(inputs)
    loss = nn.BCELoss()(pred, outputs)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

predictions = model(inputs)
for i, pred in enumerate(predictions):
    print(f"{inputs[i][0]} | {inputs[i][1]} | {pred.item():.4f}")
