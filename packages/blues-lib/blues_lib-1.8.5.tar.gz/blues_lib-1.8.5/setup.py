from setuptools import setup,find_packages

setup(
  name="blues_lib", # package name
  version="1.8.5", # package version
  long_description=open('README.md').read(),
  long_description_content_type='text/markdown',
  # must include __init__.py in the module
  packages=find_packages(), # package module
  # add from requirement.txt,本地测试注释所有包，不能从镜像立即安装
  package_data={
    'blues_lib': ['config/**/*.yaml'],
  },

  install_requires=[
    'Pillow>=10.3.0',
    'Requests>=2.31.0',
    'selenium>=4.25.0',
    'selenium_wire>=5.1.0',
    'setuptools>=47.1.0',
    'webdriver_manager>=4.0.2',
    'tld==0.13',
    'blinker==1.6.2', # can't install the new >1.8.2 version 
    'pymysql==1.0.2',
    'beautifulsoup4==4.9.3',
    'pandas==2.0.3',
    'pyperclip==1.9.0',
    'undetected_chromedriver==3.5.5',
    'paramiko==3.5.1',
    'psutil==7.0.0',
    'ddt==1.7.2',
    'pyyaml==6.0.2',
    'pytest==8.3.5',
    'pytest-html==4.1.1',
    'pytest-sugar==1.0.0',
    'pytest-cov==6.1.1',
    'jsonschema==4.21.1',
    'twine==6.1.0',
    'json5==0.12.0',
    'pyhocon==0.3.61',
    'pyautogui==0.9.54',
  ] # package dependency
)
