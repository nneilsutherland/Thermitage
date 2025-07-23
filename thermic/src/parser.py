# File for building command-line arguments

import argparse

def parse_cli() -> dict:

    """
    Parse command line arguments and return a dictionary with the input arguments. 
    If --gui is specified, run the GUI interface and return the arguments from the GUI.
    """

    parser = argparse.ArgumentParser(
        description="Matching with hand-crafted and deep-learning based local features and image retrieval."
    )
    parser.add_argument(
        "--gui", action="store_true", help="Run GUI interface", default=False
    )
    parser.add_argument(
        "-d",
        "--dir",
        type=str,
        help="Project directory, containing a folder 'images', in which all the images are present and where the results will be saved.",
        default=None,
    )
    parser.add_argument(
        "-i",
        "--images",
        type=str,
        help="Folder containing images to process. If not specified, an 'images' folder inside the project folder is assumed.",
        default=None,
    )
    parser.add_argument(
        "-c",
        "--config_file",
        type=str,
        help="Path of a YAML configuration file that contains user-defined options. If not specified, the default configuration for the selected matching configuration is used.",
        default=None,
    )
    (
        parser.add_argument(
            "-q",
            "--quality",
            type=str,
            choices=["lowest", "low", "medium", "high", "highest"],
            default="high",
            help="Set the image resolution for the matching. High means full resolution images, medium is half res, low is 1/4 res, highest is x2 upsampling. Default is high.",
        )
    )
    parser.add_argument(
        "-t",
        "--tiling",
        type=str,
        choices=["none", "preselection", "grid", "exhaustive"],
        default="none",
        help="Set the tiling strategy for the matching. Default is none.",
    )
    parser.add_argument(
        "-s",
        "--strategy",
        choices=[
            "matching_lowres",
            "bruteforce",
            "sequential",
            "retrieval",
            "custom_pairs",
            "covisibility",
        ],
        default="matching_lowres",
        help="Matching strategy",
    )
    parser.add_argument(
        "--pair_file", type=str, default=None, help="Specify pairs for matching"
    )
    parser.add_argument(
        "--overlap",
        type=int,
        help="Image overlap, if using sequential overlap strategy",
        default=1,
    )
    args = parser.parse_args()

    return vars(args)

# - - - - - - - - - - - COMMENTS - - - - - - - - - - -

"""
Arguments for
Input folders
Generated Figures
NUCs
matched feature buffer
plots - yes/no
correction - 1st order / 2nd order polynomial
colmap features - sift, asift, 
keypoints - number
numberKptsDetected - number of features for plotting to be successful



"""
