# eng1014.py
# ENG1014 Numerical Methods Module
# Authors: ENG1014 Team
# Last modified: 19/04/2025

import numpy as np

# Good Programming Practices
def sind(x):
    """
    Calculates the trigonometric sine, elementwise, for inputs in degrees.

    Args:
        x: a value or an array of numbers in degrees

    Returns:
        y: trigonometric sine of x
    """
    y = np.sin(np.deg2rad(x))
    
    return y

def cosd(x):
    """
    Calculates the trigonometric cosine, elementwise, for inputs in degrees.

    Args:
        x: a value or an array of numbers in degrees

    Returns:
        y: trigonometric cosine of x
    """
    y = np.cos(np.deg2rad(x))
    
    return y

def tand(x):
    """
    Calculates the trigonometric tangent, elementwise, for inputs in degrees.

    Args:
        x: a value or an array of numbers in degrees

    Returns:
        y: trigonometric sine of x
    """
    y = np.sin(np.deg2rad(x))
    
    return y


# Fitting Curves to Data
def linreg(x, y):
    """
    Performs linear regression on datasets x and y.

    Args:
        x: An array of numbers. Linear independent dataset. 
        y: An array of numbers. Linear dependent dataset.

    Returns:
        a0: Constant in y = a1*x + a0
        a1: Gradient in y = a1*x + a0
        r2: Coefficient of determination
    """
    
    # determining best regression coefficients
    n = len(x)
    Sx = sum(x)
    Sy = sum(y)
    Sxx = sum(x**2)
    Sxy = sum(x*y)
    a1 = (n*Sxy - Sx*Sy)/(n*Sxx - Sx**2)
    a0 = np.mean(y) - a1*np.mean(x)

    # determining r^2 value
    St = sum((y - np.mean(y))**2)
    Sr = sum((y - a0 - a1*x)**2)
    r2 = (St - Sr)/St

    return a0, a1, r2

# Systems of Linear Equations
def naive_gauss(A, b):
    """
    Uses naive Gaussian elimination to solve a system of linear equations represented
    as the matrix equation Ax=b.

    Limitation: will not work when the system has infinite or no solutions.

    Args:
        A: A 2D array containing the coefficients
        b: A 1D array or 2D row/column vector containing the solutions

    Returns:
        x: A 1D array containing the unknowns
    """
    # INPUT VALIDATION
    # check A has 2 dimensions
    ndim_A = np.ndim(A)
    if ndim_A != 2:
        raise ValueError("Error: A must be 2D")

    # check A has the same number of rows and columns
    m_A, n_A = np.shape(A)
    if m_A != n_A:
        raise ValueError("Error: A must be a square matrix")

    # check b has 1 or 2 dimensions
    ndim_b = np.ndim(b)
    if ndim_b != 1 and ndim_b != 2:
        raise ValueError("Error: b must be 1D or a 2D row/column vector")

    # if b has 2 dimensions, b is a row/column vector
    if ndim_b == 2: 
        m_b, n_b = np.shape(b)
        if m_b != 1 and n_b != 1:
            raise ValueError("Error: b must be 1D or a 2D row/column vector")
    
    # check b has the same number of elements as there are rows/columns in A
    p = np.size(b)
    if p != n_A:
        raise ValueError("Error: b must have the same number of elements as there are rows/columns in A")

    # START ALGORITHM
    # reshape b into a px1 2D array
    b_col = np.reshape(b, (p,1))
    # create Aug by concatenating A and b_col and converting the data type to floats
    Aug = np.astype(np.hstack([A,b_col]), float)
    
    # pre-allocate x as a 1D array of 0s with a data type of floats
    x = np.zeros(n_A, dtype = float)

    # FORWARD ELIMINATION
    # loop through columns from the first to the second last
    for c in range(n_A-1):

        # loop through rows from first row below the main diagonal to the last
        for r in range(c+1,n_A):
            # determine normalisation factor
            factor = Aug[r,c]/Aug[c,c]
    
            # replace row r with row r – factor × row c
            Aug[r,:] -= factor*Aug[c,:]

    # BACK SUBSTITUTION
    # solve the last row
    x[n_A-1] = Aug[n_A-1,-1]/Aug[n_A-1,n_A-1]
    
    # loop through rows from second last row to the first
    for r in range(n_A-2,-1,-1):
        # determine value of x_r
        x[r] = (Aug[r,-1] - Aug[r,r+1:n_A] @ x[r+1:n_A]) / Aug[r,r]
    
    return x

