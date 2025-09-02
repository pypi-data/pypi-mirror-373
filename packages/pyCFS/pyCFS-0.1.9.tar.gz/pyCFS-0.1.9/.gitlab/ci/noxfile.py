import nox


@nox.session
# @nox.parametrize
def tests(session):
    # Change working directory to the root of the repository
    session.chdir("../..")
    # Install dev requirements
    session.install("-r", "requirements/dev.txt", log=True)
    # Install pyCFS with vtk dependency
    session.install(".[all]", log=True)
    # Run tests with pytest
    session.run("pytest", "--cov=pycfs", "--cov-report=xml", log=True)
