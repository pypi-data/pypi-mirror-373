export PROJECT=XmovCGTools
export BASE_DIR=/data/apks/${PROJECT}

export FOLDER=${BASE_DIR}/${CI_COMMIT_TAG:-test/`date "+%Y%m%d"`}
mkdir -p ${FOLDER}

zip ${FOLDER}/${PROJECT}.zip -r ./*  -x deploy.sh -x write_info.py
chmod +x ./write_info.py
python3 ./write_info.py ${FOLDER}/${PROJECT}.zip
export DIST_FOLDER=${BASE_DIR}/dist
mkdir -p ${DIST_FOLDER}
if [[ _$CI_COMMIT_TAG != _ ]]; then
    ~/ossutil64 -c ~/.ossutilconfig cp -rf ${FOLDER} oss://xmov-distribution/${PROJECT}/${CI_COMMIT_TAG:-test/`date "+%Y%m%d"`}
    cp ${FOLDER}/*.zip ${DIST_FOLDER}
    cp ${FOLDER}/info.json ${DIST_FOLDER}
    ~/ossutil64 -c ~/.ossutilconfig cp  -f ${DIST_FOLDER}/*.zip oss://xmov-distribution/${PROJECT}/dist/
    ~/ossutil64 -c ~/.ossutilconfig cp -f ${DIST_FOLDER}/info.json oss://xmov-distribution/${PROJECT}/dist/

fi
info_file=${FOLDER}/info.json
if test -f "${info_file}"; then
    cp ${info_file} ${DIST_FOLDER}
fi