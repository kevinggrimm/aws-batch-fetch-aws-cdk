FROM amazonlinux:latest
RUN yum -y install which unzip aws-cli
ADD fetch_and_run.sh /usr/local/bin/fetch_and_run.sh

# Default directory where the image is used to star a container
WORKDIR /tmp

# Default user that the container executes as
USER nobody

# Command called when the container is started
# When running a Batch job, it is passed the contents
# of the command parameter
ENTRYPOINT ["/usr/local/bin/fetch_and_run.sh"]
