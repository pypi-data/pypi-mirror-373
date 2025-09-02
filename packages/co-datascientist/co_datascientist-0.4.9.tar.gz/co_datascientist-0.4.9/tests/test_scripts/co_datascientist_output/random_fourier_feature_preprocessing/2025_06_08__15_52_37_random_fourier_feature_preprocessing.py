import random
import math

# Pure-Python Random Fourier Feature transformer
class RandomFourierFeatures:
    def __init__(self, input_dim, output_dim, sigma=1.0, seed=0):
        random.seed(seed)
        self.input_dim = input_dim
        self.output_dim = output_dim
        # sample Gaussian weights
        self.W = [ [random.gauss(0, 1) / sigma for _ in range(output_dim)]
                   for _ in range(input_dim) ]   # shape (input_dim, output_dim)
        # sample biases uniform [0, 2pi)
        self.b = [random.random() * 2 * math.pi for _ in range(output_dim)]
        # scale factor
        self.scale = math.sqrt(2.0 / output_dim)

    def transform(self, X):
        # X: list of samples, each sample is a list of length input_dim
        phi = []
        for x in X:
            # compute W^T x + b
            z = []
            for j in range(self.output_dim):
                s = 0.0
                for i in range(self.input_dim):
                    s += x[i] * self.W[i][j]
                s += self.b[j]
                z.append(s)
            # apply scale and cosine
            phi.append([self.scale * math.cos(z_j) for z_j in z])
        return phi

# Activation and loss

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))

def bce_loss(preds, labels, eps=1e-8):
    # preds, labels: lists of floats
    n = len(preds)
    total = 0.0
    for p, y in zip(preds, labels):
        p_clamped = min(max(p, eps), 1 - eps)
        total += - (y * math.log(p_clamped) + (1 - y) * math.log(1 - p_clamped))
    return total / n

if __name__ == "__main__":
    # XOR dataset
    inputs = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
    outputs = [0.0, 1.0, 1.0, 0.0]

    # Hyperparameters
    D = 256    # RFF feature dimension
    H = 4      # hidden units
    sigma = 1.0
    lr = 0.1
    min_lr = 1e-4
    factor = 0.5
    reduce_patience_limit = 3
    early_stop_limit = 5
    max_epochs = 50

    # Initialize RFF
    rff = RandomFourierFeatures(input_dim=2, output_dim=D, sigma=sigma, seed=0)

    # Initialize MLP parameters
    random.seed(1)
    # W1: D x H, b1: H
    W1 = [ [random.gauss(0, 1) * 0.01 for _ in range(H)] for _ in range(D) ]
    b1 = [0.0 for _ in range(H)]
    # W2: H, b2: scalar
    W2 = [random.gauss(0, 1) * 0.01 for _ in range(H)]
    b2 = 0.0

    # Scheduler & early stopping trackers
    best_loss = float('inf')
    reduce_patience = 0
    early_patience = 0

    # Training loop
    for epoch in range(1, max_epochs + 1):
        # Forward
        phi = rff.transform(inputs)  # list of length 4, each length D
        # Layer 1
        z1 = []  # pre-activation
        for x_phi in phi:
            z1.append([ sum(x_phi[i] * W1[i][h] for i in range(D)) + b1[h] for h in range(H) ])
        # ReLU
        a1 = [[max(0.0, z1[j][h]) for h in range(H)] for j in range(len(z1))]
        # Layer 2
        z2 = [ sum(a1[j][h] * W2[h] for h in range(H)) + b2 for j in range(len(a1)) ]
        preds = [ sigmoid(z2_j) for z2_j in z2 ]

        # Loss
        loss = bce_loss(preds, outputs)

        # Backward
        m = len(inputs)
        dloss = [ (preds[j] - outputs[j]) / m for j in range(m) ]  # dL/dz2
        # Gradients W2 and b2
        dW2 = [ sum(a1[j][h] * dloss[j] for j in range(m)) for h in range(H) ]
        db2 = sum(dloss)
        # Gradients through ReLU
        dz1 = []  # shape m x H
        for j in range(m):
            row = []
            for h in range(H):
                da1 = dloss[j] * W2[h]
                row.append(da1 if z1[j][h] > 0 else 0.0)
            dz1.append(row)
        # Gradients W1 and b1
        dW1 = [ [ sum(phi[j][i] * dz1[j][h] for j in range(m)) for h in range(H) ] for i in range(D) ]
        db1 = [ sum(dz1[j][h] for j in range(m)) for h in range(H) ]

        # Gradient clipping
        total_norm_sq = 0.0
        for i in range(D):
            for h in range(H): total_norm_sq += dW1[i][h]**2
        for h in range(H): total_norm_sq += db1[h]**2 + dW2[h]**2
        total_norm_sq += db2**2
        total_norm = math.sqrt(total_norm_sq)
        if total_norm > 1.0:
            coef = 1.0 / total_norm
            for i in range(D):
                for h in range(H): dW1[i][h] *= coef
            for h in range(H):
                db1[h] *= coef
                dW2[h] *= coef
            db2 *= coef

        # Parameter updates
        for i in range(D):
            for h in range(H):
                W1[i][h] -= lr * dW1[i][h]
        for h in range(H):
            b1[h] -= lr * db1[h]
            W2[h] -= lr * dW2[h]
        b2 -= lr * db2

        # LR scheduling & early stopping
        if loss + 1e-6 < best_loss:
            best_loss = loss
            reduce_patience = 0
            early_patience = 0
        else:
            reduce_patience += 1
            early_patience += 1
        if reduce_patience >= reduce_patience_limit:
            lr = max(lr * factor, min_lr)
            reduce_patience = 0
        if early_patience >= early_stop_limit:
            print(f"Early stopping at epoch {epoch}")
            break

        print(f"Epoch {epoch}, Loss: {loss:.6f}, LR: {lr:.6f}")

    # Final evaluation
    phi = rff.transform(inputs)
    z1 = [[ sum(phi[j][i] * W1[i][h] for i in range(D)) + b1[h] for h in range(H)] for j in range(len(phi))]
    a1 = [[max(0.0, z1[j][h]) for h in range(H)] for j in range(len(z1))]
    z2 = [ sum(a1[j][h] * W2[h] for h in range(H)) + b2 for j in range(len(a1)) ]
    preds = [ sigmoid(z2_j) for z2_j in z2 ]
    for inp, p in zip(inputs, preds):
        print(f"{inp[0]} | {inp[1]} | {p:.4f}")

# Debugging: Removed unavailable numpy/torch imports, reimplemented RFF and MLP training in pure Python with math and random. Ensured forward/backward passes, gradient clipping, LR scheduling, and early stopping work end-to-end.