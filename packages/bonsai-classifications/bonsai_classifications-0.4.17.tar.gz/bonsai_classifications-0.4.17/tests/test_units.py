from classifications._pint_units import get_unit_registry


def test_units():
    def almost_equal(a: float, b: float, tol: float = float("1e-6")) -> bool:
        return abs(a - b) <= tol

    ureg = get_unit_registry()

    a = 1000000 * ureg.DKK_2017
    a_result = a.to("Meuro_2016")

    b = 1 * ureg.t
    b_result = b.to("tonnes")

    c = 1 * ureg.kWh
    c_result = c.to("TJ")

    assert almost_equal(a_result.m, 0.1416874676815668658358755478) == True
    assert a_result.u == "Meuro_2016"
    assert almost_equal(b_result.m, 1.0) == True
    assert b_result.u == "tonnes"
    assert almost_equal(c_result.m, 0.000003600) == True
    assert c_result.u == "terajoule"
