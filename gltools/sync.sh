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



mkdir -p "${OUTPUTDIR}"                                      || exit 1
mkdir -p "${TEMPDIR}"                                        || exit 2

pushd "${TEMPDIR}"                                           || exit 3

echo "Cloning ${NAME}"                                       || exit 4
git clone --origin source "${URL}"                           || exit 5

pushd "${REPODIR}"                                           || exit 6

git remote add dest "${DESTURL}"

git push dest "${BRANCH}"
