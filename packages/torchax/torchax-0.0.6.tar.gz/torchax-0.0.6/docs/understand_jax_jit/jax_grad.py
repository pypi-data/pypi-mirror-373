import jax

# jax.grad will take f, return another callable g; such that g computes
# gradient of f. The return value of g, will have the same pytree-shape
# as the first input of f; and by default that it the arg wrt which the gradient is
# taken

# Example


def f(a_dict, b):
  return a_dict['weight'] * b + a_dict['bias']


# a_dict is a dict with 2 keys ['weights', 'bias']
# So

# jax.grad(f)(a_dict, b) will also have 2 keys, 'weights' and 'bias'

# Now, say I only want to compute the gradient of 'weight' and want to skip
# gradient computation of 'bias'. I can accomplish this by making another function
# that has the things I want to diff, and in that format, as first input:


def f2(dict_with_weight, dict_with_bias, b):
  a_dict = copy.copy(dict_with_weight)
  a_dict.update(dict_with_weight)
  res = f(a_dict, b)
  return res


# jax.grad(f2)(dict_weight_weights, dict_with_bias, b) will also have  keys, 'weights' and 'bias'

# OR, if I want to compute gradient of b as well together with gradient of a_dict:


def f3(inputs):
  a, b = inputs
  res = f(a, b)
  return res


# jax.grad(f3)((a_dict, b)) will a 2-tuple, first have 2 keys, 'weights' and 'bias', second is gradient of b

# Creating new functions can route the inputs however you'd like; then
# jax.grad will compute the gradient wrt that.abs

# Call a torch module
# Let m be a stateful module

m = Module(...)

# This is all its weights
states = m.state_dict()

# You call the module usually like this:
result = m(input1, input2)


def functional_m(weights, inputs):
  # weights is state_dict
  # inputs is a tuple of inputs, even if there is only one input to the module
  # The incantation below calls m, with weights explicitly passed in as an argument
  return torch.func.functional_call(m, weights, inputs)


# Now we can do the usual:

from torch_xla2 import interop

gradients = interop.jax_jit(functional_m)(states, (input1, input2, ...))
