from setuptools import setup, Extension

setup(
    name="dscol",
    version="0.0.0",
    ext_modules=[
        Extension(
            "dscol.linked",
            sources=["src/dscol/linked/mod_linked.c", "src/dscol/linked/singly.c"],
            include_dirs=["src/dscol/linked"]
        )
    ],
)
