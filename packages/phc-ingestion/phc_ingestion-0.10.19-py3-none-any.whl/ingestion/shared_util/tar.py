import sys
import tarfile


def unpack(tarball, outpath):
    # Extract all files into the new directory
    tar_type = ""
    if tarball.endswith("tar.gz"):
        tar_type = "r:gz"
    elif tarball.endswith("tar"):
        tar_type = "r:"
    else:
        raise RuntimeError(
            f"Wrong input format chosen for file {tarball}. You must upload a tar or tar.gz file\n"
        )

    tar = tarfile.open(tarball, tar_type)
    tar.extractall(path=outpath)
    tar.close()
