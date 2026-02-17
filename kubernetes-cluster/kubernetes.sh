#!/bin/bash
set -e 
export KUBERNETES_VERSION=1.29
export CRIO_VERSION=1.29
sudo apt-get update -y
sudo apt install -y software-properties-common curl gpg
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab
sudo modprobe overlay
sudo modprobe br_netfilter

cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

sudo sysctl --system

sudo apt-get update -y

sudo mkdir -p /etc/apt/keyrings/

curl -fsSL https://download.opensuse.org/repositories/isv:/cri-o:/stable:/v${CRIO_VERSION}/deb/Release.key |
    gpg --dearmor --yes -o /etc/apt/keyrings/cri-o-apt-keyring.gpg 

echo "deb [signed-by=/etc/apt/keyrings/cri-o-apt-keyring.gpg] https://download.opensuse.org/repositories/isv:/cri-o:/stable:/$CRIO_VERSION/deb/ /" |
    tee /etc/apt/sources.list.d/cri-o.list

sudo apt-get update -y

curl -fsSL https://pkgs.k8s.io/core:/stable:/v${KUBERNETES_VERSION}/deb/Release.key |
    gpg --dearmor --yes -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg 

echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v${KUBERNETES_VERSION}/deb/ /" |
    tee /etc/apt/sources.list.d/kubernetes.list

sudo apt-get update -y
sudo apt-get install -y cri-o kubelet kubeadm kubectl
sudo systemctl enable --now crio.service
sudo apt-mark hold kubelet kubeadm kubectl