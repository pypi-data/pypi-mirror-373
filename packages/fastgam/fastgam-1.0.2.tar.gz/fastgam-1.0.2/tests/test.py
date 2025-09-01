import numpy as np
from fastgam.fast import FastGAM

def test_reg():
    d = 5
    s = 2
    N = 10000

    x_train = np.random.uniform(size=(d, N))
    f_train = np.zeros(N)
    for i in range(d):
        f_train += np.exp(x_train[i]/(i+1)) - 1
    y_train =  (f_train + np.random.normal(size=N)).astype(np.complex128)


    lambda_n=N**(-(2*s)/(2*s+1))
    m = 1+ int(N**(1/(2*s+1))/d)
    threshold = lambda_n/10

    model = FastGAM(d)
    model.fit(x_train, y_train,  lambda_n, m, threshold)

    N_test = 10**4
    x_test = np.random.uniform(size=(d, N_test))
    f_test = np.zeros(N_test)

    for i in range(d):
        f_test += np.exp(x_test[i]/(i+1)) - 1
    y_test =  f_test.astype(np.complex128)

    model.predict(x_test)
    mse = model.mse(y_test)
    assert True

def test_grid_search():
    d = 5
    s = 2
    N = 10000
    N_val = 1000

    lambda_N_list = [10**(-i/10) for i in range(10)]

    x_train = np.random.uniform(size=(d, N))
    f_train = np.zeros(N)
    for i in range(d):
        f_train += np.exp(x_train[i]/(i+1)) - 1
    y_train =  (f_train + np.random.normal(size=N)).astype(np.complex128)

    x_val = np.random.uniform(size=(d, N_val))
    f_val = np.zeros(N_val)
    for i in range(d):
        f_val += np.exp(x_val[i]/(i+1)) - 1
    y_val =  (f_val + np.random.normal(size=N_val)).astype(np.complex128)


    lambda_n=N**(-(2*s)/(2*s+1))
    m = 1+ int(N**(1/(2*s+1))/d)
    threshold = lambda_n/10

    model = FastGAM(d)
    model.fit_grid(x_train, y_train, x_val, y_val,lambda_N_list, m, threshold)

    N_test = 10**4
    x_test = np.random.uniform(size=(d, N_test))
    f_test = np.zeros(N_test)

    for i in range(d):
        f_test += np.exp(x_test[i]/(i+1)) - 1
    y_test =  f_test.astype(np.complex128)

    model.predict(x_test)
    mse = model.mse(y_test)
    assert True