def gauss(A, b):
    """
    Uses Gaussian elimination and partial pivoting to solve a system of 
    linear equations represented as the matrix equation Ax=b.

    Limitations: 
    1. will not work when the system has infinite or no solutions.

    Args:
        A: A 2D array containing the coefficients
        b: A 1D array or 2D row/column vector containing the solutions

    Returns:
        x: A 1D array containing the unknowns
    """
    # INPUT VALIDATION
    # check A has 2 dimensions
    ndim_A = np.ndim(A)
    if ndim_A != 2:
        raise ValueError("Error: A must be 2D")

    # check A has the same number of rows and columns
    m_A, n_A = np.shape(A)
    if m_A != n_A:
        raise ValueError("Error: A must be a square matrix")

    # check b has 1 or 2 dimensions
    ndim_b = np.ndim(b)
    if ndim_b != 1 and ndim_b != 2:
        raise ValueError("Error: b must be 1D or a 2D row/column vector")

    # if b has 2 dimensions, b is a row/column vector
    if ndim_b == 2: 
        m_b, n_b = np.shape(b)
        if m_b != 1 and n_b != 1:
            raise ValueError("Error: b must be 1D or a 2D row/column vector")
    
    # check b has the same number of elements as there are rows/columns in A
    p = np.size(b)
    if p != n_A:
        raise ValueError("Error: b must have the same number of elements as there are rows/columns in A")

    # reshape b into a px1 2D array
    b_col = np.reshape(b, (p,1))
    # create Aug by concatenating A and b_col and converting the data type to floats
    Aug = np.astype(np.hstack([A,b_col]), float)
    
    # pre-allocate x as a 1D array of 0s with a data type of floats
    x = np.zeros(n_A, dtype = float)

    # FORWARD ELIMINATION
    # loop through columns from the first to the second last
    for c in range(n_A-1):
        # PARTIAL PIVOTING
        # check if pivot is 0
        if Aug[c,c] == 0:
            # find index of max element below pivot
            index = np.argmax(np.abs(Aug[c+1:n_A,c]))

            # adjust index for A instead of subset
            rowswap = c + index + 1

            # swap rows
            Aug[[c,rowswap],:] = Aug[[rowswap,c],:]

        # loop through rows from first row below the main diagonal to the last
        for r in range(c+1,n_A):
            # determine normalisation factor
            factor = Aug[r,c]/Aug[c,c]
    
            # replace row r with row r – factor × row c
            Aug[r,:] -= factor*Aug[c,:]

    # BACK SUBSTITUTION
    # solve the last row
    x[n_A-1] = Aug[n_A-1,-1]/Aug[n_A-1,n_A-1]
    
    # loop through rows from second last row to the first
    for r in range(n_A-2,-1,-1):
        # determine value of x_r
        x[r] = (Aug[r,-1] - Aug[r,r+1:n_A]@x[r+1:n_A]) / Aug[r,r]
    
    return x
    

# Root Finding
def bisection(f, xl, xu, precision):
    """
    Finds a root of the function f(x) within the interval [xl, xu] using the bisection method.

    Args:
        f: Lambda function to be solved
        xl: Lower bound of the bracket
        xu: Upper bound by the bracket
        precision: Stopping criteria determined by the user
    
    Returns:
        xr: Root of the function f(x)
        num_iter: Number of iterations taken to find the root
    """
    # INPUT VALIDATION
    # check if f(xl) and f(xu) have different signs
    if f(xl) * f(xu) > 0:
        raise ValueError("Inappropriate brackets for closed methods")

    # BISECTION ALGORITHM
    xr = (xu + xl)/2 # estimate first guess of xr
 
    num_iter = 1 # initialise iteration counter

    # check if f(xr) is close enough to zero
    while abs(f(xr)) > precision:
        # reset interval brackets
        if f(xl) * f(xr) > 0:
            xl = xr
        else:
            xu = xr
               
        xr = (xl + xu) / 2 # estimate next guess of xr
        num_iter += 1 # increment iteration counter

    # return xr as the root and iteration counter
    return xr, num_iter

