from setuptools import Extension, setup

setup(
    include_package_data=True,
    package_data={'lfo': ['py.typed']},
    ext_package = 'lfo',
    ext_modules=[
        Extension('_lfo', ['src_c/lfo.c'], include_dirs=["include"]),
    ]
)
