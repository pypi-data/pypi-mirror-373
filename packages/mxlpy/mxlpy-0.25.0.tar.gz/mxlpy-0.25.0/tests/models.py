from mxlpy import Derived, Model, fns


def m_1v_0p_0d_0r() -> Model:
    return Model().add_variable("v1", 1.0)


def m_2v_0p_0d_0r() -> Model:
    return Model().add_variables({"v1": 1.0, "v2": 2.0})


def m_0v_1p_0d_0r() -> Model:
    return Model().add_parameter("p1", 1.0)


def m_0v_2p_0d_0r() -> Model:
    return Model().add_parameters({"p1": 1.0, "p2": 2.0})


def m_1v_1p_1d_0r() -> Model:
    return (
        Model()
        .add_variable("v1", 1.0)
        .add_parameter("p1", 1.0)
        .add_derived(
            "d1",
            fn=fns.add,
            args=["v1", "p1"],
        )
    )


def m_1v_1p_1d_1r() -> Model:
    return (
        Model()
        .add_variable("v1", 1.0)
        .add_parameter("p1", 1.0)
        .add_derived(
            "d1",
            fn=fns.add,
            args=["v1", "p1"],
        )
        .add_reaction(
            "r1",
            fn=fns.mass_action_1s,
            args=["v1", "d1"],
            stoichiometry={"v1": -1.0},
        )
    )


def m_2v_1p_1d_1r() -> Model:
    return (
        Model()
        .add_variables({"v1": 1.0, "v2": 2.0})
        .add_parameter("p1", 1.0)
        .add_derived(
            "d1",
            fn=fns.add,
            args=["v1", "v2"],
        )
        .add_reaction(
            "r1",
            fn=fns.mass_action_1s,
            args=["v1", "p1"],
            stoichiometry={"v1": -1.0, "v2": 1.0},
        )
    )


def m_2v_2p_1d_1r() -> Model:
    return (
        Model()
        .add_variables({"v1": 1.0, "v2": 2.0})
        .add_parameters({"p1": 1.0, "p2": 2.0})
        .add_derived(
            "d1",
            fn=fns.add,
            args=["v1", "v2"],
        )
        .add_reaction(
            "r1",
            fn=fns.mass_action_1s,
            args=["v1", "p1"],
            stoichiometry={"v1": -1.0, "v2": 1.0},
        )
    )


def m_2v_2p_2d_1r() -> Model:
    return (
        Model()
        .add_variables({"v1": 1.0, "v2": 2.0})
        .add_parameters({"p1": 1.0, "p2": 2.0})
        .add_derived(
            "d1",
            fn=fns.add,
            args=["v1", "v2"],
        )
        .add_derived(
            "d2",
            fn=fns.mul,
            args=["v1", "v2"],
        )
        .add_reaction(
            "r1",
            fn=fns.mass_action_1s,
            args=["v1", "p1"],
            stoichiometry={"v1": -1.0, "v2": 1.0},
        )
    )


def m_2v_2p_2d_2r() -> Model:
    return (
        Model()
        .add_variables({"v1": 1.0, "v2": 2.0})
        .add_parameters({"p1": 1.0, "p2": 2.0})
        .add_derived(
            "d1",
            fn=fns.add,
            args=["v1", "p1"],
        )
        .add_derived(
            "d2",
            fn=fns.mul,
            args=["v2", "p2"],
        )
        .add_reaction(
            "r1",
            fn=fns.mass_action_1s,
            args=["v1", "d1"],
            stoichiometry={"v1": -1.0, "v2": 1.0},
        )
        .add_reaction(
            "r2",
            fn=fns.mass_action_1s,
            args=["v2", "d2"],
            stoichiometry={"v1": 1.0, "v2": -1.0},
        )
    )


def m_dependent_derived() -> Model:
    return (
        Model()
        .add_parameter("p1", 1.0)
        .add_derived(
            "d1",
            fn=fns.constant,
            args=["p1"],
        )
        .add_derived(
            "d2",
            fn=fns.constant,
            args=["d1"],
        )
    )


def m_derived_stoichiometry() -> Model:
    return (
        Model()
        .add_variable("v1", 1.0)
        .add_reaction(
            "r1",
            fn=fns.constant,
            args=["v1"],
            stoichiometry={
                "v1": Derived(fn=fns.one_div, args=["v1"]),
            },
        )
    )
