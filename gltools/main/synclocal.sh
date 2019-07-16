#!/bin/bash
# wrapper script because I can't be arsed to wrap this all in quotes
declare -r SCRIPTPATH="$(readlink -f $0)"
declare -r SCRIPTNAME="$(basename $SCRIPTPATH .sh)"
declare -r SCRIPTDIR="$(dirname $SCRIPTPATH)"

declare -r BRANCH="%(branch)s"
declare -r NAME="%(name)s"
declare -r DST_REPO_URL="%(basedir)s/%(path_with_namespace)s.git"
declare -r SRC_REPO_URL="%(ssh_url_to_repo)s"
declare -r TEMPDIR="%(tempdir)s/%(path)s"

REPODIR=$(basename "${SRC_REPO_URL}" .git)

mkdir -p "${TEMPDIR}"                                        || exit $((LINENO+1000))
pushd "${TEMPDIR}" >/dev/null 2>&1                           || exit $((LINENO+1000))
echo "cloning ${NAME}"
git clone --origin "${SOURCE:-source}" "${SRC_REPO_URL}"     || exit $((LINENO+1000))
pushd "${REPODIR}" >/dev/null 2>&1                           || exit $((LINENO+1000))

if [ ! -d "${DST_REPO_URL}" ]
then
  mkdir -p "${DST_REPO_URL}"
  pushd "${DST_REPO_URL}"
  git init --bare
  popd
fi

echo "add remote dest"
git remote add dest "file://${DST_REPO_URL}"                 || exit $((LINENO+1000))
echo "push to remote dest"
git push dest "${BRANCH}" --tags                             || exit $((LINENO+1000))
popd >/dev/null 2>&1                                         || exit $((LINENO+1000))
rm -rf "${REPODIR}"                                          || exit $((LINENO+1000))
popd >/dev/null 2>&1                                         || exit $((LINENO+1000))
