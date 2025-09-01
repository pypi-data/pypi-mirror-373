Problem position
================

We have a mapping function M that maps (i, j) matrix positions to (x, y) ground positions, 
and we want to estimate the (i, j) matrix position corresponding to a new (x, y) ground position.
In a nutshell, we want to find: 
	
.. math:: (i^*, j^*) = Argmin_{i \in I,j\in J} f(i,j) := [M(i,j) - (x_pos, y_pos)] (*)
							
We can use the inverse Jacobian method based on the Newton-Raphson method to solve the problem (*). 


Illustrating example 
--------------------

Here's an example to illustrate how it works.
Let's say we have a mapping function M that maps (i, j) matrix positions to (x, y) ground positions 
as follows: 

.. math:: M(i, j) = (M_1(i,j), M_2(i,j)) = (x, y)


where: :math:`M_1(i,j)= x = 10i + 5` and :math:`M_2(i,j) = y = 10j + 5`

Now, we want to estimate the :math:`(i^*, j^*)` matrix position (solution of the problem (*)) corresponding
to a new ground position :math:`(x_{pos}, y_{pos})=(x=75, y=95)` using the inverse Jacobian method. We can then
use the following iterative formula (Newton-Raphson) to update the estimate of the matrix position:

.. math:: Xn+1 = Xn - J^{-1}(Xn) * F(Xn)

where :math:`Xn=(i_n,j_n)` is the current estimate of the matrix position, :math:`J(Xn)` is the Jacobian matrix of
M at :math:`Xn`, :math:`F(Xn)` is the difference between the ground position corresponding to :math:`Xn` and the desired
ground position (here :math:`(x=75, y=95)`):
	
.. math:: F(X) = M(X) - (75, 95)

and :math:`J^{-1}(Xn)` is the inverse of :math:`J(Xn)`.


To compute the Jacobian matrix of M, we can use the following gradients:

.. math:: 

	grad(M_1(i,j)) = (10, 0)
	grad(M_2(i,j)) = (0, 10)

Therefore, the Jacobian matrix of M at a given matrix position :math:`(i,j)` is:

.. math:: J(i,j) = [grad(M_1(i,j)); grad(M_2(i,j))] = [10 0; 0 10]

We can start by setting an initial estimate of the matrix position, for example, :math:`X0=(i_0=5, j_0=9)`. 
Now, we can compute the initial value of :math:`F(X0)` as follows:

.. math:: F(X0) = M(X0) - (x=75, y=95) = (x=5*10+5, y=9*10+5) - (75, 95) = (55, 95) - (75, 95) = (-20, 0)

Next, we can compute the inverse of :math:`J(X0)` as follows:

.. math:: J^{-1}(X0) = [dM/di(X0) dM/dj(X0)]^{-1} = [1/10 0; 0 1/10]

Finally, we can update the estimate of the matrix position as follows:

.. math:: X1 = X0 - J^{-1}(X0) * F(X0) = (5, 9) - [1/10 0; 0 1/10] * (-20, 0) = (-2, 0)

We can repeat this process by plugging :math:`X1` into the formula to obtain a new estimate :math:`X2`, and so on,
until the estimate converges to a sufficiently accurate value.

In summary, the inverse Jacobian method can be used to estimate the :math:`(i, j)` matrix position
corresponding to a given ground position :math:`(x, y)` by iteratively updating the estimate based on the
Jacobian matrix of the mapping function M and the difference between the estimated and desired
ground positions.

Jacobian clipping
-----------------

To compute jacobian matrix we use "central difference formulas" in the finite difference method due 
to the fact that they yield better accuracy.

That is : 

.. math:: 
	J(i,j) = [ (M_1(i+1,j) - M_1(i-1,j))/2, (M_1(i,j+1) - M_1(i,j-1))/2;  
		(M_2(i+1,j) - M_2(i-1,j))/2, (M_2(i,j+1) - M_2(i,j-1))/2] ]

where i \in 

:math:`I = [i_{min}, i_{max}]` and :math:`j\in J= [j_{min}, j_{max}]`

In our case I and J must be clipped to :  

:math:`I_{clipped} = [i_{min}+1, i_{max}-1]` and :math:`J_{clipped} = [j_{min}+1, j_{max}-1]`

In Python convention this must correspond to :

:math:`I_{clipped} = [i_{min}+1, i_{max}-2]` and :math:`J_{clipped} = [j_{min}+1, j_{max}-2]`