def falseposition(f, xl, xu, precision):
    """
    Finds a root of the function f(x) within the interval [xl, xu] using the false position method.

    Args:
        f: Lambda function to be solved
        xl: Lower bound of the bracket
        xu: Upper bound by the bracket
        precision: Stopping criteria determined by the user
    
    Returns:
        xr: Root of the function f(x)
        num_iter: Number of iterations taken to find the root
    """
    # INPUT VALIDATION
    # check if f(xl) and f(xu) have different signs
    if f(xl) * f(xu) > 0:
        raise ValueError("Inappropriate brackets for closed methods")

    # FALSE POSITION ALGORITHM
    xr = (f(xu)*xl - f(xl)*xu) / (f(xu) - f(xl)) # estimate first guess of xr
    num_iter = 1 # initialise iteration counter

    # check if f(xr) is close enough to zero
    while abs(f(xr)) > precision:
        # reset interval brackets
        if f(xl) * f(xr) > 0:
            xl = xr
        else:
            xu = xr
               
        xr = (f(xu)*xl - f(xl)*xu)/(f(xu) - f(xl)) # estimate next guess of xr
        num_iter += 1 # increment iteration counter

    # return xr as the root and iteration counter
    return xr, num_iter

def newraph(f, df, xi, precision):
    """
    Finds a root of the function f(x) using the Newton-Raphson method.

    Args:
        f: Lambda function to be solved
        df: Derivative of the function to be solved
        xi: Initial guess for the root
        precision: Stopping criteria determined by the user
    
    Returns:
        xi1: Root of the function f(x)
        num_iter: Number of iterations taken to find the root
    """  
    xi1 = xi - f(xi) / df(xi) # estimate first guess of xi1
    num_iter = 1 # initialise iteration count

    # check if f(xi1) is close enough to zero
    while abs(f(xi1)) > precision:
        xi = xi1 # update guess
        xi1 = xi - f(xi) / df(xi) # estimate next guess of xi1    
        num_iter += 1 # increment iteration

    # return xi1 as the root and iteration counter
    return xi1, num_iter

def secant(f, xi, xi_1, precision):
    """
    Finds a root of the function f(x) using the secant method.

    Args:
        f: Lambda function to be solved
        xi: Initial guess for the root
        xi_1: Previous initial guess
        precision: Stopping criteria determined by the user
    
    Returns:
        xi1: Root of the function f(x)
        num_iter: Number of iterations taken to find the root
    """
    xi1 = xi - f(xi)*(xi - xi_1) / (f(xi) - f(xi_1)) # estimate first guess of xi1
    num_iter = 1 # initialise iteration count

    # check if f(xi1) is close enough to zero
    while abs(f(xi1)) > precision:
        xi_1, xi = xi, xi1 # update guesses
        xi1 = xi - f(xi)*(xi - xi_1) / (f(xi) - f(xi_1)) # estimate next guess of xi1    
        num_iter += 1 # increment iteration

    # return xi1 as the root and iteration counter
    return xi1, num_iter

def modisecant(f, xi, pert, precision):
    """
    Finds a root of the function f(x) using the modified secant method.

    Args:
        f: Lambda function to be solved
        xi: Initial guess for the root
        pert: Pertubation (small increment to xi)
        precision: Stopping criteria determined by the user
    
    Returns:
        xi1: Root of the function f(x)
        num_iter: Number of iterations taken to find the root
    """  
    xi1 = xi - pert*f(xi) / (f(xi + pert) - f(xi)) # estimate first guess of xi1
    num_iter = 1 # initialise iteration count

    # check if f(xi1) is close enough to zero
    while abs(f(xi1)) > precision:
        xi = xi1 # update guess
        xi1 = xi - pert*f(xi) / (f(xi + pert) - f(xi)) # estimate next guess of xi1
        num_iter +=  1 # increment iteration

    # return xi1 as the root and iteration counter
    return xi1, num_iter

    
