from setuptools import setup, find_packages


def parse_requirements(filename):
    with open(filename, 'r') as file:
        return file.read().splitlines()


setup(
    name="PiAlarmAdapter",
    version="0.0.1",
    author="Francesco Scanferla",
    author_email="info@francescoscanferla.it",
    description="Application to manage contact sensors and send messages with state change to an MQTT Broker",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/francescoscanferla/PiAlarmAdapter",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
    install_requires=parse_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            'pi_alarm_adapter=app.__main__:main',
        ],
    },
)
