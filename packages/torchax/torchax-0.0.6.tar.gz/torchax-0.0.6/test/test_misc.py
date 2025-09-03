import unittest
import torch
import torchax


class MiscTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    torchax.enable_globally()

  def test_mixed_tensor_math_with_scalar(self):
    a = torch.tensor(2)
    b = torch.ones((2, 2), device='jax')
    c = a * b
    self.assertTrue(
        torch.allclose(c.cpu(),
                       torch.tensor([[2, 2], [2, 2]], dtype=torch.float32)))


if __name__ == '__main__':
  unittest.main()
