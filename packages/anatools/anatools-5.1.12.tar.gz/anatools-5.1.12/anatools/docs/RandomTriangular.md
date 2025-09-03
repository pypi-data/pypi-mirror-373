Draw random samples from a triangular distribution over the closed interval [left, right], see numpy.random.triangular for details.
* "left" - Lower limit
* "mode" - The value where the peak of the distribution occurs
* "right" - Upper limit
* "size" - Output shape, e.g., (m, n, k), will draw m * n * k samples and a sigle value is drawn for None (default) if left, mode, and right are all scalars, otherwise, np.broadcast(left, mode, right).size samples are drawn. Leave this empty to draw a single value.