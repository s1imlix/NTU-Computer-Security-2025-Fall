import numpy as np
from math import tanh, cos, sinh, exp
from scipy.optimize import minimize

INPUT_SIZE = 15
HIDDEN1_SIZE = 8
HIDDEN2_SIZE = 6
OUTPUT_SIZE = 1

TARGET = 0.7331337420

XOR_KEYS = np.array([
    0x42, 0x13, 0x37, 0x99, 0x21, 0x88, 0x45, 0x67,
    0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE
], dtype=np.uint8)

W1 = np.array([
    [0.523, -0.891, 0.234, 0.667, -0.445, 0.789, -0.123, 0.456],
    [-0.334,  0.778, -0.556, 0.223, 0.889, -0.667, 0.445, -0.221],
    [0.667, -0.234, 0.891, -0.445, 0.123, 0.556, -0.789, 0.334],
    [-0.778, 0.445, -0.223, 0.889, -0.556, 0.234, 0.667, -0.891],
    [0.123, -0.667, 0.889, -0.334, 0.556, -0.778, 0.445, 0.223],
    [-0.891, 0.556, -0.445, 0.778, -0.223, 0.334, -0.667, 0.889],
    [0.445, -0.123, 0.667, -0.889, 0.334, -0.556, 0.778, -0.234],
    [-0.556, 0.889, -0.334, 0.445, -0.778, 0.667, -0.223, 0.123],
    [0.778, -0.445, 0.556, -0.667, 0.223, -0.889, 0.334, -0.445],
    [-0.223, 0.667, -0.778, 0.334, -0.445, 0.556, -0.889, 0.778],
    [0.889, -0.334, 0.445, -0.556, 0.667, -0.223, 0.123, -0.667],
    [-0.445, 0.223, -0.889, 0.778, -0.334, 0.445, -0.556, 0.889],
    [0.334, -0.778, 0.223, -0.445, 0.889, -0.667, 0.556, -0.123],
    [-0.667, 0.889, -0.445, 0.223, -0.556, 0.778, -0.334, 0.667],
    [0.556, -0.223, 0.778, -0.889, 0.445, -0.334, 0.889, -0.556]
])

B1 = np.array([0.1, -0.2, 0.3, -0.15, 0.25, -0.35, 0.18, -0.28])

W2 = np.array([
    [0.712, -0.534, 0.823, -0.445, 0.667, -0.389],
    [-0.623, 0.889, -0.456, 0.734, -0.567, 0.445],
    [0.534, -0.712, 0.389, -0.823, 0.456, -0.667],
    [-0.889, 0.456, -0.734, 0.567, -0.623, 0.823],
    [0.445, -0.667, 0.823, -0.389, 0.712, -0.534],
    [-0.734, 0.623, -0.567, 0.889, -0.456, 0.389],
    [0.667, -0.389, 0.534, -0.712, 0.623, -0.823],
    [-0.456, 0.823, -0.667, 0.445, -0.889, 0.734]
])

B2 = np.array([0.05, -0.12, 0.18, -0.08, 0.22, -0.16])

W3 = np.array([
    [0.923],
    [-0.812],
    [0.745],
    [-0.634],
    [0.856],
    [-0.723]
])

B3 = np.array([0.42])


def xor_activate(x, key):
    lv = int(x * 1_000_000)
    lv ^= int(key)
    return lv / 1_000_000.0

def forward_pass(inputs):
    # ---- Layer 1 ----
    h1 = np.zeros(HIDDEN1_SIZE)
    for j in range(HIDDEN1_SIZE):
        s = 0.0
        for i in range(INPUT_SIZE):
            if i % 4 == 0:
                act = xor_activate(inputs[i], XOR_KEYS[i])
            elif i % 4 == 1:
                act = np.tanh(inputs[i])             # FIXED
            elif i % 4 == 2:
                act = np.cos(inputs[i])              # FIXED
            else:
                act = np.sinh(inputs[i] / 10.0)      # FIXED
            s += act * W1[i][j]
        h1[j] = np.tanh(s + B1[j])                   # FIXED

    # ---- Layer 2 ----
    h2 = np.tanh(h1 @ W2 + B2)                        # FIXED

    # ---- Output Layer ----
    out = h2 @ W3 + B3[0]
    return 1.0 / (1.0 + np.exp(-out))


# Loss function for optimizer
def loss(x):
    return abs(forward_pass(x) - TARGET)


# Initial guess: all zeros
x0 = np.zeros(INPUT_SIZE)

print("Running optimization, please wait...")

res = minimize(loss, x0, method="Nelder-Mead", options={"maxiter": 200000, "fatol": 1e-12})

print("\n=== SOLUTION FOUND ===")
print("Inputs (15 numbers):")
print(res.x)

print("\nNetwork output:")
print(forward_pass(res.x))

