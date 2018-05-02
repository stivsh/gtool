from setuptools import setup

setup(
    name='gosha_tools_for_anal_sex_with_zebra',    # This is the name of your PyPI-package.
    version='0.1',                          # Update the version number for new releases
    scripts=['gosha_load_tool'],                  # The name of your scipt, and also the command you'll be using for calling it
    install_requires=['BeautifulSoup>=3.2.1', 'requests>=2.12.5']
 )
