import finufft
import numpy as np

def kernel_vect_cpu(x1_gpu, x2_gpu, m, threshold):
  n = x1_gpu.size
  y_gpu = np.ones(n).astype(np.complex128)

  f = finufft.nufft2d1(x1_gpu, x2_gpu, y_gpu, (2*m+1,2*m+1), eps=threshold)/n

  return f

def NUFFT_Y_cpu(x_gpu, y_gpu, m, threshold):
  n = x_gpu.size

  f = finufft.nufft1d1(x_gpu, y_gpu, (2*m+1,), eps=threshold)/n

  return f


def conjugate_gradient_cpu(A_function, b, x0, tol=1e-10, display=True):
    """
    Solves Ax = b using the Conjugate Gradient method.

    Parameters:
        A : function or matrix
            Matrix or function that computes the product Ax.
        b : ndarray
            Right-hand side vector.
        x0 : ndarray
            Initial guess.
        tol : float
            Tolerance for the stopping criterion.
        max_iter : int
            Maximum number of iterations.

    Returns:
        x : ndarray
            Approximate solution to Ax = b.
    """
    m = b.shape[0]

    x = x0
    r = b - A_function(x)
    p = r.copy()
    rs_old = np.linalg.norm(r)**2

    for i in range(3*m-2):#A cause de l'embedding pour avoir un circulant: on inverse Cx qui est de taille 3m
        Ap = A_function(p)
        alpha = rs_old / np.vdot(p, Ap)
        x = x + alpha * p
        r = r - alpha * Ap
        rs_new = np.linalg.norm(r)**2

        if np.sqrt(rs_new) < tol:
          if display:
            print(f"CG converged in {i} iterations.")
          break
        p = r + (rs_new / rs_old) * p
        rs_old = rs_new
    return x

def NUFFT_inv_cpu(x_gpu, f_gpu, threshold):

  y_estimated = finufft.nufft1d2(x_gpu, f_gpu, eps=threshold)

  return y_estimated

def A_function(x, lambda_n, mat):
  return mat@ x + lambda_n * x

def gam_fit(x_gpu, y_gpu, d, m, threshold, lambda_n):
    M = 2*m+1

    cov_y = np.empty(d * M,  dtype=np.complex128)
    for i in range(d):
        cov_y[i*M:(i+1)*M] = NUFFT_Y_cpu(x_gpu[i], y_gpu, m, threshold)

    cov_x = np.empty((d * M, d * M),  dtype=np.complex128)

    for i1 in range(d):
        for i2 in range(i1, d):
            cov_x[i1*M:(i1+1)*M, i2*M:(i2+1)*M] = kernel_vect_cpu(x_gpu[i1], -x_gpu[i2], m, threshold)

            if i1 != i2:
                # Assign Hermitian symmetric block (i2, i1)
                cov_x[i2*M:(i2+1)*M, i1*M:(i1+1)*M] = (cov_x[i1*M:(i1+1)*M, i2*M:(i2+1)*M]).conj().T

    A_funct = lambda x: A_function(x, lambda_n, cov_x)

    hat_theta = conjugate_gradient_cpu(A_funct, cov_y, cov_y, threshold).astype(np.complex128)
    print("Error CG ", np.linalg.norm(A_funct(hat_theta) - cov_y))
    return hat_theta

def gam_predict(x_test, hat_theta, d, m,threshold):
    N_test = x_test.shape[1]
    estimator = np.zeros(N_test)
    for i in range(d):
        estimator += np.real(NUFFT_inv_cpu(x_test[i], hat_theta[(2*m+1)*i:(2*m+1)*(i+1)], threshold))
    return estimator