# Numerical Integration
def comp_trap(f, a, b, n):
    """
    Calculates an estimation of the integral of f(x) using the composite trapezoidal rule for uniform segments.

    Args:
        f: Lambda function of f(x)
        a: Lower limit of the integral
        b: Upper limit of the integral
        n: Number of points 

    Returns:
        I: Estimated integral
    """
    # INPUT VALIDATION
    # check if integral limits are valid
    if a == b:
        raise ValueError("Invalid integral limits")

    # check if n is a valid number of points
    if n < 2:
        raise ValueError("Invalid number of points")

    # COMP TRAP ALGORITHM
    x = np.linspace(a, b, n) # create 1D array for x
    y = f(x) # create 1D array for y
    h = x[1] - x[0] # determine width

    # calculate integral estimate
    middle_sum = np.sum(y[1:-1])
    I = h/2 * (y[0] + 2*middle_sum + y[-1])

    return I

def comp_trap_vector(x, y):
    """
    Calculates an estimation of the integral of {(xi,yi)} using the composite trapezoidal rule for non-uniform segments.

    Args:
        x: 1D array of discrete xi observations
        y: 1D array of discrete yi observations

    Returns:
        I: Estimated integral
    """
    # INPUT VALIDATION
    # check if x and y have a valid number of dimensions
    if np.ndim(x) != 1:
        raise ValueError("Invalid number of dimensions of x")
    if np.ndim(y) != 1:
        raise ValueError("Invalid number of dimensions of y")

    # check if x and y have the same number of points
    n = np.size(x)
    if n != np.size(y):
        raise ValueError("x and y must have the same number of points")
    
    # check if x has a valid number of points
    if n < 2:
        raise ValueError("Invalid number of points in x and y")

    # COMP TRAP ALGORITHM  
    h_i = x[1:] - x[:-1] # determine all widths
    bases_i = y[1:] + y[:-1] # determine all bases
    I = np.sum(h_i/2 * bases_i) # calculate integral estimate
    
    return I
    
def comp_simp13(f, a, b, n):
    """
    Calculates an estimation of the integral of f(x) using the composite Simpson's 1/3 rule.
    
    Args:
        f: Lambda function of f(x) 
        a: Lower limit of the integral
        b: Upper limit of the integral
        n: Number of points 

    Returns:
        I: Estimated integral
    """
    # INPUT VALIDATION
    # check if integral limits are valid
    if a == b:
        raise ValueError("Invalid integral limits")

    # check if n is a valid number of points
    if n < 3 or n % 2 == 0:
        raise ValueError("Invalid number of points")
    
    # COMP SIMP 1/3 ALGORITHM
    x = np.linspace(a, b, n) # create 1D array for x
    y = f(x) # create 1D array for y
    h = x[1] - x[0] # determine width

    # calculate integral estimate
    even_sum = 4 * np.sum(y[1:-1:2])
    odd_sum = 2 * np.sum(y[2:-1:2])
    I = h/3 * (y[0] + even_sum + odd_sum + y[-1])

    return I
    
