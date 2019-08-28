import os
import shutil

def main():
    ds = ['full', 'public']
    for d in ds:
        for root, dirs, files in os.walk(d):
            for file in files:
                if '.in' not in file:
                    continue
                
                rel_file = os.path.join(root, file)
                dest_rel_file = os.path.join(root, file.replace('.in', '.gr'))

                # print(rel_file, dest_rel_file)
                shutil.move(rel_file, dest_rel_file)

if __name__ == "__main__":
    main()
