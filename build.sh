VIRTUAL_ENV='env'
PACKAGE_NAME='predictor'
PACKAGE_FILE='build/package.zip'

virtualenv $VIRTUAL_ENV
source "$VIRTUAL_ENV/bin/activate"
pip install -r requirements.txt
zip -i {*,"$PACKAGE_NAME/*"}.py -ru "$PACKAGE_FILE" .
zip -ru "$PACKAGE_FILE" "$VIRTUAL_ENV/lib/python2.7/site-packages"
