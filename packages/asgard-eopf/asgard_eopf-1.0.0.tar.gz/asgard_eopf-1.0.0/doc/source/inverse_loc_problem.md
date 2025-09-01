Problem position
================

We have a mapping function $M$ that maps $(i, j)$ matrix positions to $(x, y)$ ground positions,
and we want to estimate the $(i, j)$ matrix position corresponding to a new $(x, y)$ ground position.
In a nutshell, we want to find:

$$
(i^*, j^*) = Argmin_{i \in I,j\in J} f(i,j) := [M(i,j) - (x_pos, y_pos)] (*)
$$

We can use the inverse Jacobian method based on the Newton-Raphson method to solve the problem (*).


Illustrating example
--------------------

Here's an example to illustrate how it works.
Let's say we have a mapping function $M$ that maps $(i, j)$ matrix positions to
$(x, y)$ ground positions as follows:

$$
M(i, j) = (M_1(i,j), M_2(i,j)) = (x, y)
$$

where: $M_1(i,j)= x = 10i + 5$ and $M_2(i,j) = y = 10j + 5$

Now, we want to estimate the $(i^*, j^*)$ matrix position (solution of the problem (*)) corresponding
to a new ground position $(x_{pos}, y_{pos})=(x=75, y=95)$ using the inverse Jacobian method. We can then
use the following iterative formula (Newton-Raphson) to update the estimate of the matrix position:

$$
Xn+1 = Xn - J^{-1}(Xn) * F(Xn)
$$

where $Xn=(i_n,j_n)$ is the current estimate of the matrix position, $J(Xn)$ is the Jacobian matrix of
$M$ at $Xn$, $F(Xn)$ is the difference between the ground position corresponding to $Xn$ and the desired
ground position (here $(x=75, y=95)$):

$$
F(X) = M(X) - (75, 95)
$$

and $J^{-1}(Xn)$ is the inverse of $J(Xn)$.


To compute the Jacobian matrix of $M$, we can use the following gradients:

$$
grad(M_1(i,j)) = (10, 0)
grad(M_2(i,j)) = (0, 10)
$$

Therefore, the Jacobian matrix of $M$ at a given matrix position $(i,j)$ is:

$$
J(i,j) = [grad(M_1(i,j)); grad(M_2(i,j))] = [10 0; 0 10]
$$

We can start by setting an initial estimate of the matrix position, for example, $X0=(i_0=5, j_0=9)$.
Now, we can compute the initial value of $F(X0)$ as follows:

$$
F(X0) = M(X0) - (x=75, y=95) = (x=5*10+5, y=9*10+5) - (75, 95) = (55, 95) - (75, 95) = (-20, 0)
$$

Next, we can compute the inverse of $J(X0)$ as follows:

$$
J^{-1}(X0) = [dM/di(X0) dM/dj(X0)]^{-1} = [1/10 0; 0 1/10]
$$

Finally, we can update the estimate of the matrix position as follows:

$$
X1 = X0 - J^{-1}(X0) * F(X0) = (5, 9) - [1/10 0; 0 1/10] * (-20, 0) = (-2, 0)
$$

We can repeat this process by plugging $X1$ into the formula to obtain a new estimate $X2$, and so on,
until the estimate converges to a sufficiently accurate value.

In summary, the inverse Jacobian method can be used to estimate the $(i, j)$ matrix position
corresponding to a given ground position $(x, y)$ by iteratively updating the estimate based on the
Jacobian matrix of the mapping function $M$ and the difference between the estimated and desired
ground positions.

Jacobian clipping
-----------------

To compute jacobian matrix we use "central difference formulas" in the finite difference method due
to the fact that they yield better accuracy.

That is:

$$
J(i,j) = [ (M_1(i+1,j) - M_1(i-1,j))/2, (M_1(i,j+1) - M_1(i,j-1))/2;
    (M_2(i+1,j) - M_2(i-1,j))/2, (M_2(i,j+1) - M_2(i,j-1))/2] ]
$$

where $i \in$

$I = [i_{min}, i_{max}]$ and $j\in J= [j_{min}, j_{max}]$

In our case I and J must be clipped to:

$I_{clipped} = [i_{min}+1, i_{max}-1]$ and $J_{clipped} = [j_{min}+1, j_{max}-1]$


In Python convention this must correspond to:

$I_{clipped} = [i_{min}+1, i_{max}-2]$ and $J_{clipped} = [j_{min}+1, j_{max}-2]$
