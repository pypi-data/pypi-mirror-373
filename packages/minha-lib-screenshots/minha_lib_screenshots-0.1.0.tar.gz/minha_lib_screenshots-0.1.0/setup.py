from setuptools import setup, find_packages

setup(
    name='minha_lib_screenshots',
    version='0.1.0',
    author='Seu Nome',
    author_email='seuemail@example.com',
    description='Uma biblioteca para capturar screenshots em áreas específicas, tela inteira ou janelas.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/seu-usuario/minha_lib_screenshots', # Mude para seu repositório
    packages=find_packages(),
    install_requires=[
        'mss',
        'Pillow',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)