import os
import argparse
import sys
import anatools
import re
import time

def get_package():
    # get the package name. if there are multiple then query the user as to which to use. ignore anatools
    d = os.path.join(".", "packages")
    subdirs = [os.path.join(d, o) for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))]
    package = None
    packages = []
    for subdir in subdirs:
        package = (os.path.basename(os.path.normpath(subdir)))
        if package != "anatools":
            packages.append(package)
    if len(packages) == 0:
        print("Error - No package found for node")
        sys.exit(1)
    elif len(packages) == 1:
        return packages[0]
    else:
        print("This channel has multiple packages:")
        for i, package in enumerate(packages):
            print(f"\t[{i}] {package}")
        package_number = int(input("Which package should contain the new node? "))
        return packages[package_number]

def main(args=None):

    parser = argparse.ArgumentParser(description='Create a new node from an example')
    parser.add_argument('--nodeName', help='Name of the node to create')
    parser.add_argument('--baseChannel', default="basic", help="Channel to draw examples from")
    parser.add_argument('--nodeType', help="Type of node to create")
    parser.add_argument('--package', help="Package that will contain the node")
    parser.add_argument('--description', help="What you want the node to do")
    parser.add_argument('--environment', default="prod", help="Which environment to query")
    parser.add_argument('--email', default=None)
    parser.add_argument('--password', default=None)
    parser.add_argument('--apiKey', default=None)
    parser.add_argument('--verbose', default=False)
    args = parser.parse_args()

    try:
        client = anatools.client(environment=args.environment, interactive=False, email=args.email, password=args.password, APIKey=args.apiKey, verbose=args.verbose)
    except:
        print("Unable to connect to LLM microservice")
        raise

    # get the name of the package to create the node in
    package = args.package
    if not package:
        try:
            package = get_package()
        except FileNotFoundError:
            print("Unable to open channel")
            print("Make sure you are in the root directory of the channel where you will create the node")
            sys.exit(1)

    # get a list of base channels and the valid node types for each
    channel_node_types = {}
    channel_node_type_list = client.get_llm_channel_node_types()
    # convert to dictionary for lookup
    for chan in channel_node_type_list:
        channel_node_types[chan["baseChannel"]] = chan["nodeTypes"]

    base_channel = args.baseChannel
    if base_channel not in channel_node_types:
        print(f"Unknown base channel '{base_channel}'")
        sys.exit(1)

    # get the node type
    node_type = args.nodeType
    if not node_type:
        print(f"The following node types are available in the '{base_channel}' base channel:")
        for i, n in enumerate(channel_node_types[base_channel]):
            print(f"\t[{i}] {n}")
        node_number = int(input("What type of node would you like to create? "))
        node_type = channel_node_types[base_channel][node_number]
    else:
        if node_type not in channel_node_types[base_channel]:
            print(f"Node type '{node_type}' is not available in base channel '{base_channel}'")
            sys.exit(1)

    # get the node name and module name
    node_name = args.nodeName
    if not node_name:
        node_name = input(f"What would you like to call the new node (use upper camel case): ")
    # convert name from camel case to snake case to get the module name
    module = re.sub(r'(?<!^)(?=[A-Z])', '_', node_name).lower()
    print(f"The node name will be '{node_name}' and the module name will be '{module}'")

    # get the description
    if not args.description:
        description = input("What would you like the node to do? ")
    else:
        description = args.description

    # create the prompt
    prompt_id = client.create_llm_prompt(description, base_channel, node_type, node_name)
    if not prompt_id:
        print("Service error when creating LLM prompt")
        sys.exit(1)

    retries = 0
    success = False
    while retries < 20:
        llm_response = client.get_llm_response(prompt_id)
        if llm_response is False:
            print("Service error retrieving LLM response")
            sys.exit(1)
        elif llm_response.get("status") == "queued":
            retries += 1
            time.sleep(3)
        elif llm_response.get("status") == "running":
            retries += 1
            time.sleep(3)
        elif llm_response.get("status") == "success":
            success = True
            break
        elif llm_response.get("status") == "failed":
            print("LLM query failed")
            sys.exit(1)
        else:
            print(f"Unknown response code {llm_response.get('status')}")
            sys.exit(1)

    if not success:
        print("Request timed out")
        sys.exit(1)

    yaml_path = os.path.join(".","packages", package, package, "nodes", module + ".yml")
    with open(yaml_path, "w") as f:
        f.write(llm_response["schemaResponse"])
    print(f"Created schema file: {yaml_path}")
    
    node_path = os.path.join(".","packages", package, package, "nodes", module + ".py")
    with open(node_path, "w") as f:
        f.write(llm_response["nodeResponse"])
    print(f"Created node file: {node_path}")

if __name__ == '__main__':
    sys.exit(main())