def comp_simp13_vector(x,y):
    """
    Calculates an estimation of the integral of {(xi,yi)} using the composite Simpson's 1/3 rule.

    Args:
        x: 1D array of evenly spaced discrete xi observations
        y: 1D array of evenly spaced discrete yi observations

    Returns:
        I: Estimated integral
    """
    # INPUT VALIDATION
    # check if x and y have a valid number of dimensions
    if np.ndim(x) != 1:
        raise ValueError("Invalid number of dimensions of x")
    if np.ndim(y) != 1:
        raise ValueError("Invalid number of dimensions of y")

    # check if x and y have the same number of points
    n = np.size(x)
    if n != np.size(y):
        raise ValueError("x and y must have the same number of points")
    
    # check if x has a valid number of points
    if n < 3 or n % 2 == 0:
        raise ValueError("Invalid number of points in x and y")
   
    # check if space between points is uniform
    all_h = x[1:] - x[:-1] # determine all widths    
    tolerance = 1e-8 + 1e-5 * all_h[0] if np.abs(all_h[0]) > 1 else 1e-8 # set tolerance based on the first width
    if np.sum(np.abs(all_h[0] - all_h) < tolerance) < n - 1: # bool must be entirely true
        raise ValueError("Segments must be uniform")    
    
    # COMP SIMP 1/3 ALGORITHM
    h = x[1] - x[0] # determine width
    
    # calculate integral estimate
    even_sum = 4 * np.sum(y[1:-1:2])
    odd_sum = 2 * np.sum(y[2:-1:2])
    I = h/3* (y[0] + even_sum + odd_sum + y[-1])

    return I
    
def simp38(f, a, b):
    """
    Calculates an estimation of the integral of f(x) using a single application of Simpson's 3/8 rule.

    Args:
        f: Lambda function of f(x) 
        a: Lower limit of the integral
        b: Upper limit of the integral

    Returns:
        I: Estimated integral
    """
    # INPUT VALIDATION
    # check if integral limits are valid
    if a == b:
        raise ValueError("Invalid integral limits")

    # SIMP 3/8 ALGORITHM 
    x = np.linspace(a, b, 4) # create 1D array for x
    y = f(x) # create 1D array for y
    h = x[1] - x[0] # determine width

    # calculate integral estimate
    I = 3*h/8 *(y[0] + 3*y[1] + 3*y[2] + y[-1])
    
    return I
    
def simp38_vector(x, y):
    """
    Calculates an estimation of the integral of {(xi,yi)} using a single application of Simpson's 3/8 rule.

    Args:
        x: 1D array of evenly spaced discrete xi observations
        y: 1D array of evenly spaced discrete yi observations

    Returns:
        I: Estimated integral
    """
    # INPUT VALIDATION
    # check if x and y have a valid number of dimensions
    if np.ndim(x) != 1:
        raise ValueError("Invalid number of dimensions of x")
    if np.ndim(y) != 1:
        raise ValueError("Invalid number of dimensions of y")

    # check if x and y have the same number of points
    n = np.size(x)
    if n != np.size(y):
        raise ValueError("x and y must have the same number of points")
    
    # check if x has a valid number of points
    if n != 4:
        raise ValueError("Invalid number of points in x and y")

    # check if space between points is uniform
    all_h = x[1:] - x[:-1] # determine all widths    
    tolerance = 1e-8 + 1e-5 * all_h[0] if np.abs(all_h[0]) > 1 else 1e-8 # set tolerance based on the first width
    if np.sum(np.abs(all_h[0] - all_h) < tolerance) < n - 1: # bool must be entirely true
        raise ValueError("Segments must be uniform")    
        
    # SIMP 3/8 ALGORITHM
    h = x[1] - x[0] # determine width

    # calculate integral estimate
    I = 3*h/8 *(y[0] + 3*y[1] + 3*y[2] + y[-1])

    return I
    

# ODEs
def euler(dydt, tspan, y0, h):
    """
    Uses Euler's method to solve an ODE.

    Args:
        dydt: Lambda function of the ODE, f(t,y)
        tspan: 1D array containing independent variable domain [<initial value>, <final value>]
        y0: Initial value of dependent variable
        h: Step size
    
    Returns:
        t: Vector of independent variable
        y: Vector of solution for dependent variable
    """
    # INPUT VALIDATION
    # check that tspan is a 1D array
    if np.ndim(tspan) != 1:
        raise ValueError("Invalid number of dimensions of tspan")
    
    # check that tspan only has two numbers
    if np.size(tspan) != 2:
        raise ValueError("Invalid number of values in tspan")

    # check that the independent variable's final value > initial value
    if tspan[-1] <= tspan[0]:
        raise ValueError("Invalid independent variable range")
    
    # check that the step size is positive
    if h <= 0:
        raise ValueError("Invalid step size")

    # EULER ALGORITHM
    # create t as a vector 
    t = np.arange(tspan[0], tspan[1], h)

    # add an additional t so that the range goes up to tspan[1]
    t = np.append(t, tspan[1])

    # define n, the number of points in t
    n = np.size(t)

    # Preallocate y to improve efficiency
    y = np.ones(n) * y0

    # Implement Euler's method
    for i in range(n - 1):
        if i == n - 2:  # Adjust step size for the last step
            h = t[-1] - t[-2]
        y[i + 1] = y[i] + h * dydt(t[i], y[i])

    return t, y

