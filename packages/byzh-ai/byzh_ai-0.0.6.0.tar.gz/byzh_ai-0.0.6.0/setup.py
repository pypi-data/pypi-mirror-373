from setuptools import setup, find_packages
import byzh_ai

setup(
    name='byzh_ai',
    version=byzh_ai.__version__,
    author="byzh_rc",
    description="更方便的深度学习",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'byzh_core==0.0.6.0', # !!!!!
        'thop',
        'matplotlib',
        'seaborn',
    ],
)
