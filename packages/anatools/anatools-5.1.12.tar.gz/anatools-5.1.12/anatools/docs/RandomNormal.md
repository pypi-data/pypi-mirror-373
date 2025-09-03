Draw random samples from a normal (Gaussian) distribution with mean 'loc' and standard deviation 'scale' (see numpy.random.normal for details)
* "loc" - Mean of the distribution. Input must be either a number or an array of numbers.
* "scale" - Standard deviation of the distribution. Input must be either a number or an array of numbers.
* "size" - Output shape, e.g., [m, n, k] will draw m * n * k samples and a single value is drawn for None (default) if loc and scale are both scalars, otherwise, np.broadcast(loc, scale).size samples are drawn. To draw a single value leave this empty.