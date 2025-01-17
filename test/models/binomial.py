from typing import Union
from scipy import stats as sst
from scipy.special import logit, expit as inv_logit, log1p
import numpy as np
import numpy.typing as npt


class Binomial:
    """
    Binomial model with a conjugate beta prior.

    The posterior has a closed form beta distribution.
    """

    def __init__(
        self,
        alpha: float,
        beta: float,
        x: int,
        N: int,
        seed: Union[None, int, np.random.BitGenerator, np.random.Generator] = None,
    ) -> None:
        self.alpha = alpha
        self.beta = beta
        self.x = x
        self.N = N
        self._rng = np.random.default_rng(seed)
        self._posterior = sst.beta(alpha + x, beta + N - x)

    def dims(self) -> int:
        return 1

    def log_density(self, params_unc: npt.NDArray[np.float64]) -> float:
        """
        This model's joint density is factored as the product of
        the prior density and the likelihood for testing with
        samplers that require that (e.g., SMC).

        On the log scale, this means adding the log_prior and log_likelihood terms.
        """
        return self.log_likelihood(params_unc) + self.log_prior(params_unc)

    def log_prior(self, params_unc: npt.NDArray[np.float64]) -> float:
        theta: float = inv_logit(params_unc[0])
        jac_adjust: float = np.log(theta) + log1p(-theta)
        prior: float = sst.beta.logpdf(theta, self.alpha, self.beta)
        return prior + jac_adjust

    def log_likelihood(self, params_unc: npt.NDArray[np.float64]) -> float:
        theta = inv_logit(params_unc[0])
        return sst.binom.logpmf(self.x, self.N, theta)  # type: ignore # scipy is not typed

    def initial_state(self, _: int) -> npt.NDArray[np.float64]:
        return logit(self._rng.beta(self.alpha, self.beta, size=1))  # type: ignore # scipy is not typed

    def log_density_gradient(
        self, params_unc: npt.NDArray[np.float64]
    ) -> tuple[float, npt.NDArray[np.float64]]:
        # use finite diffs for now
        epsilon = 0.000001

        lp = self.log_density(params_unc)
        lp_plus_e = self.log_density(params_unc + epsilon)
        return lp, np.array([(lp - lp_plus_e) / epsilon])

    def constrain_draws(
        self, draws: npt.NDArray[np.float64]
    ) -> npt.NDArray[np.float64]:
        return inv_logit(draws)  # type: ignore # scipy is not typed

    def posterior_mean(self) -> float:
        return self._posterior.mean()  # type: ignore # scipy is not typed

    def posterior_variance(self) -> float:
        return self._posterior.var()  # type: ignore # scipy is not typed
