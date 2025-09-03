from setuptools import find_packages, setup

setup(
    name='HasteContext', 
    version='0.2.3', 
    description='Parser-backed code-context compression using Tree-sitter',
    author='Saish; Mitali Raj; Mushtaq',
    author_email='84446371+Bainshedone@users.noreply.github.com; 129144413+Hacxmr@users.noreply.github.com; Mushtaqsaeed577@gmail.com',
    packages=find_packages(),
    install_requires=[
        'tree-sitter>=0.25.0',
        'tree-sitter-language-pack>=0.2.3,<1.0.0',
        'tiktoken>=0.11.0,<0.12.0',
        'openai>=1.99.9,<2.0.0',
        'numpy>=1.26,<3.0',
        'rank-bm25>=0.2.2,<0.3.0',
        'matplotlib>=3.10.5,<4.0.0',
        'setuptools',
        'wheel',
        'twine'
        ,'sentence-transformers'
    ],
    entry_points={
        'console_scripts': [
            'hastecontext = haste.cli:main'
        ],
    },
    # Use MANIFEST.in for more control over package contents
    include_package_data=True,
    # Explicitly exclude these files
    package_data={
        '': ['LICENSE', 'README.md'],
    },
    exclude_package_data={
        '': ['pipeline.py', 'test*.py', 'reports/*', '*.ipynb', 'message*.csv'],
    },
    url='https://github.com/Hacxmr/AST-Relevance-Compression',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    long_description_content_type='text/markdown',
    long_description=open('README.md').read() + '\n\n---\n\n**Authors**: Saish, Mitali Raj, Mushtaq',
)
