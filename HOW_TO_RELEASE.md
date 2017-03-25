How to release
-----------------

* Update CHANGELOG
* Update VERSION in graphitesend/graphitesend.py
* Update version in setup.py


    git checkout -b release/x.y.z
    git commit CHANGELOG graphitesend/graphitesend.py setup.py
    git tag -a <version>
    git push --tags
    python setup.py sdist upload

