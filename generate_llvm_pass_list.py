import os, os.path, re

llvm_dir = "../llvm/lib/Transforms"

passes = {}

for pass_dir in [d for d in os.listdir(llvm_dir) if os.path.isdir("{0}/{1}".format(llvm_dir, d))]:
    for f in os.listdir("{0}/{1}".format(llvm_dir, pass_dir)):
        if f.split(".")[1] == "cpp":
            print("{0}/{1}/{2}".format(llvm_dir, pass_dir, f))
            current_pass = f.split(".")[0]
            passes[current_pass] = {
                                        'name': current_pass,
                                        'parameters': {}
                                   }

            with open("{0}/{1}/{2}".format(llvm_dir, pass_dir, f), 'r') as file:
                data = file.read()
                if re.findall(r'DEBUG_TYPE \".*\"', data):
                    name = re.findall(r'DEBUG_TYPE \".*\"', data)
                    name = name[0].split(" ")[1][1:-1]

                    if name not in passes.keys():
                        passes[current_pass]['command'] = "-{0}".format(name)

                if re.findall(r'static\s+cl::opt<.*?;', data, re.DOTALL):
                    for parameter in re.findall(r'static\s+cl::opt<.*?;', data, re.DOTALL):
                        parameter_name = parameter.split("\"")[1]
                        parameter_type = parameter.split("<")[1].split(">")[0]

                        passes[current_pass]['parameters'][parameter_name] = {
                                                                'command': "-{0}".format(parameter_name),
                                                                'type':    parameter_type
                                                            }

                        if len(parameter.split("cl::init(")) > 1:
                            p_init = parameter.split("cl::init(")[1].split(")")[0]
                            passes[current_pass]['parameters'][parameter_name]['initial_value'] = p_init

for p in passes.values():
    print(p['name'], p['parameters'])
