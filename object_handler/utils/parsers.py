""" Parsers for the functions modules """

import argparse

def parse_arguments_simplification() -> argparse.Namespace:
    """
    Create the parser and add the arguments to the simplification function.
    """
    # Choose the simplification type
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh_simplification_method",
                        "-ms",
                        required=False,
                        type=str,
                        help="Choose the algorithm to simplify (vertex, quadric)")

    parser.add_argument("--parameter",
                        "-p",
                        required=False,
                        type=float,
                        help="Choose the algorithm parameter to simplify "
                        "(vertex: Cell Size, the size of the cell of the clustering grid "
                        "quadric: Percentage reduction (0..1), if non zero, this parameter "
                        "specifies the desired final size of the mesh as a percentage of "
                        "the initial size.)")

    parser.add_argument("--cut_type",
                        "-ct",
                        required=False,
                        type=str,
                        help="Choose the type of cut (no_cut, rectangle, "
                        "sphere, cmap, interactions)")
    return parser.parse_args()

def parse_arguments_compute_rt() -> argparse.Namespace:
    """
    Create the parser and add the arguments to the compute rt function.
    """
    parser = argparse.ArgumentParser()
    # Future implementations
    #parser.add_argument("--number",
    #                    "-n",
    #                    type=int,
    #                    required=True,
    #                    help="Number of simulations")

    return parser.parse_args()

def parse_arguments_compute_nmse() -> argparse.Namespace:
    """
    Create the parser and add the arguments to the compute nmse function.
    """
    parser = argparse.ArgumentParser()
    # Future implementations
    #parser.add_argument("--step",
    #                    "-s",
    #                    type=float,
    #                    required=True,
    #                    help="Number of steps to generate the new rx positions")

    return parser.parse_args()
