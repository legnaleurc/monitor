from ..base import FlavorFactory


class DockerFlavor(FlavorFactory):

    def do_create_browsers(self):
        return (
            DockerFirefoxESR(),
            DockerFirefoxRelease(),
            DockerFirefoxBeta(),
            DockerFirefoxESR(),
        )
