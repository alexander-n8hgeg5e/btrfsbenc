# Copyright 1999-2018 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

EAPI=6
inherit git-r3
DESCRIPTION="btrfs backup tool. config: edit code"
HOMEPAGE=""
EGIT_REPO_URI=""

LICENSE=""
SLOT="0"
KEYWORDS=""
IUSE=""

DEPEND=""
RDEPEND="${DEPEND}"


src_install(){
  dobin btrfsbenc
}
