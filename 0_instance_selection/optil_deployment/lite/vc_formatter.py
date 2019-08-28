import os
import shutil

def main():
    for root, dirs, files in os.walk('.'):
        for file in files:
            if '.gr' not in file or 'vc-lite' in file:
                continue
            
            rel_file = os.path.join(root, file)
            dest_rel_file = os.path.join(root, 'vc-lite_{}'.format(file))

            # print(rel_file, dest_rel_file)
            shutil.move(rel_file, dest_rel_file)

if __name__ == "__main__":
    main()
