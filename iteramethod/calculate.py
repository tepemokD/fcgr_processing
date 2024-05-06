from scipy.interpolate import CubicSpline, PPoly


def interpolatecubicspline(x: list,
                           y: list) -> CubicSpline:
    """
    Approximation of a tabular function
    :param x: x array
    :param y: y array
    :return: an instance of the class 'CubicSpline'
    """
    return CubicSpline(x, y, extrapolate=False)


def derivativeinterpolatecubicspline(x: list,
                                     y: list) -> PPoly:
    """
    Derivative approximation of a tabular function
    :param x: x array
    :param y: y array
    :return: an instance of the class 'PPoly'
    """
    cs = CubicSpline(x, y, extrapolate=False)
    return cs.derivative()


if __name__ == "__main__":
    pass
