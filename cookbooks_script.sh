#!/bin/bash
# Script to download all necessary cookbooks for Chef and run vagrant up.

mkdir cookbooks && cd cookbooks/

git clone https://github.com/chef-cookbooks/apt.git
git clone https://github.com/chef-cookbooks/build-essential.git
git clone https://github.com/chef-cookbooks/chef_handler.git
git clone https://github.com/chef-cookbooks/compat_resource.git
git clone https://github.com/chef-cookbooks/dmg.git
git clone https://github.com/chef-cookbooks/git.git
git clone https://github.com/chef-cookbooks/mingw.git
git clone https://github.com/chef-cookbooks/openssl.git
git clone https://github.com/chef-cookbooks/vim.git
git clone https://github.com/chef-cookbooks/windows.git
git clone https://github.com/chef-cookbooks/yum-epel.git
git clone https://github.com/chef-cookbooks/yum.git
git clone https://github.com/daptiv/seven_zip.git
git clone https://github.com/poise/python.git
git clone https://github.com/sethvargo/chef-sugar.git

cd .. && vagrant up

vagrant ssh -c "/vagrant/after_installation_script.sh"
vagrant ssh