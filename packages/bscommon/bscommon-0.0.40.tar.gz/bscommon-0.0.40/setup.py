from setuptools import setup, find_packages
# 读取所有依懒
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# 读取版本号
with open("version.txt") as f:
    version = f.read()
    vs=version.split(".")
    vs[-1]=str(int(vs[-1])+1)
    version=".".join(vs)
with open("version.txt","w") as f:
    f.write(version)

setup(
    name="bscommon",
    version=version,
    packages=find_packages(where="src"),
    package_dir={'': 'src'},
    install_requires=requirements,
    author="bs",
    description="冰鼠常用操作库"
)
