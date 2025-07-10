#!/bin/bash

SCRIPT_DIR=$(cd `dirname $0` && pwd)
cd $SCRIPT_DIR
GAME_TITLE=crash2
zip -qo -r ./${GAME_TITLE}.apworld ./${GAME_TITLE}

OUTPUT=${GAME_TITLE}jp_ap
rm -rf $OUTPUT $OUTPUT.zip
mkdir -p $OUTPUT
mv -f ./${GAME_TITLE}.apworld ${OUTPUT}
if [[ -e ./${GAME_TITLE}-ap-poptracker ]]; then
    zip -r ./${GAME_TITLE}-ap-poptracker{.zip,}
    mv ${GAME_TITLE}-ap-poptracker.zip $OUTPUT
fi
# zip -r $OUTPUT{.zip,}

