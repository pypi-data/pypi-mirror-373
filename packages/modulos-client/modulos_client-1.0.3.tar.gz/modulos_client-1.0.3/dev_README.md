### Release process
In order to release a new version of the client, the following steps should be followed:

- Create a new release on github
  - Go to the [releases page](https://github.com/Modulos/modulos_client/releases)
  - Click on `Draft a new release`
  - Set the tag version to the version you want to release
  - Set the target to `main`
  - Set the title to the version you want to release
  - Generate release notes or write them manually
  - Click on `Publish release`
- There is a [github action](https://github.com/Modulos/modulos_client/blob/main/.github/workflows/publish_pypi.yml) that will automatically publish the new version to PyPi
- Check that the new version is available on [PyPi](https://pypi.org/project/modulos-client/) after a few minutes
