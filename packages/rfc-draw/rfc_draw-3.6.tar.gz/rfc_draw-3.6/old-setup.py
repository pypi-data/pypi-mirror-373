from setuptools import setup

setup(
    # Here is the module name.
    name="rfc_draw",
    
    # version of the module
    version="3.2",

    # Name of Author
    author="Nevil Brownlee",

    # your Email address
    author_email="nevil.brownlee@gmail.com",

    # #Small Description about module
    description="Python package to make SVG drawings for RFCs", 
  
    long_description="python3 package to draw images for SVG-RFC-1.2 diagrams", 
    long_description_content_type="text", 
    
    # Any link to reach this module, ***if*** you have any webpage or github profile
    url="https://github.com/nevil-brownlee/rfc_draw",
    #packages=setup.find_packages(),

    # if module has dependencies i.e. if your package rely on other package at pypi.org
    # then you must add there, in order to download every requirement of package
    #     install_requires=[
    #      "package1",
    #    "package2",
    #    ],

    #license="GPL-3.0-or-later",

    # classifiers like program is suitable for python3, just leave as it is.
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0-or-later",
        "Operating System :: OS Independent",
        ]
    )
