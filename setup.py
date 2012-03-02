from setuptools import setup

setup(name = 'biodes',
      version = '1.1.2',
      packages = ['biodes'],
      requires = ["plone.memoize",
                  "names",
                  "lxml"
                 ],
      )

