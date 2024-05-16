import torch 

x = torch.randn(4, 2, 3)
y = torch.randn(4, 2, 3)
print(x)
print(y)
print(torch.cat([x,y], 1))