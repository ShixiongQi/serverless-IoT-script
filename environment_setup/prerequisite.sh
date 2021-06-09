sudo apt-get update
sudo wget -O /usr/local/bin/bazel https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64
sudo chmod +x /usr/local/bin/bazel

sudo apt install -y libtool 
sudo apt install -y cmake 
sudo apt install -y automake 
sudo apt install -y autoconf
sudo apt install -y make
sudo apt install -y ninja-build
sudo apt install -y curl
sudo apt install -y unzip
sudo apt install -y virtualenv
sudo apt install -y ruby
sudo apt install -y ruby-dev
sudo apt install -y rubygems
sudo apt install -y build-essential
sudo apt install -y rpm 
sudo apt install -y libc++-dev
sudo apt install -y libicu-dev
sudo gem install --no-document fpm
sudo apt install -y docker.io

wget https://releases.llvm.org/9.0.0/clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz
tar xvf clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz
mv clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-18.04 clang+llvm

path=`pwd`

echo "export PATH=$PATH:${path}/clang+llvm/bin" >> ~/.bashrc
echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${path}/clang+llvm/lib" >> ~/.bashrc

echo "please source ~/.bashrc"

