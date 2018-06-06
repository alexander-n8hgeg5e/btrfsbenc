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
EGIT_COMMIT="7a23b185e5a1caa05d5c06bc9250c2cac26df591"
LICENSE=""
SLOT="0"
KEYWORDS=""
IUSE=""

DEPEND=""
RDEPEND="${DEPEND}"


src_install(){
  dobin btrfsbenc
}
