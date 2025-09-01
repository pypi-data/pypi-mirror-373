import argparse

# Parse arguments
parser = argparse.ArgumentParser(description="Generate HTML for media directories.")
parser.add_argument(
    "--random",
    type=int,
    help="number of images to sample from all boards. "
    "use a number higher than the number of total images, or a negative number,"
    " to shuffle instead",
)
parser.add_argument(
    "--ranDir",
    type=str,
    help="Directory to search images in for --random",
)
parser.add_argument("--dir", type=str, help="Directory to use for the images")
# parser.add_argument("--csvs", nargs="+", help="List of CSV files to use")
parser.add_argument(
    "--useLists", action="store_true", help="Use list files from config"
)
parser.add_argument("--imageLists", nargs="+", help="List of imagelist files to use.")
parser.add_argument("--col", type=int, help="Number of columns to default to")
parser.add_argument("--margin", type=int, help="Margin in px")

parser.add_argument(
    "--sidecar", action="store_true", default=False, help="use links from sidecar files"
)
parser.add_argument(
    "--includeLocal",
    action="store_true",
    default=False,
    help="include local files if using lists",
)
parser.add_argument(
    "--makeConfig",
    action="store_true",
    default=False,
    help="include local files if using lists",
)

# parser.add_argument("--rancount", type=int, help="number of images to sample from all boards. use a number higher than the number of total images to shuffle instead")
parser.add_argument(
    "--upload", action="store_true", default=False, help="Upload images to Imgchest"
)
parser.add_argument("--config", type=str, default=False, help="config file to use")
parser.add_argument(
    "--saveBoards", action="store_true", help="Save generated boards to PostgreSQL"
)
parser.add_argument(
    "--gitPush", action="store_true", help="Push outputDir to existing Git repo"
)
parser.add_argument("--useSaved", action="store_true", help="use only saved images")

args = parser.parse_args()
