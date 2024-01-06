#!/bin/bash

set -e 

NAME="reverso"
REV=${1:-tip}
ANKI_ID=2060267742

git status
#hg st

CUR_DIR=$(pwd)
VER=$(awk -F"'" '/VERSION/ {print $2}' $NAME/_version.py)
PLUGIN_DIR=$(pwd)
ANKI_PKG=/tmp/$NAME-$VER.ankiaddon
cd /tmp
DEST_DIR=$(basename $PLUGIN_DIR)-$VER
rm -Rf $DEST_DIR
git clone $PLUGIN_DIR $DEST_DIR
git -R $DEST_DIR up $REV
#hg clone $PLUGIN_DIR $DEST_DIR
#hg -R $DEST_DIR up $REV
cd $DEST_DIR/$NAME
cp ../*md .

zip -r $ANKI_PKG *

ls -l $ANKI_PKG
cd ..
$CUR_DIR/readme2anki > /dev/null
echo -e "\nUpload to https://ankiweb.net/shared/info/$ANKI_ID"
