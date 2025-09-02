from setuptools import setup

setup(
    name='mnspy',
    version='0.9.18',
    packages=['mnspy', 'mnspy.raíces', 'mnspy.derivada', 'mnspy.integrales', 'mnspy.interpolación',
              'mnspy.ecuaciones_algebraicas_lineales', 'mnspy.ecuaciones_diferenciales_ordinarias',
              'mnspy.ecuaciones_diferenciales_parciales', 'mnspy.ecuaciones_diferenciales_parciales.mdf',
              'mnspy.ecuaciones_diferenciales_parciales.mef', 'mnspy.ecuaciones_diferenciales_parciales.mvf'],
    url='https://github.com/EdwinSoft/mnspy',
    package_data={
        '': ['README.md', 'requirements.txt'],
    },
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    author='Edwin Córdoba',
    author_email='edwin.cordoba@gmail.com',
    description='Paquete didáctico para métodos numéricos',
    install_requires=['scipy', 'sympy', 'matplotlib', 'tabulate', 'ipython', 'ipympl', 'jupyterlab-myst',
                      'jupyterlab-language-pack-es-ES', 'PyQt6', 'pandas', 'gmsh', 'openpyxl'],
    python_requires=">=3.10"
)
