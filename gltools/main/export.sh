#!/bin/bash
# wrapper script because I can't be arsed to wrap this all in quotes
declare -r SCRIPTPATH="$(readlink -f $0)"
declare -r SCRIPTNAME="$(basename $SCRIPTPATH .sh)"
declare -r SCRIPTDIR="$(dirname $SCRIPTPATH)"
declare -r GROUP_NAME="%(group_name)s"
declare -r GROUP_PATH="%(group_path)s"
declare -r TYPE="%(type)s"
declare -r NAME="%(name)s"
declare -r XPATH="%(path)s"
declare -r PATH_WITH_NAMESPACE="%(path_with_namespace)s"
declare -r URL="%(url)s"
declare -r OUTPUTDIR="%(outputdir)s/%(group_path)s"
declare -r TEMPDIR="%(tempdir)s/%(group_path)s"
declare -r OUTPUTFILE="%(outputdir)s/%(group_path)s/%(path)s"

REPODIR=$(basename "${URL}" .git)

function mkbundle()
{
  local outputfile=$1; shift
  git bundle create ${outputfile} master
  RETV=$?
  [[ "${RETV}" = "0" ]] && return 0
  echo "exit code: ${RETV}"
  exit 7
}

function archive()
{
  local path=$1; shift
  local tempdir="${TEMPDIR}/archive"
  mkdir -p "${tempdir}"

  git archive --prefix=${path}/ HEAD | tar -xf - -C "${tempdir}"

  install_roles "${tempdir}/${path}"

  if rsync -a --delete "${tempdir}/${path}/" "${OUTPUTFILE}/"
  then
    return 0
  else
    exit 10
  fi

}

function install_roles()
{
  local archdir=$1; shift
  [[ -e "${archdir}/roles/requirements.yml" ]] || return 0
  ansible-galaxy install -r "${archdir}/roles/requirements.yml" -p "${archdir}/roles"
}


mkdir -p "${OUTPUTDIR}"                                      || exit 1
mkdir -p "${TEMPDIR}"                                        || exit 2

pushd "${TEMPDIR}"                                           || exit 3

echo "Cloning ${NAME}"                                       || exit 4
git clone "${URL}"                                           || exit 5

pushd "${REPODIR}"                                           || exit 6

case $TYPE in 
  bundle) mkbundle "${OUTPUTFILE}.bundle";;
  portable) archive "${XPATH}";;
  *) echo "failed to handle $TYPE"; exit 8 ;;
esac

popd
popd
