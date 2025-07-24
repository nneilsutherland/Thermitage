import argparse

def parse_cli() -> dict:

    """
    Parse command line arguments and return a dictionary with the input arguments. 
    """

    parser = argparse.ArgumentParser(
        description="THERMal Image Corection (THERMIC): A tool for correcting scene-based temperature drift in thermal image sequences."
    )
    parser.add_argument(
        "-d",
        type=str,
        metavar="DIRECTORY",
        help="Project directory, containing a 'images' folder, 'config.yaml' configuration file and where the results will be saved.",
        default=None,
    )

    args = parser.parse_args()

    return vars(args)

# - - - - - - - - - - - COMMENTS - - - - - - - - - - -

"""
Arguments for
Input folders


"""
