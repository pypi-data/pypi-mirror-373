from itertools import product

from lago import LinkStream, lago_communities


def test(
    lex: str = "JM",  # "MM" or "JM"
    nb_iter: int = 1,
    omega: float = 2,  # must be >= 0
    refinement: str | None = "STNM",  # None, "STEM" or "STNM"
    fast_exploration: bool = True,
    refinement_in: bool = False,
    verbose: bool = True,
    linkstream_path="tests/linkstream.txt",
):
    linkstream = LinkStream()
    linkstream.read_txt(linkstream_path)

    communities = lago_communities(
        linkstream=linkstream,
        lex=lex,
        nb_iter=nb_iter,
        omega=omega,
        refinement=refinement,
        fast_exploration=fast_exploration,
        refinement_in=refinement_in,
        verbose=verbose,
    )

    return communities


LEX = ["MM", "JM"]
NB_ITER = [1, 2]
OMEGA = [1, 5]
REFINEMENT = [None, "STNM", "STEM"]
FAST_EXPLORATION = [True, False]
REFINEMENT_IN = [True, False]

for lex, nb_iter, omega, refinement, fast_exploration, refinement_in in product(
    LEX,
    NB_ITER,
    OMEGA,
    REFINEMENT,
    FAST_EXPLORATION,
    REFINEMENT_IN,
):
    test(
        lex=lex,
        nb_iter=nb_iter,
        omega=omega,
        refinement=refinement,
        fast_exploration=fast_exploration,
        refinement_in=refinement_in,
    )
