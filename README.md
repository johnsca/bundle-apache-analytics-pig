# Apache Analytics with Pig

This bundle is a 7 node cluster designed to scale out. Built around Apache
Hadoop components, it contains the following units:

* 1 HDFS Master
* 1 HDFS Secondary Namenode
* 1 YARN Master
* 3 Compute Slaves
* 1 Pig
  - 1 Plugin (colocated on the Pig unit)


## Usage
Deploy this bundle using juju-quickstart:

    juju quickstart u/bigdata-dev/apache-analytics-pig

See `juju quickstart --help` for deployment options, including machine 
constraints and how to deploy a locally modified version of the
apache-analytics-pig bundle.yaml.


## Testing the deployment

### Smoke test HDFS admin functionality
Once the deployment is complete and the cluster is running, ssh to the HDFS
Master unit:

    juju ssh hdfs-master/0

As the `ubuntu` user, create a temporary directory on the Hadoop file system.
The steps below verify HDFS functionality:

    hdfs dfs -mkdir -p /tmp/hdfs-test
    hdfs dfs -chmod -R 777 /tmp/hdfs-test
    hdfs dfs -ls /tmp # verify the newly created hdfs-test subdirectory exists
    hdfs dfs -rm -R /tmp/hdfs-test
    hdfs dfs -ls /tmp # verify the hdfs-test subdirectory has been removed
    exit

### Smoke test YARN and MapReduce
Run the `terasort.sh` script from the Pig unit to generate and sort data. The
steps below verify that Pig is communicating with the cluster via the plugin
and that YARN and MapReduce are working as expected:

    juju ssh pig/0
    ~/terasort.sh
    exit

### Smoke test HDFS functionality from user space
From the Pig unit, delete the MapReduce output previously generated by the
`terasort.sh` script:

    juju ssh pig/0
    hdfs dfs -rm -R /user/ubuntu/tera_demo_out
    exit

### Smoke test Pig in Local Mode
SSH to the Pig unit and run pig as follows:

    juju ssh pig/0
    pig -x local
    quit
    exit

### Smoke test Pig in MapReduce Mode
SSH to the Pig unit and test in MapReduce mode as follows:

    juju ssh pig/0
    hdfs dfs -copyFromLocal /etc/passwd /user/ubuntu/passwd
    echo "A = load '/user/ubuntu/passwd' using PigStorage(':');" > /tmp/test.pig
    echo "B = foreach A generate \$0 as id; store B into '/tmp/pig.out';" >> /tmp/test.pig
    pig -l /tmp/test.log /tmp/test.pig
    hdfs dfs -cat /tmp/pig.out/part-m-00000
    exit


## Scale Out Usage
This bundle was designed to scale out. To increase the amount of Compute
Slaves, you can add units to the compute-slave service. To add one unit:

    juju add-unit compute-slave

Or you can add multiple units at once:

    juju add-unit -n4 compute-slave


## Contact Information

- <bigdata-dev@lists.launchpad.net>


## Help

- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju community](https://jujucharms.com/community)
