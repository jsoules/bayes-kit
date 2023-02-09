from test.models.std_normal import StdNormal
from test.models.beta_binomial import BetaBinom
from bayes_kit.mala import MALA
import numpy as np


def test_mala_std_normal() -> None:
    # init with draw from posterior
    init = np.random.normal(loc=0, scale=1, size=[1])
    model = StdNormal()
    mala = MALA(model, 0.3, init)

    M = 10000
    draws = np.array([mala.sample()[0] for _ in range(M)])

    mean = draws.mean(axis=0)
    var = draws.var(axis=0, ddof=1)

    np.testing.assert_allclose(mean, model.posterior_mean(), atol=0.1)
    np.testing.assert_allclose(var, model.posterior_variance(), atol=0.1)


def test_mala_beta_binom() -> None:
    model = BetaBinom()
    M = 1000
    mala = MALA(model, 0.005, init=np.array([0.2]))

    draws = np.array([mala.sample()[0] for _ in range(M)])

    mean = draws[100:].mean(axis=0)
    var = draws[100:].var(axis=0, ddof=1)

    print(f"{draws[1:10]=}")
    print(f"{mean=}  {var=}")

    np.testing.assert_allclose(mean, model.posterior_mean(), atol=0.05)
    np.testing.assert_allclose(var, model.posterior_variance(), atol=0.008)


def test_mala_repr() -> None:
    init = np.random.normal(loc=0, scale=1, size=[1])
    model = StdNormal()

    mala_1 = MALA(model, 0.3, init, seed=123)
    mala_2 = MALA(model, 0.3, init, seed=123)
    mala_3 = MALA(model, 0.3, init, seed=321)

    M = 25
    draws_1 = np.array([mala_1.sample()[0] for _ in range(M)])
    draws_2 = np.array([mala_2.sample()[0] for _ in range(M)])
    draws_3 = np.array([mala_3.sample()[0] for _ in range(M)])

    np.testing.assert_array_equal(draws_1, draws_2)
    # Confirm that different results occur with different seeds
    with np.testing.assert_raises(AssertionError):
        np.testing.assert_array_equal(draws_1, draws_3)
