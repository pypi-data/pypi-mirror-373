Draw random samples from a uniform distribution over the half-open interval [low, high), see numpy.random.uniform for details
* "low" - Lower boundary of the interval (inclusive). Input must be either a number or an array of numbers
* "high" - Upper boundary of the interval (exclusive). Input must be either a number or an array of numbers
* "size" - Output shape, e.g, [m, n, k], will draw m * n * k samples and a single value is drawn for None (default) if low and high are both scalars, otherwise np.broadcast(low, high).size samples are drawn. Leave this empty to draw a single value.