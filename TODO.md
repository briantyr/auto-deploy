*** Additional functionality (TOEO)***
- Read instance(s) configuraion from a single configuration file using the
ConfigParser module and implement AWS instance mapping to between config file
and some sort of dynamic inventory collection.  Therefore, removing a config
entry correlates to instance deletion and upon next execution of he Python code,
delete the instance that is no longer in the config file.
   - Option 1: Use NoSQL for inventory host storage (Mongo, Redis, etc.)
   - Option 2: Use full blown relational SQL data or sqlite with ORM to manage
               inventory.
   - Option 3: Use generic text file for dynamic inventory similar to ansible,
               calling it 'hosts', and check for valid AWS private IP's.
   - Option 4: Investigate using Fabric & boto for automatic management, removing
               any burden of responsibility on custom code + additional unit
               tests for code coverage.
- Automatic unit testing for provisioned infrastructure, including cloud-init
  runs with user-data.
- Automatic unit testing for code coverage to not break existing code on updates.
- Use argparse to accept arguments such as "start-all" to start or ensure that 
  all EC2 instances are currently running.
- Dynamically create and attach EBS volume to an existing instance.
- Start AWS Services in a particular order.  If 1 out of 3 'ordered' instances
  are stopped and the other two are running, but the one stopped must be started
  first, then stop the others and call them in the correct:  