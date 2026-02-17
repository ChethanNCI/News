# STEP 1: Grab Kaniko from the official debug image
FROM gcr.io/kaniko-project/executor:v1.23.2-debug AS kaniko

# STEP 2: Build your actual Jenkins Agent
FROM jenkins/inbound-agent:latest-jdk21

USER root

# 1. Install kubectl and basic utilities
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/

# 2. Inject Kaniko into the agent
# We copy the executor binary and the SSL certs Kaniko needs to talk to Harbor
COPY --from=kaniko /kaniko/executor /usr/local/bin/kaniko
COPY --from=kaniko /kaniko/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt

# Create the directory where Kaniko looks for Docker credentials
RUN mkdir -p /kaniko/.docker

# 3. Certificate & Keytool logic (Keeping your perfect setup)
COPY jenkins.crt /usr/local/share/ca-certificates/jenkins-ca.crt
COPY harbor.crt  /usr/local/share/ca-certificates/harbor-ca.crt
COPY root-ca.crt /usr/local/share/ca-certificates/root-ca.crt

RUN update-ca-certificates

RUN keytool -importcert -noprompt -trustcacerts -alias jenkins-ca -file /usr/local/share/ca-certificates/jenkins-ca.crt -keystore $JAVA_HOME/lib/security/cacerts -storepass changeit && \
    keytool -importcert -noprompt -trustcacerts -alias harbor-ca -file /usr/local/share/ca-certificates/harbor-ca.crt -keystore $JAVA_HOME/lib/security/cacerts -storepass changeit && \
    keytool -importcert -noprompt -trustcacerts -alias root-ca -file /usr/local/share/ca-certificates/root-ca.crt -keystore $JAVA_HOME/lib/security/cacerts -storepass changeit

# Remain as root to ensure Kaniko has permission to unpack filesystems during builds
USER root