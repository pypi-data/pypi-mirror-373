from setuptools import find_packages, setup

setup(
    name="lifeguard-notification-google-chat",
    version="0.0.9",
    url="https://github.com/LifeguardSystem/lifeguard-notification-google-chat",
    author="Diego Rubin",
    author_email="contact@diegorubin.dev",
    license="GPL2",
    scripts=[],
    include_package_data=True,
    description="Lifeguard integration with Google Chat",
    install_requires=["lifeguard"],
    classifiers=["Development Status :: 3 - Alpha"],
    packages=find_packages(),
)
