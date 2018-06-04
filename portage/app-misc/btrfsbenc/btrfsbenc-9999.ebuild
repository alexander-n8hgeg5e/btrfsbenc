# Copyright 1999-2018 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

EAPI=6
inherit git-r3
DESCRIPTION="btrfs backup tool. config: edit code"
HOMEPAGE=""
EGIT_REPO_URI="${CODEDIR}""/code/btrfsbenc https://github.com/alexander-n8hgeg5e/btrfsbenc.git"
#  to get this commit installed, you need a later commit,
#  because this commit can not contain this ebuild.
#  check out the following commit that updates the manifest.
EGIT_COMMIT="3ee444c9a2c4257e38403e1bb836ca09a49504fa"
LICENSE=""
SLOT="0"
KEYWORDS=""
IUSE=""

DEPEND=""
RDEPEND="${DEPEND}"


src_install(){
  dobin btrfsbenc
}
