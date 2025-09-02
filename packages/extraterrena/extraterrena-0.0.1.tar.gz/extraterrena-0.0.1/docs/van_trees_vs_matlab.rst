Van Trees vs Matlab
========================

The Matlab documentation for the steervec function (https://au.mathworks.com/help/phased/ref/steervec.html) defines
the angles as:

"The azimuth angle is the angle between the x-axis and the projection of the arrival direction vector onto the xy plane. It is positive when measured from the x-axis toward the y-axis. The elevation angle is the angle between the arrival direction vector and xy-plane. It is positive when measured towards the z axis." (Retrieved 22nd May 2025)

Given that Matlab places arrays on the y-axis for a 1D array, and the yz-plane for a 2D array, the x-axis is the normal axis. 
The convention in this package is for the z-axis to be the normal axis in all cases.

If our vector is given in spherical co-ordinates as $(\sin(\theta)\cos(\phi),\sin(\theta)\sin(\phi) ,\cos(\theta))$.




Forwards - Van Trees to Matlab
==============================
If $\phi$, $\theta$ are the azimuth and elevation respectively from spherical co-ordinates, then the 
Matlab angles are:

$$\phi_{n} = \arctan\left(\tan(\theta) \cos(\phi)\right)$$
$$\theta_{n} = \arctan\left( \frac{\sin(\theta)\sin(\phi)}{\sqrt{\sin^{2}(\theta)\cos^{2}(\phi) + \cos^{2}(\theta)}}\right) = \arccos\left(\sqrt{\sin^{2}(\theta)\cos^{2}(\phi) + \cos^{2}(\theta)}\right) $$


We firstly project onto the xz-plane by setting the $y$ co-ordinate to zero. We then find the angle between the x-axis and the projected vector:
$$ \tan(\phi) = \frac{x}{z} = \frac{\sin(\theta)\cos(\phi)}{\cos(\theta)} = \tan(\theta)\cos(\phi)$$

Now we find the angle between the projection of $v$ and $v$. The tangent of the angle will be $\tan(\theta_{n}) = \frac{\sin(\theta)\sin(\phi)}{\sqrt{\sin^{2}(\theta)\cos^{2}(\phi) + \cos^{2}(\theta)}}$.

This is also equal to the angle between the vectors which is

$$\cos(\theta_{n}) = \frac{v.v_{proj}}{\|v\| \|v_{proj}\|} = \frac{\sin^{2}(\theta)\cos^{2}\phi + \cos^{2}(\theta)}{\sqrt{\sin^{2}(\theta)\cos^{2}\phi + \cos^{2}(\theta)}} = \sqrt{\sin^{2}(\theta)\cos^{2}\phi + \cos^{2}(\theta)}$$

Backwards - Matlab to Van Trees
===============================

The following derivation is only valid for $0<\theta< \frac{\pi}{2}$ and $0<\phi<\frac{\pi}{2}$.

We have the following from the forwards direction:
$$\phi_{n} = \arctan\left(\tan(\theta) \cos(\phi)\right)$$
$$\theta_{n} = \arctan\left( \frac{\sin(\theta)\sin(\phi)}{\sqrt{\sin^{2}(\theta)\cos^{2}(\phi) + \cos^{2}(\theta)}}\right) $$

Rearrange for $\tan(\theta)$ in the $\phi_{n}$ equation to find
$$ \tan(\theta) = \frac{\tan(\phi_{n})}{\cos(\phi)},\ (\cos(\phi) \ne 0)$$ 

Assuming that $\cos(\theta) \ne 0$, divide the top and bottom of the fraction in the equation for $\theta_{n}$ by $\cos(\theta)$ to find
$$\tan(\theta_{n}) = \frac{\tan(\theta)\sin(\phi)}{\sqrt{\tan^{2}(\theta)\cos^{2}(\phi) + 1}}$$
Now substitute the equation for $\tan(\theta)$:
$$\tan(\theta_{n}) = \frac{\tan(\phi_{n})\frac{\sin(\phi)}{\cos(\phi)}}{\sqrt{\tan^{2}(\phi_{n}) + 1}}$$
Use the identity $\tan^{2}(\phi_{n}) + 1 = \sec^{2}(\phi_{n})$ to simplify:
$$ \tan(\theta_{n}) = \frac{\tan(\phi_{n})\tan(\phi)}{\sec(\phi_{n})}$$

Rearrange for $\phi$:

$$\phi = \arctan\left(\frac{\tan(\theta_{n})}{\tan(\phi_{n})\cos(\phi_{n})}\right)$$

Finally:
$$\phi = \arctan\left(\frac{\tan(\theta_{n})}{\sin(\phi_{n})}\right)$$

We can then substitute this into the equation for $\theta$:
$$\theta = \arctan\left(\frac{\tan(\phi_{n})}{\cos\left(\arctan\left(\frac{\tan(\theta_{n})}{\sin(\phi_{n})}\right)\right)}\right)$$
