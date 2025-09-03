import argparse
from importlib.resources import files
import os
import shutil
import sys
from pathlib import Path


CPP_PACKAGE_PATH = None
try:
    import karabo_cpp

    CPP_PACKAGE_PATH = os.path.abspath(karabo_cpp.__path__[0])

except ImportError:
    pass

ACTIVATE_SH = """
#/bin/bash

# exports leading to this environment
export KARABO={karabo_path}

# additionally export the var/environment part
pushd "$KARABO/var/environment" >/dev/null
for var in $(ls)
do
   export $var="$(cat $var)"
done
popd >/dev/null
"""

def karabo_activate() -> None:
    parser = argparse.ArgumentParser(
        "karabo_activate",
        usage="karabo_activate OPTIONS...",
        description="Creates or modifies a Karabo environment, or inplace in the site-packages directory. When first run, the --init-to option is required.")
    
    parser.add_argument("--init-to", default=None,
                        help="Path at which a Karabo environment is created. Can be ommited if karabo_activate was previously executed, and a ~/.karabo file pointing to a path exists")
    
    parser.add_argument("--backbone", action="store_true",
                        help="Use this option if you would like to have the services populated with backbone services.")
    
    parser.add_argument("--broker-host", type=str, default=None,
                        help="Use this to setup or modify the default broker host. Address should be in the form `amqp://host:port`")
    
    parser.add_argument("--broker-topic", type=str, default=None,
                        help="Use this to setup or modify the default broker topic.")
    
    parser.add_argument("--project-db", type=str, default=None,
                        help="Specify the project database backend. Either `file` to use the file backedn, or `host:port` of an `existDB` installation.")
    
    parser.add_argument("--project-db-user", type=str, default=None,
                        help="Specify the project database user when using exist db backend.")
    
    parser.add_argument("--project-db-pw", type=str, default=None,
                        help="Specify the project database password when using exist db backend.")
    
    parser.add_argument("--influx-db", type=str, default=None,
                        help="Specify the influx database backend. Either a single tcp://host:port combination for reading and writing, or tcp://read_host:port,tcp://write_host:port")
   
    parser.add_argument("--influx-db-name", type=str, default=None,
                        help="Specify an Influx DB name, or set it to an empty string to use the Karabo broker topic.")
    
    parser.add_argument("--influx-db-read-user", type=str, default=None,
                        help="Influx DB read user. If only write user is given this user will also be used for reading.")
    
    parser.add_argument("--influx-db-write-user", type=str, default=None,
                        help="Influx DB write user. If only write user is given this user will also be used for reading.")
    
    parser.add_argument("--influx-db-read-pw", type=str, default=None,
                        help="Influx DB read password. If only write password is given this password will also be used for reading.")
    
    parser.add_argument("--influx-db-write-pw", type=str, default=None,
                        help="Influx DB write password. If only write password is given this password will also be used for reading.")
    
    parser.add_argument("--standalone", action="store_true",
                        help="Sets all backend settings to the defaults specified as part of $KARABO/var/containers/compose.yaml")
   
    args = parser.parse_args()

    karabo_path = args.init_to

    home = Path.home()
    
    os.makedirs(home/".karabo", exist_ok=True)
    dot_karabo = (home/".karabo"/"karaboFramework")

    if karabo_path is None:
        # check if we have .karabo file containing the path
        if os.path.exists(dot_karabo):
            with open(dot_karabo, "r") as f:
                karabo_path = f.read().strip()
        else:
            print("No .karabo file pointing to an existing installation found, please specify a path to using the --init-to option to create an installation!")
            exit(1)
    
    karabo_path = os.path.abspath(karabo_path)
    if not os.path.exists(karabo_path):
        # we create an environment
        print(f"Creating Karabo environment in {karabo_path}.")
        os.makedirs(karabo_path)

        # create symlinks to fill the subdirs the various Karabo scripts expect
        python_ex_dir = os.path.dirname(sys.executable)
        os.makedirs(f"{karabo_path}/extern", exist_ok=True)
        if CPP_PACKAGE_PATH is not None:
            print("Linking C++ dependent parts")
            
            os.symlink(f"{CPP_PACKAGE_PATH}/extern/lib", f"{karabo_path}/extern/lib")
            os.symlink(f"{CPP_PACKAGE_PATH}/extern/include", f"{karabo_path}/extern/include")
            os.symlink(f"{CPP_PACKAGE_PATH}/lib", f"{karabo_path}/lib")
            os.symlink(f"{CPP_PACKAGE_PATH}/include",f"{karabo_path}/include")
            os.symlink(f"{CPP_PACKAGE_PATH}/VERSION", f"{karabo_path}/VERSION")
        else:
            print("Skipping C++ dependent parts, because karabo.cpp is not installed")

        print(f"Linking {python_ex_dir} to {karabo_path}/extern/bin")
        os.symlink(python_ex_dir, f"{karabo_path}/extern/bin")

        if args.backbone or args.standalone:
            template = "default"
        else:
            template = "empty"

        src = os.path.abspath(f"{os.path.dirname(__file__)}/service.in/{template}")
        target = os.path.abspath(f"{karabo_path}/var/service")
        shutil.copytree(src, target)

        # replace the project server run file with a more easily configurable one
        if args.backbone or args.standalone:
            with open(os.path.abspath(f"{karabo_path}/var/service/karabo_projectDBServer/run"), "w") as f:
                f.write(files("karabo_services.overwrites").joinpath('karabo_projectDBServer.run').read_text())

            with open(os.path.abspath(f"{karabo_path}/var/service/karabo_dataLoggerManager/run"), "w") as f:
                f.write(files("karabo_services.overwrites").joinpath('karabo_dataLoggerManager.run').read_text())

      
        # create the plugins directory
        os.makedirs(f"{karabo_path}/plugins", exist_ok=True)

        #create var directories
        os.makedirs(f"{karabo_path}/var/data", exist_ok=True)
        os.makedirs(f"{karabo_path}/var/log/svscan", exist_ok=True)
        os.makedirs(f"{karabo_path}/var/environment", exist_ok=True)
        
        src = os.path.abspath(f"{os.path.dirname(__file__)}/containers")
        target = os.path.abspath(f"{karabo_path}/var/containers")
        shutil.copytree(src, target)

        if args.broker_host is None or args.standalone:
            broker = "amqp://xfel:karabo@localhost:5673"
            with open(f"{karabo_path}/var/environment/KARABO_BROKER", "w") as f:
                f.write(broker)
            
            print(f"Set Karabo broker host to {broker}.")

        if args.broker_topic is None or args.standalone:
            topic = "karabo"
            with open(f"{karabo_path}/var/environment/KARABO_BROKER_TOPIC", "w") as f:
                f.write(topic)
            
            print(f"Set Karabo broker topic to {topic}.")

        if args.project_db is None and not args.standalone:
            # default to a file backend
            with open(f"{karabo_path}/var/environment/KARABO_PROJECT_DB_BACKEND", "w") as f:
                f.write("file")
        
            print(f"Set project db backend to: file")
        elif args.standalone and args.project_db is None:
            
           
            with open(f"{karabo_path}/var/environment/KARABO_PROJECT_DB_HOST", "w") as f:
                f.write("localhost")

            print("Set project db backend host to 'localhost'.")
            
            with open(f"{karabo_path}/var/environment/KARABO_PROJECT_DB_PORT", "w") as f:
                f.write("8181")

            print("Set project db backend port to '8181'.")

            if args.project_db_user is None:
                with open(f"{karabo_path}/var/environment/KARABO_PROJECT_DB_USER", "w") as f:
                    f.write("admin")
        
                print("Set project db backend user to 'admin'.")

            if args.project_db_pw is None:
                with open(f"{karabo_path}/var/environment/KARABO_PROJECT_DB_PASSWORD", "w") as f:
                    f.write("change_me_please")
        
                print("Set project db backend user to 'change_me_please'.")
    
        if args.influx_db is None or args.standalone:
            # default to localhost
            with open(f"{karabo_path}/var/environment/KARABO_INFLUX_READ_URL", "w") as f:
                f.write("tcp://localhost:8086")

            with open(f"{karabo_path}/var/environment/KARABO_INFLUX_WRITE_URL", "w") as f:
                f.write("tcp://localhost:8086")

            print("Set Karabo logging backend to local InfluxDB at tcp://localhost:8086")


        if args.influx_db_name is None or args.standalone:
            with open(f"{karabo_path}/var/environment/KARABO_INFLUX_DBNAME", "w") as f:
                f.write("")

            print("Set Karabo logging database to the broker topic")

        if args.influx_db_read_user is None or args.standalone:
            user = "infadm"
            if args.influx_db_write_user is not None:
                user = args.influx_db_write_user
            with open(f"{karabo_path}/var/environment/KARABO_INFLUXDB_QUERY_USER", "w") as f:
                f.write(user)

            print(f"Set Influx DB read user to {user}")

        if args.influx_db_write_user is None or args.standalone:
            user  = "infadm"
            with open(f"{karabo_path}/var/environment/KARABO_INFLUXDB_WRITE_USER", "w") as f:
                f.write(user)

            print(f"Set Influx DB write user to {user}")

        if args.influx_db_read_pw is None or args.standalone:
            pw = "admpwd"
            if args.influx_db_write_pw is not None:
                pw = args.influx_db_write_pw
            with open(f"{karabo_path}/var/environment/KARABO_INFLUXDB_QUERY_PASSWORD", "w") as f:
                f.write(pw)

            print(f"Set Influx DB read password to {'*' * len(pw)}. Note that this password is contained in clear-text in {karabo_path}/var/environment/KARABO_INFLUXDB_QUERY_PASSWORD")

        if args.influx_db_write_pw is None or args.standalone:
            pw = "admpwd"
            with open(f"{karabo_path}/var/environment/KARABO_INFLUXDB_WRITE_PASSWORD", "w") as f:
                f.write(pw)

            print(f"Set Influx DB write password to {'*' * len(pw)}. Note that this password is contained in clear-text in {karabo_path}/var/environment/KARABO_INFLUXDB_QUERY_PASSWORD")


        with open(f"{karabo_path}/activate", "w") as f:
            f.write(ACTIVATE_SH.format(karabo_path=karabo_path))

    print("Checking environment for consistency")

    def check_dir(suffix):
        if not os.path.exists(f"{karabo_path}/{suffix}"):
            print(f"Expected subpath '{suffix}' in {karabo_path}, but found missing! Please reinit the Karabo environment into a new path!")
            exit(1)

    check_dir("extern")
    check_dir("lib")
    check_dir("include")
    check_dir("VERSION")
    check_dir("var")
    check_dir("activate")

    # update the .karabo file
    with open(dot_karabo, "w") as f:
        f.write(karabo_path)

    if args.broker_host is not None:
        with open(f"{karabo_path}/var/environment/KARABO_BROKER", "w") as f:
            f.write(args.broker_host)
        
        print(f"Set Karabo broker host to {args.broker_host}.")

    if args.broker_topic is not None:
        with open(f"{karabo_path}/var/environment/KARABO_BROKER_TOPIC", "w") as f:
            f.write(args.broker_topic)
        
        print(f"Set Karabo broker topic to {args.broker_topic}.")

    if args.project_db is not None:
        project_db_backend = "file" if args.project_db == "file" else "existDB"
        with open(f"{karabo_path}/var/environment/KARABO_PROJECT_DB_BACKEND", "w") as f:
            f.write(project_db_backend)
        
        if project_db_backend == "existDB":
            location = args.project_db.split("://")[-1]
            comps =  location.split(":")
            host = comps[0]
            with open(f"{karabo_path}/var/environment/KARABO_PROJECT_DB_HOST", "w") as f:
                f.write(host)
            if len(comps) == 2:
                port = comps[1]
            else:
                port = 8181
            with open(f"{karabo_path}/var/environment/KARABO_PROJECT_DB_PORT", "w") as f:
                f.write(port)
        
        print(f"Set Karabo project db to {project_db_backend}.")
    
    if args.project_db_user is not None:
        with open(f"{karabo_path}/var/environment/KARABO_PROJECT_DB_USER", "w") as f:
            f.write(args.project_db_user)

        print(f"Set project db backend user to '{args.project_db_user}'.")

    if args.project_db_pw is not None:
        with open(f"{karabo_path}/var/environment/KARABO_PROJECT_DB_PASSWORD", "w") as f:
            f.write(args.project_db_pw)

        print(f"Set project db backend user to '{args.project_db_pw}'.")

    if args.influx_db is not None:
        dbs = args.influx_db.split(",")
        if len(dbs) == 1:
            # read and write database are the same
            dbs.append(dbs[0])
        # default to localhost
        with open(f"{karabo_path}/var/environment/KARABO_INFLUX_READ_URL", "w") as f:
            f.write(dbs[0])

        with open(f"{karabo_path}/var/environment/KARABO_INFLUX_WRITE_URL", "w") as f:
            f.write(dbs[1])

        print(f"Set Karabo logging backend to local InfluxDB at {args.influx_db}")

    if args.influx_db_name is not None:
        with open(f"{karabo_path}/var/environment/KARABO_INFLUX_DBNAME", "w") as f:
                f.write(args.influx_db_name)

        print(f"Set Karabo logging database name to {args.influx_db_name}")

    if args.influx_db_read_user is not None:
        user = args.influx_db_read_user
        with open(f"{karabo_path}/var/environment/KARABO_INFLUXDB_QUERY_USER", "w") as f:
            f.write(user)

        print(f"Set Influx DB read user to {user}")

    if args.influx_db_write_user is not None:
        user = args.influx_db_write_user
        with open(f"{karabo_path}/var/environment/KARABO_INFLUXDB_WRITE_USER", "w") as f:
            f.write(user)

        print(f"Set Influx DB write user to {user}")

    if args.influx_db_read_pw is not None:
        pw = args.influx_db_read_pw
        with open(f"{karabo_path}/var/environment/KARABO_INFLUXDB_QUERY_PASSWORD", "w") as f:
            f.write(pw)

        print(f"Set Influx DB read password to {'*' * len(pw)}. Note that this password is contained in clear-text in {karabo_path}/var/environment/KARABO_INFLUXDB_QUERY_PASSWORD")

    if args.influx_db_write_pw is not None:
        pw = args.influx_db_write_pw
        with open(f"{karabo_path}/var/environment/KARABO_INFLUXDB_WRITE_PASSWORD", "w") as f:
            f.write(pw)

        print(f"Set Influx DB write password to {'*' * len(pw)}. Note that this password is contained in clear-text in {karabo_path}/var/environment/KARABO_INFLUXDB_WRITE_PASSWORD")

    print(f"Successfully set up Karabo environment in {karabo_path}. Run `source {karabo_path}/activate` to activate the environment.")

    
