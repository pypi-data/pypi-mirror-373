from setuptools import setup, find_packages
setup(
      name="lua.rock",
      include_package_data=True,
      version="1.0.0",
      description = "Generate rock file",
      summary = "This utility is used for creating rock file from specific directory and rockspec",
      license = "GPLv3",
      url = "https://github.com/huakim/python-create-luarock",
      py_modules=['lua.rock'],
      packages = ['lua/rock'],
      entry_points = {
         'console_scripts': [
            'create_luarock = lua.rock:main_create_rock'
         ],
      },
      install_requires=['luadata.luatable'],
)
