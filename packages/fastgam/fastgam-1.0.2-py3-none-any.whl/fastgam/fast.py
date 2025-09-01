from fastgam.additive import gam_fit, gam_predict, grid_search
import numpy as np


class FastGAM():
    def __init__(self, d):
        """
        Initializes the PikernelModel.

        Args:
            dimension (int): 1 for ODEs, 2 for PDEs.
            L (float): Domain size.
            PDE (callable): Differential operator (ODE or PDE) as a function.
            device (torch.device): Torch device to perform computations.
            m (int): Number of Fourier features.
            lambda_n (float): Regularization parameter for kernel norm.
            mu_n (float): Regularization parameter for enforcing physics.
            n (int): Number of training points.
            domain (str, optional): Domain type ('square' or others). Defaults to "square". Not needed in dimension 1.
        """
        self.d = d

        

    def fit(self, x_train, y_train,  lambda_n, m = 10, threshold = 1e-7):
        self.m = m
        self.lambda_n = lambda_n
        self.threshold = threshold

        self.hat_theta = gam_fit(x_train, y_train, self.d, m, threshold, lambda_n)
        return self.hat_theta

    def fit_grid(self, x_train, y_train, x_val, y_val,lambda_N_list, m = 10, threshold = 1e-7):
        self.m = m
        self.threshold = threshold
        self.hat_theta = grid_search(x_train, y_train, x_val, y_val, self.d, m, threshold, lambda_N_list)
        return

    def predict(self, x_test):
        self.estimator = gam_predict(x_test, self.hat_theta, self.d, self.m, self.threshold)
        return self.estimator

    def mse(self, y_test):
        error = self.estimator-y_test
        mse = np.mean(np.square(np.abs(error)))
        return mse
    