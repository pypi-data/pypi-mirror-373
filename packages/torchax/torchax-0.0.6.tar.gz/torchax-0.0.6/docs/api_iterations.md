
## always create a new environment, use it, discard it?

```
env = torchax.env()
with env.with_prng_key(): // or extra inputs
  do stuff

# discard env

with env.output_shape
with env.manual axis ...

env.call_torch_func(f, args, kwargs)

functions should take in env
functions in torch will get env from threadlocal property
```
env.call_stateless_torch_func()?

tx = torchax.initialize(...)
```