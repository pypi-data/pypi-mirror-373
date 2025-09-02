from setuptools import setup, find_packages

setup(
    # Forzar que setuptools detecte que hay archivos nativos
    has_ext_modules=lambda: True,  # Esto fuerza platform-specific
    packages=find_packages(),
    package_data={
        'tacotiff': ['drivers/*.so', 'drivers/*.txt'],
    },
    zip_safe=False,  # Importante para .so files
)