from typing import Protocol, Sequence, Callable, Mapping
import jax.numpy as jnp
Array = jnp.ndarray

class ThermoProvider(Protocol):
    def species(self) -> Sequence[str]: ...
    def stoichiometry_A(self) -> Array: ...              # shape: (E, K)
    def elements_b(self) -> Array: ...                   # shape: (E,)
    def chemical_potential_fn(self) -> Callable[[float, float, Array], Array]:
        """g_k(T, ln_p, n_k) or typically g_k(T) if p,n separated in your formalism"""
        ...
    def hvector_fn(self) -> Callable[[float], Array]: ...# hvector(T)
    def metadata(self) -> Mapping[str, str]: ...
