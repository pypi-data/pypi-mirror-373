# """Tests for the MCA module."""

# import numpy as np
# import pandas as pd
# import pytest

# from mxlpy.mca import (
#     parameter_elasticities,
#     response_coefficients,
#     variable_elasticities,
# )
# from mxlpy.model import Model, Reaction


# def create_test_model():
#     """Create a simple test model for MCA testing."""
#     model = Model()
#     model.add_variables({"A": 1.0, "B": 0.0})
#     model.add_parameters({"v1": 0.1, "k1": 2.0})
#     model.add_reaction(
#         name="r1",
#         fn=lambda v1, A, k1: v1 * A / k1,
#         stoichiometry={"A": -1, "B": 1},
#         args=["v1", "A", "k1"],
#     )
#     return model


# def test_parameter_elasticities() -> None:
#     """Test calculation of parameter elasticities."""
#     model = create_test_model()
#     conc = pd.Series({"A": 1.0, "B": 0.0})
#     param = pd.Series({"v1": 0.1, "k1": 2.0})

#     elast = parameter_elasticities(model, conc, param)

#     assert "r1" in elast.index
#     assert "v1" in elast.columns
#     assert "k1" in elast.columns

#     # r1 = v1 * A / k1
#     # Elasticity with respect to v1 should be 1
#     assert elast.loc["r1", "v1"] == 1.0

#     # Elasticity with respect to k1 should be -1
#     assert elast.loc["r1", "k1"] == -1.0


# def test_concentration_elasticities() -> None:
#     """Test calculation of concentration elasticities."""
#     model = create_test_model()
#     conc = pd.Series({"A": 1.0, "B": 0.0})
#     param = pd.Series({"v1": 0.1, "k1": 2.0})

#     elast = variable_elasticities(model, concs=conc, param)

#     assert "r1" in elast.index
#     assert "A" in elast.columns
#     assert "B" in elast.columns

#     # r1 = v1 * A / k1
#     # Elasticity with respect to A should be 1
#     assert elast.loc["r1", "A"] == 1.0

#     # Elasticity with respect to B should be 0
#     assert elast.loc["r1", "B"] == 0.0


# def test_response_coefficients() -> None:
#     """Test calculation of response coefficients."""
#     model = create_test_model()
#     conc = pd.Series({"A": 1.0, "B": 0.0})
#     param = pd.Series({"v1": 0.1, "k1": 2.0})

#     # Calculate elasticities
#     conc_elast = concentration_elasticities(model, conc, param)
#     param_elast = parameter_elasticities(model, conc, param)

#     # Calculate control coefficients
#     fcc = flux_control_coefficients(model, conc_elast)

#     # Calculate response coefficients
#     rc = response_coefficients(fcc, param_elast)

#     assert "r1" in rc.index
#     assert "v1" in rc.columns
#     assert "k1" in rc.columns

#     # For this simple model, response coefficient of r1 with respect to v1 should be 1
#     assert rc.loc["r1", "v1"] == 1.0

#     # For this simple model, response coefficient of r1 with respect to k1 should be -1
#     assert rc.loc["r1", "k1"] == -1.0


# def test_steady_state_flux_control_sum() -> None:
#     """Test the summation theorem for flux control coefficients."""
#     model = create_test_model()
#     conc = pd.Series({"A": 1.0, "B": 0.0})
#     param = pd.Series({"v1": 0.1, "k1": 2.0})

#     # Calculate elasticities
#     conc_elast = concentration_elasticities(model, conc, param)

#     # Calculate flux control coefficients
#     fcc = flux_control_coefficients(model, conc_elast)

#     # Calculate sum
#     fcc_sums = steady_state_flux_control_sum(fcc)

#     # For any flux, the sum of control coefficients should be 1
#     assert np.isclose(fcc_sums["r1"], 1.0)


# def test_steady_state_concentration_control_sum() -> None:
#     """Test the summation theorem for concentration control coefficients."""
#     model = create_test_model()
#     conc = pd.Series({"A": 1.0, "B": 0.0})
#     param = pd.Series({"v1": 0.1, "k1": 2.0})

#     # Calculate elasticities
#     conc_elast = concentration_elasticities(model, conc, param)

#     # Calculate control coefficients
#     fcc = flux_control_coefficients(model, conc_elast)
#     ccc = concentration_control_coefficients(model, conc_elast, fcc)

#     # Calculate sum
#     ccc_sums = steady_state_concentration_control_sum(ccc)

#     # For any concentration, the sum of control coefficients should be 0
#     assert np.isclose(ccc_sums["A"], 0.0)
#     assert np.isclose(ccc_sums["B"], 0.0)


# def test_two_step_pathway() -> None:
#     """Test MCA with a two-step linear pathway."""
#     # Create a two-step pathway model: A -> B -> C
#     model = Model()
#     model.add_variables({"A": 1.0, "B": 0.5, "C": 0.0})
#     model.add_parameters({"v1": 0.1, "v2": 0.1, "k1": 1.0, "k2": 1.0})

#     model.add_reaction(
#         name="r1",
#         fn=lambda v1, A, k1: v1 * A / (k1 + A),
#         stoichiometry={"A": -1, "B": 1},
#         args=["v1", "A", "k1"],
#     )

#     model.add_reaction(
#         name="r2",
#         fn=lambda v2, B, k2: v2 * B / (k2 + B),
#         stoichiometry={"B": -1, "C": 1},
#         args=["v2", "B", "k2"],
#     )

#     conc = pd.Series({"A": 1.0, "B": 0.5, "C": 0.0})
#     param = pd.Series({"v1": 0.1, "v2": 0.1, "k1": 1.0, "k2": 1.0})

#     # Calculate elasticities
#     conc_elast = concentration_elasticities(model, conc, param)

#     # Calculate flux control coefficients
#     fcc = flux_control_coefficients(model, conc_elast)

#     # For a linear pathway, the sum of control coefficients for each flux should be 1
#     assert np.isclose(fcc.loc["r1", "r1"] + fcc.loc["r1", "r2"], 1.0)
#     assert np.isclose(fcc.loc["r2", "r1"] + fcc.loc["r2", "r2"], 1.0)

#     # Calculate concentration control coefficients
#     ccc = concentration_control_coefficients(model, conc_elast, fcc)

#     # For each metabolite, the sum of control coefficients should be 0
#     assert np.isclose(ccc.loc["A", "r1"] + ccc.loc["A", "r2"], 0.0)
#     assert np.isclose(ccc.loc["B", "r1"] + ccc.loc["B", "r2"], 0.0)
#     assert np.isclose(ccc.loc["C", "r1"] + ccc.loc["C", "r2"], 0.0)
