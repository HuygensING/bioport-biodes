from setuptools import setup

setup(name = 'biodes',
      version = '1.1.1dev',
      packages = ['biodes'],
      requires = ["plone.memoize",
                  "names",
                 ],
      )

