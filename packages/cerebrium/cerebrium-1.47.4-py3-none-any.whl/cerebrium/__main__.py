import os

from cerebrium.main import cli


def main():
    package_name = "cerebrium"

    path_dirs = os.environ["PATH"].split(os.pathsep)
    found = False
    for dir in path_dirs:
        if os.path.exists(os.path.join(dir, package_name)):
            print(f"{package_name} found in PATH at {dir}")
            found = True
            break
    if not found:
        print(f"{package_name} not found in PATH.")

    cli()


if __name__ == "__main__":
    main()
