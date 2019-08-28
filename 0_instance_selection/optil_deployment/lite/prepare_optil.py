import os
import shutil

INSTANCE_COUNT = 20
CONFIGS = {
    'lite': {
        'input': 'full',
        'output': '../../../../../TestData/selection/vc/lite/output'    
    }
}


def make_dirs(key):
    root = 'optil'

    if os.path.exists(root):
        shutil.rmtree(root)
    os.mkdir(root)

    os.mkdir(os.path.join(root, 'private'))
    os.mkdir(os.path.join(root, 'public'))

def main():
    for key in CONFIGS.keys():
        make_dirs(key)
        
        config = CONFIGS[key]
        root = 'optil'

        for idx in range(1, INSTANCE_COUNT+1):
            pretty_idx = "{:03d}".format(idx)

            instance_type = 'private' if idx % 2 == 0 else 'public'

            input_file = os.path.join(config['input'], "vc-lite_{}.gr".format(pretty_idx))
            output_file = os.path.join(config['output'], instance_type, "vc-lite_{}.out".format(pretty_idx))
            
            dest_input_file = os.path.join(root, instance_type, "vc-lite_{}.in".format(pretty_idx))
            dest_output_file = os.path.join(root, instance_type, "vc-lite_{}.out".format(pretty_idx))

            shutil.copyfile(input_file, dest_input_file)
            shutil.copyfile(output_file, dest_output_file)
        
        private_zip = os.path.join(root, 'private.zip')
        public_zip = os.path.join(root, 'public.zip')

        os.system("zip -r -j {} {}".format(private_zip, os.path.join(root, 'private')))
        os.system("zip -r -j {} {}".format(public_zip, os.path.join(root, 'public')))

if __name__ == "__main__":
    main()