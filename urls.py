https://gis.nnvl.noaa.gov/arcgis/rest/services/TRUE/TRUE_daily_750m/ImageServer/exportImage?f=image&bbox=-19592951.542932015,-1010673.4999652989,20463310.971243862,9047216.42990866&imageSR=102100&bboxSR=102100&size=1536,514

sudo: required
language: python
python:
- '3.7'
os: "linux"
dist: bionic
services:
  #- xvfb
addons:
  apt:
    packages:
    - xvfb
    - xauth
    - libgtk-3-0
    - wine-dev
before_install:

install:
#- python3 get-pip.py
#- pip3 install --upgrade setuptools wheel
#- pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-16.04
#  wxPython
#- pip3 install --upgrade -r requirements.txt
-
#- wget https://www.python.org/ftp/python/2.7.9/python-2.7.9.amd64.msi
#- wine msiexec /i python-2.7.9.amd64.msi /qb
#- cd ~/.wine/drive_c/Python27
- bash travis/install_python.sh
- wine cmd /c python-3.6.8-amd64.exe PrependPath=1
- cd ~/.wine/drive_c/
- ls
- wine python.exe Scripts/pip.exe install pyinstaller
-
script:
- cd /home/travis/build/mysteriousham73/flexdoppler
- wine ~/.wine/drive_c/Python27/Scripts/pyinstaller.exe --onefile source/flexdoppler.py
- pyinstaller --onefile source/flexdoppler.py
- ls -a
- ls dist

before_deploy:
      # Set up git user name and tag this commit
      - git config --local user.name "mysteriousham73"
      - git config --local user.email "mysteriousham73@gmail.com"
      - export TRAVIS_TAG=${TRAVIS_TAG:-$(date +'%Y%m%d%H%M%S')-$(git log --format=%h -1)}
      - git tag $TRAVIS_TAG
deploy:
  skip_cleanup: true
  file_glob: true
  provider: releases
  api_key:
    secure: nfqZsJoc1SZfooO9657cDezp42aGUfwydrfpwZaJefra1aW4eCcFGS8nfOlvJl8GZOtzlIrmGLuGZGyiTOwozzFgz3PWAOn8/KqgOvNUDsWOFXKgV/K59bfPiabOikHd9gTpJ0pizdFfLzTpf+lwVbBF27z3gnBkUSyZgAxrdu4nu9gip+fgBZOSPJKvfhZTCuyeNGL4kXWujRMFfTS2E9puQ+my2H+SugTrLRiNFiUbpEn8NnmIONbudaKHbgHiAPOI06PDISE0gTDzfoSI3fr13CzAGj2u3F9Bj/4yAcgkuu7Zc96jjpAqxvRxO3pZgdgV07fQ88+0Dbcxz/iGukPlxP1JiwF+BYmEBGX9/TNPEs2eRNHGzrK+GxFwl5RKM/1kfrUy8FDynWThYfYYJfJt5chkC63sxtVzxE+fOMpRGr4FQu4ow2rSvMTnY3zU5KZxcx4PilG/AI/TI0EuTape/jUVZTadXNWNQf8rfzxrwX1urGQ6kvoRxucT8stQtkQgBFcJu+GT30++C2/IkWOuF3l7giriQcog+YsJ78DOAeY/Cser4BxKV8B4XidpGJgDtr/8hKw3gkr7zhWlPqZBhzmK/sOuAQu1irfE08e8RQuvzxiOgOzSaj018gcootoPt242/zuoUExBDFu/TDGR++tk2ioCTFTJ14mfGvY=
  file: dist/*

  on:
    repo: mysteriousham73/flexdoppler
    branch: master


WGS 1984 Web Mercator (Auxiliary Sphere) projection 
