import os
import sys
import subprocess
import tarfile
from csv import DictWriter

BZ_FILE = "pace2019-vc-___-public.tar.bz2"
CSV_FILE = "pace2019-vc-___-public.csv"

def write_sha1_csv(bz_file_name, output_csv_name):
    with open(output_csv_name, "w") as csv_file:
        fieldnames = ["sha1sum", "file_name"]
        writer = DictWriter(csv_file, fieldnames=fieldnames, delimiter=',')

        writer.writeheader()

        csv_lines = []

        def add_sha1sum(filename):
            result = subprocess.check_output("sha1sum {}".format(filename), shell=True).decode('utf-8')
            tokens = result.split()
            tokens[1] = os.path.basename(tokens[1])
            row = {}
            for i, field in enumerate(fieldnames):
                row[field] = tokens[i]
            
            csv_lines.append(row)

        add_sha1sum(bz_file_name)

        tar = tarfile.open(bz_file_name, "r:bz2")
        
        for tarinfo in tar:
            if not tarinfo.isreg():
                continue
            
            f = tar.extractfile(tarinfo)
            name = os.path.basename(tarinfo.name)

            with open(name, "w") as temp_file:
                temp_file.write(f.read().decode('utf-8'))
            
            add_sha1sum(name)
            os.system("rm {}".format(name))
        
        csv_lines = sorted(csv_lines, key=lambda x: x["file_name"])
        for csv_line in csv_lines:
            writer.writerow(csv_line)

def main():
    ds = ['exact', 'lite']

    for d in ds:
        bz_file = os.path.join(d, BZ_FILE.replace("___", d))
        output_csv = os.path.join(d, CSV_FILE.replace("___", d))
        public_files = d

        # print(bz_file, public_files)
        os.system("tar -cjvf {} -C {} public".format(bz_file, public_files, d))
        write_sha1_csv(bz_file, output_csv)

if __name__ == "__main__":
    main()