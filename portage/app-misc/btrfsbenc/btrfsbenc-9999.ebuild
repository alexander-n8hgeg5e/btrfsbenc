# Copyright 1999-2018 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

EAPI=6
inherit git-r3
DESCRIPTION="btrfs backup tool. config: edit code"
HOMEPAGE=""
EGIT_REPO_URI="${CODEDIR}""/btrfsbenc https://github.com/alexander-n8hgeg5e/btrfsbenc.git"
#  to get this commit installed, you need a later commit,
#  because this commit can not contain this ebuild.
#  check out the following commit that updates the manifest.
EGIT_COMMIT="8d2ce40762ac5defa196d49ddb42211dd0120f8a"
LICENSE=""
SLOT="0"
KEYWORDS=""
IUSE=""

DEPEND=""
RDEPEND="${DEPEND}"


src_install(){
  dobin btrfsbenc
}
