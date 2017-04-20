import os, os.path, re, json, sys

llvm_dirs = ["../llvm/lib/Transforms", "../llvm/lib/Analysis"]
llvm_passes = {}

for llvm_dir in llvm_dirs:
    llvm_passes[llvm_dir.split("/")[-1]] = { 'pass_class' : llvm_dir.split("/")[-1] }
    passes = llvm_passes[llvm_dir.split("/")[-1]]

    pass_dirs = [d for d in os.listdir(llvm_dir) if os.path.isdir("{0}/{1}".format(llvm_dir, d))]
    pass_dirs.append(".")

    for pass_dir in pass_dirs:
        for f in os.listdir("{0}/{1}".format(llvm_dir, pass_dir)):
            # Parses all files in directory
            if os.path.isfile("{0}/{1}/{2}".format(llvm_dir, pass_dir, f)) and f.split(".")[1] == "cpp":
                print("Processing: {0}/{1}/{2}".format(llvm_dir, pass_dir, f))

                with open("{0}/{1}/{2}".format(llvm_dir, pass_dir, f), 'r') as file:
                    data = file.read()

                    name         = ""
                    command      = ""
                    description  = ""
                    dependencies = {}
                    parameters   = {}

                    # Get details from INITIALIZE_PASS
                    if re.findall(r'(INITIALIZE_PASS)(_BEGIN)?(\(.*?\))', data, re.DOTALL):
                        init_info = re.findall(r'(INITIALIZE_PASS)(_BEGIN)?(\(.*?\))', data, re.DOTALL)

                        # Find pass name from INITIALIZE_PASS
                        name = init_info[0][2].split(",")[0].split("(")[1].strip("\n\t \"\'")

                        # Find pass command from INITIALIZE_PASS_BEGIN
                        command = "-" + init_info[0][2].split(",")[1].strip("\n\t \"\'")

                        # Find pass command from DEBUG_TYPE
                        if command.split("-")[1] == "DEBUG_TYPE" and \
                                re.findall(r'DEBUG_TYPE \".*\"', data):
                            command = re.findall(r'DEBUG_TYPE \".*\"', data)
                            command = "-" + command[0].split(" ")[1].strip("\n\t \"\'")

                        # Find pass description
                        description = init_info[0][2].split(",")[2].strip("\n\t \"\'")

                        # Find all pass dependencies
                        if re.findall(r'INITIALIZE_PASS_DEPENDENCY\(.*?\)', data, re.DOTALL):
                            for dep in re.findall(r'INITIALIZE_PASS_DEPENDENCY\(.*?\)', data, re.DOTALL):
                                dep_name = dep.split("(")[1].split(")")[0]
                                dependencies[dep_name] = { 'name': dep_name }

                    # Fallback for pass name and command
                    elif re.findall(r'DEBUG_TYPE \".*\"', data):
                        name = f.split(".")[0]
                        command = re.findall(r'DEBUG_TYPE \".*\"', data)
                        command = "-" + command[0].split(" ")[1].strip("\n\t \"\'")

                    # Find all pass parameters
                    if re.findall(r'static\s+cl::opt<.*?;', data, re.DOTALL):
                        for parameter in re.findall(r'static\s+cl::opt<.*?;', data, re.DOTALL):
                            parameter_name = parameter.split("\"")[1]
                            parameter_type = parameter.split("<")[1].split(">")[0]

                            parameters[parameter_name] = {
                                                            'command': "-{0}".format(parameter_name),
                                                            'type':    parameter_type
                                                         }

                            # Find initial values for parameters
                            if len(parameter.split("cl::init(")) > 1:
                                p_init = parameter.split("cl::init(")[1].split(")")[0]
                                parameters[parameter_name]['initial_value'] = p_init

                    # Saves pass only if an 'opt' command was found
                    if name == "":
                        print("Error initializing pass file \"{0}\": No pass command".format(f))
                    else:
                        current_pass = name
                        passes[name] = {
                                            'name': name,
                                            'command': command,
                                            'description': description,
                                            'parameters': parameters,
                                            'dependencies': dependencies
                                       }

with open("llvm_passes.json", "w") as file:
    json.dump(llvm_passes, file, indent = 4, sort_keys = True)
