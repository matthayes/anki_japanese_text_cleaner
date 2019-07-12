#!/usr/bin/env bash

set -e

ROOT_DIR=$(pwd)
TARGET_DIR=$ROOT_DIR/target
rm -rf $TARGET_DIR
mkdir -p $TARGET_DIR
TEMP_DIR=`mktemp -d`
echo Using temp dir $TEMP_DIR
cp manifest.json $TEMP_DIR
cp japanese_text_cleaner/*.py $TEMP_DIR
mkdir $TEMP_DIR/db
cp japanese_text_cleaner/db/*.py $TEMP_DIR/db
mkdir $TEMP_DIR/dialogs
cp japanese_text_cleaner/dialogs/*.py $TEMP_DIR/dialogs
mkdir $TEMP_DIR/text
cp japanese_text_cleaner/text/*.py $TEMP_DIR/text
mkdir $TEMP_DIR/user_files
echo "This folder stores files to be persisted across updates to plugin." > $TEMP_DIR/user_files/README.txt
pushd $TEMP_DIR
zip -r anki_japanese_text_cleaner.zip .
echo Moving package to $TARGET_DIR
mv anki_japanese_text_cleaner.zip $TARGET_DIR
popd
rm -rf $TEMP_DIR