def heun(dydt, tspan, y0, h):
    """
    Function that uses Heun's method to solve an ODE.

    Args:
        dydt: Lambda function of the ODE, f(t,y)
        tspan: [<initial value>, <final value>] of independent variable
        y0: Initial value of dependent variable
        h: Step size
    
    Returns:
        t: Vector of independent variable
        y: Vector of solution for dependent variable
    """
    # INPUT VALIDATION
    # Check that tspan is a 1D array
    if np.ndim(tspan) != 1:
        raise ValueError("Invalid number of dimensions of tspan")
    
    # Check that tspan only has two numbers
    if np.size(tspan) != 2:
        raise ValueError("Invalid number of values in tspan")

    # Check that the independent variable's final value > initial value
    if tspan[-1] <= tspan[0]:
        raise ValueError("Invalid independent variable range")
    
    # Check that the step size is positive
    if h <= 0:
        raise ValueError("Invalid step size")

    # HEUN ALGORITHM
    # Create t as a vector 
    t = np.arange(tspan[0], tspan[1], h)

    # Add an additional t so that the range goes up to tspan[1]
    t = np.append(t, tspan[1])

    # define n, the number of points in t
    n = np.size(t)

    # Preallocate y to improve efficiency
    y = np.ones(n) * y0

    # Implement Heun's method
    for i in range(n - 1):
        if i == n - 2:  # Adjust step size for the last step
            h = t[-1] - t[-2]
        yPred = y[i] + h * dydt(t[i], y[i])
        y[i + 1] = y[i] + h * (dydt(t[i], y[i]) + dydt(t[i + 1], yPred)) / 2

    return t, y

def midpoint(dydt, tspan, y0, h):
    """
    Function that uses the midpoint method to solve an ODE.

    Args:
        dydt: Lambda function of the ODE, f(t,y)
        tspan: [<initial value>, <final value>] of independent variable
        y0: Initial value of dependent variable
        h: Step size
    
    Returns:
        t: Vector of independent variable
        y: Vector of solution for dependent variable
    """
    # INPUT VALIDATION
    # Check that tspan is a 1D array
    if np.ndim(tspan) != 1:
        raise ValueError("Invalid number of dimensions of tspan")
    
    # Check that tspan only has two numbers
    if np.size(tspan) != 2:
        raise ValueError("Invalid number of values in tspan")

    # Check that the independent variable's final value > initial value
    if tspan[-1] <= tspan[0]:
        raise ValueError("Invalid independent variable range")
    
    # Check that the step size is positive
    if h <= 0:
        raise ValueError("Invalid step size")

    # MIDPOINT ALGORITHM
    # Create t as a vector 
    t = np.arange(tspan[0], tspan[1], h)

    # Add an additional t so that the range goes up to tspan[1]
    t = np.append(t, tspan[1])

    # define n, the number of points in t
    n = np.size(t)

    # Preallocate y to improve efficiency
    y = np.ones(n) * y0

    # Implement Midpoint method
    for i in range(n - 1):
        if i == n - 2:  # Adjust step size for the last step
            h = t[-1] - t[-2]
        yHalf = y[i] + (h / 2) * dydt(t[i], y[i])
        tHalf = t[i] + h / 2
        y[i + 1] = y[i] + h * dydt(tHalf, yHalf)

    return t, y
