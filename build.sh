VIRTUAL_ENV='env'
PACKAGE_NAME='predictor'
PACKAGE_FILE='build/package.zip'
ENTRY_POINT='go.py'

virtualenv $VIRTUAL_ENV
source "$VIRTUAL_ENV/bin/activate"
pip install -r requirements.txt
zip -u "$PACKAGE_FILE" "$ENTRY_POINT"
pushd "$VIRTUAL_ENV/lib/python2.7/site-packages"
zip -ru "$(dirs -l +1)/$PACKAGE_FILE" .
popd
