#!/bin/bash
# wrapper script because I can't be arsed to wrap this all in quotes
declare -r SCRIPTPATH="$(readlink -f $0)"
declare -r SCRIPTNAME="$(basename $SCRIPTPATH .sh)"
declare -r SCRIPTDIR="$(dirname $SCRIPTPATH)"



declare -r NAME="%(name)s"
declare -r XPATH="%(path)s"
declare -r PATH_WITH_NAMESPACE="%(path_with_namespace)s"

declare -r DST_SSH_REPO_URL="%(ssh_url_to_repo)s"
declare -r SRC_SSH_REPO_URL="%(src_ssh_url_to_repo)s"

declare -r TEMPDIR="%(tempdir)s/%(path)s"
declare -r SOURCE="%(source)s"
declare -r BRANCH="%(branch)s"

REPODIR=$(basename "${SRC_SSH_REPO_URL}" .git)

mkdir -p "${TEMPDIR}"                                        || exit $((LINENO+1000))
pushd "${TEMPDIR}" >/dev/null 2>&1                           || exit $((LINENO+1000))
echo "cloning ${NAME}"
git clone --origin "${SOURCE:-source}" "${SRC_SSH_REPO_URL}" || exit $((LINENO+1000))
pushd "${REPODIR}" >/dev/null 2>&1                           || exit $((LINENO+1000))
echo "add remote dest"
git remote add dest "${DST_SSH_REPO_URL}"                    || exit $((LINENO+1000))
echo "push to remote dest"
git push dest "${BRANCH}"                                    || exit $((LINENO+1000))
popd >/dev/null 2>&1                                         || exit $((LINENO+1000))
rm -rf "${REPODIR}"                                          || exit $((LINENO+1000))
popd >/dev/null 2>&1                                         || exit $((LINENO+1000))
